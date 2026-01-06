# Test script for BioVision API endpoints
# Usage: .\test-api.ps1

$baseUrl = "http://localhost:5000"
$adminToken = "test-token-123"  # Change this to match your ADMIN_TOKEN

Write-Host "`n=== Testing BioVision API ===`n" -ForegroundColor Cyan

# Test 0: Check token status on server
Write-Host "0. Checking server token status..." -ForegroundColor Yellow
try {
    $tokenStatus = Invoke-RestMethod -Uri "$baseUrl/api/debug/token-status" -Method Get
    if ($tokenStatus.status -eq "set") {
        Write-Host "   ✅ Server has ADMIN_TOKEN set" -ForegroundColor Green
        Write-Host "   Token length: $($tokenStatus.length)" -ForegroundColor Gray
        Write-Host "   Masked token: $($tokenStatus.masked)" -ForegroundColor Gray
        Write-Host "   First 4 chars: $($tokenStatus.first_4)" -ForegroundColor Gray
        Write-Host "   Last 4 chars: $($tokenStatus.last_4)" -ForegroundColor Gray
        Write-Host "   Test token first 4: $($adminToken.Substring(0, [Math]::Min(4, $adminToken.Length)))" -ForegroundColor Cyan
        Write-Host "   Test token last 4: $($adminToken.Substring([Math]::Max(0, $adminToken.Length - 4)))" -ForegroundColor Cyan
        
        if ($tokenStatus.first_4 -eq $adminToken.Substring(0, [Math]::Min(4, $adminToken.Length)) -and 
            $tokenStatus.last_4 -eq $adminToken.Substring([Math]::Max(0, $adminToken.Length - 4))) {
            Write-Host "   ✅ Token appears to match!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Token does NOT match! Update ADMIN_TOKEN on server or test script." -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ Server ADMIN_TOKEN not set!" -ForegroundColor Red
        Write-Host "   $($tokenStatus.warning)" -ForegroundColor Yellow
        Write-Host "   $($tokenStatus.hint)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Debug endpoint not available (might be production mode)" -ForegroundColor Yellow
}

Write-Host "`n" -NoNewline

# Test 1: GET /api/data (public, no auth required)
Write-Host "1. Testing GET /api/data (public access)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/data" -Method Get -ContentType "application/json"
    Write-Host "   ✅ Success! Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response body: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline

# Test 2: POST /api/data without token (should return 401)
Write-Host "2. Testing POST /api/data WITHOUT token (should fail with 401)..." -ForegroundColor Yellow
try {
    $body = @{
        models = @()
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/data" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ⚠️  Unexpected success! This should have failed." -ForegroundColor Red
    $response | ConvertTo-Json
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401) {
        Write-Host "   ✅ Correctly rejected (401 Unauthorized)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Unexpected status: $statusCode" -ForegroundColor Red
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline

# Test 3: POST /api/data with token (should succeed)
Write-Host "3. Testing POST /api/data WITH token (should succeed)..." -ForegroundColor Yellow
try {
    $body = @{
        models = @(
            @{
                id = "test_model_1"
                grade = "10"
                chapter = "Test Chapter"
                modelUid = "test-uid-123"
                items = @(
                    @{
                        id = "test_item_1"
                        name = "Test Organelle"
                        content = "Test content"
                        link = ""
                        world = @(0.1, 0.2, 0.3)
                        cam = @{
                            position = @(0.0, 0.0, 0.0)
                            target = @(0.1, 0.1, 0.1)
                            duration = 1.2
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/data" -Method Post -Body $body -Headers $headers
    Write-Host "   ✅ Success! Data saved." -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status Code: $statusCode" -ForegroundColor Red
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline

# Test 4: POST with invalid payload (should return 400)
Write-Host "4. Testing POST /api/data with invalid payload (should fail with 400)..." -ForegroundColor Yellow
try {
    $body = @{
        invalid = "data"
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/data" -Method Post -Body $body -Headers $headers
    Write-Host "   ⚠️  Unexpected success! This should have failed." -ForegroundColor Red
    $response | ConvertTo-Json
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "   ✅ Correctly rejected (400 Bad Request)" -ForegroundColor Green
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ Unexpected status: $statusCode" -ForegroundColor Red
    }
}

Write-Host "`n=== Tests Complete ===`n" -ForegroundColor Cyan
