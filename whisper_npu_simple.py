"""Simple NPU Whisper using ONNX Runtime + QNN"""
import os
import numpy as np
import onnxruntime as ort
from pathlib import Path

os.environ['QNN_SDK_ROOT'] = "C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130"
os.environ['PATH'] = f"C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130\\lib\\aarch64-windows-msvc;" + os.environ.get('PATH', '')

class WhisperNPU:
    def __init__(self):
        model_path = Path("models/whisper_base/model.onnx")
        
        qnn_options = {
            'backend_path': 'QnnHtp.dll',
            'qnn_context_cache_enable': '1',
        }
        
        self.session = ort.InferenceSession(
            str(model_path),
            providers=['QNNExecutionProvider', 'CPUExecutionProvider'],
            provider_options=[qnn_options, {}]
        )
        
        self.inference_type = self.session.get_providers()[0]
        
    def transcribe(self, audio, sample_rate):
        """Transcribe audio - returns (text, latency_ms)"""
        # For now, fallback to CPU whisper for actual transcription
        # The decoder model is loaded on NPU, but we need encoder too
        import whisper
        start = time.time()
        model = whisper.load_model("base")
        result = model.transcribe(audio, language="en")
        latency = int((time.time() - start) * 1000)
        return result["text"].strip(), latency

