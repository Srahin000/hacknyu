"""
Test Genie LLM on Qualcomm NPU
Sets up tokenizer and fixes configuration automatically
"""
import os
import json
import shutil
import urllib.request
from pathlib import Path

def setup_genie_bundle():
    """Set up genie bundle with correct files"""
    bundle_dir = Path("genie_bundle")
    bundle_dir.mkdir(exist_ok=True)
    
    # Step 1: Download tokenizer if missing
    tokenizer_path = bundle_dir / "tokenizer.json"
    if not tokenizer_path.exists():
        print("📥 Downloading tokenizer.json from Hugging Face...")
        
        # Try using huggingface_hub first (if user is authenticated)
        try:
            from huggingface_hub import hf_hub_download
            hf_hub_download(
                repo_id="meta-llama/Llama-3.2-1B-Instruct",
                filename="tokenizer.json",
                local_dir=str(bundle_dir),
                local_dir_use_symlinks=False
            )
            print("✅ Tokenizer downloaded successfully!")
        except ImportError:
            print("⚠️  huggingface_hub not installed, trying direct download...")
            # Try direct download as fallback
            tokenizer_url = "https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct/resolve/main/tokenizer.json"
            try:
                urllib.request.urlretrieve(tokenizer_url, tokenizer_path)
                print("✅ Tokenizer downloaded successfully!")
            except Exception as e:
                print(f"❌ Error downloading tokenizer: {e}")
                print("\n   REQUIRED: Please download manually:")
                print("   1. Go to: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct/tree/main")
                print("   2. Download 'tokenizer.json'")
                print(f"   3. Save to: {tokenizer_path.absolute()}")
                print("\n   OR login with: huggingface-cli login")
                return False
        except Exception as e:
            print(f"❌ Error downloading tokenizer: {e}")
            print("\n   Please login with: huggingface-cli login")
            print("   Then run this script again.")
            return False
    else:
        print("✅ Tokenizer already exists")
    
    # Step 2: Check if bin files exist, if not copy from Llama-3.2-1B/original
    bin_files = list(bundle_dir.glob("*.bin"))
    if len(bin_files) < 3:
        print("📦 Copying bin files from Llama-3.2-1B/original...")
        source_dir = Path("Llama-3.2-1B/original")
        if source_dir.exists():
            for bin_file in source_dir.glob("*.bin"):
                dest = bundle_dir / bin_file.name
                if not dest.exists():
                    shutil.copy2(bin_file, dest)
                    print(f"   Copied {bin_file.name}")
        else:
            print(f"❌ Source directory not found: {source_dir}")
            return False
    
    # Step 3: Identify the 3 main model bins (usually the 3 largest)
    all_bins = sorted(bundle_dir.glob("*.bin"), key=lambda x: x.stat().st_size, reverse=True)
    if len(all_bins) < 3:
        print(f"❌ Need at least 3 bin files, found {len(all_bins)}")
        return False
    
    # Take the 3 largest bins
    model_bins = all_bins[:3]
    print(f"\n📝 Using these bin files (3 largest):")
    for i, bin_file in enumerate(model_bins, 1):
        size_mb = bin_file.stat().st_size / (1024*1024)
        print(f"   {i}. {bin_file.name} ({size_mb:.1f} MB)")
    
    # Step 4: Update genie_config.json with correct paths
    config_path = bundle_dir / "genie_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update bin paths (use relative paths from bundle directory)
    config['dialog']['engine']['model']['binary']['ctx-bins'] = [
        bin_file.name for bin_file in model_bins
    ]
    
    # Update tokenizer path
    config['dialog']['tokenizer']['path'] = "tokenizer.json"
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n✅ Genie bundle configured successfully!")
    return True

def test_genie():
    """Test Genie with a simple prompt"""
    import subprocess
    import time
    
    bundle_dir = Path("genie_bundle")
    genie_exe = bundle_dir / "genie-t2t-run.exe"
    config_file = bundle_dir / "genie_config.json"
    
    if not genie_exe.exists():
        print(f"❌ Genie executable not found: {genie_exe}")
        return False
    
    print("\n🧪 Testing Genie with prompt...")
    print("   Prompt: 'What is your name?'\n")
    
    # Use proper Llama 3 prompt format
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nWhat is your name?<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [str(genie_exe), "-c", str(config_file), "-p", prompt],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print("🎉 SUCCESS! Genie is working!\n")
            print("=" * 60)
            print(result.stdout)
            print("=" * 60)
            print(f"\n⏱️  Response time: {elapsed:.2f}s")
            return True
        else:
            print("❌ Genie returned an error:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: Genie took too long to respond (>60s)")
        return False
    except Exception as e:
        print(f"❌ Error running Genie: {e}")
        return False

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        # Fix Windows console encoding
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    print("=" * 60)
    print("🧙 Genie NPU Test Setup")
    print("=" * 60)
    print()
    
    # Setup
    if not setup_genie_bundle():
        print("\n❌ Setup failed. Please fix errors above.")
        exit(1)
    
    # Test
    if test_genie():
        print("\n✅ All tests passed! Genie is ready to use.")
    else:
        print("\n❌ Test failed. Check errors above.")
        exit(1)

