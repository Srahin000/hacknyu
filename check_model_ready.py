"""
Check if NPU Model is Downloaded and Ready
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("CHECKING NPU MODEL STATUS")
print("=" * 60)

# Check for model file
model_path = Path("models/llama_npu/model.onnx")

print("\n[1/3] Checking for ONNX model...")
if model_path.exists():
    size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"✅ ONNX model found!")
    print(f"   Location: {model_path}")
    print(f"   Size: {size_mb:.1f} MB")
    
    print("\n[2/3] Next step: Deploy to NPU")
    print("   Run: python deploy_fixed.py --model models/llama_npu/model.onnx")
else:
    print("❌ ONNX model NOT found")
    print(f"   Expected location: {model_path.absolute()}")
    print("\n📥 Download instructions:")
    print("   1. Go to: https://aihub.qualcomm.com/models")
    print("   2. Search: 'Llama-3.2-1B'")
    print("   3. Download ONNX format")
    print("   4. Save to: models/llama_npu/model.onnx")

# Check for deployed model
deployed_path = Path("deployed_models/llama_npu")

print("\n[3/3] Checking for deployed NPU model...")
if deployed_path.exists():
    print(f"✅ Deployed model found!")
    print(f"   Location: {deployed_path}")
    print("\n🎉 Ready to use!")
    print("   Run: python talk_to_harry_npu.py")
else:
    print("⏳ Model not yet deployed")
    if model_path.exists():
        print("   Next: Deploy the ONNX model to NPU")
        print("   Run: python deploy_fixed.py --model models/llama_npu/model.onnx")

print("\n" + "=" * 60)
print("STATUS SUMMARY")
print("=" * 60)

status = []
if model_path.exists():
    status.append("✅ ONNX model downloaded")
else:
    status.append("❌ ONNX model - NEED TO DOWNLOAD")

if deployed_path.exists():
    status.append("✅ NPU model deployed")
else:
    status.append("⏳ NPU model - NEED TO DEPLOY")

for s in status:
    print(s)

print("\n" + "=" * 60)

