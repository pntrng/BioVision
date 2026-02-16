# Script de dong bo du lieu len Render (merge, khong ghi de)
# Su dung: powershell -ExecutionPolicy Bypass -File .\sync-data-to-render.ps1
#
# Script nay se:
# 1. Download data.json tu Render (backup)
# 2. Merge: giu lai cac model da co tren Render, them cac model moi tu local
# 3. Upload len Render

param(
    [string]$RenderUrl = "https://biovision-tihm.onrender.com",
    [string]$AdminToken = "",
    [string]$LocalDataFile = "data.json",
    [string]$BackupDir = "backups"
)

Write-Host "=== Dong bo du lieu len Render (Merge) ===" -ForegroundColor Cyan
Write-Host ""

# Kiem tra Admin Token
if (-not $AdminToken) {
    $AdminToken = Read-Host "Nhap Admin Token (tu Render Environment Variables)"
    if (-not $AdminToken) {
        Write-Host "Admin Token khong duoc de trong!" -ForegroundColor Red
        exit 1
    }
}

# Tao thu muc backup neu chua co
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Backup file local
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$localBackup = Join-Path $BackupDir "data_local_$timestamp.json"
Copy-Item $LocalDataFile $localBackup
Write-Host "[OK] Da backup file local: $localBackup" -ForegroundColor Green

# Download data tu Render
Write-Host ""
Write-Host "[1] Dang tai du lieu tu Render..." -ForegroundColor Yellow
try {
    $renderData = Invoke-RestMethod -Uri "$RenderUrl/api/data" -Method Get -ErrorAction Stop
    $renderBackup = Join-Path $BackupDir "data_render_$timestamp.json"
    $renderData | ConvertTo-Json -Depth 100 | Set-Content -Path $renderBackup -Encoding UTF8
    Write-Host "   [OK] Da tai va backup: $renderBackup" -ForegroundColor Green
    Write-Host "   - Models tren Render: $($renderData.models.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   [ERROR] Khong the tai du lieu tu Render: $_" -ForegroundColor Red
    Write-Host "   -> Co the Render chua co du lieu, se upload tu local" -ForegroundColor Yellow
    $renderData = $null
}

# Doc file local
Write-Host ""
Write-Host "[2] Dang doc file local..." -ForegroundColor Yellow
try {
    $localContent = Get-Content -Path $LocalDataFile -Raw -Encoding UTF8
    $localData = $localContent | ConvertFrom-Json
    Write-Host "   [OK] Da doc file local: $($localData.models.Count) models" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Khong the doc file local: $_" -ForegroundColor Red
    exit 1
}

# Merge du lieu
Write-Host ""
Write-Host "[3] Dang merge du lieu..." -ForegroundColor Yellow

if ($renderData -and $renderData.models) {
    # Co du lieu tren Render -> merge
    $mergedModels = @()
    $renderModelIds = @{}
    $renderModelUids = @{}
    
    # Luu lai cac model tu Render (uu tien du lieu Render)
    foreach ($model in $renderData.models) {
        $mergedModels += $model
        if ($model.id) { $renderModelIds[$model.id] = $true }
        if ($model.modelUid) { $renderModelUids[$model.modelUid] = $true }
    }
    
    Write-Host "   - Da giu lai $($renderData.models.Count) models tu Render" -ForegroundColor Gray
    
    # Them cac model moi tu local (chua co tren Render)
    $newModelsCount = 0
    foreach ($model in $localData.models) {
        $isNew = $true
        
        # Kiem tra xem model da co tren Render chua (theo ID hoac UID)
        if ($model.id -and $renderModelIds.ContainsKey($model.id)) {
            $isNew = $false
        } elseif ($model.modelUid -and $renderModelUids.ContainsKey($model.modelUid)) {
            $isNew = $false
        }
        
        if ($isNew) {
            $mergedModels += $model
            if ($model.id) { $renderModelIds[$model.id] = $true }
            if ($model.modelUid) { $renderModelUids[$model.modelUid] = $true }
            $newModelsCount++
        }
    }
    
    Write-Host "   - Da them $newModelsCount models moi tu local" -ForegroundColor Gray
    Write-Host "   - Tong cong: $($mergedModels.Count) models" -ForegroundColor Green
    
    # Tao merged data
    $mergedData = @{
        models = $mergedModels
        version = ($renderData.version + 1)
        updatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    }
} else {
    # Khong co du lieu tren Render -> upload tu local
    Write-Host "   - Render chua co du lieu, se upload tu local" -ForegroundColor Yellow
    $mergedData = $localData
    if (-not $mergedData.version) { $mergedData.version = 1 }
    if (-not $mergedData.updatedAt) {
        $mergedData.updatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    }
}

# Backup merged data
$mergedBackup = Join-Path $BackupDir "data_merged_$timestamp.json"
$mergedData | ConvertTo-Json -Depth 100 | Set-Content -Path $mergedBackup -Encoding UTF8
Write-Host "   [OK] Da luu merged data: $mergedBackup" -ForegroundColor Green

# Upload len Render
Write-Host ""
Write-Host "[4] Dang upload len Render..." -ForegroundColor Yellow
try {
    $jsonBody = $mergedData | ConvertTo-Json -Depth 100 -Compress
    $utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonBody)
    
    $headers = @{
        "Content-Type" = "application/json; charset=utf-8"
        "Authorization" = "Bearer $AdminToken"
    }
    
    $response = Invoke-RestMethod -Uri "$RenderUrl/api/data" -Method Post -Headers $headers -Body $utf8Bytes -ContentType "application/json; charset=utf-8" -ErrorAction Stop
    
    Write-Host "   [OK] Upload thanh cong!" -ForegroundColor Green
    Write-Host "   - Version: $($response.version)" -ForegroundColor Gray
    Write-Host "   - UpdatedAt: $($response.updatedAt)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "=== Hoan thanh ===" -ForegroundColor Cyan
    Write-Host "Cac file backup da duoc luu trong thu muc: $BackupDir" -ForegroundColor Gray
    
} catch {
    Write-Host "   [ERROR] Loi khi upload: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   HTTP Status: $statusCode" -ForegroundColor Red
        
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   Chi tiet: $errorBody" -ForegroundColor Red
        } catch {
            # Ignore
        }
    }
    Write-Host ""
    Write-Host "Du lieu merged da duoc luu tai: $mergedBackup" -ForegroundColor Yellow
    Write-Host "Ban co the upload thu cong bang cach chay:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\upload-data-to-render.ps1" -ForegroundColor Yellow
    exit 1
}
