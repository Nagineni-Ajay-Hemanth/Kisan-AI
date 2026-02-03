#!/bin/bash
# Docker entrypoint script for Kisan-AI backend

set -e

echo "🌾 Starting Kisan-AI Backend Server..."
echo "========================================"

# Check if database exists, if not initialize it
if [ ! -f "/app/farmx.db" ]; then
    echo "📊 Initializing database..."
    python -c "from database import init_db; init_db()"
    echo "✓ Database initialized"
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set. AI Advice feature will not work."
fi

# Check if HWSD2.mdb exists
if [ ! -f "/app/HWSD2.mdb" ]; then
    echo "⚠️  WARNING: HWSD2.mdb not found. Soil analysis may be limited."
fi

echo ""
echo "🚀 Starting FastAPI server on port ${PORT:-8000}..."
echo "API Documentation: http://localhost:${PORT:-8000}/docs"
echo "========================================"
echo ""

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
