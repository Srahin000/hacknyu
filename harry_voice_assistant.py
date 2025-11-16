"""
Harry Potter Voice Assistant - Complete Pipeline

Flow:
1. Wake Word Detection (Picovoice) - "Harry Potter"
2. Start Listening (8 seconds)
3. Speech-to-Text (Whisper)
4. LLM Response (Llama 3.2 via llama.cpp)
5. Text-to-Speech (XTTS v2)

This is the COMPLETE voice assistant pipeline!
"""

import sys
import struct
import os
import time
import json
from datetime import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
import asyncio
from threading import Thread
from typing import Set, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    try:
        # Only wrap if not already wrapped and buffer exists
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError):
        # If wrapping fails, just continue with the default stdout/stderr
        pass


class WebSocketServer:
    """WebSocket server for broadcasting avatar state changes"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.clients: Set = set()
        self.server = None
        self.server_thread: Optional[Thread] = None
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        print(f"[WebSocket] Client connected. Total clients: {len(self.clients)}")
        # Send initial idle state
        await self.broadcast_state('idle')
        
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        print(f"[WebSocket] Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.clients.discard(client)
    
    async def broadcast_state(self, state: str):
        """Broadcast avatar state change"""
        # Map internal states to avatar states
        avatar_state = state
        if state == 'generating':
            # Generating is not an avatar animation state, but we still broadcast it
            # The webapp will show it in the status indicator
            avatar_state = 'idle'  # Avatar stays idle while generating
        elif state not in ['idle', 'listening', 'talking']:
            avatar_state = 'idle'  # Default to idle for unknown states
        
        await self.broadcast({
            'type': 'state',
            'state': avatar_state,
            'internal_state': state  # Include internal state for status tracking
        })
    
    async def broadcast_audio(self, audio_url: str):
        """Broadcast audio file URL"""
        await self.broadcast({
            'type': 'audio',
            'url': audio_url
        })
    
    async def handler(self, websocket):
        """Handle WebSocket connections"""
        await self.register_client(websocket)
        try:
            # Keep connection alive
            async for message in websocket:
                # Echo back or handle client messages if needed
                pass
        except Exception as e:
            print(f"[WebSocket] Connection error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            import websockets
            print(f"[WebSocket] Creating server on localhost:{self.port}...")
            self.loop = asyncio.get_event_loop()
            self.server = await websockets.serve(
                self.handler,
                "localhost",
                self.port
            )
            self.running = True
            print(f"[WebSocket] ✅ Server started successfully on ws://localhost:{self.port}")
            print(f"[WebSocket] Server is ready to accept connections")
            await asyncio.Future()  # Run forever
        except OSError as e:
            if "Address already in use" in str(e) or "Only one usage of each socket address" in str(e):
                print(f"[WebSocket] ⚠️  Port {self.port} is already in use. Trying to continue...")
                self.running = False
            else:
                import traceback
                print(f"[WebSocket] ❌ Failed to start server: {e}")
                print(traceback.format_exc())
                self.running = False
        except Exception as e:
            import traceback
            print(f"[WebSocket] ❌ Failed to start server: {e}")
            print(traceback.format_exc())
            self.running = False
    
    def start(self):
        """Start WebSocket server in background thread"""
        try:
            self.server_thread = Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            # Give it a moment to start
            time.sleep(0.5)
        except Exception as e:
            print(f"[WebSocket] Failed to start server thread: {e}")
    
    def _run_server(self):
        """Run the asyncio server in a thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = loop
            print(f"[WebSocket] Starting server thread on port {self.port}...")
            loop.run_until_complete(self.start_server())
        except Exception as e:
            import traceback
            error_msg = f"[WebSocket] Server thread error: {e}\n{traceback.format_exc()}"
            print(error_msg)
            self.running = False
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        if self.server:
            self.server.close()


