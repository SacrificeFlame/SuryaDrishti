# SuryaDrishti - Setup Instructions

## ⚠️ Python Not Found

Python is required to run this project. Please install it first.

## Option 1: Install Python (Recommended)

### Windows:
1. Download Python 3.11+ from: https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your terminal/PowerShell
4. Verify: `python --version`

### Or Install from Microsoft Store:
1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click Install
4. Restart terminal

## Option 2: Use Docker (If Docker is installed)

If you have Docker Desktop installed:
```powershell
docker-compose up -d
```

This will start:
- Backend API on http://localhost:8000
- Redis on port 6379
- Celery worker

## After Python is Installed

Run this script again, or manually:

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r backend\requirements.txt

# 4. Setup database
python scripts\setup_database.py

# 5. Train models (optional, takes time)
python train_models.py

# 6. Start backend
cd backend
python -m uvicorn app.main:app --reload
```

## Frontend Setup (After Python is working)

1. Install Node.js from: https://nodejs.org/
2. Then:
```powershell
cd frontend
npm install
npm run dev
```

Dashboard will be at: http://localhost:3000

