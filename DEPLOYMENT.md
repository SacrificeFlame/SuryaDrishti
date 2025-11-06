# SuryaDrishti Cloud Deployment Guide

This guide covers deploying SuryaDrishti to various cloud platforms.

## 🚀 Quick Deploy Options

### Option 1: Docker Compose (Recommended for Testing)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB:
```bash
eb init -p docker suryादrishti
eb create suryादrishti-env
```

3. Deploy:
```bash
eb deploy
```

### Option 3: Google Cloud Run

1. Build and push Docker image:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/suryादrishti
```

2. Deploy:
```bash
gcloud run deploy suryादrishti \
  --image gcr.io/PROJECT_ID/suryादrishti \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Azure Container Instances

1. Build and push:
```bash
az acr build --registry REGISTRY_NAME --image suryादrishti:latest .
```

2. Deploy:
```bash
az container create \
  --resource-group RESOURCE_GROUP \
  --name suryादrishti \
  --image REGISTRY_NAME.azurecr.io/suryादrishti:latest \
  --dns-name-label suryादrishti \
  --ports 8000
```

### Option 5: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

### Option 6: Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the Docker configuration
4. Set environment variables:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`

## 📋 Pre-Deployment Checklist

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up Redis instance
- [ ] Configure CORS for production domains
- [ ] Set `DEBUG=False` in production
- [ ] Train and upload ML models to cloud storage
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure SSL/TLS certificates
- [ ] Set up automated backups
- [ ] Configure log aggregation

## 🔧 Environment Variables

Create a `.env` file or set these in your cloud platform:

```env
# Application
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/suryादrishti

# Redis
REDIS_URL=redis://host:6379/0

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Satellite Data
INSAT_API_KEY=your-api-key
USE_MOCK_DATA=False

# ML Models (if using cloud storage)
CLOUD_SEGMENTATION_MODEL_PATH=s3://bucket/models/cloud_seg_v1.pth
IRRADIANCE_MODEL_PATH=s3://bucket/models/irradiance_v1.pth
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t suryादrishti:latest ./backend
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  suryादrishti:latest
```

## ☁️ Production Architecture

### Recommended Setup:

```
┌─────────────┐
│   CDN       │ (CloudFlare/AWS CloudFront)
└──────┬──────┘
       │
┌──────▼──────┐
│ Load Balancer│ (AWS ALB / GCP LB)
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│App 1│ │App 2│ (Multiple instances)
└──┬──┘ └──┬──┘
   │       │
┌──▼───────▼──┐
│  PostgreSQL │ (Managed DB)
└─────────────┘

┌─────────────┐
│   Redis     │ (Managed Cache)
└─────────────┘

┌─────────────┐
│ Celery      │ (Background Workers)
└─────────────┘
```

## 📊 Monitoring

### Health Check Endpoint

```bash
curl https://your-domain.com/health
```

### Metrics Endpoint

```bash
curl https://your-domain.com/metrics
```

## 🔒 Security

1. **Never commit `.env` files**
2. **Use secrets management** (AWS Secrets Manager, GCP Secret Manager)
3. **Enable HTTPS** (Let's Encrypt or cloud provider SSL)
4. **Set up WAF** (Web Application Firewall)
5. **Regular security updates**
6. **Database encryption at rest**
7. **API rate limiting**

## 📈 Scaling

### Horizontal Scaling

- Run multiple backend instances behind a load balancer
- Use managed Redis for shared state
- Use managed PostgreSQL with connection pooling

### Vertical Scaling

- Increase instance size for ML inference
- Use GPU instances for faster model inference
- Enable model caching

## 🚨 Troubleshooting

### Check Logs

```bash
# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/suryादrishti

# Cloud Run
gcloud run services logs read suryादrishti
```

### Database Connection Issues

- Check firewall rules
- Verify connection string
- Test connection: `psql $DATABASE_URL`

### Redis Connection Issues

- Verify Redis URL
- Check network connectivity
- Test: `redis-cli -u $REDIS_URL ping`

## 📞 Support

For deployment issues, check:
1. Application logs
2. Cloud provider status pages
3. Docker logs
4. Database connection logs

