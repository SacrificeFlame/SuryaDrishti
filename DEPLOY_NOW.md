# Quick Deploy Script - Railway

This script helps you deploy to Railway quickly.

## Prerequisites
- GitHub account
- Railway account (free tier available)

## Steps

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `saatyakkapoor/avi_k_proj`
5. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will create it automatically
6. **Add Redis**:
   - Click "+ New" → "Database" → "Add Redis"
   - Railway will create it automatically
7. **Set Environment Variables**:
   - Go to your backend service → Variables
   - Add:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     SECRET_KEY=<random-string-32-chars>
     DEBUG=False
     ```
8. **Deploy**: Railway will auto-deploy
9. **Get URL**: Railway will provide your app URL
10. **Initialize DB**: 
    - Go to service → Deployments → View Logs
    - Or use Railway CLI: `railway run python scripts/setup_database.py`

## Your App Will Be Live At:
`https://your-app-name.up.railway.app`

## Test It:
```bash
curl https://your-app-name.up.railway.app/health
```

## Need Help?
- Railway Docs: https://docs.railway.app
- Check logs in Railway dashboard
- See RAILWAY_DEPLOY.md for detailed guide

