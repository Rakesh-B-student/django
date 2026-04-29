# Render Deployment - Quick Fix Guide

## 🔧 Most Common Issues and Immediate Fixes

---

## Issue 1: Build Script Permission Error

### Error Message:
```
/bin/sh: ./build.sh: Permission denied
```

### Fix:
```bash
# Make build.sh executable
git update-index --chmod=+x build.sh
git add build.sh
git commit -m "Fix build.sh permissions"
git push origin main
```

---

## Issue 2: Python Version Error (CRITICAL - CURRENT ISSUE)

### Error Message:
```
Using Python version 3.14.3 (default)
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'pandas' when getting requirements to build wheel
```

### Root Cause:
Render is using Python 3.14.3 which is too new. Pandas 2.0.3 doesn't support Python 3.14 and requires setuptools (pkg_resources).

### Fix (ALREADY APPLIED):
✅ Created `.python-version` file with `3.11.0`
✅ Added `setuptools>=65.5.0` to requirements.txt

### Next Steps:
1. **Commit and push the changes:**
```bash
git add .python-version requirements.txt
git commit -m "Force Python 3.11.0 for Render compatibility"
git push origin main
```

2. **In Render Dashboard:**
   - Go to your web service
   - Click "Manual Deploy"
   - Select **"Clear build cache & deploy"** (IMPORTANT!)
   - Wait for deployment to complete

3. **Verify Python version in logs:**
   - Should see: `Using Python version 3.11.0`
   - Build should complete successfully

---

## Issue 3: Module Not Found Errors

### Error Message:
```
ModuleNotFoundError: No module named 'dj_database_url'
```

### Fix:
Clear build cache and redeploy:
1. Go to Render dashboard
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

---

## Issue 4: Static Files Error

### Error Message:
```
ValueError: Missing staticfiles manifest entry
```

### Fix Option 1 - Use Simpler Storage:
Update `settings.py`:
```python
# Change from:
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# To:
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

### Fix Option 2 - Disable Compression:
```python
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
```

---

## Issue 5: Database URL Not Set

### Error Message:
```
django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured
```

### Fix:
Make sure DATABASE_URL is set in Render environment variables.

Update `settings.py` to handle missing DATABASE_URL:
```python
# Database
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## Issue 6: Gunicorn Not Starting

### Error Message:
```
Failed to find application object 'application' in 'sjbit_elective.wsgi'
```

### Fix:
Verify start command is exactly:
```
gunicorn sjbit_elective.wsgi:application
```

Check `wsgi.py` exists at `sjbit_elective/wsgi.py`

---

## Issue 7: ALLOWED_HOSTS Error

### Error Message:
```
DisallowedHost at /
```

### Fix:
Add to Render environment variables:
```
RENDER_EXTERNAL_HOSTNAME = your-app-name.onrender.com
```

Or update `settings.py`:
```python
ALLOWED_HOSTS = ['*']  # Temporary for testing
```

---

## 🚀 Complete Fresh Start Fix

If nothing works, try this complete reset:

### Step 1: Update settings.py
```python
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']  # Will restrict later

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'electives',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

### Step 2: Simplify build.sh
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### Step 3: Commit and Push
```bash
git add .
git commit -m "Fix Render deployment"
git push origin main
```

### Step 4: Redeploy on Render
1. Go to dashboard
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

---

## 📋 Environment Variables Checklist

Make sure these are set in Render:

```
✓ PYTHON_VERSION = 3.11.0
✓ DEBUG = False
✓ SECRET_KEY = [your-secret-key]
✓ DATABASE_URL = [postgresql://...]
✓ ALLOWED_HOSTS = your-app-name.onrender.com
```

---

## 🔍 Debug Commands

Run these in Render Shell to diagnose:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check Django
python -c "import django; print(django.get_version())"

# Check database connection
python manage.py check --database default

# Test collectstatic
python manage.py collectstatic --dry-run --no-input

# Check migrations
python manage.py showmigrations
```

---

## 📞 Share Error Details

To get specific help, share:

1. **Full error message** from Render logs
2. **Which step failed** (build, start, runtime)
3. **Environment variables** you set
4. **Build command** you're using
5. **Start command** you're using

---

## ⚡ Quick Test Locally

Before deploying, test locally:

```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
set DEBUG=False
set SECRET_KEY=test-key-12345

# Test collectstatic
python manage.py collectstatic --no-input

# Test with gunicorn
gunicorn sjbit_elective.wsgi:application

# Visit http://localhost:8000
```

If it works locally, it should work on Render!

---

## 🆘 Still Failing?

Share the error message and I'll help you fix it immediately!

Common error locations:
- Build logs (during deployment)
- Application logs (after deployment)
- Browser console (frontend errors)
