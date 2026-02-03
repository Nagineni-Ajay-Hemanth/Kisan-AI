# Kisan-AI Development Setup Guide

Complete guide for setting up the Kisan-AI project on any platform (Windows, Linux, macOS).

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Windows Setup](#windows-setup)
- [Linux/macOS Setup](#linuxmacos-setup)
- [Docker Setup (Recommended)](#docker-setup-recommended)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Git** - Version control
   - Windows: [Download Git for Windows](https://git-scm.com/download/win)
   - Linux: `sudo apt install git`
   - macOS: `brew install git`

2. **Python 3.10+** - Backend runtime
   - Windows: [Download Python](https://www.python.org/downloads/)
   - Linux: `sudo apt install python3.10 python3.10-venv`
   - macOS: `brew install python@3.10`

3. **Docker Desktop** (Recommended)
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: `sudo apt install docker.io docker-compose`
   - macOS: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

4. **Android Studio** (For mobile app development)
   - All platforms: [Download Android Studio](https://developer.android.com/studio)

### Optional Tools

- **VS Code**: [Download](https://code.visualstudio.com/)
- **Postman**: For API testing
- **Git GUI**: GitHub Desktop, GitKraken, etc.

---

## Windows Setup

### 1. Clone Repository

```powershell
# Open PowerShell or Command Prompt
cd C:\Users\YourUsername\Documents
git clone https://github.com/Nagineni-Ajay-Hemanth/Kisan-AI.git
cd Kisan-AI
```

### 2. Backend Setup (Traditional Method)

```powershell
# Navigate to backend
cd backend-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Backend Setup (Docker Method - Recommended)

```powershell
# Install Docker Desktop first, then:
cd C:\Users\YourUsername\Documents\Kisan-AI

# Copy environment template
copy .env.example .env

# Edit .env file with Notepad
notepad .env
# Add your GEMINI_API_KEY

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access API at http://localhost:8000/docs
```

### 4. Android App Setup

```powershell
# Open Android Studio
# File > Open > Navigate to Kisan-AI/KisanAI

# Set JAVA_HOME (if needed)
$env:JAVA_HOME="C:\Program Files\Android\Android Studio\jbr"

# Build from command line (optional)
cd KisanAI
.\gradlew assembleDebug

# APK location:
# KisanAI\app\build\outputs\apk\debug\app-debug.apk
```

---

## Linux/macOS Setup

### 1. Clone Repository

```bash
cd ~/Desktop
git clone https://github.com/Nagineni-Ajay-Hemanth/Kisan-AI.git
cd Kisan-AI
```

### 2. Backend Setup (Traditional Method)

```bash
# Navigate to backend
cd backend-server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Backend Setup (Docker Method - Recommended)

```bash
# Install Docker
sudo apt install docker.io docker-compose  # Ubuntu/Debian
# OR
brew install docker docker-compose  # macOS

# Setup
cd ~/Desktop/Kisan-AI
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 4. Android App Setup

```bash
# Open Android Studio
# File > Open > Navigate to Kisan-AI/KisanAI

# Set JAVA_HOME
export JAVA_HOME="/opt/android-studio/jbr"

# Build from command line
cd KisanAI
./gradlew assembleDebug

# Install on device
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## Docker Setup (Recommended)

Docker provides the most consistent development experience across all platforms.

### Installation

**Windows:**
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Install and restart
3. Enable WSL 2 backend (recommended)

**Linux:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # Logout and login
```

**macOS:**
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Nagineni-Ajay-Hemanth/Kisan-AI.git
cd Kisan-AI

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Start everything
docker-compose up -d

# 4. Access API
# http://localhost:8000
# http://localhost:8000/docs
```

### Docker Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after changes
docker-compose up -d --build

# Check status
docker-compose ps

# Execute commands in container
docker-compose exec backend bash
```

---

## Development Workflow

### Daily Development

1. **Start Backend**
   ```bash
   # Docker (recommended)
   docker-compose up -d
   
   # OR Traditional
   cd backend-server
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   uvicorn main:app --reload
   ```

2. **Make Changes**
   - Edit code in your favorite IDE
   - Changes auto-reload with `--reload` flag

3. **Test API**
   - Open http://localhost:8000/docs
   - Test endpoints with Swagger UI

4. **Build Android App**
   - Open project in Android Studio
   - Click "Run" or use Gradle commands

### Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
WEATHER_API_KEY=your_weather_api_key_here
PORT=8000
DEBUG=false
```

### Getting API Keys

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env`

**Weather API Key** (Optional):
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add to `.env`

---

## Project Structure

```
Kisan-AI/
├── backend-server/          # FastAPI backend
│   ├── main.py             # Main application
│   ├── database.py         # Database setup
│   ├── requirements.txt    # Python dependencies
│   ├── logic/              # AI/ML engines
│   │   ├── plant_detection_engine.py
│   │   ├── soil_engine.py
│   │   └── fertilizer.py
│   └── farmx.db           # SQLite database
│
├── KisanAI/                # Android application
│   ├── app/
│   │   └── src/main/assets/  # Frontend HTML/CSS/JS
│   └── build.gradle
│
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
└── ReadMe.md              # Project documentation
```

---

## Troubleshooting

### Windows-Specific Issues

**Python not found:**
- Ensure Python is added to PATH during installation
- Restart terminal after installation

**Permission denied on scripts:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Docker not starting:**
- Enable Virtualization in BIOS
- Enable WSL 2 feature
- Restart Docker Desktop

### Linux-Specific Issues

**Permission denied on Docker:**
```bash
sudo usermod -aG docker $USER
# Logout and login
```

**Port already in use:**
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

### Common Issues

**Module not found:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**Database locked:**
```bash
# Stop all running instances
# Delete farmx.db and restart (will recreate)
```

**API key errors:**
- Verify `.env` file exists
- Check for typos in variable names
- Ensure no quotes around values in `.env`

---

## IDE Setup

### VS Code (Recommended)

**Extensions:**
- Python
- Docker
- GitLens
- Android iOS Emulator

**Settings:**
```json
{
  "python.defaultInterpreterPath": "./backend-server/venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. Open `backend-server` as project
2. Configure Python interpreter to use `venv`
3. Mark `logic` as sources root

---

## Testing

### Backend API Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
cd backend-server
pytest tests.py
```

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/

# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"mobile":"1234567890","password":"test123","user_type":"farmer"}'
```

---

## Deployment

### Local Development
- Use Docker Compose for consistent environment
- Access at http://localhost:8000

### Production Deployment

**Cloud Platforms:**
- AWS: ECS, Fargate, EC2
- Google Cloud: Cloud Run, GKE
- Azure: Container Instances, AKS
- Heroku, Railway, Render

**Steps:**
1. Build Docker image
2. Push to container registry
3. Deploy to cloud platform
4. Configure environment variables
5. Set up domain and SSL

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Android Development](https://developer.android.com/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

## Support

For issues or questions:
1. Check this setup guide
2. Review [ReadMe.md](ReadMe.md)
3. Check [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
4. Open an issue on GitHub

---

**Happy Coding! 🚀**
