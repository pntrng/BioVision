# 🗄️ Hướng dẫn thiết lập ổ dữ liệu trung tâm trên Render

## 📋 Tổng quan

Để giải quyết vấn đề **"dữ liệu bị mất sau khi nhập một thời gian"**, bạn cần thiết lập một **ổ dữ liệu trung tâm (persistent disk)** trên Render. Điều này đảm bảo:

- ✅ Dữ liệu **không bị mất** khi redeploy
- ✅ Tất cả người dùng truy cập **cùng một nguồn dữ liệu**
- ✅ Cập nhật một lần, **mọi nơi đều thấy**

---

## 🎯 Bước 1: Chuẩn bị code trên GitHub

### 1.1. Kiểm tra code đã có hỗ trợ DATA_PATH

Code mới nhất đã hỗ trợ `DATA_PATH` environment variable. Đảm bảo bạn đã pull code mới nhất:

```powershell
cd C:\Users\HTD\Desktop\BioVision
git pull origin main
```

### 1.2. Commit và push nếu có thay đổi

Nếu bạn đã chỉnh sửa code local, commit và push lên GitHub:

```powershell
git status
git add .
git commit -m "Add DATA_PATH support for Render persistent disk"
git push origin main
```

---

## 🗄️ Bước 2: Tạo Render Disk (Ổ dữ liệu)

### 2.1. Truy cập Render Dashboard

1. Đăng nhập vào https://render.com
2. Chọn **Web Service** của bạn (ví dụ: `biovision-3d`)

### 2.2. Tạo Disk mới

1. Trong service, tìm tab **"Disks"** (hoặc **"Settings" → "Disks"**)
2. Click **"Add Disk"** hoặc **"Create Disk"**
3. Điền thông tin:
   - **Name:** `biovision-data` (tên tùy chọn)
   - **Size:** `1 GB` (đủ cho hàng nghìn models)
   - **Mount Path:** `/var/data/biovision` ⚠️ **QUAN TRỌNG!**
4. Click **"Create"** hoặc **"Save"**

### 2.3. Lưu ý về Mount Path

- **Mount Path** là đường dẫn **trong container** của Render
- Render sẽ tự động gắn disk này vào container mỗi lần deploy
- Bạn sẽ dùng đường dẫn này trong biến môi trường `DATA_PATH`

**Ví dụ Mount Path phổ biến:**
- `/var/data/biovision` ✅ (khuyến nghị)
- `/opt/render/project/data` ✅
- `/data` ✅

---

## ⚙️ Bước 3: Cấu hình Environment Variables

### 3.1. Truy cập Environment Variables

Trong Render Dashboard → Service của bạn → Tab **"Environment"**

### 3.2. Thêm/Cập nhật các biến sau

#### a) `DATA_PATH` (QUAN TRỌNG NHẤT)

```
DATA_PATH=/var/data/biovision/data.json
```

**Lưu ý:**
- `/var/data/biovision` phải **khớp chính xác** với **Mount Path** của Disk bạn vừa tạo
- `data.json` là tên file sẽ chứa toàn bộ dữ liệu

#### b) `ADMIN_TOKEN` (nếu chưa có)

```
ADMIN_TOKEN=<token-bí-mật-của-bạn>
```

**Tạo token mới (nếu cần):**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### c) `ENV`

```
ENV=production
```

### 3.3. Lưu lại

Click **"Save Changes"** hoặc **"Update"**

---

## 🚀 Bước 4: Redeploy Service

### 4.1. Trigger Deploy

Sau khi cấu hình xong, Render sẽ tự động redeploy. Nếu không:

1. Vào tab **"Events"** hoặc **"Deploys"**
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### 4.2. Kiểm tra Logs

Trong tab **"Logs"**, bạn sẽ thấy:
- ✅ App khởi động thành công
- ✅ Không có lỗi về file/directory
- ✅ Gunicorn worker đang chạy

**Ví dụ log thành công:**
```
[INFO] Booting worker with gunicorn
[INFO] Worker spawned (pid: 123)
[INFO] Listening at: http://0.0.0.0:10000
```

---

