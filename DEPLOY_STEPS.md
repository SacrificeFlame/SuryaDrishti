# 🚀 DEPLOY TO RAILWAY - FOLLOW THESE STEPS

## Quick Deploy (5 minutes)

### 1. Open Railway
👉 **Go to**: https://railway.app

### 2. Sign Up / Login
- Click "Start a New Project"
- Sign up with GitHub (recommended - one click)

### 3. Deploy Your Repo
- Click **"New Project"**
- Select **"Deploy from GitHub repo"**
- Authorize Railway (if first time)
- Find and select: **`saatyakkapoor/avi_k_proj`**
- Railway will auto-detect your Dockerfile ✅

### 4. Add PostgreSQL Database
- In your project, click **"+ New"**
- Select **"Database"** → **"Add PostgreSQL"**
- Railway creates it automatically
- Note: Railway sets `DATABASE_URL` automatically

### 5. Add Redis
- Click **"+ New"** again
- Select **"Database"** → **"Add Redis"**
- Railway creates it automatically
- Note: Railway sets `REDIS_URL` automatically

### 6. Configure Environment Variables
- Click on your **backend service** (the main one)
- Go to **"Variables"** tab
- Add these variables:

```
SECRET_KEY=<click "Generate" or use: openssl rand -hex 32>
DEBUG=False
ALLOWED_ORIGINS=https://your-app-name.up.railway.app
```

**Important**: Railway automatically provides:
- `DATABASE_URL` from PostgreSQL (already set ✅)
- `REDIS_URL` from Redis (already set ✅)
- `PORT` (automatically set ✅)

### 7. Deploy!
- Railway will automatically start deploying
- Watch the build logs
- Wait ~3-5 minutes for first deployment

### 8. Get Your URL
- Once deployed, Railway shows your URL
- Format: `https://your-app-name.up.railway.app`
- Click the URL to open your app!

### 9. Initialize Database
After first deployment, initialize the database:

**Option A: Via Railway Dashboard**
1. Go to your backend service
2. Click "Deployments" tab
3. Click on latest deployment
4. Click "View Logs"
5. Or use "Run Command" to execute: `python scripts/setup_database.py`

**Option B: Via Railway CLI**
```bash
npm i -g @railway/cli
railway login
railway link
railway run python scripts/setup_database.py
```

### 10. Test Your Deployment
```bash
# Health check
curl https://your-app-name.up.railway.app/health

# API docs
open https://your-app-name.up.railway.app/docs
```

## ✅ Success!
Your app is now live! 🎉

## 🔧 Troubleshooting

**Build fails?**
- Check logs in Railway dashboard
- Make sure Dockerfile is correct
- Check that all dependencies are in requirements.txt

**Database connection fails?**
- Make sure PostgreSQL service is running
- Check that `DATABASE_URL` is set correctly
- Railway sets this automatically, but verify in Variables tab

**App not responding?**
- Check health endpoint: `/health`
- View logs in Railway dashboard
- Make sure PORT is set (Railway sets this automatically)

## 📚 More Help
- Railway Docs: https://docs.railway.app
- See `RAILWAY_DEPLOY.md` for detailed guide
- See `DEPLOYMENT.md` for other platforms

---

**Ready?** Go to https://railway.app and start deploying! 🚀

