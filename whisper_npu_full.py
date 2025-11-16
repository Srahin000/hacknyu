"""
Full NPU Whisper - Encoder + Decoder on Snapdragon X Elite

Uses QNN Runtime with .bin files (not ONNX):
- HfWhisperApp from qai_hub_models.models._shared.hf_whisper.app
- OnnxModelTorchWrapper.OnNPU() can accept both .bin (QNN) and .onnx files
- Prefers .bin files for QNN runtime, falls back to .onnx if needed

Reference: https://github.com/quic/ai-hub-apps/tree/main/apps/windows/python/Whisper
"""

import os
import numpy as np
import time
from pathlib import Path

# Set QNN environment
os.environ['QNN_SDK_ROOT'] = "C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130"
os.environ['PATH'] = f"C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130\\lib\\aarch64-windows-msvc;" + os.environ.get('PATH', '')


class WhisperNPU:
    """Full Whisper on NPU - Encoder + Decoder using official Qualcomm approach"""
    
    def __init__(self):
        """Load encoder and decoder on NPU using official Qualcomm method"""
        
        print("Loading Whisper Encoder and Decoder on NPU...")
        
        try:
            from qai_hub_models.models._shared.hf_whisper.app import HfWhisperApp
            from qai_hub_models.utils.onnx.torch_wrapper import OnnxModelTorchWrapper
        except ImportError as e:
            raise ImportError(f"qai_hub_models not properly installed: {e}")
        
        # Check for QNN runtime .bin files first, then fallback to .onnx
        # QNN runtime uses .bin files (not ONNX)
        encoder_path = None
        decoder_path = None
        
        # Try QNN .bin files first (QNN runtime artifacts)
        possible_encoder_paths = [
            "models/whisper_base-hfwhisperencoder-qualcomm_snapdragon_x_elite.bin",
            "models/whisper_base2/model.bin",
            "models/HfWhisperEncoder/model.bin",
            "models/HfWhisperEncoder/model.onnx",  # Fallback to ONNX
            "build/whisper_base_float/precompiled/qualcomm-snapdragon-x-elite/HfWhisperEncoder/model.onnx",
        ]
        
        possible_decoder_paths = [
            "models/whisper_base-hfwhisperdecoder-qualcomm_snapdragon_x_elite.bin",
            "models/whisper_base/model.bin",
            "models/HfWhisperDecoder/model.bin",
            "models/HfWhisperDecoder/model.onnx",  # Fallback to ONNX
            "build/whisper_base_float/precompiled/qualcomm-snapdragon-x-elite/HfWhisperDecoder/model.onnx",
        ]
        
        for path in possible_encoder_paths:
            if Path(path).exists():
                encoder_path = path
                break
        
        for path in possible_decoder_paths:
            if Path(path).exists():
                decoder_path = path
                break
        
        if not encoder_path or not decoder_path:
            raise FileNotFoundError(
                f"Whisper models not found. Expected QNN runtime .bin files:\n"
                f"  - models/whisper_base-hfwhisperencoder-qualcomm_snapdragon_x_elite.bin\n"
                f"  - models/whisper_base-hfwhisperdecoder-qualcomm_snapdragon_x_elite.bin\n"
                f"\nOr ONNX fallback:\n"
                f"  - models/HfWhisperEncoder/model.onnx\n"
                f"  - models/HfWhisperDecoder/model.onnx"
            )
        
        print(f"  Using encoder: {encoder_path}")
        print(f"  Using decoder: {decoder_path}")
        
        try:
            # Use official Qualcomm approach
            self.app = HfWhisperApp(
                OnnxModelTorchWrapper.OnNPU(encoder_path),
                OnnxModelTorchWrapper.OnNPU(decoder_path),
                "openai/whisper-base",  # Model size
            )
            
            self.inference_type = "NPU (QNN Runtime)"
            print(f"  [OK] Whisper loaded on NPU (QNN Runtime)")
            
        except Exception as e:
            print(f"  [ERROR] Failed to load Whisper models: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def transcribe(self, audio, sample_rate):
        """
        Transcribe audio to text using NPU
        
        Args:
            audio: Audio array (numpy array, float32, normalized to [-1, 1])
            sample_rate: Sample rate (Hz)
        
        Returns:
            tuple: (transcription_text, latency_ms)
        """
        start_time = time.time()
        
        try:
            # HfWhisperApp.transcribe expects both audio (numpy array) and sample_rate
            # It handles all preprocessing and decoding internally
            transcription = self.app.transcribe(audio, sample_rate)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return transcription, latency_ms
            
        except Exception as e:
            print(f"  [ERROR] Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return None, 0