## 📤 Bước 5: Đưa dữ liệu hiện tại lên Render Disk (Tùy chọn)

Nếu bạn đã có dữ liệu ở máy local và muốn đưa lên Render:

### 5.1. Cách 1: Sử dụng Render Shell (Khuyến nghị)

1. Trong Render Dashboard → Service → Tab **"Shell"** hoặc **"Console"**
2. Chạy lệnh để tạo thư mục (nếu chưa có):
   ```bash
   mkdir -p /var/data/biovision
   ```
3. Tạo file `data.json` trống:
   ```bash
   echo '{"models": [], "version": 1, "updatedAt": ""}' > /var/data/biovision/data.json
   ```
4. Mở file `data.json` từ máy local của bạn (ví dụ: `C:\Users\HTD\Desktop\BioVision\data.json`)
5. **Copy toàn bộ nội dung** (Ctrl+A → Ctrl+C)
6. Trong Render Shell, chạy:
   ```bash
   cat > /var/data/biovision/data.json
   ```
7. **Dán nội dung** vào terminal (Ctrl+V)
8. Nhấn **Ctrl+D** để kết thúc

### 5.2. Cách 2: Sử dụng Admin Interface

1. Truy cập `https://<your-render-url>/admin`
2. Nhập `ADMIN_TOKEN` (từ environment variable)
3. Import dữ liệu từ file local (nếu có chức năng import)
4. Hoặc nhập lại dữ liệu thủ công

### 5.3. Cách 3: Sử dụng API (Nâng cao)

Nếu bạn có file `data.json` local, có thể POST trực tiếp:

```powershell
# PowerShell
$token = "your-admin-token"
$url = "https://your-app.onrender.com/api/data"
$data = Get-Content -Path "data.json" -Raw

Invoke-RestMethod -Uri $url -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
  } `
  -Body $data
```

---

## ✅ Bước 6: Kiểm tra và xác nhận

### 6.1. Test API Endpoint

Mở trình duyệt hoặc dùng PowerShell:

```powershell
# Test GET (không cần token)
Invoke-RestMethod -Uri "https://your-app.onrender.com/api/data" | ConvertTo-Json -Depth 10
```

**Kết quả mong đợi:**
- ✅ Trả về JSON với dữ liệu models
- ✅ Không có lỗi 404 hoặc 500

### 6.2. Test Admin Interface

1. Truy cập `https://your-app.onrender.com/admin`
2. Nhập `ADMIN_TOKEN`
3. Thử chỉnh sửa một điểm nhỏ (ví dụ: đổi tên một item)
4. Click **"Lưu"**
5. Reload trang → Dữ liệu phải còn nguyên

### 6.3. Test Guest Interface

1. Truy cập `https://your-app.onrender.com/`
2. Kiểm tra cây kiến thức hiển thị đúng
3. Click vào một model → Thông tin hiển thị đúng

### 6.4. Test Persistence (Quan trọng!)

1. Trong Admin, thêm một model mới hoặc chỉnh sửa
2. **Lưu lại**
3. Trong Render Dashboard → **"Manual Deploy"** → **"Redeploy"**
4. Chờ deploy xong (1-2 phút)
5. Reload trang Guest → **Dữ liệu phải còn nguyên!**

---

## 🔍 Troubleshooting

### ❌ Vấn đề: Dữ liệu vẫn bị mất sau redeploy

**Nguyên nhân:**
- `DATA_PATH` chưa được set đúng
- Mount Path của Disk không khớp với `DATA_PATH`
- Disk chưa được tạo hoặc chưa được mount

**Giải pháp:**
1. Kiểm tra `DATA_PATH` trong Environment Variables:
   ```
   DATA_PATH=/var/data/biovision/data.json
   ```
2. Kiểm tra Mount Path của Disk:
   - Vào **Disks** tab
   - Xem **Mount Path** (ví dụ: `/var/data/biovision`)
   - Đảm bảo `DATA_PATH` trỏ đến đúng thư mục này
3. Kiểm tra Disk đã được mount:
   - Vào **Shell** tab
   - Chạy: `ls -la /var/data/biovision`
   - Phải thấy file `data.json` hoặc thư mục tồn tại

