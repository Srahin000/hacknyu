# Start EDGEucator Dashboard
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH

Write-Host "Starting EDGEucator Dashboard..." -ForegroundColor Cyan
Write-Host ""

cd C:\Users\hackuser\Documents\HackNYU\EDGEucatorDashboard

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

Write-Host "Starting Vite dev server..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

npm run dev

