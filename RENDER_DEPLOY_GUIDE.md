# Render Deployment - Step by Step Guide

## ✅ Fixed render.yaml

The `render.yaml` file has been updated to work with Render's requirements.

## 🚀 Deploy to Render (Step by Step)

### Step 1: Deploy Blueprint
1. Go to Render dashboard
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository: `saatyakkapoor/avi_k_proj`
4. Render will detect `render.yaml`
5. Click **"Apply"** to create services

### Step 2: Create PostgreSQL Database (Manual)
Render doesn't support PostgreSQL in YAML, so create it manually:

1. In Render dashboard, click **"+ New"**
2. Select **"PostgreSQL"**
3. Name it: `suryादrishti-db`
4. Choose **"Starter"** plan (free tier)
5. Click **"Create Database"**
6. **Copy the Internal Database URL** (you'll need this)

### Step 3: Set Database URL
1. Go to your **suryादrishti-backend** service
2. Click **"Environment"** tab
3. Find **DATABASE_URL** variable
4. **Paste the Internal Database URL** from PostgreSQL service
5. Also set it for **suryादrishti-celery** worker service
6. Click **"Save Changes"**

### Step 4: Deploy
1. Render will automatically redeploy with the database URL
2. Wait for deployment to complete (~5 minutes)
3. Your app will be live!

## 📋 What Render Creates Automatically

✅ **Web Service** (Backend API)
- Auto-detects Dockerfile
- Sets up Redis connection automatically
- Generates SECRET_KEY automatically

✅ **Redis Cache**
- Auto-creates from render.yaml
- Connection string auto-set

✅ **Celery Worker**
- Background task processor
- Uses same Docker image

⚠️ **PostgreSQL** (Manual Step Required)
- Must be created manually (Step 2 above)
- Then connect via DATABASE_URL (Step 3 above)

## 🔧 Environment Variables

### Auto-Set by Render:
- `REDIS_URL` - From Redis service ✅
- `SECRET_KEY` - Auto-generated ✅
- `DEBUG` - Set to "False" ✅
- `PORT` - Set to "8000" ✅

### Manual Setup Required:
- `DATABASE_URL` - From PostgreSQL service (Step 3) ⚠️

## ✅ Verify Deployment

After deployment:
```bash
# Health check
curl https://suryादrishti-backend.onrender.com/health

# Should return: {"status":"healthy","service":"suryादrishti"}
```

## 🗄️ Initialize Database

After first deployment, initialize the database:

1. Go to your backend service in Render
2. Click **"Shell"** tab
3. Run:
   ```bash
   python scripts/setup_database.py
   ```

Or use Render CLI:
```bash
render exec suryादrishti-backend -- python scripts/setup_database.py
```

## 🎯 Quick Summary

1. ✅ Deploy Blueprint (auto-creates web, redis, worker)
2. ⚠️ Create PostgreSQL manually
3. ⚠️ Set DATABASE_URL in both web and worker services
4. ✅ Deploy completes automatically
5. ✅ Initialize database via Shell

## 🆘 Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Make sure Dockerfile is correct
- Verify all dependencies in requirements.txt

**Database connection fails?**
- Make sure PostgreSQL is created
- Verify DATABASE_URL is set correctly
- Use Internal Database URL (not external)

**App not responding?**
- Check health endpoint: `/health`
- View logs in Render dashboard
- Make sure PORT is set to 8000

---

**Ready to deploy!** Follow the steps above. 🚀

