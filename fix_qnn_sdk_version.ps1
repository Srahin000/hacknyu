# Fix QNN SDK Version Mismatch
# Model compiled with: QAIRT 2.37.1.250807093845_124904
# Currently installed: 2.31.0.250130

$RequiredVersion = "2.37.1"
$CurrentVersion = "2.31.0.250130"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " QNN SDK VERSION FIX " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model compiled with: QAIRT $RequiredVersion" -ForegroundColor Green
Write-Host "Currently installed: $CurrentVersion" -ForegroundColor Red
Write-Host ""

# Check for matching version
$QairtBase = "C:\Qualcomm\AIStack\QAIRT"
$MatchingVersion = Get-ChildItem $QairtBase -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "$RequiredVersion*" } | Sort-Object Name -Descending | Select-Object -First 1

if ($MatchingVersion) {
    $MatchingPath = $MatchingVersion.FullName
    Write-Host "Found matching version: $($MatchingVersion.Name)" -ForegroundColor Green
    Write-Host "Path: $MatchingPath" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if DLLs exist
    $DllPath = Join-Path $MatchingPath "lib\aarch64-windows-msvc"
    if (-Not (Test-Path $DllPath)) {
        Write-Host "ERROR: DLL directory not found: $DllPath" -ForegroundColor Red
        Write-Host "The SDK installation may be incomplete" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "DLL directory exists: $DllPath" -ForegroundColor Green
    $DllCount = (Get-ChildItem $DllPath -Filter "*.dll" -ErrorAction SilentlyContinue).Count
    Write-Host "Found $DllCount DLL files" -ForegroundColor Cyan
    Write-Host ""
    
    # Update environment variable
    Write-Host "Setting QNN_SDK_ROOT..." -ForegroundColor Yellow
    $env:QNN_SDK_ROOT = $MatchingPath
    [System.Environment]::SetEnvironmentVariable("QNN_SDK_ROOT", $MatchingPath, "User")
    Write-Host "QNN_SDK_ROOT = $MatchingPath" -ForegroundColor Green
    Write-Host ""
    
    # Copy DLLs to genie_bundle
    $BundleDir = "C:\Users\hackuser\Documents\HackNYU\genie_bundle"
    if (Test-Path $BundleDir) {
        Write-Host "Copying DLLs to genie_bundle..." -ForegroundColor Yellow
        Copy-Item "$DllPath\*.dll" $BundleDir -Force
        Write-Host "DLLs copied successfully" -ForegroundColor Green
        Write-Host ""
    }
    
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host " NEXT STEPS " -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Restart your PowerShell session (or run):" -ForegroundColor White
    Write-Host "   `$env:QNN_SDK_ROOT = '$MatchingPath'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Test Genie again:" -ForegroundColor White
    Write-Host "   python run_genie_safe.py `"Hello, my name is Harry Potter`"" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host "ERROR: Matching version not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available versions:" -ForegroundColor Yellow
    Get-ChildItem $QairtBase -Directory -ErrorAction SilentlyContinue | Select-Object Name | Format-Table -AutoSize
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host " SOLUTION " -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You need to download QAIRT SDK version $RequiredVersion" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Download from:" -ForegroundColor Yellow
    Write-Host "   https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Or use QPM (Qualcomm Package Manager):" -ForegroundColor Yellow
    Write-Host "   qpm install qualcomm_ai_runtime_sdk --version $RequiredVersion" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Install to: C:\Qualcomm\AIStack\QAIRT\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. Then run this script again" -ForegroundColor Yellow
    Write-Host ""
}
