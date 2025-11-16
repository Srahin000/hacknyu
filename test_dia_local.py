"""
Test Dia-1.6B TTS Model Locally

This script tests the Dia-1.6B model locally before attempting NPU deployment.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_dia_local():
    """Test Dia-1.6B model locally"""
    
    print("=" * 70)
    print(" 🎤 Dia-1.6B Local Testing ".center(70))
    print("=" * 70)
    print()
    
    print("⚠️  WARNING: Dia installation may have dependency conflicts!")
    print("   - numpy 2.2.6 conflicts with TTS (needs 1.22.0)")
    print("   - protobuf 3.19.6 conflicts with qai-hub (needs >=3.20.2)")
    print("   - torch 2.6.0 conflicts with torchvision (needs 2.4.1)")
    print()
    print("   Consider using a separate environment for Dia testing.")
    print()
    
    try:
        # Check if dia package is installed
        try:
            from dia.model import Dia
            import soundfile as sf
        except ImportError as e:
            print(f"❌ Dia package not installed: {e}")
            print()
            print("Install with:")
            print("  pip install git+https://github.com/nari-labs/dia.git")
            return False
        except Exception as e:
            print(f"⚠️  Import error (may be due to dependency conflicts): {e}")
            print()
            print("Try fixing dependencies or use a separate environment.")
            return False
        
        print("Loading Dia-1.6B model...")
        print("  ⏳ This may take a while (model is ~1.6B parameters)")
        print()
        
        # Load model (use default model name which includes version suffix)
        # Default is 'nari-labs/Dia-1.6B-0626' - this has the correct config structure
        model = Dia.from_pretrained()  # Uses default: 'nari-labs/Dia-1.6B-0626'
        
        print("✅ Model loaded successfully!")
        print()
        
        # Create output directory
        output_dir = Path("dia_test_outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Test texts
        test_texts = [
            "[S1] I solemnly swear that I am up to no good.",
            "[S1] I solemnly swear that I am up to no good! [S2] That's amazing!",
            "[S1] Oh! I solemnly swear that I am up to no good! (laughs)",
            "[S1] Woooow! I solemnly swear that I am up to no good!!! [S2] Incredible!",
        ]
        
        print("Generating test audio files...")
        print()
        
        for i, text in enumerate(test_texts):
            output_path = output_dir / f"dia_test_{i+1}.mp3"
            print(f"  Generating: {text[:60]}...")
            
            try:
                output = model.generate(text)
                sf.write(str(output_path), output, 44100)
                print(f"    ✅ Saved to {output_path}")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        print()
        print("=" * 70)
        print(f"✅ Local testing complete! Outputs saved to: {output_dir}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_model_info():
    """Check model information and requirements"""
    
    print("=" * 70)
    print(" 📋 Dia-1.6B Model Information ".center(70))
    print("=" * 70)
    print()
    print("Model: nari-labs/Dia-1.6B-0626 (default)")
    print("Note: Use Dia.from_pretrained() without arguments for the correct version")
    print("Parameters: 1.6B")
    print("VRAM Required: ~10GB")
    print("Current Support: GPU only (CUDA 12.6, PyTorch 2.0+)")
    print("CPU Support: Coming soon")
    print()
    print("Features:")
    print("  ✅ Dialogue generation with [S1] and [S2] tags")
    print("  ✅ Non-verbal sounds: (laughs), (coughs), etc.")
    print("  ✅ Voice cloning support")
    print("  ✅ Emotion and tone control")
    print()
    print("For NPU deployment:")
    print("  ⚠️  Model needs to be converted to ONNX")
    print("  ⚠️  May require quantization for NPU memory")
    print("  ⚠️  Need to check QNN runtime compatibility")
    print()


if __name__ == "__main__":
    import sys
    
    check_model_info()
    
    # Skip prompt if running non-interactively or if argument provided
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("\nRunning test automatically...\n")
        test_dia_local()
    else:
        print()
        try:
            response = input("Test Dia locally? (y/n): ").strip().lower()
            if response == 'y':
                test_dia_local()
            else:
                print("Skipping local test.")
        except EOFError:
            # Non-interactive mode (e.g., when piped)
            print("\nNon-interactive mode detected. Use --auto flag to run automatically.")
            print("Example: python test_dia_local.py --auto")

