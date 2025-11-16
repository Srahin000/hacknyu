"""
Backend server for controlling voice assistant from webapp
Provides REST API to start/stop voice assistant and WebSocket for status updates
"""

import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional
import os
import json
import threading
import queue
import time
import asyncio
import signal

app = FastAPI()

# CORS middleware for webapp
# Allow all localhost origins for development (more permissive)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",  # Allow any localhost port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global process reference
voice_assistant_process: Optional[subprocess.Popen] = None
assistant_status = {
    "running": False,
    "status": "stopped",  # stopped, starting, listening, generating, talking, idle
    "conversation_count": 0
}

# Log streaming
log_queue: queue.Queue = queue.Queue()
log_listeners: set = set()


class StatusResponse(BaseModel):
    running: bool
    status: str
    conversation_count: int


def stream_process_logs(process: subprocess.Popen):
    """Stream process stdout/stderr to log queue"""
    global assistant_status
    
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            line = line.rstrip()
            if line:
                # Add timestamp
                timestamp = time.strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {line}"
                log_queue.put(log_entry)
                # Broadcast to all listeners
                for listener in list(log_listeners):
                    try:
                        listener.put(log_entry)
                    except:
                        log_listeners.discard(listener)
    except Exception as e:
        log_entry = f"[ERROR] Log streaming failed: {e}"
        log_queue.put(log_entry)
    finally:
        # Check process exit status
        exit_code = process.poll()
        if exit_code is not None:
            timestamp = time.strftime("%H:%M:%S")
            if exit_code == 0:
                log_entry = f"[{timestamp}] Voice assistant process ended normally"
            else:
                log_entry = f"[{timestamp}] ❌ Voice assistant process crashed with exit code {exit_code}"
                assistant_status["status"] = "stopped"
                assistant_status["running"] = False
            
            log_queue.put(log_entry)
            
            # Broadcast to listeners
            for listener in list(log_listeners):
                try:
                    listener.put(log_entry)
                except:
                    log_listeners.discard(listener)


