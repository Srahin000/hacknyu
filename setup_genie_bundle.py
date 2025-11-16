import os
import json
import shutil
from pathlib import Path

QNN_SDK_ROOT = os.environ.get('QNN_SDK_ROOT', 'C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130')
BUNDLE_DIR = Path("genie_bundle")
CONFIGS_DIR = Path("ai-hub-apps/tutorials/llm_on_genie/configs")

def setup_bundle():
    BUNDLE_DIR.mkdir(exist_ok=True)
    
    genie_config_template = CONFIGS_DIR / "genie" / "llama_v3_2_1b_instruct.json"
    htp_template = CONFIGS_DIR / "htp" / "htp_backend_ext_config.json.template"
    
    if not genie_config_template.exists():
        print(f"Config template not found: {genie_config_template}")
        return False
    
    with open(genie_config_template) as f:
        config = json.load(f)
    
    if "engine" in config.get("dialog", {}):
        config["dialog"]["engine"]["backend"]["QnnHtp"]["use-mmap"] = False
        config["dialog"]["tokenizer"]["path"] = str(BUNDLE_DIR / "tokenizer.json")
        
        ctx_bins = config["dialog"]["engine"]["model"]["binary"]["ctx-bins"]
        for i, ctx_bin in enumerate(ctx_bins):
            config["dialog"]["engine"]["model"]["binary"]["ctx-bins"][i] = str(BUNDLE_DIR / Path(ctx_bin).name)
    
    with open(BUNDLE_DIR / "genie_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    with open(htp_template) as f:
        content = f.read()
        content = content.replace('"soc_model": <TODO>', '"soc_model": 60')
        content = content.replace('"dsp_arch": "<TODO>"', '"dsp_arch": "v73"')
        htp_config = json.loads(content)
    
    with open(BUNDLE_DIR / "htp_backend_ext_config.json", "w") as f:
        json.dump(htp_config, f, indent=4)
    
    genie_exe = Path(QNN_SDK_ROOT) / "bin" / "aarch64-windows-msvc" / "genie-t2t-run.exe"
    if genie_exe.exists():
        shutil.copy(genie_exe, BUNDLE_DIR / "genie-t2t-run.exe")
    
    dsp_lib = Path(QNN_SDK_ROOT) / "lib" / "hexagon-v73" / "unsigned"
    if dsp_lib.exists():
        for lib in dsp_lib.glob("*.so"):
            shutil.copy(lib, BUNDLE_DIR / lib.name)
    
    print(f"Bundle setup complete: {BUNDLE_DIR}")
    print("Next: Export model and copy .bin files + tokenizer.json to genie_bundle/")
    return True

if __name__ == "__main__":
    setup_bundle()

