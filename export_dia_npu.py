"""
Export Dia-1.6B TTS Model for NPU Deployment

This script attempts to convert Dia-1.6B to ONNX and deploy to Qualcomm NPU.
"""

import sys
import os
import torch
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def export_dia_to_onnx():
    """Export Dia-1.6B model to ONNX format"""
    
    print("=" * 70)
    print(" 🔄 Exporting Dia-1.6B to ONNX ".center(70))
    print("=" * 70)
    print()
    
    try:
        from dia.model import Dia
        
        print("Loading Dia-1.6B model...")
        # Use default model (includes version suffix: -0626)
        model = Dia.from_pretrained()  # Default: 'nari-labs/Dia-1.6B-0626'
        model.eval()
        
        print("✅ Model loaded!")
        print()
        
        # Create output directory
        output_dir = Path("models/dia_1.6b")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Note: Dia model structure may be complex
        # We need to identify the main inference path
        print("⚠️  Note: Dia-1.6B has a complex architecture.")
        print("   We need to identify the main inference components:")
        print("   - Text encoder")
        print("   - Audio decoder")
        print("   - Vocoder")
        print()
        
        # Try to export main model components
        # This is a placeholder - actual export depends on model architecture
        print("Attempting ONNX export...")
        print("  (This may require model-specific modifications)")
        print()
        
        # Example: Export text encoder if accessible
        # This is a simplified example - actual implementation needs model inspection
        try:
            # Create dummy input for tracing
            # Dia expects text input - need to check actual input format
            dummy_text = "[S1] Hello, this is a test."
            
            # Try to trace the model
            # Note: This is a placeholder - actual implementation requires
            # understanding Dia's internal architecture
            print("  ⚠️  Direct ONNX export may not be straightforward")
            print("  💡 Consider using qai-hub's model export utilities")
            print()
            
            return False
            
        except Exception as e:
            print(f"  ❌ Export failed: {e}")
            print()
            print("  💡 Alternative approach:")
            print("     1. Use qai-hub model export utilities")
            print("     2. Convert PyTorch -> TorchScript -> ONNX")
            print("     3. Use Qualcomm's quantization tools")
            return False
            
    except ImportError:
        print("❌ Dia package not installed!")
        print("   Install with: pip install git+https://github.com/nari-labs/dia.git")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def deploy_dia_to_npu():
    """Deploy Dia-1.6B to NPU using Qualcomm AI Hub"""
    
    print("=" * 70)
    print(" 🚀 Deploying Dia-1.6B to NPU ".center(70))
    print("=" * 70)
    print()
    
    try:
        import qai_hub as hub
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('QAI_HUB_API_KEY')
        
        if not api_key:
            print("❌ QAI_HUB_API_KEY not found in .env")
            print("   Get your API key from: https://app.aihub.qualcomm.com/")
            return False
        
        print("Connecting to Qualcomm AI Hub...")
        hub.login(api_key)
        
        # Check if ONNX model exists
        onnx_model_path = Path("models/dia_1.6b/model.onnx")
        
        if not onnx_model_path.exists():
            print("❌ ONNX model not found!")
            print("   Run export_dia_to_onnx() first")
            return False
        
        print("Submitting compile job to AI Hub...")
        print("  ⏳ This may take 10-30 minutes")
        print()
        
        # Submit compile job
        # Note: This is a placeholder - actual implementation needs:
        # - Correct input/output specs
        # - Target device selection
        # - Quantization settings
        
        print("⚠️  Deployment requires:")
        print("  1. ONNX model export (see export_dia_to_onnx)")
        print("  2. Model quantization (may be needed for 1.6B model)")
        print("  3. Input/output specifications")
        print("  4. Target device configuration")
        print()
        
        return False
        
    except ImportError:
        print("❌ qai-hub not installed!")
        print("   Install with: pip install qai-hub")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    
    print("\n" + "=" * 70)
    print(" 🎤 Dia-1.6B NPU Deployment ".center(70))
    print("=" * 70)
    print()
    print("This script helps deploy Dia-1.6B TTS model to Qualcomm NPU.")
    print()
    print("Steps:")
    print("  1. Test model locally (test_dia_local.py)")
    print("  2. Export to ONNX format")
    print("  3. Deploy to NPU via Qualcomm AI Hub")
    print()
    print("⚠️  Challenges:")
    print("  - Model is large (1.6B parameters, ~10GB)")
    print("  - May require quantization for NPU memory")
    print("  - Complex architecture (encoder + decoder + vocoder)")
    print("  - Currently GPU-only (CPU support coming)")
    print()
    
    print("Options:")
    print("  1. Export to ONNX")
    print("  2. Deploy to NPU (requires ONNX model)")
    print("  3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        export_dia_to_onnx()
    elif choice == "2":
        deploy_dia_to_npu()
    else:
        print("Exiting.")


if __name__ == "__main__":
    main()

