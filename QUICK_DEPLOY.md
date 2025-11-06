# Quick Reference Card

## 🚀 Deploy to Cloud (Choose One)

### Option 1: Railway (Easiest)
1. Fork repo on GitHub
2. Go to railway.app → New Project → Deploy from GitHub
3. Select your fork
4. Add env vars: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `DEBUG=False`
5. Done! 🎉

### Option 2: Render
1. Fork repo on GitHub
2. Go to render.com → New → Blueprint
3. Connect GitHub repo
4. Render auto-detects `render.yaml`
5. Click Apply → Done! 🎉

### Option 3: Docker Compose (Any VPS)
```bash
docker-compose up -d
```

### Option 4: Other Platforms
See `DEPLOYMENT.md` for AWS, GCP, Azure, Kubernetes guides

## 📋 Required Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
```

## ✅ Verify Deployment

```bash
curl https://your-domain.com/health
# Should return: {"status":"healthy","service":"suryादrishti"}
```

## 📚 Documentation

- `SETUP_COMPLETE.md` - Complete setup guide
- `CLOUD_DEPLOY.md` - Quick cloud deployment
- `DEPLOYMENT.md` - Detailed deployment docs
- `README.md` - Full project docs

## 🔧 Local Setup

```bash
# Windows
.\setup.ps1

# Linux/Mac
./setup.sh

# Then initialize
python init_system.py
```

## 🐳 Docker Local

```bash
docker-compose up -d
# Access at http://localhost:8000
```

