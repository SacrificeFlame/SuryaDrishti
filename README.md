# SuryaDrishti ☀️ - Real-Time Solar Forecasting System

**Solar power forecasting for rural Indian microgrids using satellite imagery and ML**

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

SuryaDrishti is a real-time solar forecasting system that predicts solar power fluctuations by tracking cloud movements using satellite imagery and machine learning. It helps optimize energy management for rural microgrids in India.

### Key Features

- **Real-time Forecasting** - 60-minute ahead predictions with 5-minute resolution
- **Cloud Tracking** - AI-powered cloud detection and motion tracking
- **Probabilistic Forecasts** - P10/P50/P90 quantile predictions
- **Smart Alerts** - Automatic alerts for power drops
- **Battery Scheduling** - Optimized charging/discharging schedules
- **Interactive Dashboard** - Real-time monitoring and visualization

## Tech Stack

**Backend:** FastAPI, PyTorch, OpenCV, SQLAlchemy, PostgreSQL, Redis, Celery

**Frontend:** Next.js 14, TailwindCSS, Recharts, Leaflet

**ML Models:** U-Net (cloud segmentation), Optical Flow (motion tracking), Physics-Informed NN (irradiance forecasting)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)
- Redis (for Celery)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourorg/suryadrishti.git
cd suryadrishti
```

2. **Set up backend**
```bash
cd backend
pip install -r requirements.txt
python init_db.py
```

3. **Set up frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Start the backend**
```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`  
The dashboard will be available at `http://localhost:3000`

## API Documentation

Interactive API docs available at `http://localhost:8000/docs`

## Deployment

### Railway Deployment

1. Create a Railway account and new project
2. Connect your GitHub repository
3. Create two services:
   - **Backend:** Set root directory to `backend`
   - **Frontend:** Set root directory to `frontend`
4. Add PostgreSQL database to backend service
5. Set environment variables (see `PRODUCTION_SETUP.md`)
6. Deploy!

See [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) for detailed deployment instructions.

## Environment Variables

**Backend:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key
- `ALLOWED_ORIGINS` - CORS allowed origins

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend API URL

See `.env.example` for full list of variables.

## Project Structure

```
suryadrishti/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── data/            # ML models and training data
├── scripts/         # Utility scripts
└── docs/            # Documentation
```

## Production Features

- Strong SECRET_KEY generation
- PostgreSQL/TimescaleDB support
- Redis for Celery
- CORS configuration
- Monitoring (Prometheus + Grafana)
- SSL/TLS support
- Automated backups

## Roadmap

- [x] Backend API with FastAPI
- [x] ML models (Cloud segmentation + Forecasting)
- [x] Next.js dashboard
- [x] WebSocket real-time updates
- [x] Battery scheduling
- [x] Real satellite data integration

## License

MIT License - see [LICENSE](LICENSE) file

## Contact

- **Website:** suryadrishti.in

---
