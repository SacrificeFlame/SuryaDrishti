# Quick Deployment Guide

## 🚀 Fastest Way to Deploy

### Option 1: Railway (Recommended - Easiest)

1. **Sign up:** https://railway.app
2. **Install CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Deploy Backend:**
   ```bash
   cd backend
   railway init
   railway add postgresql
   railway variables set TWILIO_ACCOUNT_SID=your_sid
   railway variables set TWILIO_AUTH_TOKEN=your_token
   railway variables set TWILIO_FROM_NUMBER=+1234567890
   railway up
   ```

4. **Deploy Frontend:**
   ```bash
   cd frontend
   railway init
   railway variables set NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
   railway up
   ```

5. **Setup Database:**
   ```bash
   railway run python scripts/setup_database.py
   railway run python seed_db.py
   railway run python create_default_devices.py
   ```

**Done!** Your app is live. 🎉

---

### Option 2: Docker Compose (Local/Server)

1. **Create `.env` file:**
   ```bash
   DB_PASSWORD=your_secure_password
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_FROM_NUMBER=+1234567890
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

2. **Start everything:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Setup database:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python scripts/setup_database.py
   docker-compose -f docker-compose.prod.yml exec backend python seed_db.py
   docker-compose -f docker-compose.prod.yml exec backend python create_default_devices.py
   ```

4. **Access:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

### Option 3: Render (Free Tier Available)

1. **Go to:** https://render.com
2. **Create Web Service** for backend
3. **Create Static Site** for frontend
4. **Add PostgreSQL** database
5. **Set environment variables**
6. **Deploy!**

---

## 📋 Pre-Deployment Checklist

- [ ] Set strong database password
- [ ] Configure Twilio credentials (for SMS)
- [ ] Set CORS origins (production domain)
- [ ] Update `NEXT_PUBLIC_API_URL` to production URL
- [ ] Enable HTTPS/SSL
- [ ] Set up domain name (optional)
- [ ] Configure backups

---

## 🔧 Common Issues

**Backend won't start:**
- Check database connection string
- Verify all environment variables are set
- Check logs: `railway logs` or `docker-compose logs backend`

**Frontend can't connect:**
- Verify `NEXT_PUBLIC_API_URL` matches backend URL
- Check CORS settings in backend
- Ensure backend is running

**Database errors:**
- Run setup scripts: `python scripts/setup_database.py`
- Check database credentials
- Verify database is running

---

## 💰 Cost Estimates

- **Railway:** Free tier → $5-20/month
- **Render:** Free tier → $7-25/month
- **Heroku:** $7-25/month (no free tier)
- **AWS EC2:** $10-50/month
- **DigitalOcean:** $12-25/month

---

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for detailed instructions for all platforms.

