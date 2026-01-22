# Script de upload du lieu tu local len Render
# Su dung: .\upload-data-to-render.ps1

param(
    [string]$RenderUrl = "https://biovision-tihm.onrender.com",
    [string]$AdminToken = "",
    [string]$DataFile = "data.json"
)

Write-Host "=== Upload Data to Render ===" -ForegroundColor Cyan
Write-Host ""

# Kiem tra file data.json
if (-not (Test-Path $DataFile)) {
    Write-Host "Khong tim thay file: $DataFile" -ForegroundColor Red
    Write-Host "Dam bao ban dang chay script tu thu muc chua data.json" -ForegroundColor Yellow
    exit 1
}

# Kiem tra Admin Token
if (-not $AdminToken) {
    $AdminToken = Read-Host "Nhap Admin Token (tu Render Environment Variables)"
    if (-not $AdminToken) {
        Write-Host "Admin Token khong duoc de trong!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Dang doc file: $DataFile" -ForegroundColor Yellow
try {
    $jsonContent = Get-Content -Path $DataFile -Raw -Encoding UTF8
    $data = $jsonContent | ConvertFrom-Json
    
    # Validate JSON structure
    if (-not $data.models) {
        Write-Host "File JSON khong hop le: thieu truong 'models'" -ForegroundColor Red
        exit 1
    }
    
    $modelCount = $data.models.Count
    Write-Host "Da doc thanh cong: $modelCount models" -ForegroundColor Green
} catch {
    Write-Host "Loi khi doc file JSON: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Dang upload len: $RenderUrl" -ForegroundColor Yellow
$tokenPreview = if ($AdminToken.Length -gt 8) { $AdminToken.Substring(0, 8) + "..." } else { "***" }
Write-Host "Token: $tokenPreview" -ForegroundColor Gray

try {
    # Ensure UTF-8 encoding for JSON body
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $jsonBytes = $utf8NoBom.GetBytes($jsonContent)
    
    $headers = @{
        "Content-Type" = "application/json; charset=utf-8"
        "Authorization" = "Bearer $AdminToken"
    }
    
    $response = Invoke-RestMethod -Uri "$RenderUrl/api/data" `
        -Method POST `
        -Headers $headers `
        -Body $jsonBytes `
        -ContentType "application/json; charset=utf-8" `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "Upload thanh cong!" -ForegroundColor Green
    Write-Host "Version: $($response.version)" -ForegroundColor Gray
    Write-Host "Updated: $($response.updatedAt)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Buoc tiep theo:" -ForegroundColor Cyan
    Write-Host "1. Mo $RenderUrl/admin" -ForegroundColor White
    Write-Host "2. Nhap Admin Token va kiem tra du lieu" -ForegroundColor White
    Write-Host "3. Mo $RenderUrl de xem trang guest" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "Loi khi upload:" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode.value__
        $statusDescription = $_.Exception.Response.StatusDescription
        
        Write-Host "HTTP $statusCode : $statusDescription" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host ""
            Write-Host "Goi y:" -ForegroundColor Yellow
            Write-Host "- Kiem tra Admin Token trong Render Environment Variables" -ForegroundColor White
            Write-Host "- Dam bao token khop chinh xac (case-sensitive)" -ForegroundColor White
        } elseif ($statusCode -eq 400) {
            Write-Host ""
            Write-Host "Goi y:" -ForegroundColor Yellow
            Write-Host "- Kiem tra cau truc JSON co dung khong" -ForegroundColor White
            Write-Host "- Xem Render Logs de biet loi chi tiet" -ForegroundColor White
        }
    } else {
        $errorMsg = $_.Exception.Message
        Write-Host "Loi: $errorMsg" -ForegroundColor Red
    }
    exit 1
}
