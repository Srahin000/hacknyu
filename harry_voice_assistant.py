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
    try:
        # Only wrap if not already wrapped and buffer exists
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError):
        # If wrapping fails, just continue with the default stdout/stderr
        pass


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
        
        try:
            from emotion_npu import EmotionNPU
            self.emotion_detector = EmotionNPU()
            self.emotion_type = self.emotion_detector.inference_type
            self.emotion_ready = True
            print(f"  ✅ Emotion detection ready ({self.emotion_type})")
        except Exception as e:
            print(f"  ⚠️  Emotion detection not available: {e}")
            print("     Continuing without emotion detection...")
            self.emotion_detector = None
            self.emotion_type = "none"
            self.emotion_ready = False
    
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
        """Speak text using pyttsx3"""
        
        print(f"🔊 Harry speaks: \"{text}\"")
        
        if not self.tts_ready:
            return None
        
        try:
            if self.tts_type == "pyttsx3":
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return None
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None
    
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
                    response = self.get_harry_response(transcription)
                    
                    if not response:
                        print("⚠️  Harry couldn't respond. Try again!")
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
                
                # Detect emotion (if available)
                emotion_data = self.detect_emotion(audio, sample_rate)
                
                # Transcribe
                transcription = self.transcribe_audio(audio, sample_rate)
                
                if not transcription or len(transcription.strip()) < 3:
                    print("⚠️  No speech detected. Try again!")
                    continue
                
                print(f"\n💬 You said: \"{transcription}\"")
                
                # Get response
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
                
                print("\n" + "="*70 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n⚡ Test mode ended.\n")


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

