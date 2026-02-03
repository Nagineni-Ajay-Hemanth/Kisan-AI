@echo off
REM Quick setup script for Kisan-AI on Windows

echo ========================================
echo Kisan-AI Quick Setup for Windows
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env file and add your GEMINI_API_KEY
    echo Opening .env file in Notepad...
    notepad .env
    echo.
    echo After adding your API key, press any key to continue...
    pause >nul
)

echo [OK] Environment file exists
echo.

REM Start Docker Compose
echo Starting Kisan-AI with Docker Compose...
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Kisan-AI is now running!
    echo ========================================
    echo.
    echo Access points:
    echo - API: http://localhost:8000
    echo - Docs: http://localhost:8000/docs
    echo.
    echo To view logs: docker-compose logs -f
    echo To stop: docker-compose down
    echo.
) else (
    echo.
    echo [ERROR] Failed to start Docker Compose
    echo Please check the error messages above
    echo.
)

pause
