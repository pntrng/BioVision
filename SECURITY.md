# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

Nếu bạn phát hiện lỗ hổng bảo mật, vui lòng:

1. **KHÔNG** tạo public issue trên GitHub
2. Gửi email đến maintainer với thông tin chi tiết
3. Bao gồm:
   - Mô tả lỗ hổng
   - Các bước để reproduce
   - Impact assessment
   - Suggested fix (nếu có)

## Security Best Practices

### Token Management

- **Rotate ADMIN_TOKEN định kỳ** (khuyến nghị mỗi 3-6 tháng)
- Không commit token vào git
- Sử dụng strong random tokens (32+ ký tự)
- Lưu token trong environment variables, không hardcode

### Deployment

- Luôn set `ENV=production` trên production server
- Sử dụng HTTPS (Render cung cấp tự động)
- Enable persistent storage cho `data.json` hoặc migrate sang database
- Review logs định kỳ để phát hiện suspicious activity

### Code Review

- Tất cả changes phải qua code review
- Security-sensitive changes cần approval từ security reviewer
- Run security scans trước khi merge

## Known Security Measures

- ✅ Bearer token authentication cho write operations
- ✅ Input validation và schema checking
- ✅ Request size limits (1MB)
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Atomic file writes
- ✅ XSS protection (HTML escaping)
- ✅ Error handling không leak stack traces

## Changelog

- 2025-01-06: Initial security review và fixes
