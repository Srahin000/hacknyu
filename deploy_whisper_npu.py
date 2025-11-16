"""
Deploy Whisper STT Model to Qualcomm AI Hub NPU

This script deploys Whisper Base English to your Snapdragon NPU
for ultra-fast speech recognition (~200ms latency)
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def deploy_whisper():
    """Deploy Whisper to Qualcomm AI Hub"""
    
    print("\n" + "="*70)
    print(" DEPLOY WHISPER TO NPU ".center(70))
    print("="*70)
    print()
    
    print("This will:")
    print("  1. Export Whisper Base EN model")
    print("  2. Compile for Snapdragon NPU")
    print("  3. Profile performance")
    print("  4. Save optimized model locally")
    print()
    print("Expected time: 10-30 minutes")
    print()
    
    input("Press ENTER to start deployment...")
    
    # Check if qai_hub_models is installed
    try:
        import qai_hub_models
        print(f"Using qai_hub_models version: {qai_hub_models.__version__}")
    except ImportError:
        print("ERROR: qai_hub_models not installed!")
        print("\nInstall with:")
        print('  pip install "qai-hub-models[whisper_base_en]"')
        return False
    
    # Check device
    print("\nDetecting target device...")
    
    try:
        import qai_hub
        
        # Get available devices
        devices = qai_hub.get_devices()
        
        if not devices:
            print("ERROR: No devices found!")
            print("\nPlease:")
            print("  1. Login to Qualcomm AI Hub: https://app.aihub.qualcomm.com/")
            print("  2. Add your device in the console")
            print("  3. Set QAI_HUB_API_KEY environment variable")
            return False
        
        print(f"\nFound {len(devices)} device(s):")
        for i, device in enumerate(devices):
            print(f"  {i+1}. {device.name} ({device.os})")
        
        # Use first device
        target_device = devices[0].name
        print(f"\nUsing device: {target_device}")
        
    except Exception as e:
        print(f"\nWarning: Could not detect device - {e}")
        print("Will use default 'Snapdragon X Elite'")
        target_device = "Snapdragon X Elite"
    
    # Deploy
    print(f"\nDeploying Whisper Base EN to {target_device}...")
    print("This will take 10-30 minutes...")
    print()
    
    try:
        from qai_hub_models.models.whisper_base_en import WhisperBaseEnglish
        
        print("[1/4] Loading Whisper model...")
        model = WhisperBaseEnglish.from_pretrained()
        print("      Model loaded!")
        
        print("\n[2/4] Exporting to ONNX...")
        # This happens automatically during compile
        
        print("\n[3/4] Compiling for NPU...")
        print("      This is the slow part (10-30 min)...")
        
        # Compile for NPU
        compile_job = qai_hub.submit_compile_job(
            model=model.get_evaluable_model(),
            device=target_device,
            name=f"whisper_base_en_npu_{target_device.replace(' ', '_')}",
        )
        
        print(f"      Compile job submitted: {compile_job.job_id}")
        print("      Waiting for compilation...")
        
        # Wait for completion
        compiled_model = compile_job.download_target_model()
        
        print("      Compilation complete!")
        
        print("\n[4/4] Saving model...")
        
        output_dir = Path("whisper_npu_deployed")
        output_dir.mkdir(exist_ok=True)
        
        # Save compiled model
        model_path = output_dir / "whisper_npu.bin"
        with open(model_path, 'wb') as f:
            f.write(compiled_model.read())
        
        print(f"      Saved to: {model_path}")
        
        print("\n" + "="*70)
        print(" DEPLOYMENT SUCCESSFUL! ".center(70))
        print("="*70)
        print()
        print(f"Model saved to: {output_dir}")
        print()
        print("Next steps:")
        print("  1. Test the model:")
        print("     python test_whisper_npu.py")
        print("  2. Run voice assistant:")
        print("     python harry_voice_assistant_npu.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n\nERROR during deployment: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n\nTroubleshooting:")
        print("  1. Check you're logged into Qualcomm AI Hub")
        print("  2. Verify device is registered")
        print("  3. Check internet connection")
        print("  4. See NPU_VOICE_ASSISTANT_DEPLOYMENT.md for details")
        
        return False


def main():
    """Main entry point"""
    
    success = deploy_whisper()
    
    if not success:
        print("\nDeployment failed. Please check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


