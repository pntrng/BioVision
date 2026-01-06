# Quick Test Guide - PowerShell

## ⚠️ LƯU Ý: Execution Policy

Nếu gặp lỗi "running scripts is disabled", dùng một trong các cách sau:

**Cách 1: Bypass cho script này (Khuyên dùng)**
```powershell
powershell -ExecutionPolicy Bypass -File .\test-api.ps1
```

**Cách 2: Bypass cho session hiện tại**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\test-api.ps1
```

**Cách 3: Chạy lệnh trực tiếp (xem bên dưới)**

---

## Bước 1: Khởi động Server

**QUAN TRỌNG:** Phải set `ADMIN_TOKEN` trước khi start server!

Mở terminal PowerShell và chạy:

```powershell
# Set environment variables (QUAN TRỌNG!)
$env:ADMIN_TOKEN = "test-token-123"
$env:ENV = "development"

# Start Flask server
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

**Lưu ý:** Token trong script (`test-api.ps1`) phải khớp với `$env:ADMIN_TOKEN` ở trên!

## Bước 2: Test API (Terminal mới)

Mở terminal PowerShell mới và chạy:

### Cách 1: Dùng script tự động (Khuyên dùng)
```powershell
# Bypass execution policy
powershell -ExecutionPolicy Bypass -File .\test-api.ps1
```

### Cách 2: Dùng file batch (Không cần Execution Policy)
```cmd
test-api.bat
```

### Cách 3: Test thủ công (Copy-paste từng lệnh)

**Test GET /api/data (public, không cần token):**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Get
```

**Test POST /api/data KHÔNG có token (sẽ bị từ chối 401):**
```powershell
$body = '{"models":[]}'
try {
    Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "✅ Đúng! Bị từ chối với mã: $($_.Exception.Response.StatusCode.value__)"
}
```

**Test POST /api/data CÓ token (sẽ thành công):**
```powershell
# QUAN TRỌNG: Token phải khớp với $env:ADMIN_TOKEN đã set khi start server!
$headers = @{
    "Authorization" = "Bearer test-token-123"
    "Content-Type" = "application/json"
}
$body = '{"models":[{"id":"test1","grade":"10","chapter":"Test","modelUid":"test-uid","items":[]}]}'
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -Headers $headers
```

**Test POST với payload sai (sẽ bị từ chối 400):**
```powershell
$headers = @{
    "Authorization" = "Bearer test-token-123"
    "Content-Type" = "application/json"
}
$body = '{"invalid":"data"}'
try {
    Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -Headers $headers
} catch {
    Write-Host "✅ Đúng! Bị từ chối với mã: $($_.Exception.Response.StatusCode.value__)"
}
```

## Bước 3: Test trong Browser

1. Mở `http://localhost:5000` → Xem trang guest (không cần token)
2. Mở `http://localhost:5000/admin` → Sẽ bị chặn (401) nếu không có token
3. Mở `http://localhost:5000/api/data` → Xem JSON data (public)

## Lưu ý

- **PowerShell `curl`** là alias của `Invoke-WebRequest`, cú pháp khác Unix `curl`
- Dùng `Invoke-RestMethod` cho JSON APIs
- Dùng `Invoke-WebRequest` cho HTML/raw responses
- Token phải khớp với `$env:ADMIN_TOKEN` đã set
