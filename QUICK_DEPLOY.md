# ⚡ Quick Deploy Reference

## 🔍 Pre-Commit Checklist

```powershell
# 1. Chạy security check
powershell -ExecutionPolicy Bypass -File .\pre-commit-check.ps1

# 2. Kiểm tra files sẽ commit
git status

# 3. Đảm bảo KHÔNG có:
#    - .env
#    - data.json
#    - __pycache__/
```

## 📤 GitHub Setup (Lần đầu)

```powershell
# 1. Khởi tạo (nếu chưa có)
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 2. Commit và push
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

## 🌐 Render Setup (Lần đầu)

1. **Tạo service:**
   - New → Web Service
   - Connect GitHub repo
   - Name: `biovision-3d`

2. **Environment Variables:**
   ```
   ADMIN_TOKEN = <generate-token>
   ENV = production
   ```

3. **Generate token:**
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Deploy:** Click "Create Web Service"

## 🔄 Update Code

```powershell
# 1. Sửa code
# ... make changes ...

# 2. Commit và push
git add .
git commit -m "Description"
git push origin main

# 3. Render tự động deploy
```

## ✅ Verify Deployment

```powershell
# Test GET (public)
Invoke-RestMethod -Uri "https://your-app.onrender.com/api/data"

# Test POST (should fail without token)
try {
    $body = '{"models":[]}'
    Invoke-RestMethod -Uri "https://your-app.onrender.com/api/data" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "✅ Blocked: $($_.Exception.Response.StatusCode.value__)"
}
```

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check `ADMIN_TOKEN` in Render env vars |
| 502 Bad Gateway | Check Render logs, verify gunicorn in requirements.txt |
| Data lost on redeploy | Normal on free tier. Use Render Disk or DB for persistence |

---

📖 **Chi tiết:** Xem [`GITHUB_DEPLOY.md`](GITHUB_DEPLOY.md)
