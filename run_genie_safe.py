"""
Safe wrapper to run Genie LLM without breaking Cursor chat
"""
import subprocess
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def copy_dlls_from_qnn_sdk(bundle_dir, required_dlls):
    """Try to copy required DLLs from QNN SDK if QNN_SDK_ROOT is set"""
    qnn_sdk_root = os.environ.get('QNN_SDK_ROOT') or os.environ.get('QAIRT_HOME')
    
    if not qnn_sdk_root:
        return False, "QNN_SDK_ROOT or QAIRT_HOME environment variable not set"
    
    qnn_sdk_root = Path(qnn_sdk_root)
    if not qnn_sdk_root.exists():
        return False, f"QNN SDK root not found: {qnn_sdk_root}"
    
    dll_source_dir = qnn_sdk_root / "lib" / "aarch64-windows-msvc"
    if not dll_source_dir.exists():
        return False, f"QNN SDK DLL directory not found: {dll_source_dir}"
    
    copied = []
    missing = []
    
    for dll in required_dlls:
        source = dll_source_dir / dll
        dest = bundle_dir / dll
        
        if source.exists():
            try:
                import shutil
                shutil.copy2(source, dest)
                copied.append(dll)
            except Exception as e:
                missing.append(f"{dll} (copy failed: {e})")
        else:
            missing.append(f"{dll} (not found in SDK)")
    
    if copied:
        return True, f"Copied {len(copied)} DLLs: {', '.join(copied)}"
    else:
        return False, f"Could not copy DLLs. Missing: {', '.join(missing)}"

