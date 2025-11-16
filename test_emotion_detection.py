"""
Test Emotion Detection on Voice Recordings

Tests the emotion detection model on existing audio files.
"""

import sys
from pathlib import Path
import soundfile as sf
from emotion_npu import EmotionNPU, EmotionCPU


def test_emotion_detection():
    """Test emotion detection on recorded audio"""
    
    print("="*70)
    print(" EMOTION DETECTION TEST ".center(70))
    print("="*70)
    print()
    
    # Initialize detector
    print("Loading emotion detection model...")
    try:
        detector = EmotionNPU()
        print()
    except Exception as e:
        print(f"NPU initialization failed: {e}")
        print("Using CPU fallback...")
        detector = EmotionCPU()
        print()
    
    print(f"Detector: {detector}")
    print(f"Inference type: {detector.inference_type}")
    print()
    
    # Find audio files to test
    audio_patterns = [
        "conversations/*/conv_*/user_audio.wav",  # User recordings in conversations
        "audio/user_*.wav",  # Old user recordings (if any)
    ]
    
    from glob import glob
    
    audio_files = []
    for pattern in audio_patterns:
        audio_files.extend(glob(pattern))
    
    if not audio_files:
        print("❌ No audio files found to test!")
        print()
        print("To generate test audio, run:")
        print("  python harry_voice_assistant.py --test")
        print()
        return
    
    print(f"Found {len(audio_files)} audio file(s) to analyze")
    print("="*70)
    print()
    
    # Test each file
    results = []
    
    for i, audio_file in enumerate(audio_files[:5], 1):  # Test first 5 files
        print(f"[{i}/{min(5, len(audio_files))}] Testing: {audio_file}")
        
        try:
            # Load audio
            audio, sr = sf.read(audio_file)
            
            # Detect emotion
            emotion, confidence, latency, all_scores = detector.detect_emotion(audio, sr)
            
            print(f"    Emotion: {emotion.upper()}")
            print(f"    Confidence: {confidence*100:.1f}%")
            print(f"    Latency: {latency}ms")
            print()
            
            results.append({
                "file": audio_file,
                "emotion": emotion,
                "confidence": confidence,
                "latency": latency,
                "scores": all_scores
            })
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            print()
    
    # Summary
    print("="*70)
    print(" SUMMARY ".center(70))
    print("="*70)
    print()
    
    if results:
        # Show all results
        for i, result in enumerate(results, 1):
            filename = Path(result["file"]).name
            print(f"{i}. {filename}")
            print(f"   Emotion: {result['emotion'].upper()} ({result['confidence']*100:.0f}% confidence)")
            print(f"   Top 3 emotions:")
            
            # Sort scores
            sorted_scores = sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)
            for emotion, score in sorted_scores[:3]:
                print(f"     • {emotion}: {score*100:.1f}%")
            print()
        
        # Average latency
        avg_latency = sum(r["latency"] for r in results) / len(results)
        print(f"Average latency: {avg_latency:.0f}ms ({detector.inference_type})")
        print()
        
        # Emotion distribution
        print("Emotion distribution:")
        emotion_counts = {}
        for result in results:
            emotion = result["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(results)) * 100
            print(f"  {emotion:10s}: {count} ({percentage:.0f}%)")
    else:
        print("No results to show.")
    
    print()
    print("="*70)
    print()
    print("✅ Testing complete!")
    print()
    print("To see emotion detection in action:")
    print("  python harry_voice_assistant.py --test")
    print()


if __name__ == "__main__":
    test_emotion_detection()

