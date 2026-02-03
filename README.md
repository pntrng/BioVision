# BioVision 3D

Thư viện mô hình 3D dạy/học Sinh học - Hệ thống quản lý và hiển thị hotspot trên mô hình Sketchfab.

## 🚀 Quick Start

### Local Development

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Tạo file `.env` từ template:**
```bash
cp .env.example .env
```

3. **Generate Admin Token:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy token vào file `.env`:
```
ADMIN_TOKEN=your-generated-token-here
ENV=development
```

4. **Chạy server:**
```bash
python app.py
```

5. **Truy cập:**
- Trang học sinh: http://localhost:5000/
- Trang admin: http://localhost:5000/admin

### Production (Render.com)

📖 **Xem hướng dẫn chi tiết:** [`GITHUB_DEPLOY.md`](GITHUB_DEPLOY.md)

**Quick Steps:**

1. **Push code lên GitHub** (đảm bảo không commit `.env` hoặc `data.json`)
2. **Tạo service trên Render:**
   - Chọn "Web Service"
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: (Render tự động đọc `Procfile`)

3. **Set Environment Variables trong Render:**
   ```
   ADMIN_TOKEN=<generate-strong-token>
   ENV=production
   ```

4. **Deploy:** Render tự động deploy khi push code

⚠️ **Lưu ý:** Render free tier không có persistent disk. `data.json` sẽ reset khi redeploy.

## 📁 Cấu trúc Project

```
BioVision/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Render start command
├── data.json             # Database file (gitignored)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── SECURITY.md           # Security policy
├── SECURITY_REVIEW.md    # Security audit report
└── templates/
    ├── admin.html        # Admin interface
    └── guest.html        # Student interface
```

## 🔐 Security

- **Authentication:** Bearer token required cho POST `/api/data`
- **Validation:** Strict schema validation cho tất cả inputs
- **Headers:** Security headers (CSP, X-Frame-Options, etc.)
- **File Writes:** Atomic writes để tránh corruption

Xem `SECURITY_REVIEW.md` và `SECURITY.md` để biết thêm chi tiết.

## 🚀 Deployment

### Pre-Commit Check

Trước khi commit, chạy security check:

```powershell
powershell -ExecutionPolicy Bypass -File .\pre-commit-check.ps1
```

### Deploy lên GitHub + Render

Xem hướng dẫn chi tiết: [`GITHUB_DEPLOY.md`](GITHUB_DEPLOY.md)

**Tóm tắt:**
1. ✅ Kiểm tra không có secrets trong code
2. ✅ Push code lên GitHub
3. ✅ Connect GitHub với Render
4. ✅ Set environment variables trong Render
5. ✅ Deploy và test

## 🧪 Testing

### Manual Testing

```bash
# Test GET (should work)
curl http://localhost:5000/api/data

# Test POST without token (should fail with 401)
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"models":[]}'

# Test POST with token (should work)
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"models":[]}'
```

### Smoke Tests

Chạy `tests/test_smoke.py` (nếu có):
```bash
pytest tests/
```

## 📝 Usage

### Admin Interface

1. Truy cập `/admin`
2. Nhập Admin Token (từ environment variable)
3. Điền thông tin:
   - Khối lớp (10, 11, 12)
   - Chương (VD: "Tế bào nhân sơ")
   - Model UID từ Sketchfab
4. Load model → Tạo hotspot → Lưu

### Student Interface

1. Truy cập `/`
2. Tìm kiếm/filter theo khối lớp, chương
3. Chọn mô hình từ danh sách
4. Click vào hotspot hoặc chọn từ sidebar để xem chi tiết

## 🎛️ UX Controls (Guest)

- **Reset góc nhìn:** nút `↺ Reset góc nhìn` trong cụm controls hoặc phím tắt `R`.
- **Trình chiếu:** nút `🖥️ Trình chiếu` trên topbar (ẩn sidebar, phóng to viewer). Có thể mở bằng URL: `/?mode=present`.

### Default Camera per Lesson

- Mặc định hệ thống lưu camera ban đầu khi viewer sẵn sàng.
- Có thể tuỳ chỉnh trong `templates/guest.html`:
  - `getDefaultCamera(model)` (override nếu muốn)
  - `defaultCameras` (map theo `modelUid`)

### Design Tokens

- Tokens ở `static/css/theme.css` (màu, font, radius, shadow).
- UI chính dùng `.card`, `.panel`, `.btn` để giữ đồng nhất.

## ✅ Manual UX Checklist

- Desktop: chọn model → reset camera → hotspot hiển thị nhãn, click mở chi tiết.
- Presenter mode: bật/tắt, viewer full width, UI không vỡ.
- Mobile: mở hamburger để chọn model, hotspot click mở chi tiết, không double-scroll.
- Loading: hiển thị overlay khi tải model, có retry nếu lỗi/timeout.

## 🛠️ Development

### Code Style

- Follow PEP 8
- Use type hints where possible
- Comment complex logic

### Security Checklist

- [ ] No secrets in code
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak info
- [ ] Security headers set
- [ ] XSS protection (escape HTML)

## 📄 License

[Your License Here]

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Run tests
5. Submit PR

---

**Lưu ý:** File `data.json` chứa dữ liệu nhạy cảm, không commit vào git.
