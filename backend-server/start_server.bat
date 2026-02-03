@echo off
REM Kisan-AI Backend Server Startup Script for Windows

echo ========================================
echo Starting Kisan-AI Backend Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found.
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo Dependencies installed.
echo.

REM Start the server
echo ========================================
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
