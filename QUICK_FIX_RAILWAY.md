# 🚀 Quick Fix: Railway Environment Variable Setup

## Problem
Your app works on your laptop but fails on other devices with "unexpected error occurred - using fallback data". This is because the frontend is trying to connect to `localhost:8000`, which only works on your local machine.

## ✅ Solution (2 minutes)

### Step 1: Get Your Backend URL
1. Go to [Railway Dashboard](https://railway.app)
2. Click on your **Backend** service
3. Go to **Settings** → **Networking**
4. Copy your Railway domain (e.g., `your-backend-production.up.railway.app`)

### Step 2: Set Environment Variable
1. In Railway, click on your **Frontend** service
2. Go to **Variables** tab
3. Click **+ New Variable**
4. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend-production.up.railway.app/api/v1`
     - Replace with your actual backend URL
     - Must start with `https://`
     - Must end with `/api/v1`
5. Click **Add**

### Step 3: Redeploy
Railway will automatically redeploy. Wait 2-3 minutes.

### Step 4: Test
1. Open your frontend URL on a different device/network
2. Check browser console (F12) → Network tab
3. Verify API calls go to your Railway backend URL, not `localhost:8000`

## ✅ Done!

Your app should now work on all devices and networks.

## Need Help?

See `RAILWAY_ENV_SETUP.md` for detailed troubleshooting.

