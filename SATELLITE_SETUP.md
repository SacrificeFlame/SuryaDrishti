# Quick Start Guide for Satellite Images

## Backend Server Must Be Running

The satellite images require the backend server to be running. 

### To Start Backend Server:

1. Open a terminal/PowerShell window
2. Navigate to the backend directory:
   ```powershell
   cd "C:\Users\Avi Kothari\Downloads\SuryaDrishti\avi_k_proj\backend"
   ```

3. Activate virtual environment (if using one):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Start the server:
   ```powershell
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Verify Backend is Running:

Open browser and go to: http://localhost:8000/docs

You should see the FastAPI documentation page.

### Test Satellite API:

Once backend is running, test the satellite endpoint:
```
http://localhost:8000/api/v1/satellite/image/with-clouds?lat=28.6139&lon=77.2090&radius_km=50
```

### Troubleshooting:

1. **Backend not starting?**
   - Check if port 8000 is already in use
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check for Python errors in the terminal

2. **Satellite images not loading?**
   - Open browser console (F12) and check for errors
   - Verify backend is running on port 8000
   - Check backend terminal for error messages
   - The system will fallback to mock data if APIs fail

3. **API Keys:**
   - Keys are configured in `backend/.env`
   - NASA Worldview works without API key (public WMS)
   - OpenWeatherMap requires API key (already configured)

### Current Configuration:
- USE_MOCK_DATA=False (will try real APIs first)
- NASA_API_KEY: configured
- OPENWEATHER_API_KEY: configured

The system will:
1. Try NASA Worldview first (public, no key needed)
2. Fallback to OpenWeatherMap (uses your API key)
3. Fallback to mock data if both fail





