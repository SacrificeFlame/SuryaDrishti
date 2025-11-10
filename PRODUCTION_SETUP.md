# SuryaDrishti Production Setup Guide

This guide covers all essential production setup steps for deploying SuryaDrishti.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ or TimescaleDB
- Redis 6+
- Node.js 18+ (for frontend)
- Docker and Docker Compose (optional, for monitoring)

## 1. Set Strong SECRET_KEY

**CRITICAL**: Generate a strong secret key for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to your `.env` file:
```bash
SECRET_KEY=your-generated-secret-key-here
```

## 2. Configure Production Database (PostgreSQL/TimescaleDB)

### Option A: Using DATABASE_URL (Recommended for Railway/Heroku)

```bash
DATABASE_URL=postgresql://user:password@host:5432/database_name
```

### Option B: Using Individual Components

```bash
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=suryadrishti
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_SSL_MODE=require
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### Enable TimescaleDB (Optional, for time-series data)

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('sensor_readings', 'timestamp');
SELECT create_hypertable('forecasts', 'timestamp');
```

## 3. Set Up Redis for Celery

### Local Redis
```bash
REDIS_URL=redis://localhost:6379/0
```

### Redis with Authentication
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_SSL=True
```

### Celery Configuration
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 4. Configure CORS for Production Domains

Add your production domains to `.env`:

```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com
FRONTEND_URLS=https://yourdomain.com,https://www.yourdomain.com
```

## 5. Obtain Satellite Data API Keys

### INSAT/MOSDAC API Keys
1. Visit https://mosdac.gov.in/
2. Register for API access
3. Add to `.env`:
```bash
INSAT_API_KEY=your-insat-api-key
MOSDAC_API_KEY=your-mosdac-api-key
```

### NASA API Key (Alternative)
1. Visit https://api.nasa.gov/
2. Generate API key
3. Add to `.env`:
```bash
NASA_API_KEY=your-nasa-api-key
```

### OpenWeather API Key
1. Visit https://openweathermap.org/api
2. Sign up and get API key
3. Add to `.env`:
```bash
OPENWEATHER_API_KEY=your-openweather-api-key
```

## 6. Set Up Monitoring (Prometheus + Grafana)

### Start Monitoring Stack

```bash
cd backend
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Dashboards
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### Configure Grafana Datasource

1. Login to Grafana
2. Go to Configuration > Data Sources
3. Add Prometheus datasource:
   - URL: http://prometheus:9090
   - Access: Server (default)

### Import Dashboards

Pre-configured dashboards are available in `backend/monitoring/grafana/dashboards/`

## 7. Configure SSL/TLS

### Option A: Using Reverse Proxy (Nginx/Traefik)

Recommended for production. Configure SSL in your reverse proxy.

### Option B: Direct SSL Configuration

```bash
SSL_ENABLED=True
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Start with SSL

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile /path/to/key.pem --ssl-certfile /path/to/cert.pem
```

## 8. Set Up Automated Backups

### Local Backups

```bash
BACKUP_ENABLED=True
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=30
BACKUP_STORAGE_PATH=./backups
```

### S3 Backups

```bash
BACKUP_ENABLED=True
BACKUP_S3_BUCKET=your-s3-bucket-name
BACKUP_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

### Run Backup Script

```bash
# Manual backup
python backend/scripts/backup_database.py

# Automated backup (cron job)
0 2 * * * cd /path/to/suryadrishti && python backend/scripts/backup_database.py
```

## 9. Environment Variables Checklist

Copy `backend/.env.example` to `backend/.env` and fill in all required values:

```bash
cp backend/.env.example backend/.env
```

### Required Variables:
- [x] `SECRET_KEY` - Strong secret key
- [x] `DATABASE_URL` - PostgreSQL connection string
- [x] `REDIS_URL` - Redis connection string
- [x] `ALLOWED_ORIGINS` - Production domains
- [x] `ENVIRONMENT=production` - Set to production

### Optional Variables:
- [ ] `INSAT_API_KEY` - For real satellite data
- [ ] `BACKUP_S3_BUCKET` - For S3 backups
- [ ] `SSL_CERT_PATH` - For SSL/TLS
- [ ] `SMTP_*` - For email notifications

## 10. Production Deployment

### Railway Deployment

1. Set all environment variables in Railway dashboard
2. Ensure `DATABASE_URL` is set automatically by Railway
3. Set `SECRET_KEY` manually
4. Set `ALLOWED_ORIGINS` with your Railway frontend URL
5. Deploy!

### Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

```bash
# Install dependencies
pip install -r backend/requirements-production.txt

# Run migrations
python backend/init_db.py

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 11. Health Checks

### API Health Check
```bash
curl http://your-domain.com/health
```

### Database Health Check
```bash
curl http://your-domain.com/api/v1/health/database
```

### Metrics Endpoint
```bash
curl http://your-domain.com/api/v1/metrics
```

## 12. Security Checklist

- [x] Strong `SECRET_KEY` set
- [x] Database uses SSL (`DB_SSL_MODE=require`)
- [x] CORS configured for production domains only
- [x] Redis uses authentication (if exposed)
- [x] SSL/TLS enabled for API
- [x] Environment variables secured (not in git)
- [x] Database backups configured
- [x] Monitoring enabled

## 13. Troubleshooting

### Database Connection Issues
- Check `DATABASE_URL` format (use `postgresql://` not `postgres://`)
- Verify SSL mode matches your database configuration
- Check firewall rules for database access

### Redis Connection Issues
- Verify `REDIS_URL` is correct
- Check Redis authentication credentials
- Ensure Redis is accessible from your application

### CORS Issues
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check browser console for CORS errors
- Ensure credentials are handled correctly

## Support

For issues or questions, please open an issue on GitHub.

