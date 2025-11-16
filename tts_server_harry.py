"""
Harry Potter TTS Server with Voice Cloning
Runs in separate conda environment (tts)
Listens on localhost:5005 for text, returns cloned voice audio
"""
import socket
import sys
import io
from pathlib import Path
import time

# Fix Windows encoding
if sys.platform == 'win32':
    import io as io_module
    sys.stdout = io_module.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io_module.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("="*70)
print(" 🎤 Harry Potter TTS Server (Voice Cloning) ".center(70))
print("="*70)
print()

# Configuration
HOST = "127.0.0.1"
PORT = 5005
VOICE_SAMPLE = Path("sound_sample/harry_sample.wav")

# Check voice sample
if not VOICE_SAMPLE.exists():
    print(f"❌ Voice sample not found: {VOICE_SAMPLE}")
    print("   Please ensure sound_sample/harry_sample.wav exists!")
    sys.exit(1)

print(f"✅ Voice sample found: {VOICE_SAMPLE.name}")
print()

# Load XTTS v2 model with voice cloning
print("Loading XTTS v2 model...")
try:
    import torch
    from TTS.api import TTS
    import soundfile as sf
    
    # Fix PyTorch loading
    original_load = torch.load
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    # Load model (takes ~10-12 seconds first time)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    print("✅ XTTS v2 loaded successfully!")
    print()
    
except Exception as e:
    print(f"❌ Failed to load TTS: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Start TCP server
print("="*70)
print(f" 🔥 TTS Server Ready! ".center(70))
print("="*70)
print(f"\n   Listening on {HOST}:{PORT}")
print(f"   Voice: Cloned from {VOICE_SAMPLE.name}")
print(f"\n   Waiting for text from NPU pipeline...\n")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(1)

request_count = 0

try:
    while True:
        # Wait for connection
        conn, addr = sock.accept()
        request_count += 1
        
        try:
            # Receive text
            text = conn.recv(4096).decode("utf-8").strip()
            
            if not text:
                conn.close()
                continue
            
            print(f"[{request_count}] Received: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
            
            # Generate speech with CLONED VOICE
            start = time.time()
            
            # Create temp file for this request
            temp_file = f"temp_tts_{request_count}.wav"
            
            # XTTS v2 voice cloning - uses your harry_sample.wav!
            tts.tts_to_file(
                text=text,
                speaker_wav=str(VOICE_SAMPLE),  # Your cloned voice!
                language="en",
                file_path=temp_file
            )
            
            # Read generated audio
            audio_data, sample_rate = sf.read(temp_file)
            
            # Convert to WAV bytes
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sample_rate, format="WAV")
            wav_bytes = buffer.getvalue()
            
            latency = int((time.time() - start) * 1000)
            print(f"[{request_count}] Generated: {len(wav_bytes)} bytes in {latency}ms")
            
            # Send audio back
            conn.sendall(wav_bytes)
            
            # Clean up temp file
            try:
                Path(temp_file).unlink()
            except:
                pass
            
        except Exception as e:
            print(f"[{request_count}] Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            conn.close()

except KeyboardInterrupt:
    print("\n\n⚡ Shutting down TTS server...")
    print(f"   Total requests: {request_count}")
    print("\n   Goodbye! ⚡\n")

finally:
    sock.close()

