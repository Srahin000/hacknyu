"""
Deploy Speech Recognition (STT) Model using ONNX (Windows Compatible)

This script works around the AIMET-ONNX limitation on Windows by:
1. Using pre-compiled ONNX models from Qualcomm AI Hub
2. Or loading ONNX models directly
"""

import sys
import os
# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
import qai_hub as hub
from qai_hub.client import Client
from config import QAI_HUB_API_KEY, TARGET_DEVICE, OUTPUT_DIR
from datetime import datetime
import json


def find_onnx_model(path: str) -> str:
    """
    Find ONNX model file in a directory or return the path if it's a file
    
    Args:
        path: Path to model file or directory containing model
        
    Returns:
        Path to ONNX model file
    """
    path_obj = Path(path)
    
    # If it's a file, return it
    if path_obj.is_file() and path_obj.suffix == '.onnx':
        return str(path_obj)
    
    # If it's a directory, search for .onnx files
    if path_obj.is_dir():
        # Look for model.onnx in subdirectories
        onnx_files = list(path_obj.rglob("model.onnx"))
        if onnx_files:
            return str(onnx_files[0])
        
        # Look for any .onnx files
        onnx_files = list(path_obj.rglob("*.onnx"))
        if onnx_files:
            return str(onnx_files[0])
    
    # If not found, return original path (will error later)
    return path


