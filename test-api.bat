@echo off
REM Simple batch file to test BioVision API
REM Usage: test-api.bat

echo.
echo === Testing BioVision API ===
echo.

set BASE_URL=http://localhost:5000
set ADMIN_TOKEN=test-token-123

echo 1. Testing GET /api/data (public access)...
powershell -Command "Invoke-RestMethod -Uri '%BASE_URL%/api/data' -Method Get | ConvertTo-Json"
echo.

echo 2. Testing POST /api/data WITHOUT token (should fail with 401)...
powershell -Command "try { $body = '{\"models\":[]}'; Invoke-RestMethod -Uri '%BASE_URL%/api/data' -Method Post -Body $body -ContentType 'application/json' } catch { Write-Host 'Status:' $_.Exception.Response.StatusCode.value__ }"
echo.

echo 3. Testing POST /api/data WITH token (should succeed)...
powershell -Command "$headers = @{'Authorization'='Bearer %ADMIN_TOKEN%'; 'Content-Type'='application/json'}; $body = '{\"models\":[{\"id\":\"test\",\"grade\":\"10\",\"chapter\":\"Test\",\"modelUid\":\"test-123\",\"items\":[]}]}'; try { Invoke-RestMethod -Uri '%BASE_URL%/api/data' -Method Post -Body $body -Headers $headers | ConvertTo-Json } catch { Write-Host 'Error:' $_.Exception.Message }"
echo.

echo 4. Testing POST with invalid payload (should fail with 400)...
powershell -Command "$headers = @{'Authorization'='Bearer %ADMIN_TOKEN%'; 'Content-Type'='application/json'}; $body = '{\"invalid\":\"data\"}'; try { Invoke-RestMethod -Uri '%BASE_URL%/api/data' -Method Post -Body $body -Headers $headers } catch { Write-Host 'Status:' $_.Exception.Response.StatusCode.value__ }"
echo.

echo === Tests Complete ===
echo.
pause
