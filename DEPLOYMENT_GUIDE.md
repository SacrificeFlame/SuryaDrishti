# Deployment Guide - SuryaDrishti

This guide covers multiple deployment options for hosting your SuryaDrishti application.

## Table of Contents

1. [Quick Start (Local Development)](#quick-start-local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Platform Deployment](#cloud-platform-deployment)
   - [Railway](#railway)
   - [Render](#render)
   - [Heroku](#heroku)
   - [AWS EC2](#aws-ec2)
   - [DigitalOcean](#digitalocean)
4. [Production Checklist](#production-checklist)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)

### Steps

1. **Clone and setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/setup_database.py
python seed_db.py
python create_default_devices.py
```

2. **Start backend:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Setup frontend:**
```bash
cd frontend
npm install
```

4. **Start frontend:**
```bash
npm run dev
```

5. **Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Option 1: Docker Compose (Recommended)

1. **Create `.env` file:**
```bash
# Backend
DATABASE_URL=postgresql://user:password@db:5432/suryादrishti
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Check logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

### Option 2: Individual Docker Containers

**Backend:**
```bash
cd backend
docker build -t suryादrishti-backend .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e TWILIO_ACCOUNT_SID=your_sid \
  -e TWILIO_AUTH_TOKEN=your_token \
  suryादrishti-backend
```

**Frontend:**
```bash
cd frontend
docker build -t suryादrishti-frontend .
docker run -d -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://your-backend-url:8000/api/v1 \
  suryादrishti-frontend
```

---

## Cloud Platform Deployment

### Railway

**Railway** is recommended for easy deployment with PostgreSQL included.

#### Backend Deployment

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
railway login
```

2. **Initialize project:**
```bash
cd backend
railway init
railway add postgresql
```

3. **Set environment variables:**
```bash
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set TWILIO_ACCOUNT_SID=your_sid
railway variables set TWILIO_AUTH_TOKEN=your_token
railway variables set TWILIO_FROM_NUMBER=+1234567890
```

4. **Deploy:**
```bash
railway up
```

5. **Run database migrations:**
```bash
railway run python scripts/setup_database.py
railway run python seed_db.py
railway run python create_default_devices.py
```

#### Frontend Deployment

1. **Initialize:**
```bash
cd frontend
railway init
```

2. **Set environment variables:**
```bash
railway variables set NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

3. **Deploy:**
```bash
railway up
```

**Cost:** Free tier available, then ~$5-20/month

---

### Render

#### Backend Deployment

1. **Create new Web Service:**
   - Connect your GitHub repository
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Add PostgreSQL database:**
   - Create new PostgreSQL database
   - Copy connection string

3. **Set environment variables:**
   - `DATABASE_URL`: PostgreSQL connection string
   - `TWILIO_ACCOUNT_SID`: Your Twilio SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio token
   - `TWILIO_FROM_NUMBER`: Your Twilio number

4. **Deploy:**
   - Render will auto-deploy on git push

#### Frontend Deployment

1. **Create new Static Site:**
   - Connect your GitHub repository
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/.next`

2. **Set environment variables:**
   - `NEXT_PUBLIC_API_URL`: Your backend URL

**Cost:** Free tier available, then ~$7-25/month

---

### Heroku

#### Backend Deployment

1. **Install Heroku CLI:**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login:**
```bash
heroku login
```

3. **Create app:**
```bash
cd backend
heroku create suryादrishti-backend
heroku addons:create heroku-postgresql:mini
```

4. **Set environment variables:**
```bash
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
heroku config:set TWILIO_FROM_NUMBER=+1234567890
```

5. **Create `Procfile`:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. **Deploy:**
```bash
git push heroku main
heroku run python scripts/setup_database.py
heroku run python seed_db.py
heroku run python create_default_devices.py
```

#### Frontend Deployment

1. **Create app:**
```bash
cd frontend
heroku create suryादrishti-frontend --buildpack https://github.com/mars/create-react-app-buildpack.git
```

2. **Set environment variables:**
```bash
heroku config:set NEXT_PUBLIC_API_URL=https://your-backend.herokuapp.com/api/v1
```

3. **Deploy:**
```bash
git push heroku main
```

**Cost:** Free tier discontinued, paid plans start at $7/month

---

### AWS EC2

#### Setup Steps

1. **Launch EC2 Instance:**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t3.small or larger
   - Configure security group:
     - Port 22 (SSH)
     - Port 80 (HTTP)
     - Port 443 (HTTPS)
     - Port 8000 (Backend API - optional)

2. **Connect to instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies:**
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm nginx postgresql
```

4. **Setup backend:**
```bash
cd /opt
sudo git clone https://github.com/your-repo/suryादrishti.git
cd suryादrishti/backend
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Setup PostgreSQL:**
```bash
sudo -u postgres psql
CREATE DATABASE suryादrishti;
CREATE USER suryauser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE suryादrishti TO suryauser;
\q
```

6. **Create systemd service for backend:**
```bash
sudo nano /etc/systemd/system/suryादrishti-backend.service
```

```ini
[Unit]
Description=SuryaDrishti Backend API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/suryादrishti/backend
Environment="PATH=/opt/suryादrishti/backend/venv/bin"
Environment="DATABASE_URL=postgresql://suryauser:password@localhost:5432/suryादrishti"
Environment="TWILIO_ACCOUNT_SID=your_sid"
Environment="TWILIO_AUTH_TOKEN=your_token"
Environment="TWILIO_FROM_NUMBER=+1234567890"
ExecStart=/opt/suryादrishti/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Start backend service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable suryादrishti-backend
sudo systemctl start suryादrishti-backend
sudo systemctl status suryादrishti-backend
```

8. **Setup Nginx reverse proxy:**
```bash
sudo nano /etc/nginx/sites-available/suryादrishti
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (after building)
    location / {
        root /opt/suryादrishti/frontend/.next;
        try_files $uri $uri/ /index.html;
    }
}
```

9. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/suryादrishti /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

10. **Setup frontend:**
```bash
cd /opt/suryादrishti/frontend
npm install
npm run build
```

**Cost:** ~$10-50/month depending on instance size

---

### DigitalOcean

#### Using App Platform (Easiest)

1. **Create App:**
   - Go to DigitalOcean App Platform
   - Connect GitHub repository
   - Select backend directory
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Add PostgreSQL database:**
   - Add database component
   - Connection string auto-provided

3. **Set environment variables:**
   - Add all required variables

4. **Deploy frontend:**
   - Create second app for frontend
   - Build command: `npm install && npm run build`
   - Publish directory: `.next`

**Cost:** ~$12-25/month

#### Using Droplet (VPS)

Similar to AWS EC2 setup above.

---

## Production Checklist

### Security

- [ ] Use HTTPS (SSL/TLS certificate)
- [ ] Set strong database passwords
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for your frontend domain
- [ ] Set up firewall rules
- [ ] Use PostgreSQL instead of SQLite in production
- [ ] Enable rate limiting on API
- [ ] Set up monitoring and alerts

### Performance

- [ ] Enable gzip compression
- [ ] Set up CDN for frontend assets
- [ ] Configure database connection pooling
- [ ] Set up Redis for caching (optional)
- [ ] Enable database indexes
- [ ] Optimize frontend bundle size

### Monitoring

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up uptime monitoring
- [ ] Monitor database performance
- [ ] Track API response times

### Backup

- [ ] Set up automated database backups
- [ ] Store backups off-site
- [ ] Test backup restoration process

---

## Environment Variables

See `ENVIRONMENT_VARIABLES.md` for complete list.

**Required for Production:**
- `DATABASE_URL` - PostgreSQL connection string
- `TWILIO_ACCOUNT_SID` - For SMS notifications
- `TWILIO_AUTH_TOKEN` - For SMS notifications
- `TWILIO_FROM_NUMBER` - Twilio phone number
- `NEXT_PUBLIC_API_URL` - Backend API URL (frontend)

---

## Database Setup

### PostgreSQL (Production)

1. **Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create database:**
```bash
sudo -u postgres psql
CREATE DATABASE suryादrishti;
CREATE USER suryauser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE suryादrishti TO suryauser;
\q
```

3. **Update connection string:**
```bash
DATABASE_URL=postgresql://suryauser:secure_password@localhost:5432/suryादrishti
```

4. **Run migrations:**
```bash
cd backend
python scripts/setup_database.py
python seed_db.py
python create_default_devices.py
```

### SQLite (Development Only)

SQLite works for development but **NOT recommended for production** due to:
- Limited concurrency
- No network access
- No user management
- Performance limitations

---

## Troubleshooting

### Backend won't start

1. **Check logs:**
```bash
# Docker
docker-compose logs backend

# Systemd
sudo journalctl -u suryादrishti-backend -f

# Railway/Render
# Check logs in dashboard
```

2. **Check database connection:**
```bash
# Test PostgreSQL connection
psql $DATABASE_URL
```

3. **Check port availability:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

### Frontend can't connect to backend

1. **Check CORS settings:**
   - Ensure frontend URL is in `CORS_ORIGINS`
   - Check backend logs for CORS errors

2. **Verify API URL:**
   - Check `NEXT_PUBLIC_API_URL` environment variable
   - Ensure it matches your backend URL

3. **Check network:**
   - Test backend URL directly: `curl https://your-backend.com/api/v1/microgrid/`
   - Check firewall rules

### Database connection errors

1. **Verify connection string:**
   - Format: `postgresql://user:password@host:port/database`
   - Check credentials

2. **Check database is running:**
```bash
# PostgreSQL
sudo systemctl status postgresql

# Docker
docker-compose ps db
```

3. **Check database exists:**
```bash
psql -U postgres -l
```

---

## Quick Deployment Commands

### Railway
```bash
railway login
railway init
railway up
```

### Render
```bash
# Just push to GitHub, Render auto-deploys
git push origin main
```

### Heroku
```bash
heroku login
heroku create
git push heroku main
```

### Docker
```bash
docker-compose up -d
```

---

## Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Test database connection
4. Check firewall/security groups
5. Review platform-specific documentation

---

**Recommended for beginners:** Railway or Render (easiest setup)
**Recommended for production:** AWS EC2 or DigitalOcean Droplet (more control)
**Recommended for quick testing:** Docker Compose (local)

