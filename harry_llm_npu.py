import os
import subprocess
import tempfile
import time
from pathlib import Path

class HarryPotterNPU:
    def __init__(self, bundle_dir="genie_bundle"):
        self.bundle_dir = Path(bundle_dir).absolute()  # Use absolute path
        self.genie_config = self.bundle_dir / "genie_config.json"
        self.genie_exe = self.bundle_dir / "genie-t2t-run.exe"
        
        if not self.genie_config.exists():
            raise FileNotFoundError(f"Config not found: {self.genie_config}")
        if not self.genie_exe.exists():
            raise FileNotFoundError(f"Genie exe not found: {self.genie_exe}")
        
        # Harry Potter character prompt - SHORT for Genie (keeps answers under max tokens)
        self.system_prompt = """You are Harry Potter, the British wizard. 

BE: Brave, loyal, friendly, helpful. Use British slang like "mate", "brilliant", "blimey".

RULES:
- Answer in 1-2 SHORT sentences
- Be natural and encouraging
- Don't overdo wizarding references"""
    
    def ask_harry(self, question):
        prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{self.system_prompt}\n\nUser: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        
        start = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            result = subprocess.run(
                [str(self.genie_exe), "-c", str(self.genie_config), "-p", prompt],
                cwd=str(self.bundle_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            latency = int((time.time() - start) * 1000)
            
            # Check return code
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else result.stdout[:200] if result.stdout else "Unknown error"
                return f"Sorry, I'm having trouble thinking right now. Try again?", latency
            
            # Parse output
            output = result.stdout
            if not output or len(output.strip()) < 5:
                return f"Hmm, I'm not sure what to say. Ask me something else?", latency
            
            # Extract response
            if "[BEGIN]:" in output:
                try:
                    response = output.split("[BEGIN]:")[1].split("[END]")[0].strip()
                except (IndexError, ValueError):
                    response = output.strip()
            else:
                response = output.strip()
            
            # Validate response
            if not response or len(response) < 3:
                return f"Sorry, I lost my train of thought. What were you asking?", latency
            
            return response, latency
            
        except subprocess.TimeoutExpired:
            return f"Sorry mate, I'm thinking too slowly. Try again?", int((time.time() - start) * 1000)
            
        except Exception as e:
            return f"Blimey, something went wrong. Let's try that again.", int((time.time() - start) * 1000)
            
        finally:
            try:
                os.unlink(prompt_file)
            except:
                pass


