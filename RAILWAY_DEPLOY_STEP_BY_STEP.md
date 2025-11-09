# Railway Deployment - Step by Step (GUARANTEED TO WORK)

## ⚠️ IMPORTANT: You MUST set Root Directory for each service!

Railway can't auto-detect because your repo has both `backend/` and `frontend/`. You MUST manually set the root directory.

---

## Step 1: Delete Any Failed Services

1. Go to your Railway project
2. Delete any services that failed to build
3. Start fresh

---

## Step 2: Deploy Backend (Python)

### 2.1 Create Backend Service

1. Click **"New Project"** (or "New" in existing project)
2. Select **"Deploy from GitHub repo"**
3. Choose your repo: `saatyakkapoor/avi_k_proj`
4. **WAIT - DON'T CLICK DEPLOY YET!**

### 2.2 Configure Root Directory (CRITICAL!)

1. Click the **gear icon** (Settings) next to your service
2. Go to **"Service"** tab
3. Scroll to **"Root Directory"**
4. **Type:** `backend` (exactly this, no slash)
5. Click **"Save"**

### 2.3 Railway Will Now Detect Python

- Railway will see `backend/requirements.txt` and `backend/nixpacks.toml`
- It will automatically use Python 3.11
- Build command will be auto-detected
- Start command will use the Procfile: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.4 Add PostgreSQL Database

1. In your project, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` environment variable

### 2.5 Set Environment Variables

1. Go to backend service → **"Variables"** tab
2. Add these (click "New Variable" for each):

```
TWILIO_ACCOUNT_SID = your_twilio_sid
TWILIO_AUTH_TOKEN = your_twilio_token
TWILIO_FROM_NUMBER = +1234567890
CORS_ORIGINS = http://localhost:3000
```

**Note:** `DATABASE_URL` is automatically added by PostgreSQL service

### 2.6 Deploy Backend

1. Click **"Deploy"** button
2. Wait for build to complete
3. Check logs if there are errors

### 2.7 Setup Database

1. Go to backend service → **"Deployments"** tab
2. Click on the latest deployment
3. Click **"View Logs"**
4. Click **"Open Shell"** button
5. Run these commands one by one:

```bash
python scripts/setup_database.py
python seed_db.py
python create_default_devices.py
```

---

## Step 3: Deploy Frontend (Node.js)

### 3.1 Create Frontend Service

1. In the **same project**, click **"New"**
2. Select **"GitHub Repo"**
3. Choose the same repo: `saatyakkapoor/avi_k_proj`
4. **WAIT - DON'T CLICK DEPLOY YET!**

### 3.2 Configure Root Directory (CRITICAL!)

1. Click the **gear icon** (Settings) next to frontend service
2. Go to **"Service"** tab
3. Scroll to **"Root Directory"**
4. **Type:** `frontend` (exactly this, no slash)
5. Click **"Save"**

### 3.3 Railway Will Now Detect Node.js

- Railway will see `frontend/package.json` and `frontend/nixpacks.toml`
- It will automatically use Node.js 18
- Build command: `npm ci && npm run build`
- Start command: `npm start` (from Procfile)

### 3.4 Set Environment Variables

1. Go to frontend service → **"Variables"** tab
2. Add:

```
NEXT_PUBLIC_API_URL = https://your-backend-service.railway.app/api/v1
```

**Important:** Replace `your-backend-service` with your actual backend service name from Railway

### 3.5 Deploy Frontend

1. Click **"Deploy"** button
2. Wait for build to complete

---

## Step 4: Get Your URLs

### Backend URL:
1. Go to backend service → **"Settings"** → **"Domains"**
2. Copy the Railway domain (e.g., `suryादrishti-backend-production.up.railway.app`)
3. Your API will be at: `https://your-backend-domain.railway.app`

### Frontend URL:
1. Go to frontend service → **"Settings"** → **"Domains"**
2. Copy the Railway domain
3. Your app will be at: `https://your-frontend-domain.railway.app`

### Update CORS:
1. Go to backend service → **"Variables"**
2. Update `CORS_ORIGINS`:
```
CORS_ORIGINS = https://your-frontend-domain.railway.app,https://your-frontend-domain.up.railway.app
```
3. Redeploy backend

### Update Frontend API URL:
1. Go to frontend service → **"Variables"**
2. Update `NEXT_PUBLIC_API_URL`:
```
NEXT_PUBLIC_API_URL = https://your-backend-domain.railway.app/api/v1
```
3. Redeploy frontend

---

## ✅ Verification Checklist

- [ ] Backend service has Root Directory = `backend`
- [ ] Frontend service has Root Directory = `frontend`
- [ ] PostgreSQL database added
- [ ] All environment variables set
- [ ] Database setup scripts run
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] CORS_ORIGINS updated with frontend URL
- [ ] NEXT_PUBLIC_API_URL updated with backend URL

---

## 🐛 If Build Still Fails

1. **Check Root Directory:**
   - Backend service: Must be exactly `backend` (no `/`, no quotes)
   - Frontend service: Must be exactly `frontend` (no `/`, no quotes)

2. **Check Logs:**
   - Go to service → "Deployments" → Click deployment → "View Logs"
   - Look for error messages

3. **Verify Files Exist:**
   - Backend should have: `requirements.txt`, `Procfile`, `nixpacks.toml`
   - Frontend should have: `package.json`, `Procfile`, `nixpacks.toml`

4. **Try Manual Build:**
   - Go to service settings
   - Set Build Command manually:
     - Backend: `pip install -r requirements.txt`
     - Frontend: `npm ci && npm run build`
   - Set Start Command manually:
     - Backend: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Frontend: `npm start`

---

## 📸 Visual Guide

**Setting Root Directory:**
1. Service Settings (gear icon) → Service tab
2. Find "Root Directory" field
3. Type: `backend` or `frontend`
4. Click Save
5. Deploy

---

**This WILL work if you set the Root Directory correctly!**

