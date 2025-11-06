# SuryaDrishti - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run the System Test
```bash
python3 test_system.py
```
Expected output: ✅ ALL TESTS PASSED

### Step 2: Start the Server
```bash
./start_server.sh
```
Or manually:
```bash
cd backend && python3 -m uvicorn app.main:app --reload
```

### Step 3: Test the API
```bash
curl http://localhost:8000/health
```

## 📡 API Examples

### Generate a Forecast
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

### List Microgrids
```bash
curl http://localhost:8000/api/v1/microgrid/ | python3 -m json.tool
```

### Get System Status
```bash
curl http://localhost:8000/api/v1/microgrid/microgrid_001/status | python3 -m json.tool
```

### Get Latest Sensor Reading
```bash
curl http://localhost:8000/api/v1/sensors/microgrid_001/latest | python3 -m json.tool
```

## 📊 What's Been Built

✅ **Backend API** - Fully functional FastAPI server  
✅ **ML Models** - Cloud segmentation + Irradiance forecasting  
✅ **Database** - SQLite with 3 sample microgrids  
✅ **Sample Data** - 1,000 synthetic satellite images  
✅ **Tests** - Integration and unit tests (all passing)  
✅ **Documentation** - Complete README and guides  

## 📁 Important Files

- `README.md` - Complete project documentation
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation status
- `test_system.py` - System integration test
- `train_models.py` - Model training script
- `start_server.sh` - Easy server startup

## 🔗 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🎯 Sample Microgrids

The database is pre-seeded with 3 microgrids:

1. **microgrid_001**: Rajasthan Solar Grid 1
   - Location: (28.4595, 77.0266)
   - Capacity: 50.0 kW

2. **microgrid_002**: Gujarat Solar Grid 2
   - Location: (23.0225, 72.5714)
   - Capacity: 75.0 kW

3. **microgrid_003**: Tamil Nadu Solar Grid 3
   - Location: (11.1271, 78.6569)
   - Capacity: 100.0 kW

## 🐛 Troubleshooting

### Server won't start?
Check if port 8000 is available:
```bash
lsof -i :8000
```

### Missing dependencies?
Install requirements:
```bash
pip3 install -r backend/requirements.txt
```

### Database missing?
Recreate it:
```bash
python3 scripts/setup_database.py
```

### Models missing?
Train them:
```bash
python3 train_models.py
```

## 💡 Next Steps

1. Explore the API at http://localhost:8000/docs
2. Try different forecast parameters
3. Check out the ML model architectures in `backend/app/ml/models/`
4. Build a frontend dashboard (see plan.md for frontend specs)
5. Integrate real satellite data

## 📚 More Information

- Full documentation: `README.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Project plan: `plan.md`

---

**Questions?** Check the README or run the system test for diagnostics.

