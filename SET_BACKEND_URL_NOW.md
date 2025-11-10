# ⚠️ URGENT: Set Backend URL in Railway

## Problem

The frontend is trying to connect to a backend URL that doesn't exist:
- ❌ `https://beauty-aryan-back-production.up.railway.app/api/v1` (doesn't exist)
- ❌ `https://api.www.suryadrishti.in/api/v1` (fallback, doesn't exist)

## Solution: Set Correct Backend URL

### Step 1: Find Your Backend Service URL

1. **Go to Railway Dashboard**: https://railway.app
2. **Find your backend service** (the one running FastAPI/Python)
3. **Click on the backend service**
4. **Go to Settings → Networking → Public Networking**
5. **Find the Railway domain** (e.g., `your-backend-service.up.railway.app`)
6. **Copy the full URL**: `https://your-backend-service.up.railway.app`

### Step 2: Update Frontend Environment Variable

1. **Go to Railway Dashboard**
2. **Select your FRONTEND service** (the one running Next.js)
3. **Go to Variables tab**
4. **Find `NEXT_PUBLIC_API_URL`** (or add it if it doesn't exist)
5. **Set the value to**: `https://your-backend-service.up.railway.app/api/v1`
   - Replace `your-backend-service.up.railway.app` with your actual backend Railway domain
   - **Important:** Include `/api/v1` at the end
6. **Click Save or Update**

### Step 3: Redeploy Frontend

1. **After updating the variable, Railway will automatically redeploy**
2. **OR manually trigger a redeploy:**
   - Go to Deployments tab
   - Click "Redeploy" or push a new commit to GitHub
3. **Wait for deployment to complete**

### Step 4: Verify

1. **Visit your frontend**: `https://www.suryadrishti.in`
2. **Open browser console** (F12)
3. **Check for**: `[API URL] Using NEXT_PUBLIC_API_URL: https://your-backend-service.up.railway.app/api/v1`
4. **Verify API calls are successful** (no `ERR_NAME_NOT_RESOLVED` errors)

## Example Configuration

### Frontend Service Variables:
```
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app/api/v1
```

**Replace `your-backend-service.up.railway.app` with your actual backend Railway domain!**

## Alternative: Use Custom Domain for Backend

If you want to use `api.suryadrishti.in` for your backend:

1. **Set up custom domain in Railway:**
   - Go to backend service → Settings → Networking
   - Add custom domain: `api.suryadrishti.in`
   - Configure DNS (add CNAME record: `api` → `your-backend-service.up.railway.app`)
   - Wait for SSL certificate to provision

2. **Update frontend variable:**
   - Set `NEXT_PUBLIC_API_URL` to: `https://api.suryadrishti.in/api/v1`

3. **Redeploy frontend**

## Quick Checklist

- [ ] Found backend Railway domain
- [ ] Updated `NEXT_PUBLIC_API_URL` in frontend service variables
- [ ] Set value to: `https://your-backend-service.up.railway.app/api/v1`
- [ ] Redeployed frontend service
- [ ] Verified backend service is running
- [ ] Tested frontend and checked browser console
- [ ] No more `ERR_NAME_NOT_RESOLVED` errors

## Troubleshooting

### Still seeing errors?

1. **Verify backend service is running:**
   - Check Railway Dashboard → Backend Service → Status
   - Check deployment logs for errors

2. **Test backend URL directly:**
   - Visit: `https://your-backend-service.up.railway.app/api/v1/health`
   - Should return: `{"status": "healthy"}`

3. **Check CORS configuration:**
   - Go to backend service → Variables
   - Verify `ALLOWED_ORIGINS` includes: `https://www.suryadrishti.in`
   - Verify `FRONTEND_URLS` includes: `https://www.suryadrishti.in`

4. **Clear browser cache:**
   - Clear cache and hard refresh (Ctrl+F5)
   - Try incognito mode

## Need Help?

1. **Check Railway logs:**
   - Frontend service logs
   - Backend service logs

2. **Verify environment variables:**
   - Frontend: `NEXT_PUBLIC_API_URL`
   - Backend: `ALLOWED_ORIGINS`, `FRONTEND_URLS`

3. **Test backend directly:**
   - Use browser or curl to test backend URL
   - Verify backend is accessible

## Summary

**The issue:** Frontend is using an old/invalid backend URL.

**The fix:** Update `NEXT_PUBLIC_API_URL` in Railway frontend service to your actual backend Railway URL.

**After fixing:** Redeploy frontend and verify API calls work.

