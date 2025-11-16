"""
Check Qualcomm AI Hub job status for LLM export
"""

import qai_hub as hub

# Your compile job ID from the error
compile_job_id = "jgzr80465"
link_job_id = "jgl3o9llg"

print("Checking compile job status...")
try:
    compile_job = hub.get_job(compile_job_id)
    print(f"\nCompile Job: {compile_job_id}")
    print(f"Status: {compile_job.get_status()}")
    
    # Try to get the model
    if hasattr(compile_job, 'get_target_model'):
        model = compile_job.get_target_model()
        if model:
            print(f"✅ Model compiled successfully: {model}")
        else:
            print("❌ Model is None - compile job failed to produce model")
    
    # Get logs
    if hasattr(compile_job, 'download_output_logs'):
        print("\nDownloading compile logs...")
        compile_job.download_output_logs("./compile_logs")
        print("✅ Logs saved to ./compile_logs/")
        
except Exception as e:
    print(f"❌ Error checking compile job: {e}")

print("\n" + "="*70)
print("\nChecking link job status...")
try:
    link_job = hub.get_job(link_job_id)
    print(f"\nLink Job: {link_job_id}")
    print(f"Status: {link_job.get_status()}")
    
except Exception as e:
    print(f"❌ Error checking link job: {e}")

print("\n" + "="*70)
print("\n💡 Recommendation:")
print("If compile job succeeded but model is None:")
print("  1. The model may be too large for NPU")
print("  2. Use CPU mode instead (you already have llama.cpp working!)")
print("  3. Try smaller model like TinyLlama")




