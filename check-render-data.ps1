# Script de kiem tra du lieu tren Render
# Su dung: powershell -ExecutionPolicy Bypass -File .\check-render-data.ps1

param(
    [string]$RenderUrl = "https://biovision-tihm.onrender.com"
)

Write-Host "=== Kiem tra du lieu tren Render ===" -ForegroundColor Cyan
Write-Host ""

# Kiem tra mindmap_order.json
Write-Host "[1] Kiem tra mindmap_order.json..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$RenderUrl/mindmap_order.json" -Method Get -ErrorAction Stop
    $grades = $response.grades
    Write-Host "   [OK] Tim thay $($grades.Count) khoi lop: $($grades -join ', ')" -ForegroundColor Green
    
    foreach ($grade in $grades) {
        $chapters = $response.chapters_by_grade[$grade]
        if ($chapters) {
            Write-Host "   - Khoi $grade : $($chapters.Count) chuong" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   [ERROR] Khong the tai mindmap_order.json: $_" -ForegroundColor Red
}

Write-Host ""

# Kiem tra data.json
Write-Host "[2] Kiem tra data.json (models)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$RenderUrl/api/data" -Method Get -ErrorAction Stop
    $models = $response.models
    Write-Host "   [OK] Tim thay $($models.Count) models" -ForegroundColor Green
    
    # Dem theo grade
    $gradesInData = @{}
    foreach ($model in $models) {
        $grade = $model.grade
        if (-not $grade) { $grade = "Khac" }
        if (-not $gradesInData.ContainsKey($grade)) {
            $gradesInData[$grade] = 0
        }
        $gradesInData[$grade]++
    }
    
    Write-Host "   Phan bo theo khoi:" -ForegroundColor Gray
    foreach ($grade in ($gradesInData.Keys | Sort-Object)) {
        Write-Host "   - Khoi $grade : $($gradesInData[$grade]) models" -ForegroundColor Gray
    }
    
    # Kiem tra xem co Khoi 11 va 12 khong
    if (-not $gradesInData.ContainsKey("11")) {
        Write-Host "   [WARN] Chua co du lieu Khoi 11!" -ForegroundColor Yellow
        Write-Host "   -> Chay: powershell -ExecutionPolicy Bypass -File .\upload-data-to-render.ps1" -ForegroundColor Yellow
    }
    if (-not $gradesInData.ContainsKey("12")) {
        Write-Host "   [WARN] Chua co du lieu Khoi 12!" -ForegroundColor Yellow
        Write-Host "   -> Chay: powershell -ExecutionPolicy Bypass -File .\upload-data-to-render.ps1" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   [ERROR] Khong the tai data: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Hoan thanh ===" -ForegroundColor Cyan
