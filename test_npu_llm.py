import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from harry_llm_npu import HarryPotterNPU

if __name__ == "__main__":
    try:
        harry = HarryPotterNPU()
        response, latency = harry.ask_harry("What is your name?")
        print(f"Response: {response}")
        print(f"Latency: {latency}ms")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)










