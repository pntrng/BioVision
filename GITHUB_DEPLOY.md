# 🚀 Hướng dẫn Deploy lên GitHub và Render (An toàn)

## 📋 Tổng quan

**File nào CẦN commit lên GitHub:**
- ✅ Code: `app.py`, `templates/`, `tests/`
- ✅ Config: `requirements.txt`, `Procfile`, `.gitignore`
- ✅ Docs: `README.md`, `SECURITY.md`, `DEPLOYMENT_GUIDE.md`, etc.
- ✅ Template: `env.example.txt` (KHÔNG phải `.env` thật)

**File nào KHÔNG được commit:**
- ❌ `.env` (chứa secrets thật)
- ❌ `data.json` (dữ liệu nhạy cảm)
- ❌ `__pycache__/` (Python cache)
- ❌ `*.log` (log files)

**Lưu ý:** `.gitignore` đã được cấu hình để tự động bỏ qua các file trên.

---

## 🔐 BƯỚC 1: Chuẩn bị trước khi commit

### 1.1. Kiểm tra không có secrets trong code

```powershell
# Kiểm tra xem có token nào hardcode không
Select-String -Path "app.py","templates/*.html" -Pattern "ADMIN_TOKEN.*=.*['\"].*['\"]" -CaseSensitive

# Kiểm tra xem có .env file không (không nên commit)
if (Test-Path .env) {
    Write-Host "⚠️  WARNING: .env file exists. Make sure it's in .gitignore!" -ForegroundColor Yellow
}
```

### 1.2. Tạo token mạnh cho production

```powershell
# Tạo token ngẫu nhiên mạnh
python -c "import secrets; print('ADMIN_TOKEN=' + secrets.token_urlsafe(32))"
```

**Lưu lại token này** - bạn sẽ cần nó cho Render!

### 1.3. Đảm bảo data.json không bị commit

```powershell
# Kiểm tra .gitignore có data.json không
Select-String -Path ".gitignore" -Pattern "data.json"

# Nếu chưa có, thêm vào .gitignore (đã có rồi)
```

---

## 📤 BƯỚC 2: Push lên GitHub

### 2.1. Khởi tạo Git repository (nếu chưa có)

```powershell
# Kiểm tra xem đã có git chưa
git status

# Nếu chưa có, khởi tạo
git init

# Thêm remote (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 2.2. Kiểm tra files sẽ được commit

```powershell
# Xem files sẽ được add
git status

# Xem files bị ignore (đảm bảo .env và data.json không có)
git status --ignored
```

**Kết quả mong đợi:**
- ✅ `app.py`, `requirements.txt`, `templates/`, etc. → sẽ được commit
- ❌ `.env`, `data.json`, `__pycache__/` → bị ignore

### 2.3. Commit và push

```powershell
# Add tất cả files (theo .gitignore)
git add .

# Kiểm tra lại lần nữa
git status

# Commit
git commit -m "Initial commit: BioVision 3D with security features"

# Push lên GitHub
git branch -M main
git push -u origin main
```

### 2.4. Verify trên GitHub

1. Vào https://github.com/YOUR_USERNAME/YOUR_REPO
2. **QUAN TRỌNG:** Kiểm tra:
   - ❌ KHÔNG có file `.env`
   - ❌ KHÔNG có file `data.json`
   - ✅ Có file `env.example.txt`
   - ✅ Có file `.gitignore`

---

## 🌐 BƯỚC 3: Deploy lên Render

### 3.1. Tạo Render account và service

1. Đăng ký/đăng nhập: https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository của bạn
4. Chọn repository: `YOUR_USERNAME/YOUR_REPO`

### 3.2. Cấu hình Render

**Settings:**

| Field | Value |
|-------|-------|
| **Name** | `biovision-3d` (hoặc tên bạn muốn) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60` |

**Hoặc dùng Procfile (đã có sẵn):**
- Render sẽ tự động đọc `Procfile`
- Start command: `web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`

### 3.3. ⚠️ QUAN TRỌNG: Set Environment Variables

Trong Render dashboard, vào **"Environment"** tab và thêm:

| Key | Value | Notes |
|-----|-------|-------|
| `ADMIN_TOKEN` | `your-generated-token-here` | Token bạn tạo ở bước 1.2 |
| `ENV` | `production` | Để tắt debug mode |
| `PORT` | (để trống) | Render tự động set |

