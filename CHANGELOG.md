# Changelog - Security & Quality Update

**Date:** 2025-01-06  
**Version:** 2.0.0  
**Type:** Security Fixes + Code Quality

---

## 🔒 Security Fixes (CRITICAL)

### Authentication & Authorization
- ✅ **Bearer Token Authentication** cho POST `/api/data`
  - Token từ environment variable `ADMIN_TOKEN`
  - Header: `Authorization: Bearer <token>`
  - Returns 401 nếu thiếu/sai token
  - Admin interface có token input field

### Input Validation
- ✅ **Schema Validation** với strict checking:
  - Validate structure: `{models: [...]}`
  - Limits: MAX_MODELS=100, MAX_ITEMS_PER_MODEL=500
  - String limits: MAX_NAME_LENGTH=200, MAX_STRING_LENGTH=1000
  - Validate world coordinates (array of 3 numbers)
  - Validate camera position/target (array of 3 numbers)

### File Operations
- ✅ **Atomic File Writes**
  - Write to temp file trước
  - Atomic replace với `os.replace()`
  - Tránh race conditions và data corruption

### Security Headers
- ✅ **HTTP Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy` với whitelist cho Sketchfab và Tailwind CDN

### Request Limits
- ✅ **Request Size Limit**: 1MB (MAX_CONTENT_LENGTH)

### Error Handling
- ✅ **Production Error Handling**:
  - Không leak stack traces trong production
  - Generic error messages cho users
  - Detailed errors chỉ trong development mode

---

## 🐛 Bug Fixes

### Code Quality
- ✅ **Resolved Merge Conflicts** trong `templates/guest.html`
  - Loại bỏ 45 merge conflict markers
  - Chọn version có floating labels với leader lines
  - Giữ logic multi-model support

### XSS Protection
- ✅ **HTML Escaping**:
  - Function `escapeHtml()` để sanitize
  - Tất cả user input được escape trước khi dùng trong innerHTML
  - Sử dụng `textContent` cho text-only content

### External Links
- ✅ **Security Attributes**:
  - Thêm `rel="noopener noreferrer"` cho external links

---

## 🚀 Deployment Improvements

### Production Server
- ✅ **Gunicorn Configuration**:
  - `Procfile` với optimized settings
  - Workers: 2, Threads: 4, Timeout: 60s
  - Bind to `0.0.0.0:$PORT` (Render requirement)

### Environment Variables
- ✅ **Environment Support**:
  - `ADMIN_TOKEN`: Required cho authentication
  - `ENV`: `development` hoặc `production`
  - `PORT`: Auto-set bởi Render

### Documentation
- ✅ **Deployment Guides**:
  - `README.md`: Quick start và usage
  - `DEPLOYMENT_GUIDE.md`: Step-by-step Render deployment
  - `SECURITY_REVIEW.md`: Security audit report
  - `SECURITY.md`: Vulnerability reporting policy

---

## 🛡️ Guardrails

### Git Configuration
- ✅ **`.gitignore`**:
  - Ignore secrets, cache, data files
  - Ignore `__pycache__`, `.env`, `*.tmp`

### CI/CD
- ✅ **GitHub Actions** (`.github/workflows/ci.yml`):
  - Lint với ruff
  - Run smoke tests với pytest
  - Security scan với pip-audit
  - Basic secret detection

### Testing
- ✅ **Smoke Tests** (`tests/test_smoke.py`):
  - GET /api/data returns 200
  - POST without token → 401
  - POST with invalid token → 401
  - POST with valid token + valid payload → 200
  - POST with invalid schema → 400
  - Security headers present
  - Admin và guest routes accessible

---

## 📦 Dependencies

### Updated
- `Flask==3.0.0` (pinned version)
- `gunicorn==21.2.0` (added for production)

### Removed
- Duplicate entries trong `requirements.txt`

---

## ⚠️ Breaking Changes

### API Changes
- **POST `/api/data`** bây giờ **REQUIRES** Bearer token
  - Old behavior: Anyone could POST
  - New behavior: Must include `Authorization: Bearer <token>` header
  - Impact: Admin interface cần nhập token

### Data Format
- **Format mới**: `{models: [...]}` thay vì `{modelUid: "", items: []}`
  - Backward compatible: Code tự động convert format cũ
  - Impact: None (automatic migration)

---

## 🔄 Migration Guide

### For Existing Deployments:

1. **Set Environment Variable:**
   ```bash
   export ADMIN_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

2. **Update Render Environment:**
   - Add `ADMIN_TOKEN` với generated token
   - Set `ENV=production`

3. **Update Admin Interface:**
   - Nhập token vào field "Admin Token"
   - Token được lưu trong localStorage

4. **Test:**
   - Verify GET `/api/data` works
   - Verify POST `/api/data` với token works
   - Verify POST without token returns 401

---

## 📊 Statistics

- **Files Modified:** 4
- **Files Created:** 10
- **Lines Changed:** ~500+
- **Security Issues Fixed:** 12
- **Merge Conflicts Resolved:** 45
- **Tests Added:** 9

---

## ✅ Verification Checklist

- [x] All merge conflicts resolved
- [x] Bearer token authentication working
- [x] Input validation implemented
- [x] Security headers present
- [x] XSS protection added
- [x] Atomic file writes working
- [x] Error handling improved
- [x] Tests passing
- [x] Documentation complete
- [x] Ready for production deployment
