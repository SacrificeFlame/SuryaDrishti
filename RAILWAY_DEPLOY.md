# Railway Deployment - Step by Step Guide

## 🚀 Deploy to Railway (5 minutes)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)

### Step 2: Deploy from GitHub
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Select repository: `saatyakkapoor/avi_k_proj`
5. Railway will auto-detect the Dockerfile

### Step 3: Add Services
Railway will automatically detect you need:
- **PostgreSQL Database** (add from template)
- **Redis** (add from template)

### Step 4: Configure Environment Variables
Go to your service → Variables tab, add:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=<generate-random-string-here>
DEBUG=False
ALLOWED_ORIGINS=https://your-app-name.up.railway.app
```

### Step 5: Deploy
1. Railway will automatically deploy
2. Wait for build to complete (~5 minutes)
3. Your app will be live at: `https://your-app-name.up.railway.app`

### Step 6: Initialize Database
Once deployed, run initialization:
1. Go to your service → Deployments
2. Click "View Logs"
3. Or use Railway CLI to run:
   ```bash
   railway run python scripts/setup_database.py
   ```

## ✅ Verify Deployment

Visit: `https://your-app-name.up.railway.app/health`

Should return: `{"status":"healthy","service":"suryादrishti"}`

## 🔧 Alternative: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Set variables
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
```

