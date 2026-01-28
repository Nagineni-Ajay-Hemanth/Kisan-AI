<div align="center">

# 🌾 Kisan AI (FarmX)
### *Empowering Farmers with Artificial Intelligence*

[![Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red)](https://pytorch.org/)
[![Android](https://img.shields.io/badge/Platform-Android-green)](https://www.android.com/)

[Features](#-features) •
[Tech Stack](#-tech-stack) •
[Installation](#-installation-guide) •
[Team](#-team)

</div>

---

## 📖 About The Project

**Kisan AI** (also known as FarmX) is a comprehensive digital assistant designed to revolutionize modern farming. By leveraging **Deep Learning** architecture, it helps farmers detect crop diseases early, analyze soil health, and receive personalized agricultural advice in their local language.

Our mission is to bridge the gap between technology and traditional farming, increasing yield and profitability for the indian farmer.

## 🚀 Features

### 🌿 Smart Disease Detection
Instantly identify crop diseases by simply uploading a photo of the affected leaf. Powered by a custom-trained **CNN (EfficientNet)** model.

### 🧪 Soil Analysis & Fertilizers
Analyze soil type from images and get precise **NPK fertilizer recommendations** tailored to your specific crop and soil conditions.

### 🤖 AI Expert Advice
A hybrid **Rule-Based + GenAI** expert system that provides holistic farming advice. It considers:
- Past & Present Soil Health
- Disease History
- Real-time Weather Data

### 🌦️ Weather & Water Planning
- **Real-time Forecasts**: Hyper-local weather updates.
- **Smart Irrigation**: Calculates exact water requirements based on crop age and recent rainfall.

### 🏪 Marketplace & Schemes
- **Direct Marketplace**: Connects farmers directly to buyers.
- **Govt Schemes**: Latest information on agricultural subsidies and schemes.

### 🗣️ Multi-Language Support
Full support for Indian languages including **Hindi (हिंदी), Telugu (తెలుగు), Tamil (தமிழ்), Kannada (ಕನ್ನಡ)**, and more, ensuring accessibility for every farmer.

---

## 🛠️ Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Backend** | Python, FastAPI, Uvicorn, SQLite |
| **AI/ML** | PyTorch, TorchVision, EfficientNet, Google GenAI |
| **Frontend** | HTML5, CSS3 (Modern/Glassmorphism), JavaScript (ES6+) |
| **Mobile** | Android (Kotlin/Java + WebView), Gradle |
| **Infrastructure** | Cloudflare Tunnel (for secure remote access) |

---

## 💻 Installation Guide

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend-server

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
./start_server.sh
```

### 2. Frontend Configuration

The frontend is designed to run embedded within the Android app or hosted statically.

1.  Ensure the backend is running.
2.  Update `frontend/shared/api-client.js` with your backend URL (e.g., Cloudflare URL or Localhost).

### 3. Android App Build

```bash
# Navigate to Android project
cd KisanAI

# Set Java Home (Adjust path to your JBR/JDK)
export JAVA_HOME="/opt/android-studio/jbr"

# Build Debug APK
./gradlew assembleDebug

# Install on Device via ADB
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 📸 Screenshots

| Dashboard | Disease Scan | Expert Advice |
|:---:|:---:|:---:|
| ![Dashboard]([https://placehold.co/200x400/2ecc71/ffffff?text=Dashboard](https://github.com/Nagineni-Ajay-Hemanth/Kisan-AI/blob/main/assets/WhatsApp%20Image%202026-01-29%20at%201.17.26%20AM.jpeg)) | ![Disease](https://placehold.co/200x400/e74c3c/ffffff?text=Scan) | ![Advice](https://placehold.co/200x400/3498db/ffffff?text=Advice) |


---

## 👥 Team

Built with ❤️ by the Kisan AI Team:

*   **B.Sreehitha**
*   **N.Ajay Hemanth**
*   **D.Hansika**
*   **A.Ruchitha**
*   **S.Bhagya Sree**
*   **Ch.Sugreshwar**

---

## 📜 License
This project is open-source and available under the [Unlicense](http://unlicense.org/).
