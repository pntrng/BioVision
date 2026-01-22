# Test upload with smaller payload to debug
param(
    [string]$RenderUrl = "https://biovision-tihm.onrender.com",
    [string]$AdminToken = ""
)

if (-not $AdminToken) {
    $AdminToken = Read-Host "Nhap Admin Token"
}

Write-Host "Testing with minimal data..." -ForegroundColor Yellow

$testData = @{
    models = @(
        @{
            id = "test_1"
            grade = "10"
            chapter = "Test Chapter"
            name = "Test Model"
            modelUid = "test123"
            feature = "Test feature"
            funFact = "Test fun fact"
            items = @()
        }
    )
    version = 1
    updatedAt = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 10

try {
    $headers = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $AdminToken"
    }
    
    Write-Host "Sending request..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$RenderUrl/api/data" `
        -Method POST `
        -Headers $headers `
        -Body $testData `
        -ErrorAction Stop
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Version: $($response.version)" -ForegroundColor Gray
    Write-Host "Updated: $($response.updatedAt)" -ForegroundColor Gray
    
} catch {
    Write-Host "ERROR:" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode.value__
        Write-Host "HTTP $statusCode" -ForegroundColor Red
        
        # Try to get error details
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response: $responseBody" -ForegroundColor Yellow
        } catch {
            Write-Host "Could not read error details" -ForegroundColor Yellow
        }
    } else {
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}
