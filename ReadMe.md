# Kisan-AI (FarmX) - Project Documentation

**Project Name:** Kisan-AI (FarmX)  
**Date:** 2026-02-05  
**Team:** Kisan AI Team  

---

# 📑 Table of Contents

1. [Chapter 1: Introduction](#chapter-1-introduction)
2. [Chapter 2: About The Project](#chapter-2-about-the-project)
3. [Chapter 3: Real World Problems & Solutions](#chapter-3-real-world-problems--solutions)
4. [Chapter 4: Tech Stack & Implementation](#chapter-4-tech-stack--implementation)
5. [Chapter 5: Conclusion](#chapter-5-conclusion)

---

# <a name="chapter-1-introduction"></a>Chapter 1: Introduction

## 1.1 Overview
Agriculture is the backbone of the Indian economy, employing a vast portion of the population. However, traditional farming methods are increasingly challenged by climate change, pest infestations, and soil degradation. **Kisan-AI (FarmX)** is a comprehensive digital assistant designed to revolutionize modern farming by bridging the gap between advanced technology and the traditional farmer.

## 1.2 Mission Statement
Our mission is to empower farmers with **Artificial Intelligence**. By providing tools for early disease detection, instant soil health analysis, and direct market access, we aim to increase crop yields, reduce input costs, and maximize profitability for the Indian farmer.

## 1.3 Scope of this Document
This document serves as detailed documentation for the Kisan-AI project. It covers the functional requirements, the real-world problems addressed, the technical architecture, and the implementation details of the software solution.

---

# <a name="chapter-2-about-the-project"></a>Chapter 2: About The Project

## 2.1 System Overview
Kisan-AI is a hybrid platform (Mobile & Web) that acts as a "Doctor for Crops". It leverages Deep Learning for visual analysis and Generative AI for personalized advice, creating a holistic ecosystem for agricultural management.

## 2.2 Functional Modules

### 🌿 Smart Disease Detection
The core feature of Kisan-AI is its ability to identify plant diseases from images.
- **Function**: Users take a photo of an affected leaf.
- **Process**: The system validates the leaf and runs it through a CNN model.
- **Output**: Instant diagnosis (e.g., "Wheat Rust") with a confidence score and treatment advice.

### 🧪 Soil Analysis & Lab
A virtual soil testing lab in the farmer's pocket.
- **Function**: Visual analysis of soil texture and color.
- **Process**: Uses computer vision to classify soil (e.g., Loamy, Red Clay) and geolocates the user to fetch auxiliary soil data.
- **Output**: Estimated NPK values and fertilizer recommendations.

### 🤖 AI Expert Advisor
A 24/7 personal agriculture consultant.
- **Description**: Unlike static FAQs, this module uses **Google Gemini GenAI** to generate context-aware advice.
- **Inputs**: It considers the farmer's specific crop, recent weather, and past disease history before answering queries.

### 🏪 Direct Marketplace
A platform to eliminate middlemen.
- **Farmer Role**: List produce with photos, set prices, and manage stock.
- **Customer Role**: Browse local produce, place orders, and track delivery.
- **Logistics**: The system calculates delivery charges based on GPS distance.

### 💬 Community Forum
A knowledge-sharing platform where farmers can post questions, share tips, and upvote helpful answers from peers.

## 2.3 User Roles
1.  **Farmer**: The primary user. Has access to all diagnostic tools, marketplace listing features, and community posting.
2.  **Customer**: The buyer. Has access to the marketplace to browse and purchase fresh produce directly from farmers.

---

# <a name="chapter-3-real-world-problems--solutions"></a>Chapter 3: Real World Problems & Solutions

## 3.1 Problem: Delayed Disease Detection
**The Challenge**: Farmers often identify diseases only when physical symptoms are severe. Sending samples to labs is time-consuming and expensive.
**The Solution (Kisan-AI)**: We implemented a custom **EfficientNet CNN model** trained on the PlantVillage dataset. This provides *instant* diagnosis (under 3 seconds) with high accuracy, allowing farmers to take preventive action immediately.

## 3.2 Problem: Lack of Soil Health Awareness
**The Challenge**: Soil testing infrastructure in India is overburdened. Farmers rely on guesswork for fertilizers, leading to soil degradation and wasted money.
**The Solution (Kisan-AI)**: Our **Soil Engine** uses colorimetry and texture analysis to provide an immediate approximation of soil health. While not a replacement for a chemical lab, it gives a "First Aid" report that helps in immediate decision-making regarding NPK ratios.

## 3.3 Problem: Exploitation by Middlemen
**The Challenge**: Farmers often sell their produce at a fraction of the market price due to lack of direct access to consumers.
**The Solution (Kisan-AI)**: The **Hyperlocal Marketplace** connects farmers directly with nearby customers (households, restaurants). The GPS-based "Delivery Charge Calculator" ensures the farmer is compensated for logistics, keeping the profit within the community.

## 3.4 Problem: Generic Advice
**The Challenge**: Government helplines often provide generic advice that doesn't account for local micro-climates or specific field history.
**The Solution (Kisan-AI)**: Our **Hybrid Expert System** specifically injects the user's *past* disease history and specific *current* weather into the prompt sent to the LLM. This ensures the advice is tailored specifically to *that* farmer's current situation.

---

# <a name="chapter-4-tech-stack--implementation"></a>Chapter 4: Tech Stack & Implementation

## 4.1 Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Backend** | Python, FastAPI | High-performance async API framework. |
| **Database** | SQLite | Lightweight relational database. |
| **AI (Vision)** | PyTorch, OpenCV | Used for Image Processing and CNN inference. |
| **AI (GenAI)** | Google Gemini 1.5 | Pro model for generating advisory text. |
| **Frontend** | HTML5, CSS3, JS | Vanilla implementation for maximum performance. |
| **Mobile** | Android (WebView) | Hybrid wrapper for the frontend. |
| **Infrastructure**| Docker | Containerization for consistent deployment. |

## 4.2 System Architecture
The system follows a modular Monolith architecture:
1.  **Client Layer**: Handles UI, Camera, and GPS.
2.  **API Layer (FastAPI)**: Routes requests, handles Authentication (JWT/Sessions), and validates data using Pydantic.
3.  **Logic Layer**: Contains the standalone engines (`plant_detection_engine.py`, `soil_engine.py`) that process complex tasks.
4.  **Data Layer**: Stores persistent data in `farmx.db`.

## 4.3 Database Schema (Key Entities)
*   **Users**: Stores profiles, language preferences, and crop types.
*   **Test_Results**: A historical log of every scan a farmer performs (Disease/Soil), used to track farm health over time.
*   **Products & Orders**: Transactional tables linking Farmers and Customers with GPS coordinate data for logistics.
*   **Community**: A structured Thread/Reply system.

## 4.4 API Implementation
The backend exposes a RESTful API. Key endpoints include:
*   `POST /predict`: Handles image upload, leaf validation, and inference.
*   `POST /auth/login-with-otp`: Secure entry without complex passwords.
*   `GET /get_user_advice/{id}`: Aggregates history + weather to prompt the AI.
*   `GET /recommend_fertilizer`: Algorithmic NPK calculator.

## 4.5 Testing Strategy
*   **Unit Tests**: `pytest` is used for backend logic verification.
*   **Leaf Validation**: A dedicated pre-check stage ensures users don't get random results if they upload non-plant images.
*   **Integration Tests**: Ensures the Database and API communicate correctly.

## 4.6 Deployment
The application is containerized using **Docker**.
*   **Dockerfile**: Defines the Python 3.10 environment and dependencies.
*   **Docker Compose**: Orchestrates the service, volume mapping (for DB persistence), and environment configuration.
*   **Android Build**: Uses Gradle to wrap the optimized frontend assets into an APK.

---

# <a name="chapter-5-conclusion"></a>Chapter 5: Conclusion

## 5.1 Summary
Kisan-AI successfully demonstrates how cutting-edge technology—Computer Vision, Generative AI, and GPS—can be democratized for the agricultural sector. By packaging these complex technologies into a simple, vernacular-friendly interface, we have created a tool that is not just technologically advanced but also socially impactful.

## 5.2 Future Scope
1.  **Offline Mode**: Implementing TensorFlow Lite models on-device to allow disease detection without internet.
2.  **IoT Integration**: Connecting with soil moisture sensors for real-time irrigation alerts.
3.  **Drone Support**: Analyzing aerial footage for large-scale farm monitoring.

## 5.3 Acknowledgments
Built by the **Kisan AI Team**.
Open Source under the Unlicense.

---
*End of Document*