def run_genie_safe(user_prompt):
    """Run Genie with proper output handling"""
    bundle_dir = Path("genie_bundle").absolute()
    genie_exe = bundle_dir / "genie-t2t-run.exe"
    config_file = bundle_dir / "genie_config.json"
    
    if not genie_exe.exists():
        print(f"❌ Genie executable not found: {genie_exe}")
        return False
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    # Check for required DLLs (Windows-specific)
    required_dlls = [
        "Genie.dll",
        "QnnGenAiTransformer.dll",
        "QnnGenAiTransformerModel.dll",
        "QnnHtp.dll",
        "QnnHtpNetRunExtensions.dll",
        "QnnHtpPrepare.dll",
        "QnnHtpV73Stub.dll",
        "QnnHtpV73CalculatorStub.dll",
        "QnnSystem.dll"
    ]
    
    missing_dlls = []
    for dll in required_dlls:
        dll_path = bundle_dir / dll
        if not dll_path.exists():
            missing_dlls.append(dll)
    
    if missing_dlls:
        print("❌ Missing required DLLs in genie_bundle:")
        for dll in missing_dlls:
            print(f"   - {dll}")
        
        # Try to automatically copy DLLs if QNN_SDK_ROOT is set
        print("\n🔍 Attempting to copy DLLs from QNN SDK...")
        success, message = copy_dlls_from_qnn_sdk(bundle_dir, missing_dlls)
        
        if success:
            print(f"✅ {message}")
            print("\n🔄 Re-checking DLLs...")
            # Re-check after copying
            still_missing = []
            for dll in required_dlls:
                if not (bundle_dir / dll).exists():
                    still_missing.append(dll)
            
            if still_missing:
                print(f"⚠️  Still missing: {', '.join(still_missing)}")
                print("\n💡 Manual copy instructions:")
                print(f'   Copy-Item "$env:QNN_SDK_ROOT\\lib\\aarch64-windows-msvc\\*.dll" "{bundle_dir}"')
                return False
            else:
                print("✅ All required DLLs are now present!")
                # Continue execution - fall through to run Genie
        else:
            print(f"❌ {message}")
            print("\n💡 These DLLs need to be copied from the QNN SDK.")
            print("   Expected location: $QNN_SDK_ROOT\\lib\\aarch64-windows-msvc\\")
            print("\n   Set QNN_SDK_ROOT environment variable, then:")
            print("   1. Copy manually using PowerShell:")
            print(f'      Copy-Item "$env:QNN_SDK_ROOT\\lib\\aarch64-windows-msvc\\*.dll" "{bundle_dir}"')
            print("\n   2. Or use the PowerShell script from ai-hub-apps:")
            print("      ai-hub-apps\\tutorials\\llm_on_genie\\powershell\\RunLlm.ps1")
            print("\n   Common QNN SDK locations:")
            print("      C:\\Qualcomm\\AIStack\\QAIRT\\<version>")
            print("      C:\\Program Files\\Qualcomm\\AIStack\\QAIRT\\<version>")
            return False
    
    # Format prompt with Llama 3 chat template
    formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    
    print(f"🤖 User: {user_prompt}\n")
    print("💭 Thinking...\n")
    
    # Debug info
    print(f"📂 Bundle directory: {bundle_dir}")
    print(f"🔧 Executable: {genie_exe.name}")
    print(f"⚙️  Config: {config_file.name}\n")
    
    # Set up environment like the PowerShell script does
    env = os.environ.copy()
    env['ADSP_LIBRARY_PATH'] = str(bundle_dir)
    
    # Also add bundle to PATH so DLLs can be found
    current_path = env.get('PATH', '')
    env['PATH'] = f"{bundle_dir}{os.pathsep}{current_path}"
    
    try:
        # Run with output capture and timeout
        result = subprocess.run(
            [str(genie_exe), "-c", str(config_file), "-p", formatted_prompt],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            encoding='utf-8',
            errors='ignore',
            env=env
        )
        
        # Show return code
        print(f"Return code: {result.returncode}\n")
        
        if result.returncode == 0:
            # Clean up the output - only show the assistant's response
            output = result.stdout.strip()
            
            # Filter out debug/verbose output if present
            lines = output.split('\n')
            response_lines = []
            
            for line in lines:
                # Skip lines that look like debug output
                if any(skip in line.lower() for skip in ['loading', 'debug', 'warning', 'initializing', 'backend', 'qnn', 'htp']):
                    continue
                response_lines.append(line)
            
            response = '\n'.join(response_lines).strip()
            
            print("🧙 Genie:")
            print("=" * 60)
            print(response if response else output)
            print("=" * 60)
            return True
        else:
            print("❌ Genie returned an error:")
            
            # Check for Windows access violation (0xC0000005 = 3221225781)
            if result.returncode == 3221225781 or result.returncode == -1073741819:
                print("\n⚠️  Access Violation (0xC0000005) detected!")
                print("   This usually means:")
                print("   1. Missing required DLLs (check above)")
                print("   2. Missing or incorrect ADSP_LIBRARY_PATH")
                print("   3. Corrupted executable or DLLs")
                print("   4. Missing Hexagon DSP libraries (.so files)")
            
            # Check for context binary creation failures (30001, 5005, etc.)
            if "err 30001" in result.stderr or "err 5005" in result.stderr or "Could not create context from binary" in result.stderr:
                error_code = "unknown"
                if "err 30001" in result.stderr:
                    error_code = "30001"
                elif "err 5005" in result.stderr:
                    error_code = "5005"
                
                print(f"\n⚠️  Error {error_code}: Could not create context from binary")
                print("   This usually indicates:")
                if error_code == "30001":
                    print("   1. QNN SDK version mismatch (MOST COMMON)")
                    print("      → Model compiled with different SDK version than runtime")
                    print("      → Check AI Hub job pages for compilation SDK version")
                    print("      → Download matching QAIRT SDK version")
                elif error_code == "5005":
                    print("   1. Binary format incompatibility")
                    print("      → Even with matching major SDK version, sub-version may differ")
                    print("      → Model compiled with: 2.37.1.250807093845_124904")
                    print("      → Your SDK: 2.37.1.250807 (may need exact match)")
                    print("      → Try re-exporting model with current SDK version")
                print("   2. Missing or corrupted model binary files")
                print("   3. Incorrect model format or architecture mismatch")
                print("\n   💡 Run: python check_genie_version_compatibility.py")
                print("   💡 Or: .\\fix_qnn_sdk_version.ps1")
                if error_code == "5005":
                    print("   💡 Consider: Re-export model with current SDK version")
            
            print("\n--- STDOUT (first 1000 chars) ---")
            stdout_preview = result.stdout[:1000] if result.stdout else "(empty)"
            print(stdout_preview)
            if len(result.stdout) > 1000:
                print(f"... ({len(result.stdout) - 1000} more characters)")
            
            print("\n--- STDERR (first 1000 chars) ---")
            stderr_preview = result.stderr[:1000] if result.stderr else "(empty)"
            print(stderr_preview)
            if len(result.stderr) > 1000:
                print(f"... ({len(result.stderr) - 1000} more characters)")
            print("\n" + "=" * 60)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: Genie took too long to respond (>120s)")
        return False
    except Exception as e:
        print(f"❌ Error running Genie: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_genie_safe.py \"Your prompt here\"")
        print("\nExample:")
        print('  python run_genie_safe.py "Hello, my name is Harry Potter"')
        sys.exit(1)
    
    # Join all arguments as the prompt
    prompt = " ".join(sys.argv[1:])
    run_genie_safe(prompt)