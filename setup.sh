#!/bin/bash
# SuryaDrishti Setup Script for Linux/Mac
# This script sets up the entire project

echo "========================================"
echo "SuryaDrishti Setup Script"
echo "========================================"
echo ""

# Check Python
echo "[1/6] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Found: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
echo "[2/6] Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Found: $NODE_VERSION"
    SKIP_FRONTEND=false
else
    echo "⚠️  Node.js not found. Frontend setup will be skipped."
    echo "   Install Node.js from https://nodejs.org/ to enable frontend"
    SKIP_FRONTEND=true
fi

# Create virtual environment
echo "[3/6] Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo "[4/6] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
echo "✅ Python dependencies installed"

# Setup database
echo "[5/6] Setting up database..."
$PYTHON_CMD scripts/setup_database.py
echo "✅ Database initialized"

# Setup frontend (if Node.js is available)
if [ "$SKIP_FRONTEND" = false ]; then
    echo "[6/6] Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "[6/6] Skipping frontend setup (Node.js not found)"
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Generate training data: python scripts/generate_sample_data.py"
echo "2. Train models: python train_models.py"
echo "3. Test system: python test_system.py"
echo "4. Start backend: cd backend && uvicorn app.main:app --reload"
if [ "$SKIP_FRONTEND" = false ]; then
    echo "5. Start frontend: cd frontend && npm run dev"
fi
echo ""

