# Debug Guide - Giải quyết lỗi Token và API

## 🔍 Vấn đề thường gặp

### 1. Test trả về 401 Unauthorized
**Nguyên nhân:** Token trong test script không khớp với token trên server.

**Giải pháp:**
```powershell
# Bước 1: Kiểm tra token trên server
Invoke-RestMethod -Uri "http://localhost:5000/api/debug/token-status" -Method Get

# Bước 2: So sánh với token trong test script
# Mở test-api.ps1, xem dòng 5: $adminToken = "test-token-123"
# Đảm bảo token này khớp với $env:ADMIN_TOKEN khi start server
```

### 2. admin.html báo "Failed to fetch"
**Nguyên nhân:** Server không chạy hoặc không thể kết nối.

**Giải pháp:**
```powershell
# Bước 1: Kiểm tra server có đang chạy không
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Get

# Bước 2: Nếu lỗi, start server lại với token:
$env:ADMIN_TOKEN = "test-token-123"
$env:ENV = "development"
python app.py
```

### 3. Token không khớp
**Triệu chứng:** Test 3 và 4 đều trả về 401.

**Giải pháp:**
```powershell
# Bước 1: Xem token trên server
$status = Invoke-RestMethod -Uri "http://localhost:5000/api/debug/token-status" -Method Get
Write-Host "Server token: $($status.first_4)...$($status.last_4)"

# Bước 2: So sánh với token bạn đang dùng
# Nếu khác, cập nhật một trong hai:
# - Sửa $env:ADMIN_TOKEN khi start server
# - Hoặc sửa $adminToken trong test-api.ps1
```

## 🛠️ Các công cụ debug

### 1. Debug Endpoint (Development only)
```powershell
# Kiểm tra token status trên server
Invoke-RestMethod -Uri "http://localhost:5000/api/debug/token-status" -Method Get
```

**Response khi có token:**
```json
{
  "status": "set",
  "length": 15,
  "masked": "test******-123",
  "first_4": "test",
  "last_4": "-123"
}
```

**Response khi không có token:**
```json
{
  "status": "not_set",
  "warning": "ADMIN_TOKEN environment variable is not set",
  "hint": "Set it with: $env:ADMIN_TOKEN = 'your-token-here'"
}
```

### 2. Server Logs
Khi start server, bạn sẽ thấy:
```
🔐 ADMIN_TOKEN loaded: test******-123 (length: 15)
```
hoặc
```
⚠️  WARNING: ADMIN_TOKEN not set! POST /api/data and /admin will be blocked.
   Set it with: $env:ADMIN_TOKEN = 'your-token-here'
```

### 3. Test Script với Debug
```powershell
# Chạy test script (sẽ tự động check token status)
powershell -ExecutionPolicy Bypass -File .\test-api.ps1
```

## 📋 Checklist Debug

Khi gặp lỗi, kiểm tra theo thứ tự:

- [ ] Server có đang chạy không? (`http://localhost:5000/api/data` trả về JSON)
- [ ] ADMIN_TOKEN có được set khi start server không? (Xem console log)
- [ ] Token trong admin.html/test script có khớp với server không? (Dùng debug endpoint)
- [ ] Browser console có lỗi gì không? (F12 → Console)
- [ ] Network tab có request nào fail không? (F12 → Network)

## 🔧 Quick Fix Commands

```powershell
# 1. Stop server (Ctrl+C trong terminal chạy server)

# 2. Set token và start lại
$env:ADMIN_TOKEN = "test-token-123"
$env:ENV = "development"
python app.py

# 3. Test trong terminal mới
powershell -ExecutionPolicy Bypass -File .\test-api.ps1

# 4. Hoặc test thủ công
$headers = @{
    "Authorization" = "Bearer test-token-123"
    "Content-Type" = "application/json"
}
$body = '{"models":[{"id":"test","grade":"10","chapter":"Test","modelUid":"test-123","items":[]}]}'
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -Headers $headers
```

## 💡 Best Practices

1. **Luôn set ADMIN_TOKEN trước khi start server:**
   ```powershell
   $env:ADMIN_TOKEN = "your-secure-token-here"
   python app.py
   ```

2. **Dùng cùng một token cho tất cả:**
   - Server: `$env:ADMIN_TOKEN`
   - Test script: `$adminToken` trong `test-api.ps1`
   - admin.html: Nhập vào input field

3. **Kiểm tra token status trước khi test:**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/api/debug/token-status"
   ```

4. **Xem server logs** để biết token có được load không.
