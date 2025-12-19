# ⚡ Quick Deploy Guide

## Fastest Way: Render (5 minutes)

1. **Go to**: https://render.com → Sign up/Login
2. **New** → **Web Service**
3. **Connect GitHub** → Select `Wasikeonesmus/Smart_keja`
4. **Settings**:
   - Name: `smartkeja-test`
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn smartkeja.wsgi:application`
5. **Environment Variables**:
   ```
   DEBUG=True
   SECRET_KEY=<run: python generate_secret_key.py>
   ALLOWED_HOSTS=smartkeja-test.onrender.com
   ```
6. **Deploy** → Done! 🎉

Your app: `https://smartkeja-test.onrender.com`

---

## Alternative: Railway (3 minutes)

1. **Go to**: https://railway.app → Sign up
2. **New Project** → **Deploy from GitHub**
3. **Select**: `Wasikeonesmus/Smart_keja`
4. **Add Variables**:
   ```
   DEBUG=True
   SECRET_KEY=<generate one>
   ```
5. **Deploy** → Done! 🎉

---

## Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Run server
python manage.py runserver
```

Visit: http://localhost:8000

---

## Generate Secret Key

```bash
python generate_secret_key.py
```

---

## Need Help?

Check `DEPLOYMENT_GUIDE.md` for detailed instructions.

