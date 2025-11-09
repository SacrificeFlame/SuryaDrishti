# Railway Deployment Guide - SuryaDrishti

Your code is now on GitHub: `https://github.com/saatyakkapoor/avi_k_proj`

## 🚀 Quick Deploy to Railway

### Step 1: Sign Up / Login to Railway

1. Go to https://railway.app
2. Sign up with GitHub (recommended) or email
3. Click "New Project"

### Step 2: Deploy Backend

1. **Create New Service:**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository: `saatyakkapoor/avi_k_proj`
   - Railway will try to auto-detect - **DON'T deploy yet!**

2. **Configure Backend Service:**
   - Go to the service settings (gear icon)
   - **IMPORTANT:** Set **Root Directory** to: `backend`
   - Railway will auto-detect Python and use `requirements.txt`
   - The `Procfile` in backend/ will be used automatically
   - Or manually set:
     - **Build Command:** (leave empty, Railway auto-detects)
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL Database:**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` environment variable

4. **Set Environment Variables:**
   - Go to "Variables" tab
   - Add these variables:
     ```
     TWILIO_ACCOUNT_SID=your_twilio_account_sid
     TWILIO_AUTH_TOKEN=your_twilio_auth_token
     TWILIO_FROM_NUMBER=+1234567890
     CORS_ORIGINS=https://your-frontend-domain.railway.app,http://localhost:3000
     ```
   - **Note:** `DATABASE_URL` is automatically set by Railway when you add PostgreSQL

5. **Deploy:**
   - Railway will automatically deploy when you push to GitHub
   - Or click "Deploy" button

6. **Setup Database:**
   - Go to "Deployments" → Click on your deployment
   - Open "Logs" tab
   - Click "Open Shell" or use Railway CLI:
   ```bash
   railway run python scripts/setup_database.py
   railway run python seed_db.py
   railway run python create_default_devices.py
   ```

### Step 3: Deploy Frontend

1. **Create New Service:**
   - In the same project, click "New" → "GitHub Repo"
   - Select the same repository
   - Railway will try to auto-detect - **DON'T deploy yet!**

2. **Configure Frontend Service:**
   - Go to the service settings (gear icon)
   - **IMPORTANT:** Set **Root Directory** to: `frontend`
   - Railway will auto-detect Node.js and use `package.json`
   - The `Procfile` in frontend/ will be used automatically
   - Or manually set:
     - **Build Command:** `npm install && npm run build`
     - **Start Command:** `npm start`

3. **Set Environment Variables:**
   - Go to "Variables" tab
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-service.railway.app/api/v1
     ```
   - **Important:** Replace `your-backend-service` with your actual backend service name from Railway

4. **Deploy:**
   - Railway will auto-deploy

### Step 4: Get Your URLs

1. **Backend URL:**
   - Go to backend service → "Settings" → "Domains"
   - Copy the Railway-provided domain (e.g., `suryादrishti-backend.railway.app`)
   - Or add a custom domain

2. **Frontend URL:**
   - Go to frontend service → "Settings" → "Domains"
   - Copy the Railway-provided domain
   - Update `NEXT_PUBLIC_API_URL` in frontend variables to use this backend URL

### Step 5: Update CORS (Important!)

1. Go to backend service → "Variables"
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-frontend-domain.railway.app,https://your-frontend-domain.up.railway.app
   ```
3. Redeploy backend

## 📋 Environment Variables Checklist

### Backend Variables:
- ✅ `DATABASE_URL` (auto-set by Railway PostgreSQL)
- ✅ `TWILIO_ACCOUNT_SID` (get from Twilio console)
- ✅ `TWILIO_AUTH_TOKEN` (get from Twilio console)
- ✅ `TWILIO_FROM_NUMBER` (your Twilio phone number, format: +1234567890)
- ✅ `CORS_ORIGINS` (your frontend URLs, comma-separated)

### Frontend Variables:
- ✅ `NEXT_PUBLIC_API_URL` (your backend Railway URL + `/api/v1`)

## 🔧 Using Railway CLI (Optional)

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Link to project:**
   ```bash
   railway link
   ```

4. **Set variables:**
   ```bash
   railway variables set TWILIO_ACCOUNT_SID=your_sid
   railway variables set TWILIO_AUTH_TOKEN=your_token
   ```

5. **Run database setup:**
   ```bash
   railway run python scripts/setup_database.py
   railway run python seed_db.py
   railway run python create_default_devices.py
   ```

## 🐛 Troubleshooting

### Backend won't start:
- Check logs: Railway dashboard → Service → "Logs"
- Verify all environment variables are set
- Check database connection string

### Frontend can't connect:
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend CORS settings
- Ensure backend is running

### Database errors:
- Run setup scripts in Railway shell
- Check PostgreSQL is running
- Verify `DATABASE_URL` is set

### Build fails:
- Check build logs in Railway
- Verify all dependencies in `requirements.txt` and `package.json`
- Check for syntax errors

## 💰 Railway Pricing

- **Free Tier:** $5 credit/month
- **Hobby Plan:** $5/month (after free tier)
- **Pro Plan:** $20/month

**Note:** PostgreSQL database is included in plans.

## 📚 Next Steps

1. ✅ Code is on GitHub
2. ✅ Deploy backend to Railway
3. ✅ Deploy frontend to Railway
4. ✅ Setup database
5. ✅ Configure environment variables
6. ✅ Test the application
7. ✅ Add custom domain (optional)

## 🎉 You're Done!

Once deployed, your app will be live at:
- **Frontend:** `https://your-frontend.railway.app`
- **Backend API:** `https://your-backend.railway.app`
- **API Docs:** `https://your-backend.railway.app/docs`

---

**Need Help?** Check Railway docs: https://docs.railway.app

