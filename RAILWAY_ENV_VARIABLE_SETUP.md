# 🚀 Railway Environment Variable Setup - Step by Step

## Your Backend URL
**Backend URL**: `https://beauty-aryan-back-production.up.railway.app`

## Quick Fix (2 minutes)

### Step 1: Set Environment Variable in Railway

1. **Go to Railway Dashboard**: https://railway.app
2. **Click on your Frontend service** (not backend)
3. **Go to the "Variables" tab** (in the service settings)
4. **Click "+ New Variable"**
5. **Add this variable**:
   - **Variable Name**: `NEXT_PUBLIC_API_URL`
   - **Variable Value**: `https://beauty-aryan-back-production.up.railway.app/api/v1`
   - **Important**: Make sure it's exactly `NEXT_PUBLIC_API_URL` (case-sensitive)
   - **Important**: Include `https://` and `/api/v1` at the end
6. **Click "Add"**

### Step 2: Trigger Rebuild

**Important**: Next.js embeds `NEXT_PUBLIC_*` variables at **build time**, so you need to rebuild:

1. After adding the variable, Railway should automatically trigger a rebuild
2. If not, go to **Deployments** tab
3. Click **"Redeploy"** or **"Deploy"** to trigger a new build
4. Wait for the build to complete (2-5 minutes)

### Step 3: Verify

1. **Open your frontend URL** on a different device/network
2. **Open Developer Tools** (F12)
3. **Go to Network tab**
4. **Refresh the page**
5. **Check API requests** - they should now go to:
   - `https://beauty-aryan-back-production.up.railway.app/api/v1/...`
   - **NOT** `localhost:8000/api/v1/...`

## Expected Result

After setting the variable and rebuilding:
- ✅ API calls go to `https://beauty-aryan-back-production.up.railway.app/api/v1/...`
- ✅ App works on all devices and networks
- ✅ No more "ERR_CONNECTION_REFUSED" errors
- ✅ No more "Using fallback data" errors

## Troubleshooting

### Still seeing `localhost:8000`?

1. **Check the variable is set correctly**:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://beauty-aryan-back-production.up.railway.app/api/v1`

2. **Verify the frontend was rebuilt**:
   - Check Railway deployments - there should be a new deployment after adding the variable
   - If not, manually trigger a redeploy

3. **Clear browser cache**:
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache completely

4. **Check build logs**:
   - In Railway, go to Frontend service → Deployments
   - Click on the latest deployment
   - Check build logs to see if the variable was used

### Backend not responding?

1. **Test backend directly**:
   - Open: https://beauty-aryan-back-production.up.railway.app/docs
   - You should see the FastAPI documentation page
   - If not, your backend might not be running

2. **Check backend logs**:
   - Go to Backend service → Logs
   - Look for any errors

3. **Verify backend is accessible**:
   - Try: https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001
   - You should get a JSON response (or an error, but not connection refused)

## Railway CLI (Alternative)

If you have Railway CLI installed:

```bash
railway variables set NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1 --service frontend
```

Then trigger a redeploy:
```bash
railway up --service frontend
```

## Summary

**The fix is simple**:
1. Set `NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1` in Railway frontend service
2. Rebuild the frontend (Railway should do this automatically)
3. Wait for deployment to complete
4. Test on a different device/network

The code is already fixed - you just need to set the environment variable and rebuild!

