# Render Deployment - Troubleshooting Guide

## 🔧 Common Issues and Solutions

---

## Issue 1: Build Script Permission Denied

### Error:
```
Permission denied: ./build.sh
```

### Solution:
Make the build script executable:

```bash
# On Windows (Git Bash)
git update-index --chmod=+x build.sh

# On Linux/Mac
chmod +x build.sh

# Commit and push
git add build.sh
git commit -m "Make build.sh executable"
git push origin main
```

---

## Issue 2: Module 'dj_database_url' Not Found

### Error:
```
ModuleNotFoundError: No module named 'dj_database_url'
```

### Solution:
This is already fixed in your `requirements.txt`. If you still see this error:

1. Verify `requirements.txt` contains:
   ```
   dj-database-url==2.1.0
   ```

2. Rebuild on Render:
   - Go to web service dashboard
   - Click "Manual Deploy"
   - Select "Clear build cache & deploy"

---

## Issue 3: Static Files Not Loading (404 Errors)

### Error:
CSS and JavaScript files return 404 errors

### Solution A: Verify WhiteNoise Configuration
Check `settings.py` has:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be here
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Solution B: Collect Static Files Manually
From Render Shell:
```bash
python manage.py collectstatic --noinput --clear
```

### Solution C: Check Static Files Settings
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

---

## Issue 4: Database Connection Error

### Error:
```
django.db.utils.OperationalError: could not connect to server
```

### Solution:
1. **Use Internal Database URL** (not External):
   - Go to PostgreSQL service
   - Copy "Internal Database URL"
   - Update `DATABASE_URL` in web service environment variables

2. **Verify DATABASE_URL Format**:
   ```
   postgresql://user:password@host:port/database
   ```

3. **Check Database Status**:
   - Go to PostgreSQL service
   - Verify status is "Available"

---

## Issue 5: 502 Bad Gateway

### Error:
Browser shows "502 Bad Gateway"

### Solution A: Check Logs
1. Go to web service dashboard
2. Click "Logs" tab
3. Look for Python errors

### Solution B: Verify Start Command
Should be:
```
gunicorn sjbit_elective.wsgi:application
```

### Solution C: Check Gunicorn Installation
From Render Shell:
```bash
pip list | grep gunicorn
```

Should show: `gunicorn 21.2.0`

---

## Issue 6: ALLOWED_HOSTS Error

### Error:
```
DisallowedHost at /
Invalid HTTP_HOST header: 'your-app.onrender.com'
```

### Solution:
Add your Render domain to environment variables:

```
ALLOWED_HOSTS = your-app-name.onrender.com
```

Or in `settings.py`, verify:
```python
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
```

---

## Issue 7: SECRET_KEY Error

### Error:
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty
```

### Solution:
Add SECRET_KEY to environment variables:

1. Generate a key: https://djecrety.ir/
2. Add to Render:
   ```
   SECRET_KEY = your-generated-50-character-key
   ```

---

## Issue 8: Migration Errors

### Error:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

### Solution A: Fresh Migrations
From Render Shell:
```bash
python manage.py migrate --run-syncdb
```

### Solution B: Reset Database (CAUTION: Deletes all data)
```bash
# Drop all tables
python manage.py flush --no-input

# Run migrations
python manage.py migrate
```

---

## Issue 9: Import CSV Command Not Found

### Error:
```
Unknown command: 'import_csv'
```

### Solution:
The management command exists in your code. Verify:

1. File exists: `electives/management/commands/import_csv.py`
2. `__init__.py` files exist in:
   - `electives/management/__init__.py`
   - `electives/management/commands/__init__.py`

If missing, create them:
```bash
touch electives/management/__init__.py
touch electives/management/commands/__init__.py
```

---

## Issue 10: Cold Start Delay

### Symptom:
First request takes 30-60 seconds

### Explanation:
This is normal on Render's free tier. The service "spins down" after 15 minutes of inactivity.

### Solutions:
1. **Upgrade to Starter Plan** ($7/month) - No spin down
2. **Use a Ping Service** - Keep service awake
   - UptimeRobot: https://uptimerobot.com/
   - Ping every 14 minutes
3. **Accept the delay** - It's a free tier limitation

---

## Issue 11: Database Expires After 90 Days

### Symptom:
Free PostgreSQL database stops working after 90 days

### Solution:
1. **Upgrade to Paid Plan** ($7/month) - No expiration
2. **Backup and Recreate**:
   ```bash
   # Backup data
   python manage.py dumpdata > backup.json
   
   # Create new database
   # Restore data
   python manage.py loaddata backup.json
   ```

---

## Issue 12: Environment Variables Not Loading

### Error:
Settings using default values instead of environment variables

### Solution:
1. **Verify Variables Are Set**:
   - Go to web service dashboard
   - Click "Environment" tab
   - Check all variables are present

2. **Restart Service**:
   - Click "Manual Deploy"
   - Select "Deploy latest commit"

3. **Check Variable Names**:
   - Must match exactly (case-sensitive)
   - No extra spaces

---

## Issue 13: Build Takes Too Long

### Symptom:
Build process exceeds 15 minutes and fails

### Solution:
1. **Check Dependencies**:
   - Remove unused packages from `requirements.txt`
   - Use specific versions (not `latest`)

2. **Clear Build Cache**:
   - Go to web service dashboard
   - Click "Manual Deploy"
   - Select "Clear build cache & deploy"

---

## Issue 14: Memory Limit Exceeded

### Error:
```
Process killed (out of memory)
```

### Solution:
1. **Optimize Code**:
   - Reduce memory usage in views
   - Use pagination for large queries
   - Optimize image processing

2. **Upgrade Plan**:
   - Free: 512 MB RAM
   - Starter: 1 GB RAM
   - Standard: 2 GB RAM

---

## Issue 15: CSRF Verification Failed

### Error:
```
CSRF verification failed. Request aborted.
```

### Solution:
Add to `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://your-app-name.onrender.com',
]
```

---

## 🔍 Debugging Steps

### Step 1: Check Logs
```
1. Go to web service dashboard
2. Click "Logs" tab
3. Look for errors (red text)
4. Note the error message
```

### Step 2: Check Environment Variables
```
1. Click "Environment" tab
2. Verify all variables are set
3. Check for typos
```

### Step 3: Check Build Logs
```
1. Click "Events" tab
2. Find latest deploy
3. Click "View build logs"
4. Look for errors
```

### Step 4: Test Locally
```bash
# Set environment variables
export DEBUG=False
export DATABASE_URL=postgresql://...

