# SuryaDrishti - Solar Forecasting Dashboard

Real-time solar forecasting and energy management dashboard for rural microgrids.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL (for production)
- Railway account (for deployment)

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## 📦 Deployment on Railway

### Backend Service
1. Create a new Railway service from GitHub repo
2. Set **Root Directory** to: `backend`
3. Add PostgreSQL database
4. Set environment variables (see [Environment Variables](#environment-variables))
5. Deploy

### Frontend Service
1. Create a new Railway service from the same GitHub repo
2. Set **Root Directory** to: `frontend`
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app/api/v1`
4. Deploy

### Custom Domain Setup
- Frontend: Configure custom domain in Railway (e.g., `www.suryadrishti.in`)
- Backend: Ensure CORS allows your frontend domain

## 🔧 Environment Variables

### Backend
```env
DATABASE_URL=postgresql://... (auto-set by Railway)
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in
FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
SECRET_KEY=your-secret-key
TWILIO_ACCOUNT_SID=your-twilio-sid (optional)
TWILIO_AUTH_TOKEN=your-twilio-token (optional)
TWILIO_FROM_NUMBER=+1234567890 (optional)
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1
```

**Important:** After changing `NEXT_PUBLIC_API_URL`, you MUST redeploy the frontend service for changes to take effect.

## 📚 Documentation

### Setup Guides
- [Railway Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Backend URL Configuration](SET_BACKEND_URL_RAILWAY.md)
- [Environment Variables](ENVIRONMENT_VARIABLES.md)

### API Documentation
- API endpoints are documented at: `https://your-backend-url/docs` (Swagger UI)
- See [API Endpoints Reference](API_ENDPOINTS_REFERENCE.md)

## 🏗️ Project Structure

```
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── scripts/     # Database scripts
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── src/         # Source code
│   └── package.json
└── README.md
```

## 🔑 Key Features

- Real-time solar forecasting
- Energy scheduling and optimization
- Device management
- Alerts and notifications
- Performance metrics and reports
- User authentication
- Dark mode support

## 🛠️ Technology Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Celery (task queue)
- Pydantic

### Frontend
- Next.js 14
- React
- TypeScript
- Tailwind CSS
- Lucide Icons

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📞 Support

For issues or questions, please open an issue on GitHub.
