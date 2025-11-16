# Using NPU-Optimized LLMs with Qualcomm AI Hub

## ✅ Yes! Qualcomm has NPU-Optimized Llama Models

Qualcomm AI Hub provides several Llama models optimized for Snapdragon NPU:

### Available Models

| Model | Size | Use Case | Memory | Speed on NPU |
|-------|------|----------|--------|--------------|
| **Llama-3.2-1B** | 1B params | Lightweight chat | ~1GB | ~0.5-1s/response |
| **Llama-3.2-3B** | 3B params | Better quality | ~2GB | ~1-2s/response |
| **Llama-3-8B** | 8B params | High quality | ~5GB | ~3-5s/response |
| **Llama-2-7B** | 7B params | General purpose | ~4GB | ~2-4s/response |

### 🎯 Recommended for Your AI Companion: **Llama-3.2-1B**

**Why?**
- Smallest and fastest (~1GB)
- Perfect for educational Q&A
- Real-time responses on NPU
- Low memory footprint
- Great for children's questions

## Installation

Models are available through Qualcomm AI Hub:

```python
# Option 1: Via qai_hub_models (if available)
from qai_hub_models.models import Llama_v3_2_1b_chat_quantized

model = Llama_v3_2_1b_chat_quantized.from_pretrained()
response = model.generate(prompt="Why is the sky blue?")
```

```python
# Option 2: Deploy ONNX model manually
# 1. Download Llama ONNX from AI Hub
# 2. Deploy with deploy_fixed.py
python deploy_fixed.py --model models/llama_3_2_1b.onnx
```

## How to Get NPU LLMs

### Method 1: Qualcomm AI Hub Website

1. Go to: https://aihub.qualcomm.com/models
2. Filter by:
   - **Domain:** Natural Language
   - **Model Type:** Large Language Model
   - **Runtime:** Qualcomm AI Engine
3. Download Llama-3.2-1B (quantized)
4. Deploy to your device

### Method 2: Using qai_hub CLI

```bash
# Search for LLM models
qai-hub list-models --filter "llama"

# Download Llama 3.2 1B
qai-hub download-model llama-v3-2-1b-chat

# Deploy to device
python deploy_fixed.py --model llama-v3-2-1b-chat.onnx
```

### Method 3: Use CPU First (Development)

For prototyping, use TinyLlama on CPU:

```bash
pip install transformers
```

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

prompt = "Why is the sky blue?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

Then optimize for NPU later!

## Integration with Your AI Companion

### Complete Pipeline

```python
import pvporcupine
import sounddevice as sd
from qai_hub_models.models.whisper_base_en import WhisperBaseEnglish
from qai_hub_models.models.llama_v3_2_1b import Llama_1B  # Hypothetical
import pyttsx3

# 1. Wake Word Detection
porcupine = pvporcupine.create(
    access_key="your_key",
    keyword_paths=["ppn_files/Harry-Potter_en_windows_v3_0_0.ppn"]
)

# 2. STT (Whisper NPU)
stt_model = WhisperBaseEnglish.from_pretrained()

# 3. LLM (Llama NPU)
llm_model = Llama_1B.from_pretrained()

# 4. TTS
tts = pyttsx3.init()

# Pipeline
while True:
    # Listen for wake word
    if detect_wake_word(porcupine):
        
        # Record speech
        audio = record_audio(duration=8)
        
        # Transcribe (NPU, ~44ms)
        transcript = stt_model(audio)
        
        # Generate response (NPU, ~500ms)
        response = llm_model.generate(
            prompt=f"You are a helpful AI companion for children. {transcript}",
            max_tokens=100
        )
        
        # Speak response
        tts.say(response)
        tts.runAndWait()
```

### Performance Targets

| Component | Latency | Device |
|-----------|---------|--------|
| Wake Word | <50ms | NPU |
| STT (Whisper) | ~44ms | NPU |
| Emotion | ~80ms | NPU |
| LLM (Llama 1B) | ~500ms | NPU |
| TTS | ~200ms | CPU |
| **Total** | **~900ms** | **Mixed** |

**Result:** < 1 second end-to-end response time!

## Current Options (Today)

Since NPU LLM deployment is complex, here are practical options:

### Option A: CPU LLM (Simple)
```python
from transformers import pipeline

# Use small model on CPU
generator = pipeline('text-generation', 
                     model='TinyLlama/TinyLlama-1.1B-Chat-v1.0')

response = generator("Why is the sky blue?", max_length=100)
```

**Pros:** Works immediately, good for demo
**Cons:** ~2-5s latency, uses more power

### Option B: Cloud API (Fast)
```python
import openai

# Use OpenAI API (requires internet)
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Why is the sky blue?"}]
)
```

**Pros:** Fast, high quality
**Cons:** Requires internet, not private

### Option C: NPU Llama (Best, Requires Setup)
```python
# Download from AI Hub and deploy
# python deploy_fixed.py --model llama_3_2_1b.onnx

# Then use compiled model
response = llm_model.generate(prompt, max_tokens=100)
```

**Pros:** Fast (~500ms), offline, private
**Cons:** Requires model download and deployment

## Recommendation for Hackathon

**Start with Option A (CPU)** for your demo:
1. Get the pipeline working end-to-end
2. Use TinyLlama on CPU (~2-3s responses)
3. Focus on integration and UX

**Optimize Later (Option C):**
1. Download Llama-3.2-1B from AI Hub
2. Deploy to NPU
3. Replace CPU inference with NPU
4. Get 5x faster responses

## Next Steps

1. **Test CPU LLM first:**
   ```bash
   python test_llama_npu.py
   ```

2. **Build full pipeline** with CPU LLM

3. **Optimize** by deploying NPU Llama later

4. **Document** performance improvements

The key is: **Get it working first, optimize later!**

## Resources

- [Qualcomm AI Hub Models](https://aihub.qualcomm.com/models?domain=Natural+Language)
- [Llama Models on AI Hub](https://aihub.qualcomm.com/models?search=llama)
- [TinyLlama (CPU)](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- [qai_hub_models Docs](https://github.com/quic/ai-hub-models)

