# Railway Backend URL Configuration Fix

## Problem

The frontend is trying to connect to `beauty-aryan-back-production.up.railway.app` which doesn't exist or isn't accessible. This causes `ERR_NAME_NOT_RESOLVED` errors.

## Root Cause

The `NEXT_PUBLIC_API_URL` environment variable in Railway is set to a backend URL that no longer exists or is incorrect. Since Next.js bakes `NEXT_PUBLIC_*` variables into the build at build time, the frontend will always use this URL until it's updated and rebuilt.

## Solution

### Step 1: Find Your Backend Service URL

1. Go to Railway Dashboard
2. Find your **backend** service
3. Go to **Settings** → **Networking** → **Public Networking**
4. Copy the Railway-provided domain (e.g., `your-backend-service.up.railway.app`)
5. Your backend API URL should be: `https://your-backend-service.up.railway.app/api/v1`

### Step 2: Update Frontend Environment Variable

1. Go to Railway Dashboard
2. Select your **frontend** service
3. Go to **Variables** tab
4. Find `NEXT_PUBLIC_API_URL` (or add it if it doesn't exist)
5. Set the value to your backend URL: `https://your-backend-service.up.railway.app/api/v1`
6. **Important:** Replace `your-backend-service.up.railway.app` with your actual backend Railway domain
7. Click **Save** or **Update**

### Step 3: Redeploy Frontend

After updating the environment variable:

1. Go to your frontend service in Railway
2. Click **Redeploy** or trigger a new deployment
3. Wait for the build to complete
4. The frontend will now use the correct backend URL

## Alternative: Use Custom Domain for Backend

If you have a custom domain for your backend:

1. Set up a custom domain for your backend service (e.g., `api.suryadrishti.in`)
2. Set `NEXT_PUBLIC_API_URL` to: `https://api.suryadrishti.in/api/v1`
3. Redeploy the frontend

## Verification

After updating and redeploying:

1. Visit your frontend: `https://www.suryadrishti.in`
2. Open browser console (F12)
3. Check for API URL logs: `[API URL] Using NEXT_PUBLIC_API_URL: ...`
4. Verify API requests are going to the correct backend URL
5. Check that API calls are successful (no `ERR_NAME_NOT_RESOLVED` errors)

## Troubleshooting

### Error: Still seeing `beauty-aryan-back-production.up.railway.app`

**Cause:** Frontend was built with the old backend URL and hasn't been redeployed.

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set correctly in Railway
2. Trigger a new deployment (push to GitHub or manually redeploy)
3. Wait for build to complete
4. Clear browser cache and try again

### Error: `ERR_NAME_NOT_RESOLVED` for new backend URL

**Cause:** Backend service doesn't exist or isn't accessible.

**Solution:**
1. Verify backend service is running in Railway
2. Check backend service logs for errors
3. Verify backend domain is correct
4. Test backend URL directly: `https://your-backend-service.up.railway.app/api/v1/health`

### Error: CORS errors

**Cause:** Backend CORS configuration doesn't allow requests from frontend domain.

**Solution:**
1. Go to backend service → **Variables**
2. Update `ALLOWED_ORIGINS` to include: `https://www.suryadrishti.in`
3. Update `FRONTEND_URLS` to include: `https://www.suryadrishti.in`
4. Redeploy backend service

## Code Changes

The code has been updated to:
1. Detect invalid backend URLs at runtime
2. Provide clear error messages in console
3. Attempt to use runtime URL detection (fallback)
4. Log API URL being used for debugging

## Important Notes

1. **NEXT_PUBLIC_API_URL must be set before build:** Next.js bakes this variable into the build, so it must be set in Railway environment variables before deploying.

2. **Redeploy after changing:** After updating `NEXT_PUBLIC_API_URL`, you must redeploy the frontend for changes to take effect.

3. **Backend must be accessible:** The backend URL must be publicly accessible and the backend service must be running.

4. **CORS must be configured:** The backend must allow requests from the frontend domain.

## Quick Fix Checklist

- [ ] Find backend service URL in Railway
- [ ] Update `NEXT_PUBLIC_API_URL` in frontend service variables
- [ ] Set value to: `https://your-backend-service.up.railway.app/api/v1`
- [ ] Redeploy frontend service
- [ ] Verify backend service is running
- [ ] Check backend CORS configuration
- [ ] Test frontend and verify API calls work
- [ ] Check browser console for errors

## Example Configuration

### Frontend Service Variables:
```
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app/api/v1
```

### Backend Service Variables:
```
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://your-frontend.railway.app
FRONTEND_URLS=https://www.suryadrishti.in
DATABASE_URL=postgresql://... (auto-set by Railway)
```

## Support

If issues persist:
1. Check Railway deployment logs
2. Verify backend service is running
3. Test backend URL directly in browser
4. Check browser console for detailed error messages
5. Verify CORS configuration in backend

