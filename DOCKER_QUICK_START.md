# Kisan-AI Docker Quick Reference

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install Docker (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # Then logout and login

# 2. Configure environment
cd /home/ajay/Desktop/Kisan-AI
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# 3. Run!
docker-compose up -d
```

## 📋 Essential Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f backend

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# Status
docker-compose ps
```

## 🌐 Access Points

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/

## 📁 Files Created

1. `Dockerfile` - Container build configuration
2. `docker-compose.yml` - Orchestration setup
3. `.dockerignore` - Build optimization
4. `.env.example` - Environment template
5. `docker-entrypoint.sh` - Startup script
6. `ReadMe.md` - Updated with Docker section

## ⚙️ Environment Variables

Required in `.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
PORT=8000
DEBUG=false
```

## 🔍 Troubleshooting

**Container won't start?**
```bash
docker-compose logs backend
```

**Port already in use?**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

**Database issues?**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## 📦 What's Included

✅ Multi-stage optimized Dockerfile  
✅ Docker Compose orchestration  
✅ Database persistence (SQLite + HWSD)  
✅ Health checks  
✅ Auto-restart on failure  
✅ Environment variable support  
✅ Production-ready configuration  

## 🎯 Next Steps

1. Install Docker if not already installed
2. Add your GEMINI_API_KEY to `.env`
3. Run `docker-compose up -d`
4. Access API at http://localhost:8000/docs
5. Deploy to cloud platform of choice

## 📚 Full Documentation

See [walkthrough.md](file:///home/ajay/.gemini/antigravity/brain/8c1af0cd-6439-41fe-84b5-fc72f3196791/walkthrough.md) for complete details.
