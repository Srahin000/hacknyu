# Official Genie runner based on ai-hub-apps tutorial
# https://github.com/quic/ai-hub-apps/tree/main/tutorials/llm_on_genie

param(
    [Parameter(Mandatory=$false)]
    [string]$Prompt = "Hello, my name is Harry Potter"
)

$BundleRoot = "genie_bundle"
$ModelName = "llama_v3_2_1b_instruct"

# Check if bundle exists
if (-Not (Test-Path $BundleRoot)) {
    Write-Error "Bundle directory not found: $BundleRoot"
    exit 1
}

# Check QNN SDK
$QnnSdkRoot = $Env:QNN_SDK_ROOT
if (-Not $QnnSdkRoot) {
    # Try common location
    $CommonPath = "C:\Qualcomm\AIStack\QAIRT\2.31.0.250130"
    if (Test-Path $CommonPath) {
        $QnnSdkRoot = $CommonPath
        $Env:QNN_SDK_ROOT = $QnnSdkRoot
        Write-Host "Using QNN SDK at: $QnnSdkRoot" -ForegroundColor Yellow
    } else {
        Write-Error "QNN_SDK_ROOT not set and not found at $CommonPath"
        Write-Host "Please set: `$env:QNN_SDK_ROOT = 'C:\Qualcomm\AIStack\QAIRT\<version>'" -ForegroundColor Yellow
        exit 1
    }
}

# Use the official PowerShell script from ai-hub-apps
$OfficialScript = "ai-hub-apps\tutorials\llm_on_genie\powershell\RunLlm.ps1"

if (Test-Path $OfficialScript) {
    Write-Host "Using official RunLlm.ps1 script..." -ForegroundColor Green
    
    # Format prompt with Llama 3 template
    $RawPrompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>`n`n$Prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    
    & $OfficialScript -ModelName $ModelName -BundleRoot $BundleRoot -RawPrompt $RawPrompt
} else {
    Write-Error "Official script not found: $OfficialScript"
    Write-Host "Falling back to direct genie-t2t-run..." -ForegroundColor Yellow
    
    # Fallback: direct execution
    $GenieExe = "$BundleRoot\genie-t2t-run.exe"
    $ConfigFile = "$BundleRoot\genie_config.json"
    
    if (-Not (Test-Path $GenieExe)) {
        Write-Error "genie-t2t-run.exe not found: $GenieExe"
        exit 1
    }
    
    # Set ADSP_LIBRARY_PATH
    $OldAdspPath = $Env:ADSP_LIBRARY_PATH
    $Env:ADSP_LIBRARY_PATH = (Resolve-Path $BundleRoot).Path
    
    # Format prompt
    $FormattedPrompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>`n`n$Prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    
    Write-Host "Running Genie..." -ForegroundColor Green
    Write-Host "Prompt: $Prompt" -ForegroundColor Cyan
    Write-Host ""
    
    & $GenieExe -c $ConfigFile -p $FormattedPrompt
    
    # Restore ADSP_LIBRARY_PATH
    $Env:ADSP_LIBRARY_PATH = $OldAdspPath
}

