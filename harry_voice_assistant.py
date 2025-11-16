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

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HarryVoiceAssistant:
    """Complete voice assistant for Harry Potter"""
    
    def __init__(self, cpu_mode=False):
        """
        Initialize all components
        
        Args:
            cpu_mode: If True, use CPU for Whisper and LLM (skip NPU)
        """
        
        print("\n" + "="*70)
        print(" ⚡ HARRY POTTER VOICE ASSISTANT ⚡".center(70))
        if cpu_mode:
            print(" 🖥️  CPU MODE (Testing while NPU downloads) ".center(70))
        print("="*70)
        print()
        
        # Component status
        self.wake_word_ready = False
        self.wake_word_type = None  # "picovoice" or "keyboard"
        self.stt_ready = False
        self.llm_ready = False
        self.tts_ready = False
        self.tts_type = None  # Will be set in _init_tts
        self.cpu_mode = cpu_mode
        
        # Storage setup
        self.storage_dir = Path("conversations")
        self.storage_dir.mkdir(exist_ok=True)
        self.conversation_count = 0
        
        # TTS parameters for Harry Potter voice
        self.tts_speaker = "male-en-2"
        self.tts_emotion = "happy"
        self.tts_speed = 1.12  # youthful pacing
        self.tts_pitch = 1.20  # kid-like pitch
        
        # Initialize components
        self._init_wake_word()
        self._init_stt()
        self._init_llm()
        self._init_tts()
        
        # Check if ready
        if not all([self.wake_word_ready, self.stt_ready, self.llm_ready, self.tts_ready]):
            print("\n❌ Not all components ready!")
            sys.exit(1)
        
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
        """Initialize Speech-to-Text (Whisper NPU or CPU)"""
        print("🎤 [2/4] Initializing Speech-to-Text...")
        
        # CPU mode: use CPU Whisper (OpenAI Whisper library)
        if self.cpu_mode:
            try:
                from whisper_cpu import WhisperCPU
                print("  Loading Whisper on CPU (OpenAI Whisper library)...")
                self.stt_model = WhisperCPU(model_size="base")
                self.stt_type = "whisper-cpu"
                print(f"  ✅ Using CPU Whisper ({self.stt_model.inference_type})")
                self.stt_ready = True
                return
            except Exception as e:
                print(f"  ❌ CPU Whisper failed: {e}")
                print(f"     Install with: pip install openai-whisper")
                import traceback
                traceback.print_exc()
                return
        
        # Normal mode: try NPU first, fallback to CPU
        try:
            # Use NPU Whisper (encoder + decoder on Snapdragon X Elite)
            from whisper_npu_full import WhisperNPU
            print("  Loading Whisper on NPU...")
            self.stt_model = WhisperNPU()
            self.stt_type = "whisper-npu"
            print(f"  ✅ Using NPU Whisper ({self.stt_model.inference_type})")
            self.stt_ready = True
            
        except Exception as e:
            print(f"  ⚠️  NPU Whisper failed, trying CPU fallback...")
            print(f"     Error: {e}")
            try:
                from whisper_cpu import WhisperCPU
                print("  Loading Whisper on CPU (fallback, OpenAI Whisper library)...")
                self.stt_model = WhisperCPU(model_size="base")
                self.stt_type = "whisper-cpu"
                print(f"  ✅ Using CPU Whisper ({self.stt_model.inference_type})")
                self.stt_ready = True
            except Exception as e2:
                print(f"  ❌ CPU Whisper also failed: {e2}")
                print(f"     Install with: pip install openai-whisper")
            import traceback
            traceback.print_exc()
    
    def _init_llm(self):
        """Initialize LLM (NPU Genie or CPU fallback)"""
        print("🧠 [3/4] Initializing Harry Potter AI...")
        
        # CPU mode: skip NPU, use CPU only
        if self.cpu_mode:
            try:
                from harry_llama_cpp import HarryPotterLlamaCpp
                import sys
                old_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')
                try:
                    self.harry = HarryPotterLlamaCpp()
                    self.llm_ready = True
                finally:
                    sys.stdout.close()
                    sys.stdout = old_stdout
                print("  ✅ Harry Potter AI loaded (CPU mode)")
                return
            except Exception as e:
                print(f"  ❌ CPU LLM error: {e}")
                return
        
        # Normal mode: try NPU first, fallback to CPU
        try:
            from harry_llm_npu import HarryPotterNPU
            self.harry = HarryPotterNPU()
            self.llm_ready = True
            print("  ✅ Harry Potter AI loaded (NPU Genie)")
            return
        except Exception as e:
            pass
        
        # Fallback to CPU
        try:
            from harry_llama_cpp import HarryPotterLlamaCpp
            import sys
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            try:
                self.harry = HarryPotterLlamaCpp()
                self.llm_ready = True
            finally:
                sys.stdout.close()
                sys.stdout = old_stdout
            print("  ✅ Harry Potter AI loaded (CPU fallback)")
        except Exception as e:
            print(f"  ❌ LLM error: {e}")
    
    def _init_tts(self):
        """Initialize Text-to-Speech using XTTS v2 with pyttsx3 fallback"""
        print("🔊 [4/4] Initializing Text-to-Speech...")
        
        # Try XTTS v2 first
        try:
            import torch
            from TTS.api import TTS
            
            # Fix for PyTorch 2.6+ weights_only=True default
            # TTS models need to load custom classes, so we temporarily allow unsafe loading
            original_load = torch.load
            def patched_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            torch.load = patched_load
            
            # Use XTTS v2 for high-quality multilingual TTS
            print("  Loading XTTS v2 model...")
            self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            
            # Restore original torch.load after TTS loads
            torch.load = original_load
            
            self.tts_type = "xtts_v2"
            self.tts_ready = True
            print("  ✅ Text-to-Speech ready (XTTS v2)")
            return
            
        except Exception as e:
            print(f"  ⚠️  XTTS v2 failed: {e}")
            print("     Trying pyttsx3 fallback...")
        
        # Fallback to pyttsx3
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 160)  # Slightly faster
            self.tts_engine.setProperty('volume', 0.9)
            
            # Try to find a good voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_type = "pyttsx3"
            self.tts_ready = True
            print("  ✅ Text-to-Speech ready (pyttsx3 fallback)")
            
        except Exception as e:
            print(f"  ❌ TTS error: {e}")
            print("     Install with: pip install TTS (for XTTS) or pip install pyttsx3 (for fallback)")
            import traceback
            traceback.print_exc()
    
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
        
        return audio.flatten(), sample_rate
    
    def save_conversation(self, audio, sample_rate, transcription, harry_response, conversation_id):
        """Save audio file and transcript with metadata"""
        
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
        
        # Save audio file
        audio_path = conv_dir / "audio.wav"
        sf.write(str(audio_path), audio, sample_rate)
        
        # Save transcript
        transcript_path = conv_dir / "transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(f"Conversation #{conversation_id}\n")
            f.write(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write("USER:\n")
            f.write(f"{transcription}\n\n")
            f.write("HARRY:\n")
            f.write(f"{harry_response}\n")
        
        # Save metadata JSON
        metadata = {
            "conversation_id": conversation_id,
            "timestamp": timestamp.isoformat(),
            "date": date_str,
            "time": time_str,
            "user_query": transcription,
            "harry_response": harry_response,
            "audio_file": str(audio_path.relative_to(self.storage_dir)),
            "transcript_file": str(transcript_path.relative_to(self.storage_dir)),
            "sample_rate": sample_rate,
            "audio_duration_seconds": len(audio) / sample_rate,
            "stt_type": self.stt_type,
            "tts_type": self.tts_type,
            "wake_word_type": self.wake_word_type
        }
        
        metadata_path = conv_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved conversation to: {conv_dir}")
        return conv_dir
    
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
        """Get response from Harry Potter AI"""
        
        print("🧠 Harry is thinking...", end='', flush=True)
        
        try:
            response, latency = self.harry.ask_harry(text)
            print(f"\r✅ Response ready! ({latency}ms)     ")
            return response
            
        except Exception as e:
            print(f"\r❌ LLM error: {e}")
            return None
    
    def speak(self, text):
        """Speak text using TTS"""
        
        print(f"🔊 Harry speaks: \"{text}\"")
        
        try:
            if self.tts_type == "xtts_v2":
                # XTTS v2: generate audio and play it
                import tempfile
                import sounddevice as sd
                import soundfile as sf
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                # Generate speech with Harry Potter voice parameters
                self.tts_engine.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    language="en",
                    speaker=self.tts_speaker,  # "male-en-2"
                    emotion=self.tts_emotion,  # "happy"
                    speed=self.tts_speed,      # 1.12 (youthful pacing)
                    pitch=self.tts_pitch       # 1.20 (kid-like pitch)
                )
                
                # Play the audio
                audio_data, sample_rate = sf.read(temp_path)
                sd.play(audio_data, sample_rate)
                sd.wait()  # Wait until playback is finished
                
                # Clean up
                import os
                os.unlink(temp_path)
            elif self.tts_type == "pyttsx3":
                # pyttsx3 fallback
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the voice assistant loop"""
        
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
                    
                    # Brief pause
                    time.sleep(0.3)
                    
                    # 2. Record audio
                    audio, sample_rate = self.record_audio(duration=8)
                    
                    # 3. Transcribe
                    transcription = self.transcribe_audio(audio, sample_rate)
                    
                    if not transcription or len(transcription.strip()) < 3:
                        print("⚠️  No speech detected. Try again!")
                        self.speak("Sorry, I didn't hear anything. Try again.")
                        print()
                        continue
                    
                    print(f"\n💬 You said: \"{transcription}\"")
                    print()
                    
                    # 4. Get LLM response
                    response = self.get_harry_response(transcription)
                    
                    if not response:
                        print("⚠️  Harry couldn't respond. Try again!")
                        continue
                    
                    print()
                    
                    # 5. Speak response
                    self.speak(response)
                    
                    print()
                    print("="*70)
                    print()
                    
        except KeyboardInterrupt:
            print("\n\n⚡ Shutting down Harry Potter Voice Assistant...")
            print(f"   Total conversations: {conversation_count}")
            print("\n   Goodbye! ⚡\n")
        
        finally:
            # Cleanup
            try:
                self.porcupine.delete()
            except:
                pass
    
    def test_mode(self):
        """Test mode - skip wake word, use keyboard input"""
        
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
                
                # Record
                audio, sample_rate = self.record_audio(duration=6)
                
                # Transcribe
                transcription = self.transcribe_audio(audio, sample_rate)
                
                if not transcription or len(transcription.strip()) < 3:
                    print("⚠️  No speech detected. Try again!")
                    continue
                
                print(f"\n💬 You said: \"{transcription}\"")
                
                # Get response
                response = self.get_harry_response(transcription)
                
                if response:
                    # Save conversation (audio + transcript)
                    self.save_conversation(audio, sample_rate, transcription, response, conversation_count)
                    
                    print()
                    self.speak(response)
                
                print("\n" + "="*70 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n⚡ Test mode ended.\n")


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Harry Potter Voice Assistant")
    parser.add_argument('--test', action='store_true', 
                       help='Test mode (skip wake word, use ENTER key)')
    parser.add_argument('--cpu', action='store_true',
                       help='CPU mode (use CPU for Whisper and LLM, skip NPU)')
    
    args = parser.parse_args()
    
    # Initialize assistant
    assistant = HarryVoiceAssistant(cpu_mode=args.cpu)
    
    # Run in appropriate mode
    if args.test:
        assistant.test_mode()
    else:
        assistant.run()


if __name__ == "__main__":
    main()

