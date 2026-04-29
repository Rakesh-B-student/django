# Render Deployment Guide - SJBIT Elective System

## 📋 Complete Guide to Deploy on Render.com

This guide will help you deploy your Django application to Render.com with PostgreSQL database.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
git remote add origin https://github.com/yourusername/sjbit-elective-system.git
git push -u origin main
```

### Step 2: Create Render Account
1. Go to https://render.com/
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `sjbit-elective-db`
3. Database: `sjbit_elective_db`
4. User: `sjbit_user`
5. Region: Choose closest to you
6. Plan: **Free**
7. Click "Create Database"
8. **Save the Internal Database URL** (you'll need it)

### Step 4: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `sjbit-elective-system`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn sjbit_elective.wsgi:application`
   - **Plan**: **Free**

### Step 5: Add Environment Variables
In the web service settings, add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `DEBUG` | `False` |
| `SECRET_KEY` | (Generate random string) |
| `DATABASE_URL` | (Paste Internal Database URL from Step 3) |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |

Click "Create Web Service"

---

## 📁 Files Created for Deployment

### 1. `build.sh` - Build Script
Automatically runs during deployment:
- Installs dependencies
- Collects static files
- Runs database migrations

### 2. `requirements.txt` - Updated
Added production dependencies:
- `gunicorn` - Production server
- `psycopg2-binary` - PostgreSQL adapter
- `whitenoise` - Static file serving
- `dj-database-url` - Database URL parser

### 3. `settings.py` - Updated
Configured for production:
- PostgreSQL database support
- WhiteNoise for static files
- Security settings
- Environment variables

### 4. `render.yaml` - Configuration (Optional)
Blueprint for automated deployment

---

## 🔧 Detailed Setup Instructions

### Prerequisites:
- ✅ GitHub account
- ✅ Render.com account
- ✅ Project pushed to GitHub

---

## 📊 Step-by-Step Deployment

### Part 1: Prepare Your Code

#### 1.1 Verify Files
Make sure these files exist:
- ✅ `build.sh`
- ✅ `requirements.txt` (updated)
- ✅ `sjbit_elective/settings.py` (updated)
- ✅ `.gitignore`

#### 1.2 Make build.sh Executable
```bash
chmod +x build.sh
```

#### 1.3 Test Locally (Optional)
```bash
# Install production dependencies
pip install -r requirements.txt

# Test build script
./build.sh

# Test with gunicorn
gunicorn sjbit_elective.wsgi:application
```

#### 1.4 Commit and Push
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

---

### Part 2: Create Render Account

#### 2.1 Sign Up
1. Go to https://render.com/
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render

#### 2.2 Verify Email
Check your email and verify your account

---

### Part 3: Create PostgreSQL Database

#### 3.1 Create Database
1. From Render Dashboard, click "New +"
2. Select "PostgreSQL"

#### 3.2 Configure Database
```
Name: sjbit-elective-db
Database: sjbit_elective_db
User: sjbit_user
Region: Singapore (or closest to you)
PostgreSQL Version: 15
Plan: Free
```

#### 3.3 Create Database
Click "Create Database"

#### 3.4 Save Connection Info
After creation, you'll see:
- **Internal Database URL**: `postgresql://sjbit_user:...@...`
- **External Database URL**: `postgresql://sjbit_user:...@...`

**Copy the Internal Database URL** - you'll need it for the web service!

---

### Part 4: Create Web Service

#### 4.1 Create Service
1. From Render Dashboard, click "New +"
2. Select "Web Service"

#### 4.2 Connect Repository
1. Click "Connect account" (if not connected)
2. Select your repository: `sjbit-elective-system`
3. Click "Connect"

#### 4.3 Configure Service
```
Name: sjbit-elective-system
Region: Singapore (same as database)
Branch: main
Runtime: Python 3
Build Command: ./build.sh
Start Command: gunicorn sjbit_elective.wsgi:application
Plan: Free
```

#### 4.4 Advanced Settings
Click "Advanced" and add environment variables:

**Environment Variables**:
```
PYTHON_VERSION = 3.11.0
DEBUG = False
SECRET_KEY = [Generate a random 50-character string]
DATABASE_URL = [Paste Internal Database URL from database]
ALLOWED_HOSTS = your-app-name.onrender.com
```

**To generate SECRET_KEY**:
```python
import secrets
print(secrets.token_urlsafe(50))
```

Or use: https://djecrety.ir/

#### 4.5 Create Web Service
Click "Create Web Service"

---

### Part 5: Wait for Deployment

#### 5.1 Monitor Build
You'll see the build logs in real-time:
```
==> Cloning from GitHub...
==> Running build command: ./build.sh
==> Installing dependencies...
==> Collecting static files...
==> Running migrations...
==> Build successful!
==> Starting service...
```

This takes 5-10 minutes for first deployment.

#### 5.2 Check Status
Wait for status to change to "Live" (green)

---

### Part 6: Post-Deployment Setup

#### 6.1 Create Superuser
1. Go to your web service dashboard
2. Click "Shell" tab
3. Run:
```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: (press Enter to skip)
- Password: `your-secure-password`

#### 6.2 Import Data (Optional)
If you want to import CSV data:

**Option A: Via Shell**
```bash
# Upload CSV files first, then:
python manage.py import_csv
```

**Option B: Via Django Admin**
1. Login to admin: `https://your-app.onrender.com/admin/`
2. Manually add departments, courses, students

