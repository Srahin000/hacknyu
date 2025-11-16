# Check Genie version in installed QAIRT SDKs

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host " GENIE VERSION CHECKER " -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$QairtBase = "C:\Qualcomm\AIStack\QAIRT"
$SDKs = Get-ChildItem $QairtBase -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending

if (-not $SDKs) {
    Write-Host "No QAIRT SDKs found in $QairtBase" -ForegroundColor Red
    exit 1
}

Write-Host "Checking Genie versions in installed SDKs:" -ForegroundColor Yellow
Write-Host ""

foreach ($sdk in $SDKs) {
    $sdkPath = $sdk.FullName
    $sdkName = $sdk.Name
    
    Write-Host "SDK: $sdkName" -ForegroundColor Cyan
    
    # Check Genie.dll version
    $genieDll = Join-Path $sdkPath "lib\aarch64-windows-msvc\Genie.dll"
    
    if (Test-Path $genieDll) {
        try {
            # Try to run genie-t2t-run to get version
            $genieExe = Join-Path $sdkPath "bin\aarch64-windows-msvc\genie-t2t-run.exe"
            if (Test-Path $genieExe) {
                $output = & $genieExe --version 2>&1 | Out-String
                if ($output -match "version\s+([\d\.]+)") {
                    $genieVersion = $matches[1]
                    Write-Host "  Genie version: $genieVersion" -ForegroundColor White
                    
                    # Check if it meets requirements
                    if ([version]$genieVersion -ge [version]"1.13.0") {
                        Write-Host "  Status: COMPATIBLE (>= 1.13)" -ForegroundColor Green
                    } else {
                        Write-Host "  Status: TOO OLD (need >= 1.13)" -ForegroundColor Red
                    }
                } else {
                    # Fallback to DLL version
                    $version = (Get-Item $genieDll).VersionInfo
                    Write-Host "  DLL FileVersion: $($version.FileVersion)" -ForegroundColor White
                    Write-Host "  DLL ProductVersion: $($version.ProductVersion)" -ForegroundColor White
                }
            } else {
                $version = (Get-Item $genieDll).VersionInfo
                Write-Host "  DLL FileVersion: $($version.FileVersion)" -ForegroundColor White
            }
        } catch {
            Write-Host "  Error checking version: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  Genie.dll not found" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host " REQUIREMENTS " -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Model requires:" -ForegroundColor White
Write-Host "  - Genie >= 1.13" -ForegroundColor Green
Write-Host "  - QAIRT SDK 2.37.1.250807093845_124904 (or compatible)" -ForegroundColor Green
Write-Host ""
Write-Host "Recommendation:" -ForegroundColor Yellow
Write-Host "  Look for QAIRT SDK 2.38+ or 2.39+ which includes Genie 1.13+" -ForegroundColor White
Write-Host ""

