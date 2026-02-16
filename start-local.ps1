# Script để khởi động server local cho BioVision
# Usage: powershell -ExecutionPolicy Bypass -File .\start-local.ps1

Write-Host "=== BioVision Local Server ===" -ForegroundColor Cyan
Write-Host ""

# Thiết lập environment variables
$env:ENV = "development"
$env:ADMIN_TOKEN = "test-token-123"

Write-Host "[INFO] Environment variables set:" -ForegroundColor Green
Write-Host "  - ENV: $env:ENV"
Write-Host "  - ADMIN_TOKEN: $($env:ADMIN_TOKEN.Substring(0,4))****"
Write-Host ""

# Kiểm tra xem port 5000 có đang được sử dụng không
$portInUse = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[WARN] Port 5000 is already in use!" -ForegroundColor Yellow
    Write-Host "       Please stop the existing server first or use a different port."
    Write-Host ""
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne "y") {
        exit
    }
}

Write-Host "[INFO] Starting Flask server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  - Guest page: http://localhost:5000/" -ForegroundColor White
Write-Host "  - Admin page: http://localhost:5000/admin" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Khởi động server
python app.py
