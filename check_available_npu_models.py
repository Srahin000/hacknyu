"""
Check Available NPU Models from Qualcomm AI Hub
"""

import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("CHECKING AVAILABLE NPU MODELS")
print("=" * 60)

print("\n[1/3] Checking qai_hub_models...")

try:
    import qai_hub_models
    print("✓ qai_hub_models installed")
    
    # Try to find available LLM models
    print("\n[2/3] Searching for LLM models...")
    
    # Check for Llama models
    llama_models = []
    
    try:
        from qai_hub_models.models import llama_v2_7b_chat_quantized
        llama_models.append("llama_v2_7b_chat_quantized")
    except ImportError:
        pass
    
    try:
        from qai_hub_models.models import llama_v3_8b_chat_quantized
        llama_models.append("llama_v3_8b_chat_quantized")
    except ImportError:
        pass
    
    try:
        from qai_hub_models.models import llama_v3_2_1b_chat_quantized
        llama_models.append("llama_v3_2_1b_chat_quantized")
    except ImportError:
        pass
    
    try:
        from qai_hub_models.models import llama_v3_2_3b_chat_quantized
        llama_models.append("llama_v3_2_3b_chat_quantized")
    except ImportError:
        pass
    
    print("\n[3/3] Available LLM Models:")
    print("=" * 60)
    
    if llama_models:
        print("\n✅ Found NPU-optimized models:")
        for model in llama_models:
            print(f"  • {model}")
        
        print("\n📝 To use:")
        print(f"  from qai_hub_models.models import {llama_models[0]}")
        print(f"  model = {llama_models[0]}.from_pretrained()")
        print(f"  response = model.generate('Hello!')")
        
    else:
        print("\n⚠️  No pre-built LLM models found in qai_hub_models")
        print("\nYou need to:")
        print("  1. Download ONNX model from: https://aihub.qualcomm.com/models")
        print("  2. Save to: models/llama_npu/")
        print("  3. Deploy: python deploy_fixed.py --model models/llama_npu/model.onnx")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE: Check AI Hub Website")
    print("=" * 60)
    print("\nFor latest models, visit:")
    print("  https://aihub.qualcomm.com/models?search=llama")
    print("\nLook for:")
    print("  • Llama-3.2-1B (smallest, fastest)")
    print("  • Llama-3.2-3B (good balance)")
    print("  • Llama-3-8B (best quality)")
    print("\nDownload ONNX format and deploy with deploy_fixed.py")
    
except ImportError as e:
    print(f"✗ qai_hub_models not properly installed: {e}")
    print("\nTry:")
    print("  pip install --upgrade qai-hub-models")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("""
For fastest NPU deployment:

1. Go to: https://aihub.qualcomm.com/models
2. Search: "Llama-3.2-1B" 
3. Download ONNX version
4. Save to: models/llama_npu/
5. Deploy: python deploy_fixed.py --model models/llama_npu/model.onnx

Expected speed: ~500ms (vs current 6-7s)
""")

