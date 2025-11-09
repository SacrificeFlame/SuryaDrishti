# 🔧 Railway Database 404 Fix

## Problem
Getting 404 errors for all API endpoints:
- `/api/v1/microgrid/microgrid_001` - 404
- `/api/v1/microgrid/microgrid_001/status` - 404
- `/api/v1/sensors/microgrid_001/latest` - 404

## Root Cause
The database on Railway doesn't have `microgrid_001` or the database tables don't exist.

## ✅ Solution Applied

The backend has been updated to **automatically initialize the database** on startup:

1. **Auto-creates database tables** if they don't exist
2. **Auto-seeds `microgrid_001`** if it doesn't exist
3. **Auto-creates default devices** and system configuration
4. **Handles both SQLite (local) and PostgreSQL (Railway)**

## What Happens Now

When the backend starts on Railway:
1. Database tables are created automatically
2. `microgrid_001` is created if it doesn't exist
3. Default devices are created (Essential Loads, Lighting, Irrigation Pump, etc.)
4. System configuration is created
5. Initial sensor reading is created

## Next Steps

### Option 1: Wait for Auto-Deployment (Recommended)
1. The changes have been pushed to GitHub
2. Railway will automatically redeploy the backend
3. On startup, the database will be initialized automatically
4. Wait 2-3 minutes for deployment to complete
5. Test the endpoints again

### Option 2: Manual Database Initialization (If Needed)

If you want to manually initialize the database:

1. **Connect to Railway backend**:
   - Go to Railway Dashboard → Backend Service
   - Go to **Settings** → **Connect**
   - Use Railway CLI or connect via SSH

2. **Run initialization script**:
   ```bash
   python init_db.py
   ```

3. **Or use Railway's one-click command**:
   - Go to Backend Service → **Deployments**
   - Click **"Redeploy"** to trigger a new deployment
   - The startup script will automatically initialize the database

## Verify It's Working

After the backend redeploys:

1. **Test backend health**:
   - Open: https://beauty-aryan-back-production.up.railway.app/health
   - Should return: `{"status": "healthy", "service": "suryादrishti"}`

2. **Test microgrid endpoint**:
   - Open: https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001
   - Should return microgrid information (not 404)

3. **Test status endpoint**:
   - Open: https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001/status
   - Should return system status (not 404)

4. **Check backend logs**:
   - Go to Railway Dashboard → Backend Service → **Logs**
   - Look for: `✅ Database seeded with default data` or `Database already has microgrid microgrid_001`

## Database Configuration

The backend now automatically:
- Detects Railway's PostgreSQL database (via `DATABASE_URL` environment variable)
- Converts `postgres://` to `postgresql://` for SQLAlchemy compatibility
- Falls back to SQLite for local development

## Troubleshooting

### Still getting 404 errors?

1. **Check backend logs**:
   - Railway Dashboard → Backend Service → Logs
   - Look for database initialization errors

2. **Verify DATABASE_URL is set**:
   - Railway automatically provides `DATABASE_URL` for PostgreSQL
   - Check Backend Service → Variables → `DATABASE_URL` should exist

3. **Check if backend is running**:
   - Test: https://beauty-aryan-back-production.up.railway.app/docs
   - Should show FastAPI documentation

4. **Manual database check**:
   - If you have database access, verify `microgrid_001` exists:
   ```sql
   SELECT * FROM microgrids WHERE id = 'microgrid_001';
   ```

### Database connection errors?

1. **Check Railway PostgreSQL**:
   - Go to Railway Dashboard
   - Verify PostgreSQL service is running
   - Check that `DATABASE_URL` is set in backend environment variables

2. **Verify psycopg2 is installed**:
   - The backend uses `psycopg2-binary` for PostgreSQL
   - This is included in `requirements-production.txt`

## Expected Result

After the backend redeploys with the updated code:
- ✅ All API endpoints return data (not 404)
- ✅ Frontend can fetch microgrid data
- ✅ Frontend can fetch sensor data
- ✅ Frontend can fetch forecast data
- ✅ No more "Using fallback data" errors

## Summary

The backend will now **automatically initialize the database** on every startup. This means:
- No manual database setup needed
- Works on first deployment
- Works after database resets
- Works on new Railway environments

Just wait for Railway to redeploy the backend, and the database will be initialized automatically!