# Test with gunicorn
gunicorn sjbit_elective.wsgi:application

# Visit http://localhost:8000
```

### Step 5: Use Render Shell
```
1. Go to web service dashboard
2. Click "Shell" tab
3. Run diagnostic commands:
   - python manage.py check
   - python manage.py showmigrations
   - python manage.py collectstatic --dry-run
```

---

## 🆘 Getting Help

### Render Support:
- **Documentation**: https://render.com/docs
- **Community Forum**: https://community.render.com/
- **Status Page**: https://status.render.com/
- **Support Email**: support@render.com

### Django Resources:
- **Documentation**: https://docs.djangoproject.com/
- **Forum**: https://forum.djangoproject.com/
- **Stack Overflow**: Tag with `django` and `render`

---

## 📋 Diagnostic Commands

Run these in Render Shell to diagnose issues:

```bash
# Check Django configuration
python manage.py check

# Check database connection
python manage.py dbshell

# List migrations
python manage.py showmigrations

# Test static files
python manage.py collectstatic --dry-run

# Check installed packages
pip list

# Check Python version
python --version

# Check environment variables
env | grep DATABASE_URL
env | grep SECRET_KEY
env | grep DEBUG

# Test import
python -c "import django; print(django.get_version())"
```

---

## ✅ Health Check Checklist

Use this to verify your deployment:

- [ ] Build completes without errors
- [ ] Service status is "Live" (green)
- [ ] Homepage loads (no 502 error)
- [ ] Static files load (CSS, JS)
- [ ] Admin panel accessible
- [ ] Login works
- [ ] Database queries work
- [ ] No errors in logs
- [ ] HTTPS works (automatic)
- [ ] Environment variables set

---

## 🔐 Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY is unique and secure
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF_TRUSTED_ORIGINS set
- [ ] Database password is strong
- [ ] Admin password is strong
- [ ] No sensitive data in Git
- [ ] HTTPS enforced (automatic)

---

## 📊 Performance Tips

### 1. Enable Caching
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
```

### 2. Optimize Database Queries
```python
# Use select_related and prefetch_related
students = Student.objects.select_related('department').all()
```

### 3. Compress Static Files
WhiteNoise automatically compresses files (already configured)

### 4. Use CDN for Media Files
Consider using AWS S3 or Cloudinary for uploaded files

---

## 🎯 Quick Fixes

### Fix 1: Rebuild Everything
```bash
# From Render dashboard
1. Click "Manual Deploy"
2. Select "Clear build cache & deploy"
3. Wait for rebuild
```

### Fix 2: Reset Database
```bash
# From Render Shell (CAUTION: Deletes data)
python manage.py flush --no-input
python manage.py migrate
python manage.py createsuperuser
```

### Fix 3: Restart Service
```bash
# From Render dashboard
1. Click "Manual Deploy"
2. Select "Deploy latest commit"
```

---

## 📞 Still Having Issues?

If you're still stuck:

1. **Check Render Status**: https://status.render.com/
2. **Search Community**: https://community.render.com/
3. **Review Logs**: Look for specific error messages
4. **Test Locally**: Reproduce the issue on your machine
5. **Contact Support**: support@render.com

---

**Most issues can be resolved by checking logs and environment variables!** 🔍
