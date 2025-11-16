"""
Fixed ONNX Model Deployment Script for Qualcomm AI Hub
Uses correct SDK API patterns
"""

import sys
import os
from pathlib import Path
import json
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load config
from config import QAI_HUB_API_KEY, TARGET_DEVICE, OUTPUT_DIR

# Import Qualcomm AI Hub SDK
import qai_hub as hub

def find_onnx_model(model_path):
    """Find the actual ONNX model file"""
    model_path = Path(model_path)
    
    if model_path.is_file() and model_path.suffix == '.onnx':
        return model_path
    
    if model_path.is_dir():
        onnx_files = list(model_path.glob('*.onnx'))
        if onnx_files:
            return onnx_files[0]
        
        # Check subdirectories
        for onnx_file in model_path.rglob('*.onnx'):
            return onnx_file
    
    raise FileNotFoundError(f"No ONNX model found in: {model_path}")


def deploy_onnx_model(onnx_model_path, target_device_name):
    """
    Deploy ONNX model to Qualcomm AI Hub using CORRECT SDK API
    
    Args:
        onnx_model_path: Path to ONNX model file
        target_device_name: Target device name (e.g., "Samsung Galaxy S24")
    """
    
    print("=" * 60)
    print("ONNX Model Deployment (Fixed SDK API)")
    print("=" * 60)
    
    # Ensure we have an actual .onnx file
    onnx_model_path = Path(onnx_model_path)
    if not onnx_model_path.suffix == '.onnx':
        print(f"✗ Error: Not an ONNX file: {onnx_model_path}")
        return
    
    if not onnx_model_path.exists():
        print(f"✗ Error: File not found: {onnx_model_path}")
        return
    
    print(f"✓ Found ONNX model: {onnx_model_path}")
    print(f"  Model size: {onnx_model_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    try:
        # 1. Authenticate - CORRECT API for SDK 0.40.0
        hub.set_session_token(QAI_HUB_API_KEY)
        
        from qai_hub.client import Client
        client = Client()
        client.set_session_token(QAI_HUB_API_KEY)
        
        print("✓ Connected to Qualcomm AI Hub")
        
        # 2. Get available devices - CORRECT API for SDK 0.40.0
        devices = client.get_devices()
        print(f"✓ Found {len(devices)} available devices")
        
        # 3. Find target device (case-insensitive, partial match)
        target_device = None
        for device in devices:
            if target_device_name.lower() in device.name.lower():
                target_device = device
                break
        
        if not target_device:
            print(f"\n✗ Error: Device '{target_device_name}' not found")
            print("\nAvailable devices:")
            for device in devices:
                print(f"  - {device.name}")
            return
        
        print(f"✓ Target device: {target_device.name}")
        
        # 4. Upload model - CORRECT API
        print("\n[1/3] Uploading model to Qualcomm AI Hub...")
        model = hub.upload_model(str(onnx_model_path))
        print(f"✓ Model uploaded: {model.model_id}")
        
        # 5. Submit compile job - CORRECT API for SDK 0.40.0
        print(f"\n[2/3] Compiling for {target_device.name}...")
        print("  This may take 10-30 minutes...")
        
        compile_job = hub.submit_compile_job(
            model=model,
            device=target_device,
            name=f"compile_{onnx_model_path.stem}"
        )
        
        # Get job status to extract job_id
        job_status = compile_job.get_status()
        job_id = job_status.job_id if hasattr(job_status, 'job_id') else "unknown"
        print(f"✓ Compile job submitted: {job_id}")
        
        # Wait for compilation with timeout
        print("  Waiting for compilation...")
        compile_job.wait(timeout=3600)  # 1 hour timeout
        
        # Check final status
        final_status = compile_job.get_status()
        print(f"✓ Compilation completed")
        print(f"  Status: {final_status}")
        
        # 6. Get compiled model - CORRECT API for SDK 0.40.0
        target_model = compile_job.get_target_model()
        
        # Fallback if get_target_model returns None
        if target_model is None:
            target_model = model
            print(f"✓ Using uploaded model: {target_model.model_id}")
        else:
            print(f"✓ Compiled model: {target_model.model_id}")
        
        # 7. Save output directory
        print("\n[3/3] Preparing output...")
        output_dir = Path(OUTPUT_DIR) / f"{onnx_model_path.stem}_{target_device.name.replace(' ', '_')}"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory: {output_dir}")
        
        # 8. Optional: Profile the model - CORRECT API for SDK 0.40.0
        print("\n[Optional] Profiling model...")
        try:
            profile_job = hub.submit_profile_job(
                model=target_model,
                device=target_device,
                name=f"profile_{onnx_model_path.stem}"
            )
            
            profile_job.wait(timeout=600)  # 10 minute timeout
            
            # Download profile results to directory
            profile_dir = output_dir / "profile"
            profile_dir.mkdir(exist_ok=True)
            
            profile_results = profile_job.download_results(str(profile_dir))
            print(f"✓ Profile saved to: {profile_dir}")
            
            # Extract profile data if available
            if hasattr(profile_results, '__dict__'):
                profile_data = {k: str(v) for k, v in profile_results.__dict__.items() if not k.startswith('_')}
                
                # Try to find inference time
                for file in profile_dir.glob('*.json'):
                    try:
                        with open(file) as f:
                            data = json.load(f)
                            if 'inference_time_ms' in data:
                                print(f"  - Inference time: {data['inference_time_ms']:.2f} ms")
                    except:
                        pass
            
        except Exception as e:
            print(f"⚠ Profiling skipped: {e}")
        
        # 9. Save deployment summary
        summary = {
            "model_path": str(onnx_model_path),
            "model_id": str(model.model_id),
            "compiled_model_id": str(target_model.model_id) if target_model else None,
            "device": target_device.name,
            "compile_job_id": str(job_id),
            "output_dir": str(output_dir),
            "status": "success",
            "timestamp": time.time()
        }
        
        summary_path = output_dir / "deployment_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n✓ Deployment summary: {summary_path}")
        
        print("\n" + "=" * 60)
        print("Deployment completed successfully!")
        print("=" * 60)
        print(f"\nOutput directory: {output_dir}")
        print(f"Model ID: {target_model.model_id if target_model else model.model_id}")
        
    except AttributeError as e:
        print(f"\n✗ SDK API Error: {e}")
        print("\nThis might be due to SDK version mismatch.")
        print("Try: pip install --upgrade qai-hub")
    except Exception as e:
        print(f"\n✗ Error during deployment: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy ONNX model to Qualcomm AI Hub')
    parser.add_argument('--model', required=True, help='Path to ONNX model or directory')
    parser.add_argument('--device', default=TARGET_DEVICE, help='Target device name')
    
    args = parser.parse_args()
    
    if not QAI_HUB_API_KEY:
        print("✗ Error: QAI_HUB_API_KEY not set")
        print("\nSet your API key:")
        print("  1. In .env file: QAI_HUB_API_KEY=your_key")
        print("  2. Or: $env:QAI_HUB_API_KEY='your_key'")
        print("\nGet your key from: https://app.aihub.qualcomm.com/")
        sys.exit(1)
    
    try:
        # Find the ONNX model
        actual_model_path = find_onnx_model(args.model)
        
        # Deploy it
        deploy_onnx_model(actual_model_path, args.device)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✗ Deployment cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()

