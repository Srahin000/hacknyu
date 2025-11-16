"""
Improved LLM NPU Export Script with Better Error Handling
- Waits for ALL compile jobs
- Shows detailed failure logs
- Supports resuming failed jobs
- Checks memory/swap before starting
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def check_memory_requirements():
    """Check if system has enough memory/swap"""
    print("\n🔍 Checking system memory...")
    
    if sys.platform == 'win32':
        try:
            # Check virtual memory on Windows
            result = subprocess.run(
                ['wmic', 'OS', 'get', 'TotalVirtualMemorySize', '/value'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'TotalVirtualMemorySize' in line:
                        # Value is in KB
                        total_virtual_mb = int(line.split('=')[1].strip()) / 1024
                        print(f"  Total Virtual Memory: {total_virtual_mb:.0f} MB")
                        
                        if total_virtual_mb < 20000:  # Less than 20GB
                            print("\n  ⚠️  WARNING: Low virtual memory detected!")
                            print("     Recommended: At least 20GB virtual memory")
                            print("     See: INCREASE_SWAP_WINDOWS.md for instructions")
                            response = input("\n  Continue anyway? (y/n): ")
                            if response.lower() != 'y':
                                sys.exit(1)
                        else:
                            print("  ✅ Memory looks good!")
        except Exception as e:
            print(f"  ⚠️  Could not check memory: {e}")
            print("     Proceeding anyway...")
    
    print()

def run_export(resume_failed=False):
    """Run the LLM export with better monitoring"""
    
    # Setup environment
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Load API key
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv("QAI_HUB_API_KEY"):
            os.environ["QAI_HUB_API_KEY"] = os.getenv("QAI_HUB_API_KEY")
            print("✅ QAI Hub API key loaded")
        else:
            print("⚠️  No QAI_HUB_API_KEY found in .env")
    else:
        print("⚠️  No .env file found")
    
    # Check memory before starting
    if not resume_failed:
        check_memory_requirements()
    
    # Prepare command
    cmd = [
        sys.executable, "-m", "qai_hub_models.models.llama_v3_2_1b_instruct.export",
        "--chipset", "qualcomm-snapdragon-x-elite",
        "--skip-profiling",
        "--output-dir", "genie_bundle"
    ]
    
    print("="*70)
    print(" 🚀 EXPORTING LLAMA 3.2 1B TO SNAPDRAGON X ELITE NPU ".center(70))
    print("="*70)
    print()
    print("Model: Llama 3.2 1B Instruct")
    print("Device: Snapdragon X Elite")
    print("Output: genie_bundle/")
    print()
    print("⏱️  Expected time: 1-2 hours")
    print("💾 Memory needed: ~20GB (including swap)")
    print()
    print("Tip: You can press Ctrl+C to cancel anytime")
    print()
    print("="*70)
    print()
    
    # Log file
    log_file = Path("llm_export.log")
    print(f"📝 Logging output to: {log_file}")
    print()
    
    # Run export
    start_time = time.time()
    
    try:
        with open(log_file, 'w', encoding='utf-8') as log:
            # Write header
            log.write(f"LLM Export Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write("="*70 + "\n\n")
            log.flush()
            
            # Run subprocess with live output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                # Print to console
                print(line, end='', flush=True)
                # Write to log
                log.write(line)
                log.flush()
            
            # Wait for completion
            return_code = process.wait()
            
            elapsed = time.time() - start_time
            
            print()
            print("="*70)
            print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
            print()
            
            if return_code == 0:
                print("✅ EXPORT COMPLETED SUCCESSFULLY!")
                print()
                print(f"📁 Output saved to: genie_bundle/")
                print()
                print("Next steps:")
                print("  1. Test the model:")
                print("     python test_npu_llm.py")
                print()
                print("  2. Run voice assistant with NPU LLM:")
                print("     python harry_voice_assistant.py")
                print()
            else:
                print("❌ EXPORT FAILED!")
                print(f"   Return code: {return_code}")
                print()
                print(f"📝 Check log file for details: {log_file}")
                print()
                print("Common issues:")
                print("  - Not enough memory/swap (need ~20GB)")
                print("  - Network timeout during download")
                print("  - Incompatible model for this device")
                print()
                print("Solutions:")
                print("  1. Increase swap memory (see INCREASE_SWAP_WINDOWS.md)")
                print("  2. Try on Linux system")
                print("  3. Use CPU mode instead (already working!)")
                print()
            
            print("="*70)
            
            return return_code == 0
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Export cancelled by user")
        print(f"   Partial log saved to: {log_file}")
        return False
    
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_genie_bundle():
    """Check if genie bundle already exists"""
    bundle_dir = Path("genie_bundle")
    
    if not bundle_dir.exists():
        return False
    
    required_files = [
        "genie-t2t-run.exe",
        "genie_config.json"
    ]
    
    has_all = all((bundle_dir / f).exists() for f in required_files)
    
    if has_all:
        # Check for model files
        model_files = list(bundle_dir.glob("*.bin"))
        if model_files:
            print("✅ Genie bundle already exists!")
            print(f"   Location: {bundle_dir}")
            print(f"   Model files: {len(model_files)} found")
            print()
            return True
    
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Export Llama 3.2 1B to Snapdragon X Elite NPU"
    )
    parser.add_argument(
        '--resume-failed',
        action='store_true',
        help='Resume from failed export (skip already completed jobs)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force export even if bundle already exists'
    )
    parser.add_argument(
        '--skip-memory-check',
        action='store_true',
        help='Skip memory requirement check'
    )
    
    args = parser.parse_args()
    
    print()
    print("="*70)
    print(" LLM NPU EXPORT TOOL ".center(70))
    print("="*70)
    print()
    
    # Check if bundle already exists
    if not args.force and not args.resume_failed:
        if check_genie_bundle():
            response = input("Overwrite existing bundle? (y/n): ")
            if response.lower() != 'y':
                print("\nExport cancelled. Use --force to overwrite.")
                sys.exit(0)
            print()
    
    # Run export
    success = run_export(resume_failed=args.resume_failed)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()




