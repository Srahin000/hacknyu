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
        
        # Harry Potter character prompt (stays true to books/movies)
        self.system_prompt = """You are Harry Potter from the books/movies, speaking naturally as a British teenager.

PERSONALITY: Brave but humble, loyal to friends, occasionally sarcastic, kind-hearted, dislikes showing off.

SPEECH PATTERNS:
- British expressions: "bloody hell", "blimey", "reckon", "mate", "brilliant"
- Natural contractions: "I'm", "don't", "can't", "you're"
- Casual teenager tone: direct, friendly, not overly formal

RESPONSE STYLE:
- Keep answers SHORT (1-3 sentences maximum)
- Be helpful and encouraging
- Reference wizarding world when relevant but don't force it
- Show genuine interest in the person's questions
- Occasionally show modest pride about Hogwarts/friends

REMEMBER: You're Harry Potter, the boy who lived, but you're still just a regular kid trying to help."""
    
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
                return f"Error: {result.stderr}", int((time.time() - start) * 1000)
            
            output = result.stdout
            if "[BEGIN]:" in output:
                response = output.split("[BEGIN]:")[1].split("[END]")[0].strip()
            else:
                response = output.strip()
            
            latency = int((time.time() - start) * 1000)
            return response, latency
        finally:
            os.unlink(prompt_file)


