"""
Quick Chat with Harry - Simple Interactive Test
"""

import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("CHAT WITH HARRY POTTER")
print("=" * 60)
print("\n⚡ Loading Harry's AI...")

try:
    from harry_llm import HarryPotterLLM
    
    harry = HarryPotterLLM(use_npu=False)
    
    print("\n" + "=" * 60)
    print("✓ Harry is ready to chat!")
    print("=" * 60)
    print("\nTips:")
    print("  • Type your question and press ENTER")
    print("  • Type 'quit' to exit")
    print("  • Type 'reset' to clear history")
    print("\n" + "=" * 60)
    
    print("\nHarry: Hey! What do you want to know?")
    
    while True:
        try:
            # Get input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Commands
            if user_input.lower() in ['quit', 'exit']:
                print("\nHarry: Take care!")
                break
            
            if user_input.lower() == 'reset':
                harry.reset_context()
                print("\nHarry: Alright, starting fresh!")
                continue
            
            # Generate response
            print("\n[Thinking...]", end='', flush=True)
            response, latency = harry.respond(user_input)
            
            # Show response
            print('\r' + ' ' * 20 + '\r', end='')
            print(f"Harry: {response}")
            print(f"       [{latency:.1f}s]")
            
        except KeyboardInterrupt:
            print("\n\nHarry: See you later!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break
    
except Exception as e:
    print(f"\n✗ Failed to load: {e}")
    import traceback
    traceback.print_exc()
    print("\nMake sure harry_llm.py is working:")
    print("  python harry_llm.py")
    sys.exit(1)

