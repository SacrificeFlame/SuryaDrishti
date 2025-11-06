@echo off
echo ========================================
echo SuryaDrishti - Railway Deployment Helper
echo ========================================
echo.
echo This script will help you deploy to Railway.
echo.
echo Prerequisites:
echo - GitHub account
echo - Railway account (free tier available)
echo.
echo Steps:
echo 1. Open https://railway.app in your browser
echo 2. Sign up/Login with GitHub
echo 3. Click "New Project" ^> "Deploy from GitHub repo"
echo 4. Select: saatyakkapoor/avi_k_proj
echo 5. Add PostgreSQL database (Railway will auto-set DATABASE_URL)
echo 6. Add Redis database (Railway will auto-set REDIS_URL)
echo 7. Set environment variables:
echo    - SECRET_KEY (generate random string)
echo    - DEBUG=False
echo    - ALLOWED_ORIGINS=https://your-app-name.up.railway.app
echo 8. Railway will auto-deploy!
echo.
echo For detailed instructions, see DEPLOY_STEPS.md
echo.
echo Opening Railway in your browser...
start https://railway.app
echo.
echo ========================================
echo Deployment Guide: DEPLOY_STEPS.md
echo Quick Reference: DEPLOY_NOW.md
echo ========================================
pause

