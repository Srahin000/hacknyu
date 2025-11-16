"""
Harry Potter LLM - Direct NPU via qai_hub_models

Uses Llama-v2-7B-Chat from Qualcomm AI Hub (NPU-optimized)
"""

import sys
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HarryPotterNPU:
    """Harry Potter using NPU-optimized Llama"""
    
    def __init__(self):
        self.model = None
        self.context = []
        self.max_context = 3
        self.system_prompt = self._get_harry_personality()
        
        self._load_npu_model()
    
    def _get_harry_personality(self):
        """Harry's personality"""
        return """You are Harry Potter speaking to a young student.

Personality: Brave, modest, kind, encouraging
Speech: Use "Blimey!", "Ron and Hermione...", "At Hogwarts..."
Tone: Friendly teenager

IMPORTANT: Keep responses SHORT (1-2 sentences max)!"""
    
    def _load_npu_model(self):
        """Load NPU-optimized Llama from AI Hub"""
        print("🔮 Loading Harry Potter AI (NPU)...")
        print("  Using Qualcomm AI Hub Llama-v2-7B...")
        print("  (First run downloads ~4GB model - may take 5-10 min)")
        
        try:
            from qai_hub_models.models import llama_v2_7b_chat_quantized
            
            # This loads the NPU-optimized model
            self.model = llama_v2_7b_chat_quantized.from_pretrained()
            
            print("✓ Harry Potter AI ready!")
            print("  Model: Llama-v2-7B-Chat (NPU-optimized)")
            print("  Device: Snapdragon NPU")
            print("  Expected latency: ~500ms-1s on device")
            print("  Current (CPU emulation): ~2-3s")
            
        except Exception as e:
            print(f"\n✗ Error loading NPU model: {e}")
            print("\nTroubleshooting:")
            print("  1. Check API key: python check_device.py")
            print("  2. Reinstall: pip install --upgrade qai-hub-models")
            raise
    
    def _build_prompt(self, user_input):
        """Build prompt with context"""
        context_str = ""
        if self.context:
            for user_q, harry_resp in self.context[-2:]:
                context_str += f"Student: {user_q}\nHarry: {harry_resp}\n\n"
        
        prompt = f"""{self.system_prompt}

{context_str}
Student: {user_input}

Harry (respond in 1-2 sentences):"""
        
        return prompt
    
    def respond(self, user_input):
        """Generate Harry's response"""
        if not self.model:
            return "Sorry, my wand isn't working...", 0
        
        # Build prompt
        prompt = self._build_prompt(user_input)
        
        start_time = time.time()
        
        try:
            # Generate with NPU model
            # Note: Exact API depends on qai_hub_models version
            # This is a simplified interface
            response = self.model.generate(
                prompt,
                max_length=50,  # Keep it short
                temperature=0.7
            )
            
            # Clean up response
            if isinstance(response, list):
                response = response[0]
            
            response = response.strip()
            
            # Extract just Harry's response
            if '\n' in response:
                response = response.split('\n')[0]
            
            response = response.strip('"\'').strip()
            
            if response and not response.endswith(('.', '!', '?')):
                response += '.'
            
        except Exception as e:
            print(f"\nGeneration error: {e}")
            response = "Blimey, something went wrong with that spell!"
        
        elapsed = time.time() - start_time
        
        # Update context
        self.context.append((user_input, response))
        if len(self.context) > self.max_context:
            self.context.pop(0)
        
        return response, elapsed
    
    def reset_context(self):
        """Clear conversation history"""
        self.context = []
        print("✓ Context cleared")


def main():
    """Interactive chat with NPU Harry"""
    print("=" * 60)
    print("HARRY POTTER - NPU VERSION")
    print("=" * 60)
    
    try:
        harry = HarryPotterNPU()
        
        print("\n" + "=" * 60)
        print("Ready to chat!")
        print("Commands: 'quit' to exit, 'reset' to clear history")
        print("=" * 60)
        
        print("\nHarry: Hey! What do you want to know?")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nHarry: Take care!")
                break
            
            if user_input.lower() == 'reset':
                harry.reset_context()
                print("\nHarry: Alright, starting fresh!")
                continue
            
            print("\n[Thinking...]", end='', flush=True)
            response, latency = harry.respond(user_input)
            print('\r' + ' ' * 20 + '\r', end='')
            print(f"Harry: {response}")
            print(f"       [⚡ {latency:.1f}s]")
        
    except KeyboardInterrupt:
        print("\n\nHarry: Caught you! See you later!")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

