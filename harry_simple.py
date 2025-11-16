"""
Harry Potter AI - Simple Transformers Version

Uses the official Hugging Face Transformers library.
Simpler than llama.cpp, works with your HF access.
"""

import sys
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class HarryPotterSimple:
    """Harry Potter AI using Transformers"""
    
    def __init__(self, model_name="meta-llama/Llama-3.2-1B-Instruct"):
        """
        Initialize Harry Potter LLM
        
        Args:
            model_name: Hugging Face model ID
        """
        
        print("🔮 Loading Harry Potter AI...")
        print(f"📂 Model: {model_name}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use FP16 for speed
            device_map="auto",  # Auto device placement
            low_cpu_mem_usage=True
        )
        
        # Harry's personality
        self.system_prompt = """You are Harry Potter from the books.

Personality: Brave, modest, loyal, kind, sometimes sarcastic with enemies.
Speech: British teenager, natural and conversational.

IMPORTANT: Keep responses SHORT (1-2 sentences maximum).
Answer directly as Harry would speak."""
        
        print(f"✓ Harry Potter AI ready!")
        print(f"  Device: {self.model.device}")
        print(f"  Expected latency: ~2-4s per response")
        print()
    
    def ask_harry(self, question):
        """Ask Harry a question"""
        
        # Build messages in chat format
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        start_time = time.time()
        
        # Apply chat template and tokenize
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=60,  # Short responses
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Decode only the new tokens (not the input)
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        ).strip()
        
        return response, latency_ms


def main():
    """Interactive chat with Harry"""
    
    print("\n" + "="*70)
    print(" ⚡ CHAT WITH HARRY POTTER ⚡".center(70))
    print(" (Transformers version - Simple & Official)".center(70))
    print("="*70)
    print()
    
    # Initialize Harry
    try:
        harry = HarryPotterSimple()
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nMake sure you:")
        print("  1. Have Hugging Face access to Llama 3.2")
        print("  2. Are logged in: huggingface-cli login")
        print("  3. Accepted the license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct")
        return
    
    print("Type your questions below. Commands:")
    print("  'quit' or 'exit' - End conversation")
    print("  'stats' - Show performance stats")
    print()
    print("-"*70)
    print()
    
    latencies = []
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n⚡ Harry: See you later! Stay safe!")
                break
            
            if user_input.lower() == 'stats':
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
                    print(f"\n📊 Stats:")
                    print(f"  Responses: {len(latencies)}")
                    print(f"  Avg latency: {avg_latency:.0f}ms")
                    print(f"  Min latency: {min(latencies)}ms")
                    print(f"  Max latency: {max(latencies)}ms")
                else:
                    print("\n📊 No stats yet - ask Harry something first!")
                print()
                continue
            
            # Ask Harry
            print("🔮 ", end='', flush=True)
            response, latency = harry.ask_harry(user_input)
            latencies.append(latency)
            
            # Display response
            print(f"\r⚡ Harry: {response}")
            print(f"   (Latency: {latency}ms)")
            print()
    
    except KeyboardInterrupt:
        print("\n\n⚡ Harry: Interrupted! Goodbye!")
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

