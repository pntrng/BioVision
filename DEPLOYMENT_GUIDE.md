# Deployment Guide - BioVision 3D

## 🚀 Render.com Deployment

### Step 1: Prepare Repository

1. **Commit all changes:**
```bash
git add .
git commit -m "Security fixes and deployment config"
git push origin main
```

2. **Verify files:**
   - ✅ `Procfile` exists
   - ✅ `requirements.txt` has gunicorn
   - ✅ `app.py` uses environment variables

### Step 2: Create Render Service

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `biovision-3d` (or your choice)
   - **Region:** Singapore (or closest to users)
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`

### Step 3: Set Environment Variables

In Render dashboard → Environment:

```
ADMIN_TOKEN=<generate-strong-token>
ENV=production
```

**Generate token:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
Kx9mP2vQ7wR4tY8uI3oP6aS1dF5gH0jK2lM9nB4vC7xZ
```

Copy this to `ADMIN_TOKEN` in Render.

### Step 4: Persistent Storage (IMPORTANT)

**Option A: Render Disk (Recommended for MVP)**
1. In Render dashboard → Disks
2. Create new disk (1GB is enough)
3. Mount path: `/opt/render/project/src`
4. This persists `data.json` across redeploys

**Option B: Database (Recommended for Production)**
- Use Render PostgreSQL
- Update `app.py` to use database instead of JSON file
- More reliable, supports concurrent access

### Step 5: Deploy & Verify

1. **Deploy:**
   - Render auto-deploys on git push
   - Or click "Manual Deploy" in dashboard

2. **Check logs:**
   - Should see: "Booting worker with gunicorn"
   - No errors about missing ADMIN_TOKEN

3. **Test endpoints:**
```bash
# Replace YOUR_APP_URL with your Render URL
export APP_URL="https://biovision-3d.onrender.com"
export TOKEN="your-admin-token"

# Test GET (should work)
curl $APP_URL/api/data

# Test POST without token (should fail with 401)
curl -X POST $APP_URL/api/data \
  -H "Content-Type: application/json" \
  -d '{"models":[]}'

# Test POST with token (should work)
curl -X POST $APP_URL/api/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"models":[]}'
```

### Step 6: Access Application

- **Student Interface:** `https://your-app.onrender.com/`
- **Admin Interface:** `https://your-app.onrender.com/admin`

**First time admin access:**
1. Go to `/admin`
2. Enter Admin Token (from Render environment variable)
3. Token is saved in localStorage for future use

---

## 🔧 Troubleshooting

### Issue: "Failed to fetch" error

**Cause:** Server not running or wrong URL

**Fix:**
1. Check Render logs for errors
2. Verify service is "Live" (not "Suspended")
3. Check environment variables are set

### Issue: "401 Unauthorized" when saving

**Cause:** Wrong or missing ADMIN_TOKEN

**Fix:**
1. Verify `ADMIN_TOKEN` in Render environment variables
2. Check token in admin.html matches exactly
3. Token is case-sensitive

### Issue: Data lost after redeploy

**Cause:** No persistent storage

**Fix:**
1. Enable Render Disk (see Step 4)
2. OR migrate to PostgreSQL database

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Cause:** Dependencies not installed

**Fix:**
1. Check `requirements.txt` exists
2. Verify build command: `pip install -r requirements.txt`
3. Check build logs in Render

---

## 📊 Monitoring

### Render Dashboard:
- **Metrics:** CPU, Memory, Response time
- **Logs:** Real-time application logs
- **Events:** Deploy history, errors

### Health Checks:
- GET `/api/data` should return 200
- Response time < 1s

---

## 🔄 Updates & Maintenance

### Update Code:
```bash
git push origin main
# Render auto-deploys
```

### Rotate Token:
1. Generate new token
2. Update `ADMIN_TOKEN` in Render
3. Update token in admin.html (users need to re-enter)

### Backup Data:
- If using Render Disk: Download `data.json` periodically
- If using PostgreSQL: Use Render backup feature

---

## ✅ Pre-Deployment Checklist

- [ ] All code committed và pushed
- [ ] `ADMIN_TOKEN` generated và set trong Render
- [ ] `ENV=production` set trong Render
- [ ] Persistent storage configured (Disk hoặc DB)
- [ ] Test endpoints với curl
- [ ] Verify admin interface works
- [ ] Verify guest interface works
- [ ] Check security headers present
- [ ] Review Render logs for errors

---

## 📞 Support

Nếu gặp vấn đề:
1. Check Render logs
2. Review `SECURITY_REVIEW.md` for troubleshooting
3. Verify environment variables
4. Test locally với cùng config
