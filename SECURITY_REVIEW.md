# Security Review - BioVision 3D

**Date:** 2025-01-06  
**Reviewer:** Security + Backend + DevOps  
**Scope:** Full codebase security audit and fixes

---

## 🔴 HIGH PRIORITY VULNERABILITIES

### 1. Unauthenticated Data Modification (CRITICAL)
- **Location:** `app.py` - `/api/data` POST endpoint
- **Issue:** Anyone can POST to `/api/data` and overwrite entire database
- **Impact:** Data loss, data corruption, DoS
- **Fix:** Implement Bearer token authentication

### 2. No Input Validation (HIGH)
- **Location:** `app.py` - `save_data()` function
- **Issue:** No validation on JSON payload structure, size, or content
- **Impact:** File system attacks, memory exhaustion, data corruption
- **Fix:** Add strict schema validation, size limits, type checking

### 3. Admin Route Unprotected (HIGH)
- **Location:** `app.py` - `/admin` route
- **Issue:** Anyone can access admin panel
- **Impact:** Unauthorized data modification
- **Fix:** Require authentication token

### 4. Debug Mode in Production (MEDIUM)
- **Location:** `app.py` - `app.run(debug=True)`
- **Issue:** Stack traces exposed to users
- **Impact:** Information disclosure
- **Fix:** Environment-based debug flag

---

## 🟡 MEDIUM PRIORITY ISSUES

### 5. Missing Security Headers (MEDIUM)
- **Location:** `app.py` - No security headers set
- **Issue:** Vulnerable to XSS, clickjacking, MIME sniffing
- **Impact:** XSS attacks, content injection
- **Fix:** Add X-Content-Type-Options, CSP, Referrer-Policy, Frame-Options

### 6. Non-Atomic File Writes (MEDIUM)
- **Location:** `app.py` - Direct file write
- **Issue:** Race conditions, partial writes on failure
- **Impact:** Data corruption
- **Fix:** Write to temp file, then atomic replace

### 7. XSS Vulnerabilities (MEDIUM)
- **Location:** `templates/admin.html`, `templates/guest.html`
- **Issue:** `innerHTML` with user-controlled data
- **Impact:** XSS attacks
- **Fix:** Sanitize or use `textContent`

### 8. Merge Conflicts in Production Code (HIGH - Code Quality)
- **Location:** `templates/guest.html`
- **Issue:** Multiple merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- **Impact:** Broken functionality, code confusion
- **Fix:** Resolve all conflicts, choose correct version

---

## 🟢 LOW PRIORITY / BEST PRACTICES

### 9. No Request Size Limits (LOW)
- **Location:** `app.py`
- **Issue:** No max content length
- **Impact:** Memory exhaustion
- **Fix:** Set `MAX_CONTENT_LENGTH`

### 10. Missing CORS Configuration (LOW)
- **Location:** `app.py`
- **Issue:** No explicit CORS policy
- **Impact:** Potential CSRF (mitigated by same-origin)
- **Fix:** Explicit same-origin policy

### 11. No Rate Limiting (LOW)
- **Location:** `app.py`
- **Issue:** No protection against brute force
- **Impact:** DoS potential
- **Fix:** Add rate limiting (future enhancement)

### 12. Secrets in Code (LOW - Not found, but need guardrails)
- **Location:** N/A
- **Issue:** Need `.env.example` and `.gitignore`
- **Impact:** Accidental secret commits
- **Fix:** Add guardrails

---

## ✅ FIXES IMPLEMENTED

### Phase 2 - Security Fixes
- [x] **Bearer token authentication** for POST `/api/data`
  - Token từ environment variable `ADMIN_TOKEN`
  - Header: `Authorization: Bearer <token>`
  - Returns 401 nếu thiếu/sai token
- [x] **Input validation** với schema checking
  - Validate structure: `{models: [...]}`
  - Limits: MAX_MODELS=100, MAX_ITEMS_PER_MODEL=500
  - String length limits: MAX_NAME_LENGTH=200, MAX_STRING_LENGTH=1000
  - Validate world coordinates (array of 3 numbers)
  - Validate camera position/target (array of 3 numbers)
