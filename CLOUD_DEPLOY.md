# Quick Start Guide for Cloud Deployment

## 🚀 One-Click Deploy Options

### Deploy to Railway (Easiest)

1. Fork this repository
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your fork
5. Railway will auto-detect the configuration
6. Add environment variables in Railway dashboard:
   - `DATABASE_URL` (Railway will create PostgreSQL)
   - `REDIS_URL` (Railway will create Redis)
   - `SECRET_KEY` (generate a random string)
   - `DEBUG=False`

### Deploy to Render

1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will use `render.yaml` for configuration
6. Click "Apply" to deploy

### Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set DATABASE_URL=postgresql://...
fly secrets set REDIS_URL=redis://...
fly secrets set SECRET_KEY=your-secret-key
```

### Deploy to Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create suryादrishti

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set config vars
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main
```

## 🐳 Docker Deployment

### Local Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deploy to Any Docker Host

```bash
# Build image
docker build -t suryादrishti:latest ./backend

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  suryादrishti:latest
```

## ☁️ Cloud Platform Guides

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:
- AWS (Elastic Beanstalk, ECS, EKS)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- Kubernetes
- And more!

## 📋 Pre-Deployment Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up Redis
- [ ] Configure CORS domains
- [ ] Set `DEBUG=False`
- [ ] Train ML models
- [ ] Set up monitoring
- [ ] Configure SSL/TLS
- [ ] Set up backups

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your values
```

## 📊 Verify Deployment

After deployment, check:

```bash
# Health check
curl https://your-domain.com/health

# API docs
open https://your-domain.com/docs
```

## 🆘 Need Help?

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
- Review logs: `docker-compose logs` or cloud platform logs
- Test locally first: `python test_system.py`

