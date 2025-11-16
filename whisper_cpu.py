"""
CPU Whisper - Uses OpenAI Whisper library for CPU inference

Since the NPU models are QNN artifacts (.bin files) that require QNN runtime,
we use OpenAI Whisper library for CPU mode. This provides full Whisper functionality
on CPU while NPU models are being set up.
"""

import time
import numpy as np


class WhisperCPU:
    """CPU-based Whisper STT using OpenAI Whisper library"""
    
    def __init__(self, model_size="base"):
        """
        Initialize CPU Whisper using OpenAI library
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
                       "base" matches the NPU model size
        """
        print(f"Loading Whisper CPU model ({model_size})...")
        
        try:
            import whisper
            self.model = whisper.load_model(model_size)
            self.inference_type = f"CPU (whisper-{model_size})"
            print(f"  ✅ Whisper CPU ready ({model_size})")
        except ImportError:
            print("  ❌ OpenAI whisper not installed!")
            print("     Install with: pip install openai-whisper")
            raise
        except Exception as e:
            print(f"  ❌ Failed to load Whisper: {e}")
            raise
    
    def transcribe(self, audio, sample_rate):
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio: Audio array (numpy array, float32, normalized to [-1, 1])
            sample_rate: Sample rate (Hz)
        
        Returns:
            tuple: (transcription_text, latency_ms)
        """
        start_time = time.time()
        
        try:
            # Ensure audio is float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Whisper expects audio at 16kHz, but it can handle other rates
            # It will resample internally if needed
            result = self.model.transcribe(
                audio,
                language="en",
                task="transcribe",
                fp16=False  # Use FP32 for CPU
            )
            
            transcription = result["text"].strip()
            latency_ms = int((time.time() - start_time) * 1000)
            
            return transcription, latency_ms
            
        except Exception as e:
            print(f"  ❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return None, 0

