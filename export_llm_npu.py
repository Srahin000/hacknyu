import subprocess
import sys
import os
from pathlib import Path

if __name__ == "__main__":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv("QAI_HUB_API_KEY"):
            os.environ["QAI_HUB_API_KEY"] = os.getenv("QAI_HUB_API_KEY")
    
    cmd = [
        sys.executable, "-m", "qai_hub_models.models.llama_v3_2_1b_instruct.export",
        "--chipset", "qualcomm-snapdragon-x-elite",
        "--skip-profiling",
        "--output-dir", "genie_bundle"
    ]
    print("Exporting Llama 3.2 1B for Snapdragon X Elite...")
    subprocess.run(cmd)

