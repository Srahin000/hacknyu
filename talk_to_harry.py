"""
Talk to Harry Potter - Interactive Chat
"""

print("=" * 60)
print("LOADING HARRY POTTER AI...")
print("=" * 60)

from harry_llm import HarryPotterLLM

harry = HarryPotterLLM(use_npu=False)

print("\n" + "=" * 60)
print("Harry is ready! Start chatting!")
print("Commands: 'quit' to exit, 'reset' to clear history")
print("=" * 60)

print("\nHarry: Hey! What's up?")

while True:
    user_input = input("\nYou: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("\nHarry: See you later!")
        break
    
    if user_input.lower() == 'reset':
        harry.reset_context()
        print("\nHarry: Okay, starting fresh!")
        continue
    
    print("\n[Harry is thinking...]", end='', flush=True)
    response, time_taken = harry.respond(user_input)
    print('\r' + ' ' * 30 + '\r', end='')
    print(f"Harry: {response}")
    print(f"       [took {time_taken:.1f}s]")

