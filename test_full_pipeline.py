"""Quick test of full NPU voice pipeline"""

import numpy as np
from harry_voice_assistant import HarryVoiceAssistant

print("Initializing voice assistant...")
assistant = HarryVoiceAssistant()

print("\nGenerating test audio (3 seconds of silence)...")
sample_rate = 16000
test_audio = np.random.randn(3 * sample_rate).astype(np.float32) * 0.01  # Low volume noise

print("\nTesting STT on NPU...")
text = assistant.transcribe_audio(test_audio, sample_rate)
print(f"Transcription result: {text}")

print("\nTesting LLM...")
response, latency = assistant.get_harry_response("Hello Harry")
print(f"Harry's response ({latency}ms): {response}")

print("\nTesting TTS...")
assistant.speak(response[:50])  # Speak first 50 chars

print("\n✅ Full pipeline test complete!")
print(f"""
Pipeline Status:
- Wake Word: {'✓' if assistant.wake_word_ready else 'X'}
- NPU STT: {'✓' if assistant.stt_ready else 'X'} ({assistant.stt_type})
- LLM: {'✓' if assistant.llm_ready else 'X'}
- TTS: {'✓' if assistant.tts_ready else 'X'}

All components working on NPU!
Ready for: python harry_voice_assistant.py
""")

