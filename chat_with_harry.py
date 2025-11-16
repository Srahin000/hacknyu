"""
Interactive Chat with Harry Potter

Real-time conversation with Harry using the fast LLM
"""

import sys
from harry_llm import HarryPotterLLM

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    """Interactive chat with Harry Potter"""
    print("\n" + "=" * 60)
    print("⚡ CHAT WITH HARRY POTTER ⚡")
    print("=" * 60)
    print("\nInitializing Harry's AI...")
    
    # Initialize Harry
    harry = HarryPotterLLM(use_npu=False)
    
    print("\n" + "=" * 60)
    print("Harry Potter is ready to chat!")
    print("=" * 60)
    print("\nCommands:")
    print("  - Type your question and press ENTER")
    print("  - Type 'reset' to clear conversation history")
    print("  - Type 'quit' or 'exit' to end chat")
    print("\n" + "=" * 60)
    
    # Welcome message
    print("\nHarry: Hey there! Harry Potter here. What would you like to know?")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check for commands
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nHarry: Take care! See you around Hogwarts!")
                break
            
            if user_input.lower() == 'reset':
                harry.reset_context()
                print("\nHarry: Alright, starting fresh! What's on your mind?")
                continue
            
            # Get Harry's response
            print("\n[Harry is thinking...]", end='', flush=True)
            response, latency = harry.respond(user_input)
            
            # Clear "thinking" line and show response
            print('\r' + ' ' * 30 + '\r', end='')
            print(f"Harry: {response}")
            print(f"      [⚡ {latency:.2f}s]")
            
        except KeyboardInterrupt:
            print("\n\nHarry: Caught you trying to disapparate! See you later!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("Harry: Blimey, something went wrong with that spell...")
    
    print("\n" + "=" * 60)
    print("Chat ended. Thanks for talking with Harry!")
    print("=" * 60)


if __name__ == "__main__":
    main()

