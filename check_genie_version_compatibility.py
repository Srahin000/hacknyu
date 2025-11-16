"""
Check Genie bundle version compatibility
Extracts version info from export logs and compares with installed SDK
"""
import json
import re
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def extract_job_ids_from_binaries():
    """Extract AI Hub job IDs from binary filenames"""
    bundle_dir = Path("genie_bundle")
    bin_files = list(bundle_dir.glob("*.bin"))
    
    job_ids = set()
    for bin_file in bin_files:
        # Pattern: job_<job_id>_optimized_bin_<hash>.bin
        match = re.search(r'job_([a-z0-9]+)_', bin_file.name)
        if match:
            job_ids.add(match.group(1))
    
    return sorted(job_ids)

def check_export_log():
    """Check export log for version information"""
    log_path = Path("llm_export.log")
    if not log_path.exists():
        return None, "Export log not found"
    
    version_info = {}
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Look for QAIRT/QNN version patterns
        patterns = [
            r'QAIRT[:\s]+([\d\.]+)',
            r'QNN[:\s]+([\d\.]+)',
            r'version[:\s]+([\d\.]+)',
            r'([\d]+\.[\d]+\.[\d]+\.[\d]+)',  # Version like 2.31.0.250130
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                version_info[pattern] = matches[:5]  # First 5 matches
        
        # Look for job URLs or IDs
        job_urls = re.findall(r'https://app\.aihub\.qualcomm\.com/jobs/[a-z0-9]+', content)
        if job_urls:
            version_info['job_urls'] = job_urls[:5]
        
    except Exception as e:
        return None, f"Error reading log: {e}"
    
    return version_info, None

def get_installed_qnn_sdk_version():
    """Get installed QNN SDK version"""
    qnn_sdk_root = os.environ.get('QNN_SDK_ROOT') or os.environ.get('QAIRT_HOME')
    
    if not qnn_sdk_root:
        # Try common locations
        common_paths = [
            Path("C:/Qualcomm/AIStack/QAIRT"),
            Path("C:/Program Files/Qualcomm/AIStack/QAIRT"),
        ]
        
        for base_path in common_paths:
            if base_path.exists():
                # Get latest version directory
                versions = sorted([d for d in base_path.iterdir() if d.is_dir()], reverse=True)
                if versions:
                    qnn_sdk_root = str(versions[0])
                    break
    
    if not qnn_sdk_root:
        return None, "QNN_SDK_ROOT not set and not found in common locations"
    
    qnn_path = Path(qnn_sdk_root)
    
    # Extract version from path (e.g., C:\Qualcomm\AIStack\QAIRT\2.31.0.250130)
    version_match = re.search(r'([\d]+\.[\d]+\.[\d]+\.[\d]+)', str(qnn_path))
    if version_match:
        version = version_match.group(1)
        return version, str(qnn_path)
    
    # Try to find version file
    version_files = [
        qnn_path / "VERSION.txt",
        qnn_path / "version.txt",
        qnn_path / "VERSION",
    ]
    
    for vf in version_files:
        if vf.exists():
            try:
                with open(vf, 'r') as f:
                    version = f.read().strip()
                    return version, str(qnn_path)
            except:
                pass
    
    return None, f"Could not determine version from path: {qnn_path}"

def main():
    print("=" * 70)
    print(" GENIE VERSION COMPATIBILITY CHECKER ".center(70))
    print("=" * 70)
    print()
    
    # 1. Check installed QNN SDK
    print("1️⃣ INSTALLED QNN SDK:")
    version, path = get_installed_qnn_sdk_version()
    if version:
        print(f"   ✅ Version: {version}")
        print(f"   📂 Path: {path}")
    else:
        print(f"   ❌ {path}")
        print("   💡 Set QNN_SDK_ROOT environment variable")
    print()
    
    # 2. Check export log
    print("2️⃣ EXPORT LOG ANALYSIS:")
    log_info, error = check_export_log()
    if error:
        print(f"   ⚠️  {error}")
    elif log_info:
        print("   ✅ Found version information:")
        for key, values in log_info.items():
            if isinstance(values, list) and values:
                print(f"      {key}: {', '.join(values[:3])}")
    else:
        print("   ⚠️  No version information found in log")
    print()
    
    # 3. Extract job IDs from binaries
    print("3️⃣ AI HUB JOB IDs (from binary filenames):")
    job_ids = extract_job_ids_from_binaries()
    if job_ids:
        print(f"   Found {len(job_ids)} unique job ID(s):")
        for job_id in job_ids:
            print(f"      - {job_id}")
            print(f"        🔗 https://app.aihub.qualcomm.com/jobs/{job_id}")
        print()
        print("   💡 Check these job pages to find:")
        print("      - QAIRT/QNN version used for compilation")
        print("      - Any errors or warnings")
        print("      - Model compatibility information")
    else:
        print("   ⚠️  Could not extract job IDs from binary filenames")
    print()
    
    # 4. Recommendations
    print("=" * 70)
    print(" RECOMMENDATIONS ".center(70))
    print("=" * 70)
    print()
    
    if version and job_ids:
        print("📋 Next Steps:")
        print("   1. Visit the AI Hub job pages listed above")
        print("   2. Check the 'QAIRT Version' or 'QNN Version' field")
        print("   3. Compare with your installed version:", version)
        print()
        print("   If versions don't match:")
        print("      → Download matching QAIRT SDK version")
        print("      → Set QNN_SDK_ROOT to the matching version")
        print("      → OR re-export model with current SDK version")
    elif not version:
        print("⚠️  QNN SDK not found!")
        print("   Set QNN_SDK_ROOT environment variable")
        print("   Example: $env:QNN_SDK_ROOT = 'C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130'")
    else:
        print("📋 Check AI Hub job pages to find compilation version")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