class HarryVoiceAssistant:
    """Complete voice assistant for Harry Potter"""
    
    def __init__(self, enable_context=True, enable_insights=True):
        """
        Initialize all components
        
        Args:
            enable_context: Enable conversation context (loads insights from previous conversations)
            enable_insights: Enable automatic insight generation after each conversation
        """
        
        print("\n" + "="*70)
        print(" ⚡ HARRY POTTER VOICE ASSISTANT ⚡".center(70))
        print(" 🚀 NPU-Powered with Qualcomm Genie ".center(70))
        print("="*70)
        print()
        
        # Component status
        self.wake_word_ready = False
        self.wake_word_type = None  # "picovoice" or "keyboard"
        self.stt_ready = False
        self.llm_ready = False
        self.tts_ready = False
        self.emotion_ready = False
        self.stt_type = None  # Will be set in _init_stt
        self.tts_type = None  # Will be set in _init_tts
        self.emotion_type = None  # Will be set in _init_emotion
        self.enable_context = enable_context
        self.enable_insights = enable_insights
        
        # Storage setup
        self.storage_dir = Path("conversations")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Single audio folder for ALL audio files
        self.audio_dir = Path("audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        self.conversation_count = 0
        
        # WebSocket server for avatar communication (will be initialized AFTER models load)
        self.websocket_server: Optional[WebSocketServer] = None
        self.current_avatar_state = 'idle'
        
        # Context manager (reads insights)
        self.context_manager = None
        if self.enable_context:
            try:
                from context_manager import ContextManager
                self.context_manager = ContextManager()
                print("🧠 Context enabled (loads previous conversation insights)")
            except Exception as e:
                print(f"⚠️  Context system disabled: {e}")
                self.enable_context = False
        
        # User/Child management
        self.user_manager = None
        self.current_user = None
        self.current_child = None
        try:
            from user_child_manager import UserChildManager
            self.user_manager = UserChildManager()
            # Ensure default user/child exists
            self.current_user, self.current_child = self.user_manager.ensure_default_setup()
            print(f"👤 User: {self.current_user['name']} ({self.current_user['email']})")
            print(f"👶 Child: {self.current_child['name']} (ID: {self.current_child['childId']})")
        except Exception as e:
            print(f"⚠️  User/Child management disabled: {e}")
            self.current_child = {"childId": "child-default"}
        
        # Conversation analyzer (generates insights in background)
        self.analyzer = None
        if self.enable_insights:
            try:
                from conversation_analyzer import ConversationAnalyzer
                self.analyzer = ConversationAnalyzer(cpu_mode=False)  # Use NPU for analysis
                print("🔍 Insight generation enabled (analyzes conversations in background)")
            except Exception as e:
                print(f"⚠️  Insight generation disabled: {e}")
                self.enable_insights = False
        
        # TTS parameters for Harry Potter cloned voice
        self.voice_sample_path = Path("sound_sample/harry_sample.wav")
        if not self.voice_sample_path.exists():
            print(f"⚠️  Voice sample not found: {self.voice_sample_path}")
            print("   Voice cloning will not work without the sample file!")
        
        # Note: XTTS v2 voice cloning uses the sample directly
        # Speed/pitch/emotion control is limited in cloning mode
        
        # Initialize components
        self._init_wake_word()
        self._init_stt()
        self._init_llm()
        self._init_tts()
        self._init_emotion()
        
        # Check if ready (emotion is optional)
        if not all([self.wake_word_ready, self.stt_ready, self.llm_ready, self.tts_ready]):
            print("\n❌ Not all critical components ready!")
            sys.exit(1)
        
        # NOW start WebSocket server (after PyTorch/models loaded to avoid threading conflicts)
        try:
            print("\n🌐 Starting WebSocket server for avatar communication...")
            self.websocket_server = WebSocketServer(port=8765)
            self.websocket_server.start()
            # Give it time to bind to the port
            time.sleep(1.5)
            # Check if server is actually running
            if self.websocket_server.running:
                print("  ✅ WebSocket server ready on ws://localhost:8765")
            else:
                print("  ⚠️  WebSocket server may not be running properly")
        except Exception as e:
            import traceback
            print(f"  ⚠️  WebSocket server failed (avatar features disabled): {e}")
            self.websocket_server = None
        
        print("\n" + "="*70)
        print("✅ ALL SYSTEMS READY!".center(70))
        print("="*70)
        print()
    
    def _init_wake_word(self):
        """Initialize Picovoice wake word detection with fallback"""
        print("🔊 [1/4] Initializing Wake Word Detection...")
        
        try:
            import pvporcupine
            from dotenv import load_dotenv
            
            load_dotenv()
            access_key = os.getenv('PICOVOICE_ACCESS_KEY')
            
            if not access_key:
                print("  ⚠️  PICOVOICE_ACCESS_KEY not found in .env")
                print("     Get your free key at: https://console.picovoice.ai/")
                print("     Using keyboard fallback (press ENTER to activate)")
                self.wake_word_type = "keyboard"
                self.wake_word_ready = True
                return
            
            ppn_file = Path("ppn_files/Harry-Potter_en_windows_v3_0_0.ppn")
            if not ppn_file.exists():
                print(f"  ⚠️  Wake word file not found: {ppn_file}")
                print("     Using keyboard fallback (press ENTER to activate)")
                self.wake_word_type = "keyboard"
                self.wake_word_ready = True
                return
            
            # Try to create Porcupine with better error handling
            try:
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keyword_paths=[str(ppn_file)]
                )
                self.wake_word_type = "picovoice"
                self.wake_word_ready = True
                print("  ✅ Wake word ready: 'Harry Potter' (Picovoice)")
            except Exception as create_error:
                error_str = str(create_error)
                if "00000136" in error_str or "136" in error_str:
                    print("  ⚠️  Picovoice initialization failed (code 136)")
                    print("     Common causes:")
                    print("     - Invalid or expired access key")
                    print("     - Platform/architecture mismatch")
                    print("     - Missing system dependencies")
                    print("     Using keyboard fallback (press ENTER to activate)")
                else:
                    print(f"  ⚠️  Picovoice error: {create_error}")
                    print("     Using keyboard fallback (press ENTER to activate)")
                self.wake_word_type = "keyboard"
                self.wake_word_ready = True
            
        except ImportError:
            print("  ⚠️  pvporcupine not installed")
            print("     Install with: pip install pvporcupine")
            print("     Using keyboard fallback (press ENTER to activate)")
            self.wake_word_type = "keyboard"
            self.wake_word_ready = True
        except Exception as e:
            print(f"  ⚠️  Wake word error: {e}")
            print("     Using keyboard fallback (press ENTER to activate)")
            self.wake_word_type = "keyboard"
            self.wake_word_ready = True
    
    def _init_stt(self):
        """Initialize Speech-to-Text (Whisper NPU only)"""
        print("🎤 [2/4] Initializing Speech-to-Text...")
        
        try:
            # Use NPU Whisper (encoder + decoder on Snapdragon X Elite)
            from whisper_npu_full import WhisperNPU
            print("  Loading Whisper on NPU...")
            self.stt_model = WhisperNPU()
            self.stt_type = "whisper-npu"
            print(f"  ✅ Using NPU Whisper ({self.stt_model.inference_type})")
            self.stt_ready = True
            
        except Exception as e:
            print(f"  ❌ NPU Whisper failed: {e}")
            print(f"     Make sure Whisper models are deployed to NPU")
            print(f"     See: WHISPER_NPU_FIX.md")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _init_llm(self):
        """Initialize LLM (NPU Genie only)"""
        print("🧠 [3/4] Initializing Harry Potter AI...")
        
        try:
            from harry_llm_npu import HarryPotterNPU
            self.harry = HarryPotterNPU()
            self.llm_ready = True
            print("  ✅ Harry Potter AI loaded (Qualcomm Genie on NPU)")
        except Exception as e:
            print(f"  ❌ Genie LLM failed: {e}")
            print(f"     Make sure Genie bundle is properly configured")
            print(f"     Test with: python run_genie_safe.py \"Hello\"")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _init_emotion(self):
        """Initialize Emotion Detection (NPU or skip)"""
        print("😊 [4/5] Initializing Emotion Detection...")
        
        # DISABLED FOR HACKATHON SPEED - emotion model is slow to load
        print("  ⚠️  Emotion detection disabled (for faster startup)")
        print("     Enable by uncommenting code in _init_emotion()")
        self.emotion_detector = None
        self.emotion_type = "none"
        self.emotion_ready = False
        return
        
        # Uncomment below to enable emotion detection:
        # try:
        #     from emotion_npu import EmotionNPU
        #     self.emotion_detector = EmotionNPU()
        #     self.emotion_type = self.emotion_detector.inference_type
        #     self.emotion_ready = True
        #     print(f"  ✅ Emotion detection ready ({self.emotion_type})")
        # except Exception as e:
        #     print(f"  ⚠️  Emotion detection not available: {e}")
        #     print("     Continuing without emotion detection...")
        #     self.emotion_detector = None
        #     self.emotion_type = "none"
        #     self.emotion_ready = False
    
    def _init_tts(self):
        """Initialize Text-to-Speech (pyttsx3 for now)"""
        print("🔊 [5/5] Initializing Text-to-Speech...")
        
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 160)
            self.tts_engine.setProperty('volume', 0.9)
            
            # Try to find a good voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_type = "pyttsx3"
            self.tts_ready = True
            print(f"  ✅ Text-to-Speech ready (pyttsx3)")
            
        except Exception as e:
            print(f"  ❌ TTS error: {e}")
            print(f"     Install with: pip install pyttsx3")
            self.tts_type = "none"
            self.tts_ready = False
    
    def listen_for_wake_word(self):
        """Listen for 'Harry Potter' wake word or keyboard input"""
        
        if self.wake_word_type == "keyboard":
            # Keyboard fallback: wait for ENTER key
            input("Press ENTER to activate...")
            return True
        
        # Picovoice wake word detection
        stream = sd.InputStream(
            channels=1,
            samplerate=self.porcupine.sample_rate,
            blocksize=self.porcupine.frame_length,
            dtype='int16'
        )
        
        stream.start()
        
        try:
            frame_count = 0
            while True:
                # Read audio frame
                audio_frame, _ = stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, audio_frame)
                
                # Check for wake word
                keyword_index = self.porcupine.process(pcm)
                
                # Visual feedback
                frame_count += 1
                if frame_count % 30 == 0:  # Every ~1 second
                    print(".", end='', flush=True)
                
                if keyword_index >= 0:
                    return True
                    
        finally:
            stream.stop()
            stream.close()
    
    def record_audio(self, duration=8):
        """Record audio for specified duration"""
        
        sample_rate = 16000
        
        print("\n🎤 LISTENING... (speak now!)")
        print("=" * 70)
        
        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        
        # Show countdown
        for i in range(duration):
            remaining = duration - i
            print(f"\r🔴 Recording... {remaining} seconds left    ", end='', flush=True)
            time.sleep(1)
        
        sd.wait()
        print("\r✅ Recording complete!                    ")
        
        audio = audio.flatten()
        
        # AUTO-GAIN BOOST: Fix quiet microphones
        max_amplitude = np.abs(audio).max()
        if max_amplitude > 0:
            # Target amplitude is 0.5 (leaves headroom for peaks)
            target_amplitude = 0.5
            gain = target_amplitude / max_amplitude
            
            # Limit gain to prevent noise amplification
            # If original is super quiet (<0.01), something is wrong, cap the gain
            if max_amplitude < 0.01:
                gain = min(gain, 20.0)  # Max 20x boost for very quiet audio
            elif max_amplitude < 0.1:
                gain = min(gain, 10.0)  # Max 10x boost for quiet audio
            else:
                gain = min(gain, 5.0)   # Max 5x boost for normal-ish audio
            
            audio = audio * gain
            
            # Clip to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)
        
        return audio, sample_rate
    
    def save_conversation(self, audio, sample_rate, transcription, harry_response, conversation_id, emotion_data=None):
        """Save audio file and transcript to organized conversation folder ONLY"""
        
        # Create timestamp for this conversation
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")
        
        # Create date directory
        date_dir = self.storage_dir / date_str
        date_dir.mkdir(exist_ok=True)
        
        # Create conversation directory
        conv_dir = date_dir / f"conv_{conversation_id:04d}_{time_str}"
        conv_dir.mkdir(exist_ok=True)
        
        # Save user audio in conversation folder (NOT in audio/ folder - that's for TTS only)
        audio_path_organized = conv_dir / "user_audio.wav"
        sf.write(str(audio_path_organized), audio, sample_rate)
        
        # Build transcript content with emotion if available
        transcript_parts = [
            f"Conversation #{conversation_id}",
            f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"{'=' * 70}",
            ""
        ]
        
        if emotion_data and emotion_data[0]:
            emotion, confidence, _, _ = emotion_data
            transcript_parts.append(f"EMOTION: {emotion.upper()} ({confidence*100:.0f}% confidence)")
            transcript_parts.append("")
        
        transcript_parts.extend([
            f"USER:\n{transcription}",
            "",
            f"HARRY:\n{harry_response}"
        ])
        
        transcript_content = "\n".join(transcript_parts)
        
        # Save transcript in conversation folder
        transcript_path_organized = conv_dir / "transcript.txt"
        with open(transcript_path_organized, 'w', encoding='utf-8') as f:
            f.write(transcript_content)
        
        # Build metadata JSON
        metadata = {
            "conversation_id": conversation_id,
            "timestamp": timestamp.isoformat(),
            "date": date_str,
            "time": time_str,
            "user_query": transcription,
            "harry_response": harry_response,
            "sample_rate": sample_rate,
            "audio_duration_seconds": len(audio) / sample_rate,
            "stt_type": self.stt_type,
            "tts_type": self.tts_type,
            "emotion_type": self.emotion_type,
            "wake_word_type": self.wake_word_type
        }
        
        # Add user/child IDs if available
        if self.current_user:
            metadata["userId"] = self.current_user.get("userId")
        if self.current_child:
            metadata["childId"] = self.current_child.get("childId")
        
        # Add emotion data if available
        if emotion_data and emotion_data[0]:
            emotion, confidence, latency, all_scores = emotion_data
            metadata["emotion"] = {
                "detected": emotion,
                "confidence": confidence,
                "latency_ms": latency,
                "all_scores": all_scores
            }
        
        # Save metadata JSON in organized folder
        metadata_path = conv_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation saved: {conv_dir.name}/")
        
        return conv_dir
    
    def detect_emotion(self, audio, sample_rate):
        """Detect emotion from audio"""
        
        if not self.emotion_ready or self.emotion_detector is None:
            return None, 0.0, 0, {}
        
        try:
            emotion, confidence, latency, all_scores = self.emotion_detector.detect_emotion(audio, sample_rate)
            print(f"😊 Emotion detected: {emotion.upper()} ({confidence*100:.0f}% confidence, {latency}ms on {self.emotion_type})")
            return emotion, confidence, latency, all_scores
        except Exception as e:
            print(f"⚠️  Emotion detection failed: {e}")
            return None, 0.0, 0, {}
    
    def transcribe_audio(self, audio, sample_rate):
        """Transcribe audio to text using Whisper (NPU or CPU)"""

        if self.stt_type == "whisper-npu":
            print("🔄 Transcribing on NPU...", end='', flush=True)
        else:
            print("🔄 Transcribing on CPU...", end='', flush=True)

        try:
            transcription, latency = self.stt_model.transcribe(audio, sample_rate)
            if self.stt_type == "whisper-npu":
                print(f"\r✅ Transcribed! ({latency}ms on NPU)       ")
            else:
                print(f"\r✅ Transcribed! ({latency}ms on CPU)       ")
            return transcription

        except Exception as e:
            print(f"\r❌ Transcription failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_harry_response(self, text):
        """Get response from Harry Potter AI with context from previous conversations"""
        
        print("🧠 Harry is thinking...", end='', flush=True)
        
        try:
            # Add context from previous conversations if enabled
            if self.enable_context and self.context_manager:
                context = self.context_manager.build_context_for_harry()
                if context:
                    # Prepend context to the user's question
                    text_with_context = context + "\n\nCURRENT QUESTION: " + text
                else:
                    text_with_context = text
            else:
                text_with_context = text
            
            # Generate Harry's response
            response, latency = self.harry.ask_harry(text_with_context)
            print(f"\r✅ Response ready! ({latency}ms)     ")
            return response
            
        except Exception as e:
            print(f"\r❌ LLM error: {e}")
            return None
    
    def speak(self, text, conversation_id=None, conv_dir=None):
        """Speak text using pyttsx3 and broadcast to avatar"""
        
        print(f"🔊 Harry speaks: \"{text}\"")
        
        # Broadcast talking state
        self._broadcast_state('talking')
        
        if not self.tts_ready:
            self._broadcast_state('idle')
            return None
        
        try:
            if self.tts_type == "pyttsx3":
                # ALWAYS use timestamped filename for webapp accessibility
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"harry_{timestamp}.wav"
                
                # Save to main audio directory (for webapp)
                audio_path = self.audio_dir / audio_filename
                
                # Also save to conversation directory if available
                if conversation_id and conv_dir:
                    conv_audio_path = conv_dir / "harry_response.wav"
                else:
                    conv_audio_path = None
                
                # Generate audio file
                print(f"[TTS] Generating audio file: {audio_path}")
                self.tts_engine.save_to_file(text, str(audio_path))
                self.tts_engine.runAndWait()
                
                # Wait for file to be written
                time.sleep(0.2)
                
                # Check if file was created
                if not audio_path.exists():
                    print(f"[TTS] ❌ Audio file was not created: {audio_path}")
                    self._broadcast_state('idle')
                    return None
                
                print(f"[TTS] ✅ Audio file created: {audio_path} ({audio_path.stat().st_size} bytes)")
                
                # Copy to conversation directory if available
                if conv_audio_path:
                    try:
                        import shutil
                        shutil.copy2(audio_path, conv_audio_path)
                        print(f"[TTS] Copied to conversation: {conv_audio_path}")
                    except Exception as e:
                        print(f"[TTS] Warning: Failed to copy to conversation directory: {e}")
                
                # Copy to webapp public directory for serving
                webapp_audio_dir = Path("EDGEucatorWebApp/public/audio")
                webapp_audio_dir.mkdir(parents=True, exist_ok=True)
                webapp_audio_path = webapp_audio_dir / audio_path.name
                
                try:
                    import shutil
                    print(f"[TTS] Copying audio to webapp: {audio_path} → {webapp_audio_path}")
                    shutil.copy2(audio_path, webapp_audio_path)
                    print(f"[TTS] ✅ Audio copied to webapp successfully")
                    # Use webapp-relative path
                    audio_url = f"/audio/{audio_path.name}"
                except Exception as e:
                    print(f"[TTS] ❌ Failed to copy audio to webapp: {e}")
                    # Fallback: use original path (may not work if not accessible)
                    audio_url = f"/audio/{audio_path.name}"
                
                self._broadcast_audio(audio_url)
                print(f"[WebSocket] Sent audio URL to webapp: {audio_url}")
                
                # Don't broadcast idle here - webapp will do it after audio finishes playing
                return audio_path
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            self._broadcast_state('idle')
            return None
    
    def _broadcast_state(self, state: str):
        """Broadcast avatar state change (thread-safe)"""
        if self.websocket_server and state != self.current_avatar_state:
            self.current_avatar_state = state
            try:
                # Use thread-safe method to schedule coroutine in server's event loop
                if self.websocket_server.loop and self.websocket_server.loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.websocket_server.broadcast_state(state),
                        self.websocket_server.loop
                    )
                else:
                    # Fallback: create new event loop for this call
                    asyncio.run(self.websocket_server.broadcast_state(state))
            except Exception as e:
                print(f"[WebSocket] Failed to broadcast state: {e}")
    
    def _broadcast_audio(self, audio_url: str):
        """Broadcast audio URL (thread-safe)"""
        if self.websocket_server:
            print(f"[WebSocket] Broadcasting audio URL: {audio_url}")
            try:
                if self.websocket_server.loop and self.websocket_server.loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.websocket_server.broadcast_audio(audio_url),
                        self.websocket_server.loop
                    )
                else:
                    asyncio.run(self.websocket_server.broadcast_audio(audio_url))
            except Exception as e:
                print(f"[WebSocket] Failed to broadcast audio: {e}")
        else:
            print(f"[WebSocket] Cannot broadcast audio - WebSocket server not running")
    
    def run(self):
        """Run the voice assistant loop"""
        
        # Broadcast initial idle state
        self._broadcast_state('idle')
        
        print("\n" + "="*70)
        print(" 🎯 VOICE ASSISTANT READY ".center(70))
        print("="*70)
        print()
        if self.wake_word_type == "keyboard":
            print("  ⌨️  Press ENTER to activate")
        else:
            print("  👂 Say 'HARRY POTTER' to activate")
        print("  💬 Then ask your question")
        print("  ⚡ Harry will respond with voice")
        print()
        print(f"  💾 Conversations saved to: {self.storage_dir}")
        print()
        print("  Press Ctrl+C to exit")
        print()
        print("="*70)
        print()
        
        conversation_count = 0
        
        try:
            while True:
                # 1. Wait for wake word
                if self.wake_word_type == "keyboard":
                    print("🟢 Press ENTER to activate", end='', flush=True)
                else:
                    print("🟢 Listening for wake word", end='', flush=True)
                
                detected = self.listen_for_wake_word()
                
                if detected:
                    conversation_count += 1
                    
                    print(f"\r✨ WAKE WORD DETECTED! (#{conversation_count})")
                    print("=" * 70)
                    
                    # Broadcast listening state
                    self._broadcast_state('listening')
                    
                    # Brief pause
                    time.sleep(0.3)
                    
                    # 2. Record audio
                    audio, sample_rate = self.record_audio(duration=8)
                    
                    # 3. Detect emotion (if available)
                    emotion_data = self.detect_emotion(audio, sample_rate)
                    
                    # 4. Transcribe
                    transcription = self.transcribe_audio(audio, sample_rate)
                    
                    if not transcription or len(transcription.strip()) < 3:
                        print("⚠️  No speech detected. Try again!")
                        self.speak("Sorry, I didn't hear anything. Try again.", conversation_count)
                        print()
                        continue
                    
                    print(f"\n💬 You said: \"{transcription}\"")
                    print()
                    
                    # 5. Get LLM response
                    # Broadcast generating state before LLM processing
                    self._broadcast_state('generating')
                    response = self.get_harry_response(transcription)
                    
                    if not response:
                        print("⚠️  Harry couldn't respond. Try again!")
                        self._broadcast_state('idle')  # Return to idle on error
                        continue
                    
                    print()
                    
                    # 6. Save conversation (audio + transcript + emotion)
                    conv_dir = self.save_conversation(audio, sample_rate, transcription, response, conversation_count, emotion_data)
                    
                    # 7. Generate insights in background (if enabled)
                    if self.enable_insights and self.analyzer:
                        print("🔍 Generating insights in background...")
                        self.analyzer.analyze_conversation_async(conv_dir)
                    
                    # 8. Speak response (save to audio/ folder and conversation folder)
                    self.speak(response, conversation_count, conv_dir)
                    
                    print()
                    print("="*70)
                    print()
                    
                    # Return to idle state after conversation
                    self._broadcast_state('idle')
                    
        except KeyboardInterrupt:
            print("\n\n⚡ Shutting down Harry Potter Voice Assistant...")
            print(f"   Total conversations: {conversation_count}")
            print("\n   Goodbye! ⚡\n")
        
        finally:
            # Cleanup
            self._broadcast_state('idle')
            if self.websocket_server:
                self.websocket_server.stop()
            try:
                self.porcupine.delete()
            except:
                pass
    
    def test_mode(self):
        """Test mode - skip wake word, use keyboard input"""
        
        # Broadcast initial idle state
        self._broadcast_state('idle')
        
        print("\n" + "="*70)
        print(" 🧪 TEST MODE - Voice Pipeline Test ".center(70))
        print("="*70)
        print()
        print("  This mode skips wake word detection")
        print("  Press ENTER to record, then Harry will respond")
        print()
        print(f"  💾 Conversations saved to: {self.storage_dir}")
        print()
        print("="*70)
        print()
        
        conversation_count = 0
        
        try:
            while True:
                input("Press ENTER to start recording (or Ctrl+C to quit)...")
                
                conversation_count += 1
                
                # Broadcast listening state
                self._broadcast_state('listening')
                
                # Record
                audio, sample_rate = self.record_audio(duration=6)
                
                # Detect emotion (if available)
                emotion_data = self.detect_emotion(audio, sample_rate)
                
                # Transcribe
                transcription = self.transcribe_audio(audio, sample_rate)
                
                if not transcription or len(transcription.strip()) < 3:
                    print("⚠️  No speech detected. Try again!")
                    continue
                
                print(f"\n💬 You said: \"{transcription}\"")
                
                # Get response
                # Broadcast generating state before LLM processing
                self._broadcast_state('generating')
                response = self.get_harry_response(transcription)
                
                if response:
                    # Save conversation (audio + transcript + emotion)
                    conv_dir = self.save_conversation(audio, sample_rate, transcription, response, conversation_count, emotion_data)
                    
                    # Generate insights in background (if enabled)
                    if self.enable_insights and self.analyzer:
                        print("🔍 Generating insights in background...")
                        self.analyzer.analyze_conversation_async(conv_dir)
                    
                    print()
                    self.speak(response, conversation_count, conv_dir)
                
                # Return to idle after conversation
                self._broadcast_state('idle')
                
                print("\n" + "="*70 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n⚡ Test mode ended.\n")
            self._broadcast_state('idle')


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Harry Potter Voice Assistant (NPU-Powered)")
    parser.add_argument('--test', action='store_true',
                       help='Test mode (skip wake word, use ENTER key)')
    parser.add_argument('--no-context', action='store_true',
                       help='Disable conversation context (ignore previous insights)')
    parser.add_argument('--no-insights', action='store_true',
                       help='Disable automatic insight generation')
    
    args = parser.parse_args()
    
    # Initialize assistant
    assistant = HarryVoiceAssistant(
        enable_context=not args.no_context,
        enable_insights=not args.no_insights
    )
    
    # Run in appropriate mode
    if args.test:
        assistant.test_mode()
    else:
        assistant.run()


if __name__ == "__main__":
    main()

