"""
Re-export Llama 3.2 1B model for your current QAIRT SDK version (2.37.1.250807)
This will create binaries compatible with your exact SDK version.
"""
import subprocess
import sys
import os
from pathlib import Path
import time

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_requirements():
    """Check if requirements are met"""
    print("=" * 70)
    print(" CHECKING REQUIREMENTS ".center(70))
    print("=" * 70)
    print()
    
    # Check QNN SDK
    qnn_sdk = os.environ.get('QNN_SDK_ROOT')
    if qnn_sdk and '2.37' in qnn_sdk:
        print(f"✅ QNN SDK: {qnn_sdk}")
    else:
        print("⚠️  QNN_SDK_ROOT not set to 2.37")
        qnn_sdk = "C:\\Qualcomm\\AIStack\\QAIRT\\2.37.1.250807"
        if Path(qnn_sdk).exists():
            print(f"   Found SDK at: {qnn_sdk}")
            os.environ['QNN_SDK_ROOT'] = qnn_sdk
        else:
            print("❌ QAIRT SDK 2.37 not found")
            return False
    
    # Check qai-hub-models
    try:
        import qai_hub_models
        print(f"✅ qai-hub-models installed")
    except ImportError:
        print("❌ qai-hub-models not installed")
        print("   Install with: pip install qai-hub-models")
        return False
    
    # Check API key
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv("QAI_HUB_API_KEY"):
            print("✅ QAI Hub API key loaded")
        else:
            print("⚠️  QAI_HUB_API_KEY not found in .env")
    else:
        print("⚠️  No .env file found (API key may be needed)")
    
    print()
    return True

def show_export_info():
    """Show information about the export process"""
    print("=" * 70)
    print(" EXPORT INFORMATION ".center(70))
    print("=" * 70)
    print()
    print("Model: Llama 3.2 1B Instruct")
    print("Target: Snapdragon X Elite")
    print("Output: genie_bundle_v2_37")
    print()
    print("⏱️  Expected time: 1-2 hours")
    print("💾 Memory needed: ~20GB (including swap)")
    print()
    print("This will create NEW binaries compatible with your SDK version.")
    print()

def run_export():
    """Run the export command"""
    output_dir = "genie_bundle_v2_37"
    
    # Prepare command
    cmd = [
        sys.executable, "-m", 
        "qai_hub_models.models.llama_v3_2_1b_instruct.export",
        "--chipset", "qualcomm-snapdragon-x-elite",
        "--skip-profiling",
        "--output-dir", output_dir
    ]
    
    print("=" * 70)
    print(" STARTING EXPORT ".center(70))
    print("=" * 70)
    print()
    print("Command:", " ".join(cmd))
    print()
    print("Press Ctrl+C to cancel anytime")
    print()
    print("=" * 70)
    print()
    
    # Log file
    log_file = Path("llm_reexport.log")
    
    start_time = time.time()
    
    try:
        with open(log_file, 'w', encoding='utf-8') as log:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            for line in process.stdout:
                print(line, end='')
                log.write(line)
                log.flush()
            
            process.wait()
            
            elapsed = time.time() - start_time
            
            if process.returncode == 0:
                print()
                print("=" * 70)
                print(" EXPORT SUCCESSFUL! ".center(70))
                print("=" * 70)
                print()
                print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
                print(f"📂 Output: {output_dir}/")
                print()
                print("Next steps:")
                print("1. Backup old bundle: mv genie_bundle genie_bundle_old")
                print(f"2. Use new bundle: mv {output_dir} genie_bundle")
                print("3. Test Genie: python run_genie_safe.py \"test\"")
                return True
            else:
                print()
                print("=" * 70)
                print(" EXPORT FAILED ".center(70))
                print("=" * 70)
                print()
                print(f"Check log file: {log_file}")
                return False
                
    except KeyboardInterrupt:
        print("\n\n❌ Export cancelled by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print()
    print("=" * 70)
    print(" RE-EXPORT MODEL FOR SDK 2.37 ".center(70))
    print("=" * 70)
    print()
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        sys.exit(1)
    
    show_export_info()
    
    response = input("Do you want to start the export? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Export cancelled")
        sys.exit(0)
    
    print()
    success = run_export()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

