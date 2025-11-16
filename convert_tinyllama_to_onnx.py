"""
Convert TinyLlama to ONNX for NPU Deployment

Exports TinyLlama model to ONNX format optimized for Qualcomm NPU
"""

import sys
import torch
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def convert_tinyllama_to_onnx():
    """Convert TinyLlama to ONNX format"""
    
    print("=" * 60)
    print("CONVERTING TINYLLAMA TO ONNX FOR NPU")
    print("=" * 60)
    
    try:
        print("\n[1/5] Loading TinyLlama model...")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        model.eval()
        
        print("✓ Model loaded")
        
        # Create output directory
        output_dir = Path("models/tinyllama_npu")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "model.onnx"
        
        print(f"\n[2/5] Creating dummy inputs...")
        # Fixed input shapes for NPU compatibility
        batch_size = 1
        seq_length = 128  # Fixed sequence length
        
        # Create dummy input
        dummy_input_ids = torch.randint(
            0, tokenizer.vocab_size, 
            (batch_size, seq_length),
            dtype=torch.long
        )
        
        dummy_attention_mask = torch.ones(
            (batch_size, seq_length),
            dtype=torch.long
        )
        
        print(f"✓ Input shape: {dummy_input_ids.shape}")
        print(f"  Fixed sequence length: {seq_length}")
        
        print("\n[3/5] Exporting to ONNX...")
        print("  (This may take 5-10 minutes...)")
        
        # Export to ONNX with static shapes
        torch.onnx.export(
            model,
            (dummy_input_ids, dummy_attention_mask),
            str(output_path),
            export_params=True,
            opset_version=14,  # Compatible with most runtimes
            do_constant_folding=True,
            input_names=['input_ids', 'attention_mask'],
            output_names=['logits'],
            dynamic_axes=None  # NO dynamic axes - static shapes for NPU
        )
        
        print(f"✓ ONNX model exported: {output_path}")
        print(f"  File size: {output_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Save tokenizer
        print("\n[4/5] Saving tokenizer...")
        tokenizer.save_pretrained(output_dir)
        print(f"✓ Tokenizer saved: {output_dir}")
        
        # Create config file
        print("\n[5/5] Creating config...")
        config = {
            "model_name": model_name,
            "seq_length": seq_length,
            "vocab_size": tokenizer.vocab_size,
            "onnx_model": "model.onnx"
        }
        
        import json
        with open(output_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✓ Config saved")
        
        print("\n" + "=" * 60)
        print("✅ CONVERSION COMPLETE!")
        print("=" * 60)
        print(f"\nONNX model: {output_path}")
        print(f"Model directory: {output_dir}")
        
        print("\n📋 Next steps:")
        print(f"\n1. Deploy to NPU:")
        print(f"   python deploy_fixed.py --model {output_path}")
        print(f"\n2. This will compile for Snapdragon NPU (takes 10-30 min)")
        print(f"\n3. After deployment, update harry_llm.py to use NPU model")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n⚠️  WARNING:")
    print("ONNX export for large language models is complex.")
    print("TinyLlama may not export perfectly to ONNX.")
    print("\nAlternative: Use Qualcomm AI Hub pre-optimized models")
    print("Visit: https://aihub.qualcomm.com/models")
    print("\nContinue anyway? This may take 10+ minutes.")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        success = convert_tinyllama_to_onnx()
        
        if not success:
            print("\n" + "=" * 60)
            print("ALTERNATIVE APPROACH")
            print("=" * 60)
            print("""
Since direct ONNX export is complex, consider:

1. Use Qualcomm AI Hub's pre-optimized models:
   - Llama-3.2-1B (already optimized)
   - Llama-2-7B (already optimized)
   
2. Download from: https://aihub.qualcomm.com/models
   - Search for "Llama"
   - Download ONNX version
   - Deploy with deploy_fixed.py

3. For now, use CPU model with optimization:
   - Quantize to 4-bit
   - Use GPTQ or AWQ quantization
   - Still 2-3x faster than current
""")
    else:
        print("\n✓ Cancelled")
        print("\nFor faster responses, consider:")
        print("1. Download pre-optimized Llama from AI Hub")
        print("2. Use 4-bit quantization on CPU")
        print("3. Deploy smaller model to NPU")

