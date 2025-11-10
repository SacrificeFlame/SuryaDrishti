# 🚀 Set Backend URL in Railway - QUICK SETUP

## Your Backend URL
```
https://beauty-aryan-back-production.up.railway.app
```

## Step-by-Step Instructions

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Log in to your account
3. Open your project

### Step 2: Set NEXT_PUBLIC_API_URL in Frontend Service
1. **Find your FRONTEND service** (the one running Next.js)
2. Click on the frontend service
3. Go to **Variables** tab
4. **Find or add:** `NEXT_PUBLIC_API_URL`
5. **Set the value to:**
   ```
   https://beauty-aryan-back-production.up.railway.app/api/v1
   ```
6. Click **Save**

### Step 3: Verify Backend CORS Configuration
1. **Find your BACKEND service** (the one running Python/FastAPI)
2. Click on the backend service
3. Go to **Variables** tab
4. **Check if `ALLOWED_ORIGINS` exists:**
   - If it exists, make sure it includes: `https://www.suryadrishti.in`
   - If it doesn't exist, add it with value: `https://www.suryadrishti.in,https://suryadrishti.in`
5. **OR check if `FRONTEND_URLS` exists:**
   - If it exists, make sure it includes: `https://www.suryadrishti.in`
   - If it doesn't exist, add it with value: `https://www.suryadrishti.in,https://suryadrishti.in`

### Step 4: Redeploy Frontend (CRITICAL!)
1. After saving `NEXT_PUBLIC_API_URL`, Railway will auto-redeploy
2. **OR manually trigger a redeploy:**
   - Go to frontend service → **Deployments** tab
   - Click **Redeploy** button
   - Wait for deployment to complete (this is IMPORTANT!)

### Step 5: Redeploy Backend (if you changed CORS)
1. If you changed `ALLOWED_ORIGINS` or `FRONTEND_URLS`, redeploy the backend:
   - Go to backend service → **Deployments** tab
   - Click **Redeploy** button
   - Wait for deployment to complete

### Step 6: Verify It Works
1. **Refresh your frontend website:** https://www.suryadrishti.in
2. **Open browser console** (F12)
3. **Look for:** `[API URL] Using NEXT_PUBLIC_API_URL: https://beauty-aryan-back-production.up.railway.app/api/v1`
4. **Check for errors:**
   - Should see no `ERR_NAME_NOT_RESOLVED` errors
   - Should see no CORS errors
   - API calls should work

## Quick Checklist

- [ ] Set `NEXT_PUBLIC_API_URL` to `https://beauty-aryan-back-production.up.railway.app/api/v1` in frontend service
- [ ] Verified backend CORS includes `https://www.suryadrishti.in`
- [ ] Redeployed frontend service
- [ ] Redeployed backend service (if CORS was changed)
- [ ] Tested frontend and verified no errors in console
- [ ] API calls are working

## Troubleshooting

### Still seeing errors?

1. **Check if backend is running:**
   - Go to backend service → **Deployments** tab
   - Check if latest deployment is successful
   - Check **Logs** tab for any errors

2. **Test backend directly:**
   - Open: `https://beauty-aryan-back-production.up.railway.app/api/v1/health`
   - Should return: `{"status": "healthy"}` or similar
   - If you see an error, the backend might be down

3. **Check CORS:**
   - Make sure `ALLOWED_ORIGINS` or `FRONTEND_URLS` includes `https://www.suryadrishti.in`
   - Redeploy backend after changing CORS settings

4. **Verify frontend was redeployed:**
   - Check frontend service → **Deployments** tab
   - Make sure latest deployment completed successfully
   - The build should include the new `NEXT_PUBLIC_API_URL` value

5. **Clear browser cache:**
   - Clear cache and hard refresh (Ctrl+F5)
   - Try incognito mode

## Environment Variables Summary

### Frontend Service Variables:
```
NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1
```

### Backend Service Variables:
```
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in
```
OR
```
FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
```

## Need Help?

If you're still having issues:
1. Check Railway service logs (frontend and backend)
2. Verify backend is accessible: `https://beauty-aryan-back-production.up.railway.app`
3. Check browser console for specific error messages
4. Make sure both services are deployed and running