### ❌ Vấn đề: "Permission denied" khi ghi file

**Nguyên nhân:** Quyền truy cập thư mục không đúng

**Giải pháp:**
Trong Render Shell:
```bash
chmod 755 /var/data/biovision
chmod 644 /var/data/biovision/data.json
```

### ❌ Vấn đề: File không tồn tại

**Giải pháp:**
1. Trong Render Shell:
   ```bash
   mkdir -p /var/data/biovision
   touch /var/data/biovision/data.json
   chmod 666 /var/data/biovision/data.json
   ```
2. Redeploy service
3. App sẽ tự động tạo file nếu chưa có (nhờ `ensure_data_file()`)

### ❌ Vấn đề: "No space left on device"

**Nguyên nhân:** Disk đã đầy

**Giải pháp:**
1. Vào **Disks** tab
2. Xem **Usage** của disk
3. Nếu > 80%, tăng size disk:
   - Click **"Edit"** trên disk
   - Tăng size (ví dụ: 1GB → 2GB)
   - Save và redeploy

---

## 📊 Kiểm tra trạng thái Disk

### Xem thông tin Disk

1. Render Dashboard → Service → **Disks**
2. Bạn sẽ thấy:
   - **Name:** Tên disk
   - **Size:** Dung lượng
   - **Usage:** Dung lượng đã dùng
   - **Mount Path:** Đường dẫn mount

### Xem file trong Disk (qua Shell)

```bash
# Xem danh sách file
ls -lh /var/data/biovision/

# Xem nội dung file (nếu nhỏ)
cat /var/data/biovision/data.json

# Xem kích thước file
du -h /var/data/biovision/data.json
```

---

## 🔄 Quy trình làm việc sau khi setup

### Khi cần chỉnh sửa dữ liệu:

1. ✅ Truy cập `https://your-app.onrender.com/admin`
2. ✅ Nhập `ADMIN_TOKEN`
3. ✅ Chỉnh sửa và **Lưu**
4. ✅ Tất cả người dùng truy cập `https://your-app.onrender.com/` sẽ thấy dữ liệu mới ngay lập tức

### Khi cần cập nhật code:

1. ✅ Chỉnh sửa code trên máy local
2. ✅ `git commit` và `git push`
3. ✅ Render tự động deploy code mới
4. ✅ **Dữ liệu vẫn nằm trên Disk, không bị mất!**

---

## 📝 Checklist hoàn thành

Trước khi kết thúc, đảm bảo:

- [ ] Render Disk đã được tạo với Mount Path `/var/data/biovision`
- [ ] Environment Variable `DATA_PATH=/var/data/biovision/data.json` đã được set
- [ ] Environment Variable `ADMIN_TOKEN` đã được set
- [ ] Environment Variable `ENV=production` đã được set
- [ ] Service đã được redeploy sau khi cấu hình
- [ ] Đã test GET `/api/data` → trả về dữ liệu
- [ ] Đã test POST qua Admin → lưu thành công
- [ ] Đã test redeploy → dữ liệu không bị mất
- [ ] Đã test Guest interface → hiển thị đúng dữ liệu

---

## 🎉 Hoàn thành!

Bây giờ bạn đã có:
- ✅ **Ổ dữ liệu trung tâm** trên Render Disk
- ✅ **Dữ liệu bền vững** không bị mất khi redeploy
- ✅ **Đồng bộ tự động** - cập nhật một lần, mọi nơi đều thấy

**Lưu ý cuối cùng:**
- Backup `data.json` định kỳ (download từ Render Shell)
- Giữ `ADMIN_TOKEN` bí mật, không commit vào Git
- Monitor disk usage để tránh hết dung lượng

---

## 📞 Cần hỗ trợ?

Nếu gặp vấn đề:
1. Kiểm tra Render Logs
2. Xem lại các bước trong hướng dẫn này
3. Kiểm tra `DEBUG_GUIDE.md` cho các lỗi thường gặp
4. Xem `DEPLOYMENT_GUIDE.md` cho hướng dẫn tổng quan
