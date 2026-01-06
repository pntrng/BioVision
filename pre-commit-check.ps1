# Pre-commit security check script
# Usage: .\pre-commit-check.ps1

Write-Host "`n=== Pre-Commit Security Check ===`n" -ForegroundColor Cyan

$errors = 0
$warnings = 0

# Check 1: .env file should not be committed
Write-Host "1. Checking for .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "   ⚠️  WARNING: .env file exists!" -ForegroundColor Yellow
    Write-Host "      Make sure it's in .gitignore (it should be)" -ForegroundColor Gray
    $warnings++
} else {
    Write-Host "   ✅ No .env file found" -ForegroundColor Green
}

# Check 2: data.json should not be committed
Write-Host "`n2. Checking for data.json in git..." -ForegroundColor Yellow
$gitStatus = git status --porcelain data.json 2>$null
if ($gitStatus -match "data\.json") {
    Write-Host "   ❌ ERROR: data.json is tracked by git!" -ForegroundColor Red
    Write-Host "      Run: git rm --cached data.json" -ForegroundColor Gray
    $errors++
} else {
    Write-Host "   ✅ data.json is ignored (good)" -ForegroundColor Green
}

# Check 3: Check .gitignore has required entries
Write-Host "`n3. Checking .gitignore..." -ForegroundColor Yellow
$gitignore = Get-Content .gitignore -Raw
$required = @(".env", "data.json", "__pycache__")
$missing = @()

foreach ($item in $required) {
    if ($gitignore -notmatch [regex]::Escape($item)) {
        $missing += $item
    }
}

if ($missing.Count -gt 0) {
    Write-Host "   ⚠️  WARNING: .gitignore missing: $($missing -join ', ')" -ForegroundColor Yellow
    $warnings++
} else {
    Write-Host "   ✅ .gitignore has all required entries" -ForegroundColor Green
}

# Check 4: Check for hardcoded tokens in code
Write-Host "`n4. Checking for hardcoded secrets..." -ForegroundColor Yellow
$suspicious = Select-String -Path "app.py", "templates/*.html" -Pattern "(ADMIN_TOKEN|password|secret).*=.*['\"][^'\"]{10,}['\"]" -CaseSensitive -ErrorAction SilentlyContinue
if ($suspicious) {
    Write-Host "   ⚠️  WARNING: Found potential hardcoded secrets:" -ForegroundColor Yellow
    $suspicious | ForEach-Object {
        Write-Host "      $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" -ForegroundColor Gray
    }
    $warnings++
} else {
    Write-Host "   ✅ No hardcoded secrets found" -ForegroundColor Green
}

# Check 5: Check if env.example.txt exists
Write-Host "`n5. Checking for env.example.txt..." -ForegroundColor Yellow
if (Test-Path "env.example.txt") {
    Write-Host "   ✅ env.example.txt exists (good for documentation)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WARNING: env.example.txt not found" -ForegroundColor Yellow
    $warnings++
}

# Check 6: Check requirements.txt has gunicorn
Write-Host "`n6. Checking requirements.txt for gunicorn..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $req = Get-Content requirements.txt -Raw
    if ($req -match "gunicorn") {
        Write-Host "   ✅ gunicorn found in requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  WARNING: gunicorn not in requirements.txt (needed for Render)" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "   ❌ ERROR: requirements.txt not found!" -ForegroundColor Red
    $errors++
}

# Check 7: Check Procfile exists
Write-Host "`n7. Checking for Procfile..." -ForegroundColor Yellow
if (Test-Path "Procfile") {
    Write-Host "   ✅ Procfile exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WARNING: Procfile not found (needed for Render)" -ForegroundColor Yellow
    $warnings++
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ All checks passed! Safe to commit." -ForegroundColor Green
    exit 0
} elseif ($errors -eq 0) {
    Write-Host "⚠️  $warnings warning(s) found. Review before committing." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "❌ $errors error(s) found. Fix before committing!" -ForegroundColor Red
    exit 1
}