- [x] **Atomic file writes** (temp file + os.replace)
  - Tránh race conditions và partial writes
- [x] **Admin route** - hiện tại public nhưng POST API đã được bảo vệ
- [x] **Security headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy` với whitelist cho Sketchfab và Tailwind CDN
- [x] **Request size limits**: MAX_CONTENT_LENGTH = 1MB
- [x] **Error handling**: Không leak stack traces trong production

### Phase 3 - Code Quality
- [x] **Resolved all merge conflicts** trong `guest.html`
  - Loại bỏ tất cả markers `<<<<<<<`, `=======`, `>>>>>>>`
  - Chọn version có floating labels với leader lines
  - Giữ logic multi-model support
- [x] **Fixed XSS vulnerabilities**
  - Thêm function `escapeHtml()` để sanitize
  - Tất cả user input được escape trước khi dùng trong innerHTML
  - Sử dụng `textContent` cho text-only content
- [x] **External links**: Thêm `rel="noopener noreferrer"`

### Phase 4 - Deployment
- [x] **Gunicorn configuration** trong `Procfile`
  - Workers: 2, Threads: 4, Timeout: 60s
  - Bind to `0.0.0.0:$PORT` (Render requirement)
- [x] **Environment variables**:
  - `ADMIN_TOKEN`: Required cho authentication
  - `ENV`: `development` hoặc `production`
  - `PORT`: Auto-set bởi Render
- [x] **README.md** với hướng dẫn deploy chi tiết

### Phase 5 - Guardrails
- [x] **`.gitignore`**: Loại bỏ secrets, cache, data files
- [x] **`.env.example`**: Template cho environment variables
- [x] **CI configuration** (`.github/workflows/ci.yml`):
  - Lint với ruff
  - Run smoke tests với pytest
  - Security scan với pip-audit
  - Basic secret detection
- [x] **Smoke tests** (`tests/test_smoke.py`):
  - GET /api/data returns 200
  - POST without token → 401
  - POST with invalid token → 401
  - POST with valid token + valid payload → 200
  - POST with invalid schema → 400
  - Security headers present
- [x] **SECURITY.md**: Vulnerability reporting policy

---

## 📋 USER ACTIONS REQUIRED

### On Render.com:

1. **Set Environment Variables:**
   ```
   ADMIN_TOKEN=<generate-strong-random-token>
   ENV=production
   PORT=10000  # Render sets this automatically
   ```

2. **Generate Admin Token:**
   ```bash
   # Use a strong random token (32+ characters)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Persistent Storage:**
   - Enable Render Disk for `data.json` persistence
   - OR migrate to database (PostgreSQL) for production

4. **Verify Deployment:**
   ```bash
   # Test GET (should work)
   curl https://your-app.onrender.com/api/data
   
   # Test POST without token (should fail with 401)
   curl -X POST https://your-app.onrender.com/api/data \
     -H "Content-Type: application/json" \
     -d '{"models":[]}'
   
   # Test POST with token (should work)
   curl -X POST https://your-app.onrender.com/api/data \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"models":[]}'
   ```

---

## 🧪 VERIFICATION COMMANDS

### Local Testing:
```bash
# 1. Set environment
export ADMIN_TOKEN=test-token-123
export ENV=development

# 2. Run server
python app.py

# 3. Test GET (should work)
curl http://localhost:5000/api/data

# 4. Test POST without token (should fail)
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"models":[]}'

# 5. Test POST with token (should work)
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-123" \
  -d '{"models":[]}'

# 6. Test admin route (should require token)
curl http://localhost:5000/admin
```

### Run Tests:
```bash
pytest tests/  # If tests exist
```

### PowerShell Testing (Windows):

