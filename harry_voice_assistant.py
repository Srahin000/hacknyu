"""
Harry Potter Voice Assistant - Complete Pipeline

Flow:
1. Wake Word Detection (Picovoice) - "Harry Potter"
2. Start Listening (8 seconds)
3. Speech-to-Text (Whisper)
4. LLM Response (Llama 3.2 via llama.cpp)
5. Text-to-Speech (pyttsx3)

This is the COMPLETE voice assistant pipeline!
"""

import sys
import struct
import os
import time
import numpy as np
import sounddevice as sd
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HarryVoiceAssistant:
    """Complete voice assistant for Harry Potter"""
    
    def __init__(self):
        """Initialize all components"""
        
        print("\n" + "="*70)
        print(" ⚡ HARRY POTTER VOICE ASSISTANT ⚡".center(70))
        print("="*70)
        print()
        
        # Component status
        self.wake_word_ready = False
        self.stt_ready = False
        self.llm_ready = False
        self.tts_ready = False
        
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
        """Initialize Picovoice wake word detection"""
        print("🔊 [1/4] Initializing Wake Word Detection...")
        
        try:
            import pvporcupine
            from dotenv import load_dotenv
            
            load_dotenv()
            access_key = os.getenv('PICOVOICE_ACCESS_KEY')
            
            if not access_key:
                print("  ❌ PICOVOICE_ACCESS_KEY not found in .env")
                print("     Get your free key at: https://console.picovoice.ai/")
                return
            
            ppn_file = Path("ppn_files/Harry-Potter_en_windows_v3_0_0.ppn")
            if not ppn_file.exists():
                print(f"  ❌ Wake word file not found: {ppn_file}")
                return
            
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=[str(ppn_file)]
            )
            
            self.wake_word_ready = True
            print("  ✅ Wake word ready: 'Harry Potter'")
            
        except Exception as e:
            print(f"  ❌ Wake word error: {e}")
    
    def _init_stt(self):
        """Initialize Speech-to-Text (Whisper NPU)"""
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
            print(f"     Make sure models/whisper_base and models/whisper_base2 exist")
            import traceback
            traceback.print_exc()
    
    def _init_llm(self):
        """Initialize LLM (Llama via llama.cpp)"""
        print("🧠 [3/4] Initializing Harry Potter AI...")
        
        try:
            from harry_llama_cpp import HarryPotterLlamaCpp
            
            # Suppress the verbose output from HarryPotterLlamaCpp
            import sys
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            try:
                self.harry = HarryPotterLlamaCpp()
                self.llm_ready = True
            finally:
                sys.stdout.close()
                sys.stdout = old_stdout
            
            print("  ✅ Harry Potter AI loaded (llama.cpp)")
            
        except Exception as e:
            print(f"  ❌ LLM error: {e}")
    
    def _init_tts(self):
        """Initialize Text-to-Speech"""
        print("🔊 [4/4] Initializing Text-to-Speech...")
        
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 160)  # Slightly faster
            self.tts_engine.setProperty('volume', 0.9)
            
            # Try to find a good voice
            voices = self.tts_engine.getProperty('voices')
            # Prefer male voice if available
            for voice in voices:
                if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_ready = True
            print("  ✅ Text-to-Speech ready")
            
        except Exception as e:
            print(f"  ❌ TTS error: {e}")
            print("     Install with: pip install pyttsx3")
    
    def listen_for_wake_word(self):
        """Listen for 'Harry Potter' wake word"""
        
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
    
    def transcribe_audio(self, audio, sample_rate):
        """Transcribe audio to text using NPU Whisper"""

        print("🔄 Transcribing on NPU...", end='', flush=True)

        try:
            # NPU Whisper (encoder + decoder)
            transcription, latency = self.stt_model.transcribe(audio, sample_rate)
            print(f"\r✅ Transcribed! ({latency}ms on NPU)       ")
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
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    def run(self):
        """Run the voice assistant loop"""
        
        print("\n" + "="*70)
        print(" 🎯 VOICE ASSISTANT READY ".center(70))
        print("="*70)
        print()
        print("  👂 Say 'HARRY POTTER' to activate")
        print("  💬 Then ask your question")
        print("  ⚡ Harry will respond with voice")
        print()
        print("  Press Ctrl+C to exit")
        print()
        print("="*70)
        print()
        
        conversation_count = 0
        
        try:
            while True:
                # 1. Wait for wake word
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
        print("="*70)
        print()
        
        try:
            while True:
                input("Press ENTER to start recording (or Ctrl+C to quit)...")
                
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
    
    args = parser.parse_args()
    
    # Initialize assistant
    assistant = HarryVoiceAssistant()
    
    # Run in appropriate mode
    if args.test:
        assistant.test_mode()
    else:
        assistant.run()


if __name__ == "__main__":
    main()

