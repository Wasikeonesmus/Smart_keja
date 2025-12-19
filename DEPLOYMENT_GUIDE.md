# SmartKeja Testing Deployment Guide

This guide will help you deploy SmartKeja for testing purposes (not production).

## 🚀 Quick Start (Choose One)

### Option 1: Render (Recommended - Easiest, Free Tier)

1. **Sign up at Render**: https://render.com
2. **Create New Web Service**:
   - Connect your GitHub repository: `Wasikeonesmus/Smart_keja`
   - Select branch: `main`
   - Name: `smartkeja-test`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn smartkeja.wsgi:application`

3. **Environment Variables** (in Render dashboard):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=smartkeja-test.onrender.com
   PYTHON_VERSION=3.11.0
   ```

4. **Deploy**: Click "Create Web Service"

Your app will be available at: `https://smartkeja-test.onrender.com`

---

### Option 2: Railway (Free Tier Available)

1. **Sign up at Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Select Repository**: `Wasikeonesmus/Smart_keja`
4. **Railway will auto-detect** Python and deploy
5. **Add Environment Variables**:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=*.railway.app
   ```

Your app will be available at: `https://your-app-name.railway.app`

---

### Option 3: PythonAnywhere (Free Tier Available)

1. **Sign up**: https://www.pythonanywhere.com
2. **Open Bash Console**
3. **Clone repository**:
   ```bash
   git clone https://github.com/Wasikeonesmus/Smart_keja.git
   cd Smart_keja
   ```
4. **Create virtual environment**:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Run migrations**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```
6. **Configure Web App**:
   - Go to Web tab
   - Source code: `/home/yourusername/Smart_keja`
   - WSGI file: Edit and point to `smartkeja.wsgi`
   - Static files: `/static/` → `/home/yourusername/Smart_keja/staticfiles/`

Your app will be available at: `https://yourusername.pythonanywhere.com`

---

## Pre-Deployment Checklist

### 1. Update Settings for Testing

The `smartkeja/settings.py` is already configured for testing with:
- `DEBUG = True`
- `ALLOWED_HOSTS = ['*']`

### 2. Generate Secret Key

Run this command to generate a secure secret key:
```bash
python generate_secret_key.py
```

Or use Python directly:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Update Requirements

Make sure `requirements.txt` includes:
```
Django>=4.2.0
Pillow>=10.0.0
gunicorn>=21.2.0
whitenoise>=6.6.0
```

### 4. Static Files

The deployment will run `collectstatic` automatically. Make sure `STATIC_ROOT` is set in settings.

---

## Post-Deployment Steps

1. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create Superuser** (if needed):
   ```bash
   python manage.py createsuperuser
   ```

3. **Test the Application**:
   - Visit your deployment URL
   - Test property listings
   - Test search functionality
   - Test booking flow

---

## Environment Variables for Testing

Set these in your deployment platform:

```
DEBUG=True
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=your-app-domain.com
DATABASE_URL=sqlite:///db.sqlite3 (or PostgreSQL for production)
```

---

## Troubleshooting

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` in settings
- Verify static files path in deployment config

### Database Issues
- Run migrations: `python manage.py migrate`
- Check database connection settings

### 500 Errors
- Check logs in deployment platform
- Verify `DEBUG=True` for testing
- Check `ALLOWED_HOSTS` includes your domain

---

## Notes for Testing Deployment

- ✅ `DEBUG=True` is enabled (shows error pages)
- ✅ `ALLOWED_HOSTS=['*']` allows all hosts
- ✅ SQLite database (simple, no setup needed)
- ⚠️ Not suitable for production (use PostgreSQL, set DEBUG=False)

---

## Quick Deploy Commands

### Render
```bash
# Already configured via render.yaml
# Just connect GitHub repo in Render dashboard
```

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

### Local Testing with ngrok (Quick Test)
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Your local server will be accessible via ngrok URL
```

---

## Support

For issues, check:
- Deployment platform logs
- Django error logs
- Static files configuration
- Database migrations