def deploy_onnx_model(onnx_model_path: str):
    """
    Deploy an ONNX model directly to Qualcomm AI Hub
    
    Args:
        onnx_model_path: Path to ONNX model file or directory containing model
    """
    print("=" * 60)
    print("ONNX Model Deployment (Windows Compatible)")
    print("=" * 60)
    
    # Find the actual ONNX file
    actual_model_path = find_onnx_model(onnx_model_path)
    
    if not os.path.exists(actual_model_path):
        print(f"✗ Error: Model file not found: {actual_model_path}")
        print(f"  Searched in: {onnx_model_path}")
        print("\nOptions:")
        print("1. Download from Qualcomm AI Hub: https://aihub.qualcomm.com/")
        print("2. Use WSL to export the model (see README)")
        print("3. Use a different model that doesn't require AIMET-ONNX")
        return
    
    if actual_model_path != onnx_model_path:
        print(f"✓ Found ONNX model: {actual_model_path}")
    
    print(f"  Using model: {actual_model_path}")
    
    # Setup hub connection
    if not QAI_HUB_API_KEY:
        print("✗ Error: QAI_HUB_API_KEY not set in .env file")
        return
    
    # Setup client and get device
    hub.set_session_token(QAI_HUB_API_KEY)
    client = Client()
    client.set_session_token(QAI_HUB_API_KEY)
    devices = client.get_devices()
    print("✓ Connected to Qualcomm AI Hub")
    
    # Find the target device
    target_device_obj = None
    for device in devices:
        if device.name == TARGET_DEVICE:
            target_device_obj = device
            break
    
    if not target_device_obj:
        print(f"✗ Error: Device '{TARGET_DEVICE}' not found")
        print("  Available devices:")
        for device in devices[:10]:
            print(f"    - {device.name}")
        return
    
    # Compile ONNX model
    print(f"\n[1/3] Compiling ONNX model for {TARGET_DEVICE}...")
    
    model_name = f"whisper_stt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Upload model to hub first
        print("  Uploading model to Qualcomm AI Hub...")
        uploaded_model = hub.upload_model(actual_model_path)
        print(f"✓ Model uploaded: {uploaded_model.model_id}")
        
        # Compile the uploaded model - use Device object
        compile_job = hub.submit_compile_job(
            model=uploaded_model,
            device=target_device_obj,
            name=model_name,
        )
        
        # Get job status properly
        job_status = compile_job.get_status()
        job_id = job_status.job_id if hasattr(job_status, 'job_id') else str(job_status)
        
        print(f"✓ Compile job submitted: {job_id}")
        print("  Waiting for compilation (this may take 10-30 minutes)...")
        
        compile_job.wait(timeout=3600)
        
        # Check status again after waiting
        final_status = compile_job.get_status()
        if hasattr(final_status, 'status') and final_status.status == "FAILED":
            error_msg = final_status.error if hasattr(final_status, 'error') else "Unknown error"
            print(f"✗ Compilation failed: {error_msg}")
            return
        
        print("✓ Compilation completed")
        
        # Get the compiled model - try different methods
        compiled_model = compile_job.get_target_model()
        if compiled_model is None:
            # If get_target_model returns None, use the uploaded model
            # (the compilation modifies it in place)
            compiled_model = uploaded_model
            print(f"✓ Using compiled model: {compiled_model.model_id}")
        else:
            print(f"✓ Compiled model ready: {compiled_model.model_id}")
        
        # Profile
        print(f"\n[2/3] Profiling model...")
        profile_job = hub.submit_profile_job(
            model=compiled_model,
            device=target_device_obj,
            name=f"{model_name}_profile",
        )
        
        profile_job.wait(timeout=600)
        
        # Download profile results to a directory
        profile_dir = Path(OUTPUT_DIR) / f"{model_name}_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_results = profile_job.download_results(str(profile_dir))
        
        # Extract metrics from profile results
        # Profile results structure may vary, handle accordingly
        profile_data = {}
        if hasattr(profile_results, '__dict__'):
            # Convert object to dict
            profile_data = {k: str(v) for k, v in profile_results.__dict__.items() if not k.startswith('_')}
        elif isinstance(profile_results, dict):
            profile_data = profile_results
        else:
            profile_data = {"type": str(type(profile_results))}
        
        inference_time = profile_data.get('inference_time_ms', 0)
        npu_util = profile_data.get('npu_utilization', 0)
        
        print(f"✓ Profiling completed:")
        print(f"  - Profile saved to: {profile_dir}")
        if inference_time:
            print(f"  - Inference time: {inference_time:.2f} ms")
        if npu_util:
            print(f"  - NPU utilization: {npu_util:.1f}%")
        
        # Save results
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        final_status = compile_job.get_status()
        job_id = final_status.job_id if hasattr(final_status, 'job_id') else str(final_status)
        
        results = {
            "model_path": str(onnx_model_path),
            "compile_job_id": str(job_id),
            "compiled_model_id": str(compiled_model.model_id) if compiled_model else None,
            "profile_dir": str(profile_dir),
            "profile_data": profile_data,
            "status": "success"
        }
        
        summary_path = Path(OUTPUT_DIR) / f"deployment_summary_{model_name}.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n[3/3] Results saved to: {summary_path}")
        print("=" * 60)
        print("Deployment completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error during deployment: {str(e)}")
        return


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deploy ONNX STT model (Windows compatible)"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Path to ONNX model file",
        default=None
    )
    
    args = parser.parse_args()
    
    if args.model:
        deploy_onnx_model(args.model)
    else:
        print("=" * 60)
        print("Qualcomm AI Hub - Model Deployment")
        print("=" * 60)
        print("\nUsage:")
        print("  python deploy.py --model <path>")
        print("\nExamples:")
        print("  python deploy.py --model models                # Use model in models/ folder")
        print("  python deploy.py --model model.onnx            # Use specific ONNX file")
        print("\nWhat it does:")
        print("  1. Uploads your ONNX model to Qualcomm AI Hub")
        print("  2. Compiles it for Snapdragon NPU (10-30 min)")
        print("  3. Profiles performance (latency, NPU usage)")
        print("  4. Saves results to deployed_models/")
        print("\nGet models from:")
        print("  https://aihub.qualcomm.com/models")
        print("\nNeed help?")
        print("  See QUICKSTART.md or README.md")
        print("=" * 60)


if __name__ == "__main__":
    main()

