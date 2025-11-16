"""
Check Qualcomm AI Hub device availability and connection

This script helps verify:
1. API key is set correctly
2. Target device is available
3. Connection to Qualcomm AI Hub is working
"""

import os
import sys
# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import qai_hub as hub
from qai_hub.client import Client
from config import QAI_HUB_API_KEY, TARGET_DEVICE


def check_api_key():
    """Check if API key is set"""
    print("Checking API key...")
    if not QAI_HUB_API_KEY:
        print("✗ QAI_HUB_API_KEY not set")
        print("  Set it with: $env:QAI_HUB_API_KEY='your_key' (PowerShell)")
        print("  Or run: qai-hub configure --api_token your_key")
        return False
    print("✓ API key is set")
    return True


def check_connection():
    """Check connection to Qualcomm AI Hub"""
    print("\nChecking connection to Qualcomm AI Hub...")
    try:
        # Create client and set session token
        client = Client()
        client.set_session_token(QAI_HUB_API_KEY)
        
        # Test connection by trying to get devices
        devices = client.get_devices()
        print("✓ Successfully connected to Qualcomm AI Hub")
        return True, client
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        print("  Verify your API key at: https://app.aihub.qualcomm.com/")
        print("  Or configure using: qai-hub configure --api_token your_key")
        return False, None


def list_available_devices(client):
    """List available devices"""
    print("\nFetching available devices...")
    try:
        devices = client.get_devices()
        print(f"✓ Found {len(devices)} available device(s):")
        for device in devices:
            device_name = device.name if hasattr(device, 'name') else str(device)
            print(f"  - {device_name}")
        return [d.name if hasattr(d, 'name') else str(d) for d in devices]
    except Exception as e:
        print(f"⚠ Could not list devices: {str(e)}")
        print("  Common device names:")
        print("    - samsung-galaxy-s24")
        print("    - samsung-galaxy-s23")
        print("    - samsung-galaxy-s22")
        return []


def check_target_device(available_devices=None):
    """Check if target device is available"""
    print(f"\nChecking target device: {TARGET_DEVICE}")
    
    if not available_devices:
        print(f"⚠ Could not verify device availability")
        return False
    
    # Normalize device names for comparison (case-insensitive, handle spaces/hyphens)
    target_normalized = TARGET_DEVICE.lower().replace('-', ' ').replace('_', ' ')
    available_normalized = {d.lower().replace('-', ' ').replace('_', ' '): d for d in available_devices}
    
    # Check for exact match
    if TARGET_DEVICE in available_devices:
        print(f"✓ Target device '{TARGET_DEVICE}' is available")
        return True
    
    # Check for normalized match
    if target_normalized in available_normalized:
        matched_device = available_normalized[target_normalized]
        print(f"✓ Found matching device: '{matched_device}'")
        print(f"  Note: Config uses '{TARGET_DEVICE}', but device name is '{matched_device}'")
        print(f"  Consider updating config.py to use: '{matched_device}'")
        return True
    
    # Check for partial match (e.g., "samsung galaxy s24" matches "Samsung Galaxy S24")
    matches = [d for d in available_devices if target_normalized in d.lower().replace('-', ' ').replace('_', ' ')]
    if matches:
        print(f"✓ Found {len(matches)} similar device(s):")
        for match in matches[:5]:  # Show first 5 matches
            print(f"  - {match}")
        if len(matches) > 5:
            print(f"  ... and {len(matches) - 5} more")
        print(f"\n  Recommended: Update config.py to use one of these exact names")
        return True
    
    print(f"⚠ Target device '{TARGET_DEVICE}' not found in available devices")
    print("  Available Samsung Galaxy S24 devices:")
    samsung_s24 = [d for d in available_devices if 's24' in d.lower() or 'samsung galaxy s24' in d.lower()]
    for device in samsung_s24[:5]:
        print(f"    - {device}")
    print("  Verify at: https://aihub.qualcomm.com/")
    return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("Qualcomm AI Hub Device Check")
    print("=" * 60)
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Check connection
    success, client = check_connection()
    if not success:
        sys.exit(1)
    
    # List devices
    devices = list_available_devices(client)
    
    # Check target device
    check_target_device(devices)
    
    print("\n" + "=" * 60)
    print("Device check completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify your target device is correct in config.py")
    print("2. Run deployment script: python deploy_stt.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

