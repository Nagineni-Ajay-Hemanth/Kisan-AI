#!/bin/bash

# FarmX Backend Server Startup Script

echo "Starting FarmX Backend Server..."
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Start the server
echo "🚀 Starting FastAPI server..."
echo "Backend will be available at: http://0.0.0.0:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
