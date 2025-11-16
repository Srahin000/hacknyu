"""
Harry Potter AI - Fast CPU version using llama.cpp (GGUF)

This is a TEMPORARY solution while waiting for NPU export.
Uses llama.cpp with quantized GGUF model for fast CPU inference.

Performance: ~1-2s per response (much better than 6-7s!)
"""

import os
import sys
import time

try:
    from llama_cpp import Llama
except ImportError:
    print("ERROR: llama-cpp-python not installed!")
    print("\nInstall it:")
    print("  pip install llama-cpp-python")
    print("\nOr use precompiled wheels:")
    print("  pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
    sys.exit(1)


class HarryPotterLlamaCpp:
    """Harry Potter AI using llama.cpp (fast CPU inference)"""
    
    def __init__(self, model_path=None):
        """
        Initialize Harry Potter LLM with llama.cpp
        
        Args:
            model_path: Path to GGUF model file
                       If None, will check common locations
        """
        
        # Find GGUF model
        if model_path is None:
            # Check common locations
            possible_paths = [
                "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",  # User's location
                "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
                "llama_gguf/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path is None:
                print("ERROR: GGUF model not found!")
                print("\nDownload it from:")
                print("  https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF")
                print("\nDownload file: Llama-3.2-1B-Instruct-Q4_K_M.gguf")
                print("Save to: C:\\Users\\hackuser\\Documents\\HackNYU\\")
                sys.exit(1)
        
        if not os.path.exists(model_path):
            print(f"ERROR: Model not found: {model_path}")
            sys.exit(1)
        
        print(f"Loading Harry Potter AI...")
        print(f"Model: {model_path}")
        
        # Load model with llama.cpp
        # Q4_K_M = 4-bit quantization, good balance of speed/quality
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=8,  # Use 8 CPU threads
            n_gpu_layers=0,  # CPU only (set to 35+ if you have GPU)
            verbose=False
        )
        
        # Harry's personality
        self.system_prompt = """You are Harry Potter from the books.

Personality: Brave, modest, loyal, kind, sometimes sarcastic.
Speech: British teenager, natural and conversational.

IMPORTANT: Keep responses SHORT (1-2 sentences maximum).
Answer directly as Harry would speak."""
        
        print("Harry Potter AI ready! (CPU-optimized)")
        print("  Expected latency: ~1-2s per response")
        print()
    
    def ask_harry(self, question):
        """Ask Harry a question"""
        
        start_time = time.time()
        
        # Use chat completion API (handles prompt format automatically)
        # This is better than manual prompt building
        output = self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=80,  # Longer for complete responses
            temperature=0.7,
            top_p=0.9,
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract response from chat completion
        response = output["choices"][0]["message"]["content"].strip()
        
        return response, latency_ms


def main():
    """Interactive chat with Harry"""
    
    print("\n" + "="*70)
    print(" CHAT WITH HARRY POTTER ".center(70))
    print(" (Fast CPU version with llama.cpp)".center(70))
    print("="*70)
    print()
    
    # Initialize Harry
    harry = HarryPotterLlamaCpp()
    
    print("Type your questions below. Commands:")
    print("  'quit' or 'exit' - End conversation")
    print("  'stats' - Show performance stats")
    print()
    print("NOTE: This is the FAST CPU version (~1-2s)")
    print("      NPU version will be ~500ms after export completes!")
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
                print("\nHarry: See you later! Stay safe!")
                break
            
            if user_input.lower() == 'stats':
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
                    print(f"\nStats:")
                    print(f"  Responses: {len(latencies)}")
                    print(f"  Avg latency: {avg_latency:.0f}ms")
                    print(f"  Min latency: {min(latencies)}ms")
                    print(f"  Max latency: {max(latencies)}ms")
                else:
                    print("\nNo stats yet - ask Harry something first!")
                print()
                continue
            
            # Ask Harry
            print("Thinking...", end='', flush=True)
            response, latency = harry.ask_harry(user_input)
            latencies.append(latency)
            
            # Display response
            print(f"\rHarry: {response}")
            print(f"   (CPU latency: {latency}ms)")
            print()
    
    except KeyboardInterrupt:
        print("\n\nHarry: Interrupted! Goodbye!")
    
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

