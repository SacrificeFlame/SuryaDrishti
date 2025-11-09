# 🔍 Railway 404 Error Diagnosis & Fix Guide

## Problem
All API endpoints returning 404 errors:
- `/api/v1/microgrid/microgrid_001` - 404
- `/api/v1/microgrid/microgrid_001/status` - 404
- `/api/v1/sensors/microgrid_001/latest` - 404
- `/api/v1/forecast/microgrid/microgrid_001` - 404

## Root Cause Analysis

The 404 errors indicate that **`microgrid_001` doesn't exist in the database**. This happens because:
1. Database initialization on startup might be failing silently
2. Database connection might not be working on Railway
3. Database tables might not be created

## ✅ Solution Applied

### 1. Database Health Check Endpoint
Added `/api/v1/health/database` endpoint to diagnose the issue:

```bash
curl https://beauty-aryan-back-production.up.railway.app/api/v1/health/database
```

This endpoint will tell you:
- If the database is connected
- How many microgrids exist
- If `microgrid_001` exists
- Detailed error messages if something is wrong

### 2. Manual Database Initialization Endpoint
Added `/api/v1/init-database` endpoint (POST) to manually initialize the database:

```bash
curl -X POST https://beauty-aryan-back-production.up.railway.app/api/v1/init-database
```

This endpoint will:
- Create all database tables
- Create `microgrid_001` if it doesn't exist
- Create default devices
- Create system configuration
- Create initial sensor reading

### 3. Improved Error Logging
- Added detailed error logging in microgrid endpoints
- Shows available microgrids when 404 occurs
- Better traceback logging for debugging

## 🔧 Step-by-Step Fix

### Step 1: Check Database Health
1. Open: https://beauty-aryan-back-production.up.railway.app/api/v1/health/database
2. Check the response:
   - If `microgrid_001_exists: false` → Database is connected but microgrid doesn't exist
   - If `database: "error"` → Database connection is failing
   - If `status: "unhealthy"` → There's an error

### Step 2: Initialize Database (If Needed)
If `microgrid_001_exists: false`, call the initialization endpoint:

1. **Using curl**:
   ```bash
   curl -X POST https://beauty-aryan-back-production.up.railway.app/api/v1/init-database
   ```

2. **Using browser**:
   - Install a REST client extension (e.g., REST Client for VS Code, Postman)
   - Make a POST request to: `https://beauty-aryan-back-production.up.railway.app/api/v1/init-database`

3. **Expected response**:
   ```json
   {
     "status": "success",
     "message": "Database initialized and seeded",
     "microgrid_001_created": true,
     "devices_created": 5,
     "config_created": true
   }
   ```

### Step 3: Verify Fix
After initialization, test the endpoints:

1. **Test microgrid endpoint**:
   - https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001
   - Should return microgrid information (not 404)

2. **Test status endpoint**:
   - https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001/status
   - Should return system status (not 404)

3. **Test forecast endpoint**:
   - https://beauty-aryan-back-production.up.railway.app/api/v1/forecast/microgrid/microgrid_001?horizon_hours=24
   - Should return forecast data (not 404)

### Step 4: Check Backend Logs
1. Go to Railway Dashboard → Backend Service → **Logs**
2. Look for:
   - `✅ Database seeded with default data` (if initialization succeeded)
   - `Database already has microgrid microgrid_001` (if already exists)
   - Error messages if initialization failed

## 🐛 Troubleshooting

### Database Connection Errors

If the health check shows `database: "error"`:

1. **Check Railway PostgreSQL Service**:
   - Go to Railway Dashboard
   - Verify PostgreSQL service is running
   - Check that `DATABASE_URL` is set in backend environment variables

2. **Verify DATABASE_URL**:
   - Railway automatically provides `DATABASE_URL` for PostgreSQL
   - Check Backend Service → Variables → `DATABASE_URL` should exist
   - Format: `postgres://user:password@host:port/database`

3. **Check psycopg2 Installation**:
   - The backend uses `psycopg2-binary` for PostgreSQL
   - This is included in `requirements-production.txt`
   - Check backend logs for import errors

### Database Initialization Fails

If `/api/v1/init-database` returns an error:

1. **Check Backend Logs**:
   - Look for detailed error messages
   - Check for table creation errors
   - Check for constraint violations

2. **Check Database Permissions**:
   - Railway PostgreSQL should have full permissions
   - If using custom PostgreSQL, ensure user has CREATE TABLE permissions

3. **Manual Database Check**:
   - If you have database access, check if tables exist:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

### Routes Not Found (True 404)

If endpoints return 404 but routes are registered:

1. **Check Route Registration**:
   - Verify routes are registered in `backend/app/main.py`
   - Check backend logs for route registration errors

2. **Check Backend Deployment**:
   - Verify backend is running on Railway
   - Check backend logs for startup errors
   - Verify backend URL is correct

## 📊 Expected Results

After fixing:

✅ **Database Health Check**:
```json
{
  "status": "healthy",
  "database": "connected",
  "microgrid_count": 1,
  "microgrid_001_exists": true,
  "microgrid_001_details": {
    "id": "microgrid_001",
    "name": "Rajasthan Solar Grid 1",
    "latitude": 28.4595,
    "longitude": 77.0266,
    "capacity_kw": 50.0
  }
}
```

✅ **Microgrid Endpoint**:
- Returns microgrid information
- No 404 errors

✅ **Status Endpoint**:
- Returns system status
- No 404 errors

✅ **Forecast Endpoint**:
- Returns forecast data
- No 404 errors

✅ **Frontend**:
- No more "Using fallback data" errors
- All data loads correctly
- App works on all devices

## 🎯 Quick Fix Command

If you have access to Railway CLI or can make HTTP requests:

```bash
# Initialize database
curl -X POST https://beauty-aryan-back-production.up.railway.app/api/v1/init-database

# Verify database health
curl https://beauty-aryan-back-production.up.railway.app/api/v1/health/database

# Test microgrid endpoint
curl https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001
```

## 📝 Summary

The backend now has:
1. ✅ Automatic database initialization on startup
2. ✅ Database health check endpoint (`/api/v1/health/database`)
3. ✅ Manual database initialization endpoint (`/api/v1/init-database`)
4. ✅ Better error logging and diagnostics

**Next Steps**:
1. Wait for Railway to redeploy the backend (2-3 minutes)
2. Check database health: https://beauty-aryan-back-production.up.railway.app/api/v1/health/database
3. If `microgrid_001_exists: false`, call `/api/v1/init-database` to initialize
4. Test the endpoints again
5. Verify frontend works correctly

The backend will automatically initialize the database on startup, but if that fails, you can manually initialize it using the `/api/v1/init-database` endpoint.

