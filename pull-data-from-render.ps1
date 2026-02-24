# Script: Download data from Render down to local data.json (Render → Local)
# Su dung:
#   powershell -ExecutionPolicy Bypass -File .\pull-data-from-render.ps1
# Hoac:
#   powershell -ExecutionPolicy Bypass -File .\pull-data-from-render.ps1 -RenderUrl "https://your-app.onrender.com" -OutputFile "data.json"

param(
    [string]$RenderUrl = "https://biovision-tihm.onrender.com",
    [string]$OutputFile = "data.json",
    [string]$BackupDir = "backups"
)

Write-Host "=== Download du lieu tu Render ve LOCAL (Render → Local) ===" -ForegroundColor Cyan
Write-Host ""

# 1) Backup file local neu ton tai
if (Test-Path $OutputFile) {
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir "data_local_before_render_$timestamp.json"

    Copy-Item $OutputFile $backupPath
    Write-Host "[OK] Da backup file local: $OutputFile -> $backupPath" -ForegroundColor Green
} else {
    Write-Host "[INFO] Khong tim thay file local $OutputFile, se tao moi tu Render" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[1] Dang tai du lieu tu $RenderUrl/api/data ..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$RenderUrl/api/data" -Method Get -ErrorAction Stop

    $models = $response.models
    $count = if ($models) { $models.Count } else { 0 }

    # Ghi de file local bang du lieu tu Render
    $response | ConvertTo-Json -Depth 100 | Set-Content -Path $OutputFile -Encoding UTF8
    Write-Host "   [OK] Da luu du lieu vao: $OutputFile ($count models)" -ForegroundColor Green

    # Thong ke theo khoi de de quan sat
    if ($models) {
        Write-Host ""
        Write-Host "   Phan bo theo khoi (theo Render):" -ForegroundColor Gray
        $grades = @{}
        foreach ($m in $models) {
            $g = if ($m.grade) { $m.grade } else { "Khac" }
            if (-not $grades.ContainsKey($g)) {
                $grades[$g] = 0
            }
            $grades[$g]++
        }

        foreach ($g in ($grades.Keys | Sort-Object)) {
            Write-Host "   - Khoi $g : $($grades[$g]) models" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "   [ERROR] Khong the tai du lieu tu Render: $_" -ForegroundColor Red
    Write-Host "   -> Kiem tra lai RenderUrl hoac ket noi mang." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Hoan thanh: LOCAL da duoc cap nhat tu Render ===" -ForegroundColor Cyan

