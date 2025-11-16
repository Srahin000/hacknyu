"""
Fix genie_config.json to use absolute paths
This may resolve error 30001 if path resolution is the issue
"""
import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def fix_genie_config_paths():
    """Update genie_config.json to use absolute paths"""
    bundle_dir = Path("genie_bundle").absolute()
    config_path = bundle_dir / "genie_config.json"
    
    print(f"📂 Bundle directory: {bundle_dir}")
    print(f"📝 Config file: {config_path}")
    print()
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    # Backup original
    backup_path = config_path.with_suffix('.json.backup')
    print(f"💾 Creating backup: {backup_path.name}")
    import shutil
    shutil.copy2(config_path, backup_path)
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("🔧 Updating paths to absolute...")
    
    # Update ctx-bins to absolute paths
    if 'ctx-bins' in config.get('dialog', {}).get('engine', {}).get('model', {}).get('binary', {}):
        ctx_bins = config['dialog']['engine']['model']['binary']['ctx-bins']
        print(f"   Found {len(ctx_bins)} ctx-bins")
        
        updated_bins = []
        for bin_name in ctx_bins:
            bin_path = bundle_dir / bin_name
            if bin_path.exists():
                abs_path = str(bin_path)
                updated_bins.append(abs_path)
                print(f"   ✅ {bin_name} -> {abs_path}")
            else:
                print(f"   ⚠️  {bin_name} not found, keeping relative path")
                updated_bins.append(bin_name)
        
        config['dialog']['engine']['model']['binary']['ctx-bins'] = updated_bins
    
    # Update tokenizer path
    tokenizer_path = config.get('dialog', {}).get('tokenizer', {}).get('path', '')
    if tokenizer_path:
        tokenizer_full = bundle_dir / tokenizer_path if not Path(tokenizer_path).is_absolute() else Path(tokenizer_path)
        if tokenizer_full.exists():
            config['dialog']['tokenizer']['path'] = str(tokenizer_full)
            print(f"   ✅ tokenizer: {tokenizer_path} -> {tokenizer_full}")
        else:
            print(f"   ⚠️  tokenizer not found at {tokenizer_full}")
    
    # Update extensions path
    extensions = config.get('dialog', {}).get('engine', {}).get('backend', {}).get('extensions', '')
    if extensions:
        ext_full = bundle_dir / extensions if not Path(extensions).is_absolute() else Path(extensions)
        if ext_full.exists():
            config['dialog']['engine']['backend']['extensions'] = str(ext_full)
            print(f"   ✅ extensions: {extensions} -> {ext_full}")
        else:
            print(f"   ⚠️  extensions not found at {ext_full}")
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print()
    print("✅ Config updated with absolute paths!")
    print(f"   Backup saved to: {backup_path}")
    print()
    print("🧪 Try running Genie again:")
    print('   python run_genie_safe.py "Hello, my name is Harry Potter"')
    
    return True

if __name__ == "__main__":
    fix_genie_config_paths()