@app.get("/api/logs/stream")
async def stream_logs():
    """Stream logs using Server-Sent Events (SSE)"""
    async def event_generator():
        # Create a queue for this client
        client_queue = queue.Queue()
        log_listeners.add(client_queue)
        
        try:
            # Send initial message
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            
            # Send any existing logs from the queue
            while not log_queue.empty():
                try:
                    log_entry = log_queue.get_nowait()
                    yield f"data: {json.dumps({'type': 'log', 'message': log_entry})}\n\n"
                except queue.Empty:
                    break
            
            # Stream new logs
            while True:
                try:
                    # Check client queue for new logs (with timeout for graceful shutdown)
                    log_entry = client_queue.get(timeout=1)
                    yield f"data: {json.dumps({'type': 'log', 'message': log_entry})}\n\n"
                except queue.Empty:
                    # Send keepalive
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
        except asyncio.CancelledError:
            # Client disconnected or server shutting down
            pass
        finally:
            log_listeners.discard(client_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def count_conversations():
    """Count total conversations from metadata files"""
    conversations_dir = Path("conversations")
    if not conversations_dir.exists():
        return 0
    
    count = 0
    for date_dir in conversations_dir.iterdir():
        if date_dir.is_dir():
            for conv_dir in date_dir.iterdir():
                if conv_dir.is_dir() and conv_dir.name.startswith("conv_"):
                    metadata_file = conv_dir / "metadata.json"
                    if metadata_file.exists():
                        count += 1
    return count


@app.options("/api/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.get("/api/status")
async def get_status():
    """Get current voice assistant status"""
    global voice_assistant_process, assistant_status
    
    # Check if process is still running
    if voice_assistant_process and voice_assistant_process.poll() is not None:
        exit_code = voice_assistant_process.poll()
        if assistant_status["running"]:
            # Process just died
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] ⚠️ Voice assistant process died unexpectedly (exit code: {exit_code})"
            log_queue.put(log_entry)
        
        assistant_status["running"] = False
        assistant_status["status"] = "stopped"
        voice_assistant_process = None
    
    # Update conversation count
    assistant_status["conversation_count"] = count_conversations()
    
    return assistant_status


@app.post("/api/start")
async def start_assistant():
    """Start the voice assistant"""
    global voice_assistant_process, assistant_status
    
    if assistant_status["running"]:
        return JSONResponse(
            {"error": "Voice assistant is already running"},
            status_code=400
        )
    
    try:
        # Get the script path
        script_path = Path(__file__).parent / "harry_voice_assistant.py"
        
        if not script_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Voice assistant script not found: {script_path}"
            )
        
        # Start the voice assistant process
        assistant_status["running"] = True
        assistant_status["status"] = "starting"
        
        # Start process (non-blocking)
        # Note: Voice assistant takes time to initialize (loading models, etc.)
        # Use unbuffered Python output (-u flag) to see logs immediately
        voice_assistant_process = subprocess.Popen(
            [sys.executable, "-u", str(script_path)],  # -u for unbuffered output
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(script_path.parent),  # Run from project directory for imports
            env={**os.environ, "PYTHONUNBUFFERED": "1"}  # Force unbuffered
        )
        
        # Send initial log message
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] Voice assistant process started (PID: {voice_assistant_process.pid})"
        log_queue.put(log_entry)
        
        # Start log streaming thread
        log_thread = threading.Thread(
            target=stream_process_logs,
            args=(voice_assistant_process,),
            daemon=True
        )
        log_thread.start()
        
        # Wait a moment to see if process crashes immediately
        time.sleep(0.5)
        if voice_assistant_process.poll() is not None:
            # Process already exited
            exit_code = voice_assistant_process.poll()
            log_entry = f"[{time.strftime('%H:%M:%S')}] ❌ Voice assistant failed to start (exit code: {exit_code})"
            log_queue.put(log_entry)
            assistant_status["running"] = False
            assistant_status["status"] = "stopped"
            raise HTTPException(
                status_code=500,
                detail=f"Voice assistant crashed immediately with exit code {exit_code}"
            )
        
        # Status will be "starting" - the voice assistant will take time to initialize
        # The webapp will poll status and see when it's ready
        assistant_status["status"] = "starting"
        log_entry = f"[{time.strftime('%H:%M:%S')}] Waiting for voice assistant to initialize..."
        log_queue.put(log_entry)
        
        return {
            "success": True,
            "message": "Voice assistant started",
            "pid": voice_assistant_process.pid
        }
        
    except Exception as e:
        assistant_status["running"] = False
        assistant_status["status"] = "stopped"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start voice assistant: {str(e)}"
        )


@app.post("/api/stop")
async def stop_assistant():
    """Stop the voice assistant"""
    global voice_assistant_process, assistant_status
    
    if not assistant_status["running"] or voice_assistant_process is None:
        return JSONResponse(
            {"error": "Voice assistant is not running"},
            status_code=400
        )
    
    try:
        # Terminate the process
        voice_assistant_process.terminate()
        
        # Wait a bit for graceful shutdown
        try:
            voice_assistant_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't stop
            voice_assistant_process.kill()
            voice_assistant_process.wait()
        
        voice_assistant_process = None
        assistant_status["running"] = False
        assistant_status["status"] = "stopped"
        
        return {
            "success": True,
            "message": "Voice assistant stopped"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop voice assistant: {str(e)}"
        )


def cleanup_on_shutdown():
    """Cleanup function called on shutdown"""
    global voice_assistant_process
    print("\n[Shutdown] Cleaning up...")
    
    # Stop voice assistant if running
    if voice_assistant_process and voice_assistant_process.poll() is None:
        print("[Shutdown] Stopping voice assistant process...")
        try:
            voice_assistant_process.terminate()
            voice_assistant_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            voice_assistant_process.kill()
            voice_assistant_process.wait()
        except Exception as e:
            print(f"[Shutdown] Error stopping process: {e}")
    
    print("[Shutdown] Cleanup complete.")


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        cleanup_on_shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("="*70)
    print(" Voice Assistant Control Server ".center(70))
    print("="*70)
    print("\nStarting server on http://localhost:8000")
    print("API endpoints:")
    print("  GET  /api/status - Get assistant status")
    print("  POST /api/start  - Start voice assistant")
    print("  POST /api/stop   - Stop voice assistant")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        cleanup_on_shutdown()
    finally:
        cleanup_on_shutdown()

