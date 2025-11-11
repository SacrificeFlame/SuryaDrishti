# Deployment Guide - SuryaDrishti

Complete guide for deploying SuryaDrishti on Railway.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Backend Railway URL: `https://beauty-aryan-back-production.up.railway.app`

## Step 1: Deploy Backend

### 1.1 Create Backend Service
1. Go to Railway Dashboard (https://railway.app)
2. Create a new project
3. Click "New" → "GitHub Repo"
4. Select your repository
5. **Important:** Set **Root Directory** to: `backend`

### 1.2 Add PostgreSQL Database
1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway automatically creates `DATABASE_URL` environment variable

### 1.3 Set Environment Variables
Go to backend service → **Variables** tab and add:

```env
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in
FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
SECRET_KEY=your-secret-key-here
```

**Optional (for notifications):**
```env
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_FROM_NUMBER=+1234567890
```

### 1.4 Deploy Backend
1. Railway will automatically detect Python and deploy
2. Wait for deployment to complete
3. Note your backend Railway URL (e.g., `beauty-aryan-back-production.up.railway.app`)

### 1.5 Initialize Database
1. Go to backend service → **Deployments** tab
2. Click on latest deployment → **View Logs**
3. Click **Open Shell**
4. Run:
```bash
python scripts/init_database.py
```

## Step 2: Deploy Frontend

### 2.1 Create Frontend Service
1. In the same Railway project, click "New" → "GitHub Repo"
2. Select the same repository
3. **Important:** Set **Root Directory** to: `frontend`

### 2.2 Set Environment Variables
Go to frontend service → **Variables** tab and add:

```env
NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1
```

**Replace `beauty-aryan-back-production.up.railway.app` with your actual backend Railway URL!**

### 2.3 Deploy Frontend
1. Railway will automatically detect Node.js and deploy
2. Wait for deployment to complete
3. **Important:** After setting `NEXT_PUBLIC_API_URL`, you MUST redeploy for changes to take effect

## Step 3: Configure Custom Domain (Optional)

### 3.1 Frontend Custom Domain
1. Go to frontend service → **Settings** → **Networking**
2. Add custom domain: `www.suryadrishti.in`
3. Configure DNS (add CNAME record)
4. Wait for SSL certificate provisioning

### 3.2 Update Backend CORS
1. Go to backend service → **Variables**
2. Ensure `ALLOWED_ORIGINS` includes your custom domain:
   ```
   ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in
   ```
3. Redeploy backend

## Step 4: Verify Deployment

### 4.1 Test Backend
1. Visit: `https://beauty-aryan-back-production.up.railway.app/docs`
2. Should see Swagger UI documentation
3. Test health endpoint: `https://beauty-aryan-back-production.up.railway.app/api/v1/health`

### 4.2 Test Frontend
1. Visit your frontend URL
2. Open browser console (F12)
3. Should see: `[API URL] Using NEXT_PUBLIC_API_URL: https://...`
4. Verify no errors in console
5. Test login and dashboard

## Troubleshooting

### Backend Not Starting
- Check backend service logs
- Verify `DATABASE_URL` is set correctly
- Check if database is accessible
- Verify all environment variables are set

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- **Redeploy frontend after changing the variable**
- Check backend CORS configuration
- Verify backend is running and accessible

### CORS Errors
- Ensure `ALLOWED_ORIGINS` includes your frontend domain
- Redeploy backend after changing CORS settings
- Check browser console for specific CORS errors

### Database Issues
- Verify `DATABASE_URL` is set correctly
- Run database initialization script
- Check database connection in logs

## Environment Variables Reference

### Backend
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto-set by Railway) |
| `ALLOWED_ORIGINS` | Yes | Comma-separated list of allowed origins |
| `FRONTEND_URLS` | Yes | Comma-separated list of frontend URLs |
| `SECRET_KEY` | Yes | Secret key for JWT tokens |
| `TWILIO_ACCOUNT_SID` | No | Twilio account SID for notifications |
| `TWILIO_AUTH_TOKEN` | No | Twilio auth token |
| `TWILIO_FROM_NUMBER` | No | Twilio phone number |

### Frontend
| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL (must include `/api/v1`) |

## Quick Checklist

- [ ] Backend service deployed with root directory `backend`
- [ ] PostgreSQL database added
- [ ] Backend environment variables set
- [ ] Database initialized
- [ ] Frontend service deployed with root directory `frontend`
- [ ] `NEXT_PUBLIC_API_URL` set to backend URL
- [ ] Frontend redeployed after setting `NEXT_PUBLIC_API_URL`
- [ ] Custom domain configured (if applicable)
- [ ] Backend CORS updated for custom domain
- [ ] Both services tested and working

## Need Help?

- Check Railway service logs
- Verify environment variables
- Test backend API directly
- Check browser console for errors
- Review [SET_BACKEND_URL_RAILWAY.md](SET_BACKEND_URL_RAILWAY.md) for backend URL configuration