---

## 🌐 Access Your Application

### URLs:
- **Homepage**: `https://your-app-name.onrender.com/`
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`
- **Login**: `https://your-app-name.onrender.com/login/`

### Default Credentials:
- **Admin**: Username you created in superuser step
- **Students**: Import from CSV or create manually

---

## 🔧 Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `PYTHON_VERSION` | Python version to use | `3.11.0` |
| `DEBUG` | Debug mode (False for production) | `False` |
| `SECRET_KEY` | Django secret key | `random-50-char-string` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `ALLOWED_HOSTS` | Allowed domains | `your-app.onrender.com` |

---

## 📊 Database Management

### View Database
1. Go to your PostgreSQL service
2. Click "Connect" → "External Connection"
3. Use any PostgreSQL client (pgAdmin, DBeaver, etc.)

### Backup Database
```bash
# From Render Shell
pg_dump $DATABASE_URL > backup.sql
```

### Restore Database
```bash
# From Render Shell
psql $DATABASE_URL < backup.sql
```

---

## 🔄 Updating Your Application

### Method 1: Git Push (Automatic)
```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Render automatically redeploys!
```

### Method 2: Manual Deploy
1. Go to web service dashboard
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

---

## 🐛 Troubleshooting

### Problem: Build Failed
**Check**:
- Build logs for errors
- `requirements.txt` is correct
- `build.sh` has correct permissions

**Solution**:
```bash
# Make build.sh executable
chmod +x build.sh
git add build.sh
git commit -m "Fix build.sh permissions"
git push
```

### Problem: Static Files Not Loading
**Check**:
- WhiteNoise is in MIDDLEWARE
- STATIC_ROOT is set
- collectstatic ran successfully

**Solution**:
```bash
# From Render Shell
python manage.py collectstatic --noinput
```

### Problem: Database Connection Error
**Check**:
- DATABASE_URL is correct
- Database is running
- Internal URL is used (not External)

**Solution**:
1. Go to PostgreSQL service
2. Copy Internal Database URL
3. Update DATABASE_URL in web service

### Problem: 502 Bad Gateway
**Check**:
- Start command is correct
- Gunicorn is installed
- Application starts without errors

**Solution**:
Check logs for errors:
```
==> Logs tab in Render dashboard
```

### Problem: ALLOWED_HOSTS Error
**Solution**:
Add your Render domain to ALLOWED_HOSTS:
```
ALLOWED_HOSTS = your-app-name.onrender.com
```

---

## 💰 Render Free Tier Limits

### Web Service (Free):
- ✅ 750 hours/month
- ✅ Automatic HTTPS
- ✅ Custom domains
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Cold start: 30-60 seconds

### PostgreSQL (Free):
- ✅ 1 GB storage
- ✅ Automatic backups (7 days)
- ⚠️ Expires after 90 days
- ⚠️ Limited connections

### Upgrade Options:
- **Starter**: $7/month (no spin down)
- **Standard**: $25/month (more resources)

---

## 🔐 Security Best Practices

### 1. Environment Variables
- ✅ Never commit SECRET_KEY
- ✅ Use strong passwords
- ✅ Rotate keys regularly

### 2. Database
- ✅ Use Internal URL (not External)
- ✅ Regular backups
- ✅ Strong database password

### 3. Django Settings
- ✅ DEBUG = False in production
- ✅ ALLOWED_HOSTS configured
- ✅ HTTPS enforced

### 4. User Management
- ✅ Strong admin password
- ✅ Limit admin access
- ✅ Regular security updates

---

## 📈 Monitoring

### View Logs
1. Go to web service dashboard
2. Click "Logs" tab
3. View real-time logs

### Metrics
1. Click "Metrics" tab
2. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

### Alerts
Set up email alerts for:
- Service down
- High error rate
- Resource limits

---

## 🎯 Checklist

### Pre-Deployment:
- [ ] Code pushed to GitHub
- [ ] `build.sh` created and executable
- [ ] `requirements.txt` updated
- [ ] `settings.py` configured
- [ ] `.gitignore` excludes sensitive files

### Deployment:
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Web service created
- [ ] Environment variables set
- [ ] Build successful
- [ ] Service is "Live"

### Post-Deployment:
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Database connected
- [ ] Application working

---

## 🆘 Getting Help

### Render Support:
- Documentation: https://render.com/docs
- Community: https://community.render.com/
- Status: https://status.render.com/

### Django Resources:
- Documentation: https://docs.djangoproject.com/
- Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

## ✨ Success!

Your application is now live on Render! 🎉

**Your URL**: `https://your-app-name.onrender.com/`

Share it with your users and enjoy your deployed application!

---

## 📝 Quick Reference

### Useful Commands (Render Shell):
```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Import CSV data
python manage.py import_csv

# Check Django version
python manage.py version

# Open Django shell
python manage.py shell
```

### Git Commands:
```bash
# Update and redeploy
git add .
git commit -m "Update"
git push origin main
```

---

**Deployment Complete!** 🚀
