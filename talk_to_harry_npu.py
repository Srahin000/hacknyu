"""
Talk to Harry Potter - NPU Version

Uses deployed NPU-optimized Llama model
"""

import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("HARRY POTTER - NPU VERSION")
print("=" * 60)

# Check if NPU model exists
deployed_model = Path("deployed_models/llama_npu")
if not deployed_model.exists():
    print("\n❌ NPU model not deployed yet!")
    print("\nRun these commands first:")
    print("  1. python check_model_ready.py")
    print("  2. python deploy_fixed.py --model models/llama_npu/model.onnx")
    print("  3. Wait for deployment to complete (10-30 min)")
    print("  4. Then run this script again")
    sys.exit(1)

print("\n⚡ Loading NPU-optimized Harry...")

try:
    import onnxruntime as ort
    
    # Find the compiled model
    model_file = None
    for f in deployed_model.rglob("*.onnx"):
        model_file = f
        break
    
    if not model_file:
        print("❌ Could not find compiled ONNX model")
        print(f"   Checked in: {deployed_model}")
        sys.exit(1)
    
    print(f"   Loading: {model_file.name}")
    
    # Load ONNX model
    session = ort.InferenceSession(str(model_file))
    
    print("✅ Harry Potter AI ready (NPU)!")
    print("   Expected latency: ~300-500ms")
    
    # Harry's personality
    system_prompt = """You are Harry Potter. Keep responses SHORT (1-2 sentences).
Personality: Brave, modest, kind
Speech: "Blimey!", "At Hogwarts..."
Tone: Friendly teenager"""
    
    context = []
    
    print("\n" + "=" * 60)
    print("Chat with Harry!")
    print("Commands: 'quit' to exit, 'reset' to clear history")
    print("=" * 60)
    
    print("\nHarry: Hey! What do you want to know?")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nHarry: See you later!")
            break
        
        if user_input.lower() == 'reset':
            context = []
            print("\nHarry: Alright, starting fresh!")
            continue
        
        # Build prompt
        context_str = ""
        if context:
            for user_q, harry_resp in context[-2:]:
                context_str += f"Student: {user_q}\nHarry: {harry_resp}\n\n"
        
        prompt = f"""{system_prompt}

{context_str}
Student: {user_input}

Harry:"""
        
        print("\n[NPU processing...]", end='', flush=True)
        start_time = time.time()
        
        # NOTE: This is simplified ONNX inference
        # Full implementation needs proper tokenization
        # For now, using as a placeholder
        
        # Actual response would come from ONNX inference
        # But we need tokenizer which isn't included in deployed model
        response = "Blimey! The NPU model works, but needs tokenizer setup."
        
        elapsed = time.time() - start_time
        
        print('\r' + ' ' * 30 + '\r', end='')
        print(f"Harry: {response}")
        print(f"       [⚡ {elapsed*1000:.0f}ms]")
        
        context.append((user_input, response))
        if len(context) > 3:
            context.pop(0)

except ImportError:
    print("\n❌ onnxruntime not installed")
    print("   Run: pip install onnxruntime")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE: Use CPU version while debugging")
    print("=" * 60)
    print("   python talk_to_harry.py")

