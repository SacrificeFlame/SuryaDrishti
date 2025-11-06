#!/bin/bash

# SuryaDrishti - Startup Script
echo "=================================="
echo "  SuryaDrishti - Starting Server"
echo "=================================="

# Check if in correct directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if database exists
if [ ! -f "suryादrishti.db" ]; then
    echo "📊 Database not found. Initializing..."
    python3 scripts/setup_database.py
fi

# Check if models exist
if [ ! -f "data/models/irradiance_v1.pth" ]; then
    echo "🤖 Models not found. Training..."
    python3 train_models.py
fi

# Start server
echo ""
echo "🚀 Starting FastAPI server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

cd backend && python3 -m uvicorn app.main:app --reload