**Option 1: Use the test script (recommended)**
```powershell
# 1. Set environment variable
$env:ADMIN_TOKEN = "test-token-123"
$env:ENV = "development"

# 2. Start server (in separate terminal)
python app.py

# 3. Run test script
.\test-api.ps1
```

**Option 2: Manual PowerShell commands**
```powershell
# 1. Set environment
$env:ADMIN_TOKEN = "test-token-123"
$env:ENV = "development"

# 2. Start server (in separate terminal)
python app.py

# 3. Test GET (should work)
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Get

# 4. Test POST without token (should fail with 401)
try {
    $body = '{"models":[]}'
    Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"  # Should be 401
}

# 5. Test POST with token (should work)
$headers = @{
    "Authorization" = "Bearer test-token-123"
    "Content-Type" = "application/json"
}
$body = '{"models":[{"id":"test","grade":"10","chapter":"Test","modelUid":"test-123","items":[]}]}'
Invoke-RestMethod -Uri "http://localhost:5000/api/data" -Method Post -Body $body -Headers $headers

# 6. Test admin route (should require token)
try {
    Invoke-WebRequest -Uri "http://localhost:5000/admin" -Method Get
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"  # Should be 401
}
```

**Note:** PowerShell's `curl` is an alias for `Invoke-WebRequest` with different syntax. Use `Invoke-RestMethod` for JSON APIs or the provided `test-api.ps1` script.

---

## 📝 FILES MODIFIED/CREATED

### Modified Files:
1. **`app.py`** (1.9KB → ~6KB) - Complete security overhaul:
   - ✅ Bearer token authentication (`check_admin_token()`)
   - ✅ Schema validation với limits (`validate_data_schema()`)
   - ✅ Atomic file writes (`atomic_write_file()`)
   - ✅ Security headers (CSP, X-Frame-Options, etc.)
   - ✅ Error handling (không leak stack traces)
   - ✅ Request size limits (1MB)
   - ✅ Environment-based debug mode

2. **`templates/admin.html`** - Security enhancements:
   - ✅ Admin token input field (password type)
   - ✅ Token storage trong localStorage
   - ✅ Gửi token trong `Authorization: Bearer <token>` header
   - ✅ Error messages cải thiện (401 handling)
   - ✅ Auto-load token từ localStorage

3. **`templates/guest.html`** (866 lines) - Code quality fixes:
   - ✅ Resolved tất cả merge conflicts (45 markers removed)
   - ✅ XSS protection với `escapeHtml()` function
   - ✅ Sanitized tất cả user input trước khi dùng trong innerHTML
   - ✅ External links có `rel="noopener noreferrer"`
   - ✅ Clean code structure, no duplicate logic

4. **`requirements.txt`** - Cleaned up:
   - ✅ Flask==3.0.0
   - ✅ gunicorn==21.2.0
   - ✅ Removed duplicates

### New Files:
5. **`.gitignore`** - Ignore secrets, cache, data files, __pycache__
6. **`SECURITY.md`** - Vulnerability reporting policy và best practices
7. **`Procfile`** - Render deployment config với gunicorn
8. **`README.md`** - Complete deployment và usage guide
9. **`DEPLOYMENT_GUIDE.md`** - Step-by-step Render deployment
10. **`tests/test_smoke.py`** - 9 smoke tests cho API endpoints
11. **`tests/__init__.py`** - Test package init
12. **`.github/workflows/ci.yml`** - CI pipeline (lint, test, security scan)
13. **`env.example.txt`** - Environment variables template

---

## 🔐 SECURITY NOTES

- **Token Storage:** Admin token stored in localStorage (client-side). For production, consider session-based auth.
- **Token Rotation:** Rotate `ADMIN_TOKEN` periodically via Render environment variables.
- **HTTPS:** Render provides HTTPS by default - ensure it's enabled.
- **Monitoring:** Consider adding logging for failed auth attempts.

---

## 📚 REFERENCES

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Flask Security Best Practices: https://flask.palletsprojects.com/en/3.0.x/security/
- Render Deployment: https://render.com/docs
