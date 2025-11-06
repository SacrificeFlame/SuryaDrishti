# 🚀 SuryaDrishti - Complete System Startup Guide

## All TODOs Completed! ✅

This guide shows you how to run the complete SuryaDrishti solar forecasting system with both backend and frontend.

---

## ⚡ Quick Start (Recommended)

### Terminal 1: Backend API
```bash
cd /Users/saatyakthegreat/avik
./start_server.sh
```

### Terminal 2: Frontend Dashboard
```bash
cd /Users/saatyakthegreat/avik/frontend
npm install  # First time only
npm run dev
```

### Access the System
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📋 Step-by-Step Setup

### 1. Verify System Components

```bash
# Check if everything is set up
python3 test_system.py
```

Expected output: ✅ ALL TESTS PASSED

### 2. Start Backend

```bash
cd backend
python3 -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Test Backend API

In a new terminal:
```bash
# Health check
curl http://localhost:8000/health

# List microgrids
curl http://localhost:8000/api/v1/microgrid/

# Get system status
curl http://localhost:8000/api/v1/microgrid/microgrid_001/status
```

### 4. Start Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
- Local: http://localhost:3000
```

### 5. Access Dashboard

Open your browser and go to:
- **Home**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard

---

## 🎯 What You'll See

### Home Page (http://localhost:3000)
- Landing page with project overview
- Feature highlights
- System status indicators
- "Launch Dashboard" button

### Dashboard (http://localhost:3000/dashboard)
- **Current Status Cards**
  - Current Irradiance: 850 W/m²
  - Power Output: 40.9 kW
  - Forecast Confidence: 85%
  - Forecast Points: 5

- **Interactive Forecast Chart**
  - P10/P50/P90 quantile lines
  - Power output overlay
  - 60-minute forecast horizon

- **Alerts Panel**
  - Real-time alert feed
  - Severity indicators
  - Action recommendations

- **System Status**
  - Battery SOC gauge
  - Diesel generator status
  - Load distribution

- **Forecast Details Table**
  - Detailed predictions for each time horizon
  - All three quantiles (P10/P50/P90)

---

## 🔌 Real-Time Updates

The dashboard automatically:
- ✅ Refreshes forecast every 5 minutes
- ✅ Connects to WebSocket for real-time alerts
- ✅ Updates system status dynamically

---

## 🐳 Using Docker (Alternative Method)

```bash
# Start all services at once
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 🧪 Testing the Complete System

### 1. System Integration Test
```bash
python3 test_system.py
```

### 2. Generate a Forecast
```bash
curl -X POST "http://localhost:8000/api/v1/forecast/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.4595,
    "longitude": 77.0266,
    "radius_km": 10,
    "current_conditions": {
      "irradiance": 850,
      "temperature": 32,
      "humidity": 45
    }
  }' | python3 -m json.tool
```

### 3. View in Dashboard
1. Open http://localhost:3000/dashboard
2. The forecast should be visible in the chart
3. Check the forecast details table

---

## 📊 Available Microgrids

The system comes pre-seeded with 3 microgrids:

1. **microgrid_001** - Rajasthan Solar Grid 1
   - Location: (28.4595, 77.0266)
   - Capacity: 50.0 kW

2. **microgrid_002** - Gujarat Solar Grid 2
   - Location: (23.0225, 72.5714)
   - Capacity: 75.0 kW

3. **microgrid_003** - Tamil Nadu Solar Grid 3
   - Location: (11.1271, 78.6569)
   - Capacity: 100.0 kW

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it if needed
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

**Database not found:**
```bash
python3 scripts/setup_database.py
```

**Models not found:**
```bash
python3 train_models.py
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Use different port
PORT=3001 npm run dev
```

**Dependencies not installed:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection error:**
- Make sure backend is running at http://localhost:8000
- Check CORS settings in backend/app/main.py
- Verify no firewall blocking connections

### WebSocket Issues

**WebSocket not connecting:**
1. Check backend is running
2. Verify WebSocket endpoint: ws://localhost:8000/ws/updates
3. Check browser console for errors

---

## 📚 Key Files Reference

### Backend
- `backend/app/main.py` - Main API application
- `backend/app/api/v1/forecast.py` - Forecast endpoints
- `backend/app/services/irradiance_predictor.py` - Core forecasting logic
- `backend/app/ml/models/` - ML model implementations

### Frontend
- `frontend/src/app/page.tsx` - Home page
- `frontend/src/app/dashboard/page.tsx` - Dashboard
- `frontend/src/hooks/useForecast.ts` - Forecast data hook
- `frontend/src/hooks/useWebSocket.ts` - WebSocket hook

### Scripts
- `test_system.py` - System integration test
- `train_models.py` - Model training
- `scripts/setup_database.py` - Database initialization
- `scripts/generate_sample_data.py` - Data generation

---

## 🎓 Next Steps

1. **Explore the Dashboard**
   - Navigate through different views
   - Check real-time updates
   - View forecast details

2. **Test Different Scenarios**
   - Generate forecasts for different locations
   - Try different weather conditions
   - Monitor system responses

3. **Customize**
   - Modify forecast parameters in `backend/app/core/config.py`
   - Adjust frontend styling in `frontend/tailwind.config.js`
   - Add new microgrids to the database

4. **Extend**
   - Add new ML models
   - Implement additional visualizations
   - Integrate real satellite data

---

## 📈 Performance Expectations

- **Forecast Generation**: <2 seconds
- **Model Inference**: <100ms
- **Dashboard Load**: <1 second
- **API Response**: <200ms
- **WebSocket Latency**: Real-time

---

## ✅ Success Checklist

After startup, verify:
- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Dashboard displays without errors
- [ ] Forecast chart shows data
- [ ] System status cards populated
- [ ] WebSocket connection indicator shows "Connected"

---

## 🎉 You're All Set!

The complete SuryaDrishti system is now running. You have:

✅ A fully functional solar forecasting backend  
✅ An interactive real-time dashboard  
✅ Trained ML models generating predictions  
✅ WebSocket real-time updates  
✅ Complete API with documentation  
✅ 1,000 training samples  
✅ 3 operational microgrids  

**Enjoy exploring your solar forecasting system!**

---

## 📞 Need Help?

- **Quick Reference**: See QUICK_START.md
- **API Guide**: http://localhost:8000/docs
- **Full Documentation**: README.md
- **Implementation Details**: IMPLEMENTATION_SUMMARY.md
- **Completion Status**: COMPLETION_SUMMARY.md

---

*Last Updated: November 6, 2025*

