# FarmX Frontend

This is the frontend website for FarmX - a smart farming application. The frontend is a static website (HTML, CSS, JavaScript) that can be deployed to any web hosting service.

## Features

- 🌾 Plant disease detection
- 🌱 Soil type classification
- 💡 Expert farming advice
- 🌦️ Weather information
- 💰 Market prices
- 🛡️ Crop protection tips
- 🌍 Multi-language support (English, Hindi, Telugu)

## Configuration

### Setting Up Backend Connection

Before deploying, you **must** configure the backend API URL:

1. Open `shared/config.js`
2. Update the `API_URL` with your backend server address:

```javascript
window.FARMX_CONFIG = {
    API_URL: "https://your-backend-url.com",  // Change this!
    DEBUG: false
};
```

**Backend URL Options:**
- Local testing: `http://localhost:8000`
- ngrok tunnel: `https://abc123.ngrok.io`
- Cloudflare tunnel: `https://your-tunnel.trycloudflare.com`
- Custom domain: `https://api.yourdomain.com`

## Deployment Options

### Option 1: Netlify (Recommended)

1. Create account at [netlify.com](https://www.netlify.com)
2. Drag and drop the `frontend` folder to Netlify
3. Your site will be live in seconds!

**Or using Netlify CLI:**
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod
```

### Option 2: Vercel

1. Create account at [vercel.com](https://vercel.com)
2. Install Vercel CLI: `npm install -g vercel`
3. Deploy:
```bash
cd frontend
vercel --prod
```

### Option 3: GitHub Pages

1. Create a GitHub repository
2. Push the `frontend` folder contents
3. Go to Settings → Pages
4. Select branch and folder
5. Your site will be at `https://username.github.io/repo-name`

### Option 4: Any Static Host

The frontend is pure HTML/CSS/JS, so it works with any static hosting:
- Firebase Hosting
- Cloudflare Pages
- AWS S3 + CloudFront
- Azure Static Web Apps
- Surge.sh
- Render

Simply upload the contents of the `frontend` folder.

## Local Testing

To test locally before deployment:

### Using Python
```bash
cd frontend
python3 -m http.server 8080
```
Then visit: `http://localhost:8080`

### Using Node.js
```bash
cd frontend
npx http-server -p 8080
```

### Using PHP
```bash
cd frontend
php -S localhost:8080
```

## File Structure

```
frontend/
├── index.html              # Homepage/Dashboard
├── auth/
│   └── login.html         # Login/Register page
├── disease/
│   └── index.html         # Disease detection
├── fertilizer/
│   └── index.html         # Fertilizer recommendations
├── weather/
│   └── index.html         # Weather information
├── advice/
│   └── index.html         # Expert advice
├── market/
│   └── index.html         # Market prices
├── protect/
│   └── index.html         # Crop protection
└── shared/
    ├── config.js          # ⚠️ Configure backend URL here
    ├── api-client.js      # API communication
    ├── style.css          # Global styles
    ├── translations.js    # Multi-language support
    ├── language-manager.js
    ├── auth-guard.js
    └── assets/            # Images and icons
```

## Important Notes

### CORS Configuration

Make sure your backend server allows requests from your frontend domain. In the backend's `main.py`, update:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Your deployed URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### HTTPS Requirement

For security, especially if using features like camera access, deploy to HTTPS. All the recommended hosting services provide free HTTPS.

### Browser Compatibility

The app works on:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Customization

### Changing Colors/Theme

Edit `shared/style.css` and modify the CSS variables:

```css
:root {
    --primary: #4CAF50;
    --secondary: #2196F3;
    /* ... other variables */
}
```

### Adding Languages

1. Add translations in `shared/translations.js`
2. Add language button in `shared/language-manager.js`

## Troubleshooting

### "Failed to fetch" errors
- Check that `config.js` has the correct backend URL
- Ensure backend server is running and accessible
- Check browser console for CORS errors

### Images not loading
- Verify all image paths are relative
- Check that `shared/assets/` folder has all images

### Login not working
- Verify backend URL in `config.js`
- Check backend server logs
- Ensure database is initialized

## Support

For backend setup, see `backend-server/README.md`

## License

FarmX © 2026
