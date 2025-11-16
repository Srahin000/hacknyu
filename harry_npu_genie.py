"""
Harry Potter AI - NPU-Powered via Qualcomm Genie SDK

This uses the official Qualcomm QAIRT/Genie SDK to run Llama 3.2 1B
on Snapdragon NPU for fast (~500ms) Harry Potter responses.
"""

import subprocess
import sys
import os
import time

class HarryPotterNPU:
    """Harry Potter AI powered by Qualcomm NPU via Genie SDK"""
    
    def __init__(self, genie_bundle_path="harry_genie_bundle"):
        self.genie_path = os.path.abspath(genie_bundle_path)
        self.genie_exe = "genie-t2t-run.exe"  # Should be in PATH from QAIRT setup
        self.config_path = os.path.join(self.genie_path, "genie_config.json")
        
        # Verify bundle exists
        if not os.path.exists(self.genie_path):
            print(f"❌ Error: Genie bundle not found at: {self.genie_path}")
            print("\nYou need to export the model first:")
            print("  pip install \"qai-hub-models[llama-v3-2-1b-instruct]\"")
            print("  python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \\")
            print("    --chipset qualcomm-snapdragon-x-elite \\")
            print("    --skip-profiling \\")
            print("    --output-dir harry_genie_bundle")
            sys.exit(1)
        
        if not os.path.exists(self.config_path):
            print(f"❌ Error: genie_config.json not found in bundle")
            sys.exit(1)
        
        # Harry's personality system prompt
        self.system_prompt = """You are Harry Potter from the books.

Personality traits:
- Brave but not reckless
- Modest about your achievements
- Loyal to friends
- Kind and empathetic
- Sometimes sarcastic with enemies
- Speaks like a British teenager

IMPORTANT: Keep responses SHORT (1-2 sentences maximum).
Answer directly and naturally, as Harry would speak."""
        
        print("🔮 Harry Potter AI initialized!")
        print(f"📂 Bundle: {self.genie_path}")
        print(f"⚡ NPU: Snapdragon X Elite")
        print(f"🧠 Model: Llama 3.2 1B")
        print()
    
    def ask_harry(self, question):
        """
        Ask Harry a question and get NPU-powered response
        
        Returns: (response_text, latency_ms)
        """
        
        # Build Llama 3.2 format prompt with system + user message
        # Note: In PowerShell, `n is newline. In Python strings, \n is newline.
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{self.system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        
        # Build command
        cmd = [
            self.genie_exe,
            "-c", self.config_path,
            "-p", prompt
        ]
        
        try:
            start_time = time.time()
            
            # Run Genie (this executes on NPU!)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.genie_path,
                timeout=30  # 30 second timeout
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Parse output
            output = result.stdout
            
            # Genie output format: [BEGIN]: <response>[END]
            if "[BEGIN]:" in output or "[BEGIN]" in output:
                # Extract text between [BEGIN] and [END]
                if "[BEGIN]:" in output:
                    response = output.split("[BEGIN]:")[1]
                else:
                    response = output.split("[BEGIN]")[1]
                
                if "[END]" in response:
                    response = response.split("[END]")[0]
                
                response = response.strip()
                
                # Clean up response
                response = response.replace("\\n", " ").replace("\n", " ").strip()
                
                return response, latency_ms
            
            else:
                # Fallback if format unexpected
                print(f"Unexpected output format:\n{output}")
                return "Sorry, something went wrong with the magic...", latency_ms
        
        except subprocess.TimeoutExpired:
            return "The spell took too long to cast...", 30000
        
        except FileNotFoundError:
            print(f"\n❌ Error: {self.genie_exe} not found!")
            print("\nMake sure QAIRT SDK is installed and environment variables are set:")
            print("  $env:QAIRT_HOME = \"C:\\Path\\To\\QAIRT\"")
            print("  $env:Path should include QAIRT bin directory")
            return "QAIRT SDK not configured properly.", 0
        
        except Exception as e:
            print(f"\n❌ Error running Genie: {e}")
            import traceback
            traceback.print_exc()
            return "Something went wrong...", 0


def main():
    """Interactive chat with Harry Potter on NPU"""
    
    print("\n" + "="*70)
    print(" ⚡ CHAT WITH HARRY POTTER ⚡".center(70))
    print(" (Powered by Qualcomm NPU - Snapdragon X Elite)".center(70))
    print("="*70)
    print()
    
    # Initialize Harry
    harry = HarryPotterNPU()
    
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
            
            # Ask Harry (NPU inference!)
            print("🔮 ", end='', flush=True)
            response, latency = harry.ask_harry(user_input)
            latencies.append(latency)
            
            # Display response
            print(f"\r⚡ Harry: {response}")
            print(f"   (NPU latency: {latency}ms)")
            print()
    
    except KeyboardInterrupt:
        print("\n\n⚡ Harry: Interrupted! Goodbye!")
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

