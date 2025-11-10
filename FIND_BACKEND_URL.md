# 🔍 How to Find Your Backend Railway URL

## Quick Steps

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Log in to your account
3. Open your project

### Step 2: Find Your Backend Service
1. Look for the service that runs **Python/FastAPI** (your backend)
2. It should be named something like:
   - `backend`
   - `suryadrishti-backend`
   - `api`
   - Or similar

### Step 3: Get the Backend URL
1. Click on your **backend service**
2. Go to **Settings** tab (gear icon)
3. Scroll down to **Networking** section
4. Look for **Public Networking** or **Domains**
5. You'll see a Railway domain like:
   - `your-backend-service.up.railway.app`
   - `suryadrishti-backend-production.up.railway.app`
   - Or similar

### Step 4: Copy the Full Backend URL
- The backend URL should be: `https://your-backend-service.up.railway.app`
- Add `/api/v1` at the end for the API endpoint
- **Full URL:** `https://your-backend-service.up.railway.app/api/v1`

### Step 5: Test the Backend URL
1. Open the backend URL in your browser: `https://your-backend-service.up.railway.app`
2. You should see:
   - API documentation (Swagger UI)
   - Or a JSON response
   - Or an error page (which is fine, it means the backend is accessible)

3. Test the API endpoint: `https://your-backend-service.up.railway.app/api/v1/health`
   - Should return: `{"status": "healthy"}` or similar

### Step 6: Set NEXT_PUBLIC_API_URL in Frontend
1. Go back to Railway Dashboard
2. Open your **frontend service** (the one running Next.js)
3. Go to **Variables** tab
4. Find or add: `NEXT_PUBLIC_API_URL`
5. Set the value to: `https://your-backend-service.up.railway.app/api/v1`
   - **Replace `your-backend-service.up.railway.app` with your actual backend domain!**
6. Click **Save**

### Step 7: Redeploy Frontend (IMPORTANT!)
1. After saving the variable, Railway will auto-redeploy
2. OR manually trigger a redeploy:
   - Go to **Deployments** tab
   - Click **Redeploy** or push a new commit to GitHub
3. **Wait for deployment to complete** (this is critical!)

### Step 8: Verify
1. Refresh your frontend website
2. Open browser console (F12)
3. Look for: `[API URL] Using NEXT_PUBLIC_API_URL: https://your-backend-service.up.railway.app/api/v1`
4. Verify no more `ERR_NAME_NOT_RESOLVED` errors

## Common Issues

### Issue 1: "I can't find my backend service"
- Check all services in your Railway project
- Look for the one that says "Python" or "FastAPI"
- Check the service logs to see if it's running

### Issue 2: "My backend service is not running"
- Go to backend service → **Deployments** tab
- Check if there are any errors
- Check the **Logs** tab for error messages
- Make sure the backend service is deployed and running

### Issue 3: "I set the variable but it's still not working"
- **Did you redeploy the frontend?** (This is critical!)
- Next.js bakes environment variables into the build at build time
- Changing the variable alone is NOT enough - you MUST redeploy!
- Wait for the deployment to complete before testing

### Issue 4: "I don't see a Railway domain for my backend"
- Make sure your backend service has **Public Networking** enabled
- Go to backend service → Settings → Networking → Public Networking
- Enable it if it's not enabled
- Railway will generate a domain automatically

### Issue 5: "The backend URL doesn't work"
- Test the backend URL directly in your browser
- Check if the backend service is running (check logs)
- Verify the backend is listening on the correct port
- Check if there are any CORS errors in the browser console

## Still Having Issues?

1. **Check Railway logs:**
   - Frontend service logs
   - Backend service logs

2. **Verify backend is accessible:**
   - Test backend URL in browser
   - Check backend health endpoint

3. **Verify environment variables:**
   - Frontend: `NEXT_PUBLIC_API_URL`
   - Backend: `CORS_ORIGINS` (should include your frontend URL)

4. **Check CORS configuration:**
   - Backend `CORS_ORIGINS` should include your frontend domain
   - Example: `https://www.suryadrishti.in,https://your-frontend.railway.app`

## Example Configuration

### Frontend Service Variables:
```
NEXT_PUBLIC_API_URL=https://suryadrishti-backend-production.up.railway.app/api/v1
```

### Backend Service Variables:
```
CORS_ORIGINS=https://www.suryadrishti.in,https://your-frontend.railway.app
DATABASE_URL=postgresql://... (auto-set by Railway)
```

## Need Help?

If you're still having issues:
1. Check Railway service logs
2. Verify backend is running and accessible
3. Make sure you redeployed after changing the variable
4. Check browser console for specific error messages

