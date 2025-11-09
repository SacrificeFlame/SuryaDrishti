# Railway Environment Variables Setup Guide

## Problem
The frontend is using `localhost:8000` as a fallback, which only works on your local machine. Other devices can't connect because they're trying to reach `localhost` on their own machines, not your server.

## Solution
Set the `NEXT_PUBLIC_API_URL` environment variable in Railway to point to your backend service's public URL.

## Steps to Fix

### 1. Get Your Backend Railway URL
1. Go to your Railway project dashboard
2. Click on your **Backend** service
3. Go to the **Settings** tab
4. Find the **Domains** section
5. Copy the Railway-provided domain (e.g., `backend-production.up.railway.app`)
6. Or if you have a custom domain, use that

### 2. Set Frontend Environment Variable
1. Go to your Railway project dashboard
2. Click on your **Frontend** service
3. Go to the **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Variable Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend-url.railway.app/api/v1`
     - Replace `your-backend-url.railway.app` with your actual backend URL
     - Make sure to include `https://` and `/api/v1` at the end
6. Click **Add**

### 3. Redeploy Frontend
1. After adding the environment variable, Railway will automatically redeploy
2. Or manually trigger a redeploy from the **Deployments** tab
3. Wait for the build to complete

### 4. Verify
1. Open your frontend URL in a browser
2. Open Developer Tools (F12)
3. Go to the **Network** tab
4. Refresh the page
5. Check that API requests are going to your Railway backend URL, not `localhost:8000`

## Example Configuration

**Backend Service:**
- Railway URL: `backend-production-abc123.up.railway.app`
- Port: 8000 (internal)

**Frontend Environment Variable:**
```
NEXT_PUBLIC_API_URL=https://backend-production-abc123.up.railway.app/api/v1
```

## Important Notes

1. **Use HTTPS**: Railway provides HTTPS URLs, always use `https://` not `http://`
2. **Include `/api/v1`**: The frontend expects the API base URL to include `/api/v1`
3. **Public Access**: Make sure your backend service is publicly accessible (not private)
4. **CORS**: Your backend should already have CORS configured to allow requests from your frontend domain

## Troubleshooting

### Still seeing `localhost:8000` errors?
1. Check that `NEXT_PUBLIC_API_URL` is set correctly in Railway
2. Verify the variable name is exactly `NEXT_PUBLIC_API_URL` (case-sensitive)
3. Make sure you redeployed the frontend after adding the variable
4. Clear your browser cache and hard refresh (Ctrl+Shift+R)

### Backend not accessible?
1. Check that your backend service is running
2. Verify the backend URL is correct
3. Test the backend URL directly in a browser: `https://your-backend-url.railway.app/api/v1/microgrid/microgrid_001`
4. Check backend logs for CORS errors

### CORS Errors?
If you see CORS errors in the browser console:
1. Check your backend's CORS configuration in `backend/app/main.py`
2. Make sure your frontend domain is in the allowed origins
3. For Railway, you might need to allow `*` or your specific Railway frontend domain

## Quick Fix Command (Railway CLI)

If you have Railway CLI installed:
```bash
railway variables set NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1 --service frontend
```

