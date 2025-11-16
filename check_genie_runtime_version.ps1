# Check Genie Runtime Version
# Model requires: Genie 1.13 or newer
# Current: 1.11.0 (TOO OLD!)

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host " GENIE RUNTIME VERSION CHECK " -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$RequiredGenieVersion = "1.13"
$CurrentGenieVersion = "1.11.0"

Write-Host "Model requires: Genie >= $RequiredGenieVersion" -ForegroundColor Green
Write-Host "Current runtime: Genie $CurrentGenieVersion" -ForegroundColor Red
Write-Host ""

# Check all available QAIRT SDK versions
$QairtBase = "C:\Qualcomm\AIStack\QAIRT"
$Versions = Get-ChildItem $QairtBase -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending

Write-Host "Checking installed QAIRT SDK versions for Genie 1.13+..." -ForegroundColor Cyan
Write-Host ""

$FoundCompatible = $false

foreach ($Version in $Versions) {
    $GenieDllPath = Join-Path $Version.FullName "lib\aarch64-windows-msvc\Genie.dll"
    
    if (Test-Path $GenieDllPath) {
        # Try to get version from DLL
        $GenieDll = Get-Item $GenieDllPath
        $FileVersion = $GenieDll.VersionInfo.FileVersion
        
        Write-Host "SDK: $($Version.Name)" -ForegroundColor White
        Write-Host "  Genie.dll version: $FileVersion" -ForegroundColor Cyan
        
        # Check if this version might be >= 1.13
        # We need a newer SDK version
        if ($Version.Name -match "2\.3[89]" -or $Version.Name -match "2\.4") {
            Write-Host "  Status: Likely compatible (newer SDK)" -ForegroundColor Green
            $FoundCompatible = $true
        } else {
            Write-Host "  Status: Check by running genie-t2t-run" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host " SOLUTION " -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

if ($FoundCompatible) {
    Write-Host "Found potentially compatible SDK versions above." -ForegroundColor Green
    Write-Host "Try using a newer QAIRT SDK (2.38+ or 2.39+)" -ForegroundColor White
} else {
    Write-Host "You need a newer QAIRT SDK with Genie 1.13+" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "1. Download latest QAIRT SDK:" -ForegroundColor White
    Write-Host "   https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Look for QAIRT 2.38, 2.39, or newer" -ForegroundColor White
    Write-Host "   These versions include Genie 1.13+" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Or re-export model with your current SDK (2.37.1)" -ForegroundColor White
    Write-Host "   python reexport_model_for_sdk_2_37.py" -ForegroundColor Cyan
    Write-Host "   This will create binaries compatible with Genie 1.11" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan

