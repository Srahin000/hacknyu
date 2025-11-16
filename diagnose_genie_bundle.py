"""
Diagnose Genie bundle to identify missing files and configuration issues
"""
import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def diagnose_genie_bundle():
    """Diagnose the genie_bundle structure"""
    bundle_dir = Path("genie_bundle")
    
    print("=" * 70)
    print(" GENIE BUNDLE DIAGNOSTIC ".center(70))
    print("=" * 70)
    print()
    
    # 1. Check directory structure
    print("1️⃣ DIRECTORY STRUCTURE:")
    print(f"   Bundle path: {bundle_dir.absolute()}")
    print(f"   Exists: {bundle_dir.exists()}")
    
    models_dir = bundle_dir / "models"
    encoder_dir = models_dir / "encoder" if models_dir.exists() else None
    decoder_dir = models_dir / "decoder" if models_dir.exists() else None
    
    print(f"   models/ directory: {models_dir.exists()}")
    if encoder_dir:
        print(f"   models/encoder/: {encoder_dir.exists()}")
    if decoder_dir:
        print(f"   models/decoder/: {decoder_dir.exists()}")
    print()
    
    # 2. List all .bin files with sizes
    print("2️⃣ BINARY FILES (.bin):")
    bin_files = list(bundle_dir.glob("*.bin"))
    if bin_files:
        for bin_file in sorted(bin_files, key=lambda x: x.stat().st_size, reverse=True):
            size_mb = bin_file.stat().st_size / (1024 * 1024)
            print(f"   {bin_file.name:60} {size_mb:8.2f} MB")
    else:
        print("   ❌ No .bin files found!")
    print()
    
    # 3. Check for critical Genie files
    print("3️⃣ CRITICAL GENIE FILES:")
    critical_files = {
        "contexts.bin": bundle_dir / "contexts.bin",
        "model.hpm": bundle_dir / "model.hpm",
        "model.dlc": bundle_dir / "model.dlc",
        "model.json": bundle_dir / "model.json",
        "weights.bin": bundle_dir / "weights.bin",
        "metadata.bin": bundle_dir / "metadata.bin",
    }
    
    for name, path in critical_files.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name:20} {path.exists()}")
    
    # Check encoder/decoder structure
    if encoder_dir and encoder_dir.exists():
        print("\n   Encoder directory files:")
        for f in encoder_dir.glob("*"):
            print(f"      {f.name}")
    
    if decoder_dir and decoder_dir.exists():
        print("\n   Decoder directory files:")
        for f in decoder_dir.glob("*"):
            print(f"      {f.name}")
    print()
    
    # 4. Check genie_config.json
    print("4️⃣ GENIE CONFIG:")
    config_path = bundle_dir / "genie_config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"   ✅ genie_config.json exists")
        print(f"   Model type: {config.get('dialog', {}).get('engine', {}).get('model', {}).get('type', 'unknown')}")
        
        # Check ctx-bins
        ctx_bins = config.get('dialog', {}).get('engine', {}).get('model', {}).get('binary', {}).get('ctx-bins', [])
        if ctx_bins:
            print(f"   ctx-bins referenced: {len(ctx_bins)}")
            for i, bin_name in enumerate(ctx_bins, 1):
                bin_path = bundle_dir / bin_name
                exists = bin_path.exists()
                status = "✅" if exists else "❌"
                print(f"      {status} {i}. {bin_name}")
                if not exists:
                    print(f"         ⚠️  File not found!")
        
        # Check tokenizer
        tokenizer_path = config.get('dialog', {}).get('tokenizer', {}).get('path', '')
        if tokenizer_path:
            full_path = bundle_dir / tokenizer_path if not Path(tokenizer_path).is_absolute() else Path(tokenizer_path)
            exists = full_path.exists()
            status = "✅" if exists else "❌"
            print(f"   {status} tokenizer: {tokenizer_path}")
    else:
        print("   ❌ genie_config.json not found!")
    print()
    
    # 5. Check other important files
    print("5️⃣ OTHER FILES:")
    other_files = {
        "tokenizer.json": bundle_dir / "tokenizer.json",
        "htp_backend_ext_config.json": bundle_dir / "htp_backend_ext_config.json",
        "genie-t2t-run.exe": bundle_dir / "genie-t2t-run.exe",
    }
    
    for name, path in other_files.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name}")
    print()
    
    # 6. Summary and recommendations
    print("=" * 70)
    print(" DIAGNOSIS SUMMARY ".center(70))
    print("=" * 70)
    print()
    
    # Check if this looks like AI Hub export format
    has_ctx_bins = bool(ctx_bins) if config_path.exists() else False
    has_critical_genie_files = any(f.exists() for f in critical_files.values())
    
    if has_ctx_bins and not has_critical_genie_files:
        print("📋 FORMAT DETECTED: Qualcomm AI Hub Export Format")
        print("   - Using ctx-bins (context binaries)")
        print("   - This format should work with genie-t2t-run")
        print()
        print("⚠️  POTENTIAL ISSUES:")
        print("   1. Check if all ctx-bins referenced in config exist")
        print("   2. Verify paths in genie_config.json are correct")
        print("   3. Ensure QNN SDK version matches model compilation version")
        print("   4. Check if model was compiled for correct chipset (v73 for X Elite)")
    elif has_critical_genie_files:
        print("📋 FORMAT DETECTED: Genie Compiled Format")
        print("   - Has contexts.bin, model.hpm, or model.dlc")
        print("   - This is the standard Genie format")
    else:
        print("❌ FORMAT UNKNOWN")
        print("   - Missing both ctx-bins and critical Genie files")
        print("   - Model may not be in Genie-compatible format")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    diagnose_genie_bundle()