**Cách set:**
1. Click **"Add Environment Variable"**
2. Key: `ADMIN_TOKEN`
3. Value: Paste token bạn đã tạo (ví dụ: `xK9mP2qR7vW4nT8yZ1aB3cD5eF6gH7j`)
4. Click **"Save Changes"**
5. Lặp lại cho `ENV=production`

### 3.4. Deploy

1. Click **"Create Web Service"**
2. Render sẽ tự động:
   - Clone code từ GitHub
   - Install dependencies (`pip install -r requirements.txt`)
   - Start server với gunicorn
3. Đợi deploy xong (2-5 phút)
4. Bạn sẽ có URL: `https://your-app-name.onrender.com`

---

## 🔒 BƯỚC 4: Bảo mật sau khi deploy

### 4.1. Kiểm tra security headers

```powershell
# Test security headers
$response = Invoke-WebRequest -Uri "https://your-app-name.onrender.com" -Method Get
$response.Headers
```

**Kiểm tra có:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy: ...`

### 4.2. Test API endpoints

```powershell
# Test GET (public)
Invoke-RestMethod -Uri "https://your-app-name.onrender.com/api/data" -Method Get

# Test POST without token (should fail)
try {
    $body = '{"models":[]}'
    Invoke-RestMethod -Uri "https://your-app-name.onrender.com/api/data" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "✅ Correctly blocked: $($_.Exception.Response.StatusCode.value__)"
}

# Test POST with token (should work)
$headers = @{
    "Authorization" = "Bearer YOUR_ADMIN_TOKEN_HERE"
    "Content-Type" = "application/json"
}
$body = '{"models":[{"id":"test","grade":"10","chapter":"Test","modelUid":"test-123","items":[]}]}'
Invoke-RestMethod -Uri "https://your-app-name.onrender.com/api/data" -Method Post -Body $body -Headers $headers
```

### 4.3. Test admin page

1. Mở: `https://your-app-name.onrender.com/admin`
2. **Kỳ vọng:** Bị chặn (401) nếu không có token
3. Đây là đúng! Admin page cần authentication.

### 4.4. Lưu ý về data.json trên Render

⚠️ **Quan trọng:** Render free tier không có persistent disk. Mỗi lần redeploy, `data.json` sẽ bị reset về empty.

**Giải pháp:**
1. **Tạm thời:** Chấp nhận mất data khi redeploy
2. **Lâu dài:** 
   - Upgrade lên Render paid plan (có persistent disk)
   - Hoặc migrate sang database (PostgreSQL trên Render)

---

## 📝 Checklist trước khi deploy

- [ ] Đã kiểm tra không có `.env` trong Git
- [ ] Đã kiểm tra không có `data.json` trong Git
- [ ] Đã tạo token mạnh cho production
- [ ] Đã push code lên GitHub
- [ ] Đã verify trên GitHub (không có secrets)
- [ ] Đã set `ADMIN_TOKEN` trong Render environment variables
- [ ] Đã set `ENV=production` trong Render
- [ ] Đã test API sau khi deploy
- [ ] Đã test admin page (bị chặn khi không có token)

---

## 🆘 Troubleshooting

### Lỗi: "ADMIN_TOKEN not configured"
**Nguyên nhân:** Chưa set environment variable trong Render.
**Giải pháp:** Vào Render dashboard → Environment → Add `ADMIN_TOKEN`

### Lỗi: "ModuleNotFoundError: No module named 'gunicorn'"
**Nguyên nhân:** `requirements.txt` thiếu gunicorn.
**Giải pháp:** Đảm bảo `requirements.txt` có `gunicorn==21.2.0`

### Lỗi: "Port already in use"
**Nguyên nhân:** Start command sai.
**Giải pháp:** Dùng `$PORT` trong start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Lỗi: Deploy thành công nhưng 502 Bad Gateway
**Nguyên nhân:** App crash khi start.
**Giải pháp:** 
1. Xem logs trong Render dashboard
2. Kiểm tra environment variables đã set chưa
3. Test local với `gunicorn` trước

---

## 🔄 Cập nhật code sau này

```powershell
# 1. Sửa code local
# ... make changes ...

# 2. Commit và push
git add .
git commit -m "Description of changes"
git push origin main

# 3. Render tự động deploy (nếu đã bật Auto-Deploy)
# Hoặc manual deploy trong Render dashboard
```

---

## 📚 Tài liệu tham khảo

- Render Docs: https://render.com/docs
- GitHub Docs: https://docs.github.com
- Flask Security: https://flask.palletsprojects.com/en/3.0.x/security/
- Xem thêm: `DEPLOYMENT_GUIDE.md`, `SECURITY_REVIEW.md`
