import os
import subprocess
import tempfile
import time
from pathlib import Path

class HarryPotterNPU:
    def __init__(self, bundle_dir="genie_bundle"):
        self.bundle_dir = Path(bundle_dir)
        self.genie_config = self.bundle_dir / "genie_config.json"
        self.genie_exe = self.bundle_dir / "genie-t2t-run.exe"
        
        if not self.genie_config.exists():
            raise FileNotFoundError(f"Config not found: {self.genie_config}")
        if not self.genie_exe.exists():
            raise FileNotFoundError(f"Genie exe not found: {self.genie_exe}")
        
        self.system_prompt = "You are Harry Potter. Be brave, modest, loyal. Keep responses SHORT (1-2 sentences)."
    
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
            
            if result.returncode != 0:
                return f"Error: {result.stderr}", int((time.time() - start) * 1000))
            
            output = result.stdout
            if "[BEGIN]:" in output:
                response = output.split("[BEGIN]:")[1].split("[END]")[0].strip()
            else:
                response = output.strip()
            
            latency = int((time.time() - start) * 1000)
            return response, latency
        finally:
            os.unlink(prompt_file)


