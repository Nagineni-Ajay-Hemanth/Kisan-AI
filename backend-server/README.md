# FarmX Backend Server

This is the backend server for the FarmX application. It handles all the heavy processing including:
- User authentication and database management
- Plant disease detection using ML models
- Soil type classification using ML models
- Fertilizer recommendations
- User advice generation based on test results

## Prerequisites

- Python 3.8 or higher
- At least 4GB RAM (for ML model inference)
- 5GB free disk space (for datasets and models)

## Quick Start

### 1. Start the Server

The easiest way to start the server is using the startup script:

```bash
./start_server.sh
```

This script will:
- Create a virtual environment (if it doesn't exist)
- Install all dependencies
- Start the FastAPI server on port 8000

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Accessing the Server

Once started, the server will be available at:
- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## Exposing to the Internet

To allow your frontend (hosted on a website) to access this backend running on your local machine, you need to expose it to the internet. Here are your options:

### Option 1: ngrok (Recommended for Testing)

1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 8000`
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Update your frontend's `config.js` with this URL

### Option 2: Cloudflare Tunnel (Free, Permanent)

1. Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
2. Run: `cloudflared tunnel --url http://localhost:8000`
3. Copy the provided URL
4. Update your frontend's `config.js` with this URL

### Option 3: localtunnel

```bash
npx localtunnel --port 8000
```

### Option 4: Port Forwarding (Advanced)

1. Configure port forwarding on your router (port 8000)
2. Find your public IP address
3. Use `http://YOUR_PUBLIC_IP:8000` as the backend URL
4. **Important**: Ensure proper firewall and security measures

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with mobile and password
- `POST /auth/send-otp` - Send OTP to mobile
- `POST /auth/login-with-otp` - Login with OTP

### Predictions
- `POST /predict` - Detect plant disease from image
- `POST /predict_soil` - Detect soil type from image

### Recommendations
- `GET /recommend_fertilizer?crop={crop}&soil_type={soil_type}` - Get fertilizer recommendations
- `GET /get_user_advice/{user_id}` - Get personalized advice based on user's test results

## Directory Structure

```
backend-server/
├── main.py                 # FastAPI application
├── models/                 # ML model files
│   ├── plant_disease_model.pth
│   └── soil_type_model.pth
├── datasets/               # Training datasets for class names
│   ├── PlantVillage/
│   └── Soil Types/
├── database/               # SQLite database
│   └── farmx.db
├── requirements.txt        # Python dependencies
├── start_server.sh         # Startup script
└── README.md              # This file
```

## Database

The application uses SQLite database (`database/farmx.db`) with the following tables:

### users
- `id` (INTEGER, PRIMARY KEY)
- `mobile` (TEXT, UNIQUE)
- `password` (TEXT)
- `username` (TEXT)

### test_results
- `id` (INTEGER, PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY)
- `test_type` (TEXT: 'disease' or 'soil')
- `result` (TEXT)
- `confidence` (REAL)
- `timestamp` (DATETIME)

## Security Considerations

> **⚠️ IMPORTANT**: This server is configured for development. For production:

1. **CORS**: Update `main.py` to specify your frontend domain instead of `allow_origins=["*"]`
2. **HTTPS**: Use a reverse proxy (nginx) with SSL certificate
3. **Authentication**: Implement JWT tokens or session management
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Firewall**: Configure firewall rules properly
6. **Environment Variables**: Move sensitive config to environment variables

## Troubleshooting

### Models not loading
- Ensure `.pth` files are in the `models/` directory
- Check that datasets are in `datasets/` directory (needed for class names)

### Database errors
- Ensure `database/farmx.db` exists and has write permissions
- The database will be created automatically on first run

### Port already in use
- Change the port in `start_server.sh`: `--port 8001`
- Or kill the process using port 8000: `lsof -ti:8000 | xargs kill`

### CORS errors from frontend
- Ensure CORS is configured correctly in `main.py`
- Check that the frontend is using the correct backend URL

## Support

For issues or questions, check the main FarmX documentation or API documentation at `/docs`.
