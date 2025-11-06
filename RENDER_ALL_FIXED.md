# Render.yaml Fixed - All Issues Resolved! ✅

## What Was Fixed

1. ✅ **Redis IP Allow List**: Added `ipAllowList: []` (empty array allows internal access)
2. ✅ **Worker startCommand**: Removed (Docker runtime doesn't support it)
3. ✅ **SECRET_KEY Reference**: Changed from `fromService` to `sync: false` (must set manually)

## Solution Implemented

### Entrypoint Script Approach
Created `backend/docker-entrypoint.sh` that:
- Checks `CELERY_WORKER` environment variable
- Runs Celery worker if `CELERY_WORKER=true`
- Runs FastAPI server otherwise

### Updated Dockerfile
- Uses entrypoint script instead of hardcoded CMD
- Same Dockerfile works for both web and worker services

### Updated render.yaml
- Redis: Added `ipAllowList: []`
- Worker: Uses `CELERY_WORKER=true` env var instead of startCommand
- Worker SECRET_KEY: Changed to `sync: false` (set manually)

## 🚀 Deploy Steps

### Step 1: Deploy Blueprint
1. In Render, click "New" → "Blueprint"
2. Select your repo
3. Click "Apply"
4. Render will create web service and Redis

### Step 2: Create PostgreSQL (Manual)
1. Click "+ New" → "PostgreSQL"
2. Name: `suryादrishti-db`
3. Plan: Starter
4. Copy Internal Database URL

### Step 3: Set Environment Variables

**For suryादrishti-backend service:**
- `DATABASE_URL` = (PostgreSQL Internal URL)
- `SECRET_KEY` = (Auto-generated, copy this value)

**For suryादrishti-celery worker:**
- `DATABASE_URL` = (Same PostgreSQL URL)
- `SECRET_KEY` = (Same value as backend service)
- `CELERY_WORKER` = `true` (Already set ✅)

### Step 4: Deploy
Render will automatically redeploy with all configurations!

## ✅ Verify

After deployment:
```bash
curl https://suryादrishti-backend.onrender.com/health
```

## 📝 Important Notes

- **SECRET_KEY**: Must be set manually in both services (same value)
- **DATABASE_URL**: Must be set manually in both services
- **Worker**: Automatically runs Celery when `CELERY_WORKER=true` is set
- **Redis**: Configured with empty IP allow list for internal access

All fixes have been pushed to GitHub! 🎉

