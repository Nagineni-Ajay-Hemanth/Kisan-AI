from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sqlite3
import os
from datetime import datetime

import cv2
import numpy as np
import sys


# Import new logic engine
from logic.plant_detection_engine import AutoPlantDiseaseDetector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Database Setup ---
from database import init_db, get_db_connection

# Initialize DB on startup
init_db()

# --- Models ---
class UserRegister(BaseModel):
    mobile: str
    password: str
    username: str = None
    city: str = None
    state: str = None
    crop: str = "Wheat"
    language: str = "en"

class UserLogin(BaseModel):
    mobile: str
    password: str

# --- Paths ---
# --- Paths ---
# DATASET_PATH = os.path.join(BASE_DIR, "datasets", "PlantVillage") # Removed
# MODEL_PATH = os.path.join(BASE_DIR, "models", "plant_disease_model.pth") # Removed


# --- Initialize Plant Detector Engine ---
plant_detector = AutoPlantDiseaseDetector()

# --- Disease Model Setup ---
# --- Disease Model Setup ---
# Legacy PyTorch model code removed. Using AutoPlantDiseaseDetector instead.
# Class names are now handled by the engine's database.



# Load Model (Legacy Removed)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = models.efficientnet_b0(weights=None) ...

# --- Soil Engine Setup ---
from logic.soil_engine import SoilEngine

try:
    soil_engine = SoilEngine()
    print("Soil Engine initialized successfully.")
except Exception as e:
    print(f"Error initializing Soil Engine: {e}")
    soil_engine = None



# --- Auth Endpoints ---
import random

# In-memory OTP Cache (for demo purposes)
OTP_CACHE = {}

class OTPRequest(BaseModel):
    mobile: str

class OTPLogin(BaseModel):
    mobile: str
    otp: str

@app.post("/auth/send-otp")
def send_otp(req: OTPRequest):
    # Check if user exists (Optional: can also allow OTP for registration)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (req.mobile,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        # For this demo, let's allow OTP only for existing users, 
        # or we could auto-create. Let's stick to "Login" semantic.
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    # Generate 4-digit OTP
    otp = str(random.randint(1000, 9999))
    OTP_CACHE[req.mobile] = otp
    
    print(f"DEMO OTP for {req.mobile}: {otp}") # Print to console for verification
    
    return {"message": "OTP sent successfully", "otp": otp} # Returning OTP for Easy Testing

@app.post("/auth/login-with-otp")
def login_with_otp(req: OTPLogin):
    # Verify OTP
    stored_otp = OTP_CACHE.get(req.mobile)
    if not stored_otp or stored_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Get User
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (req.mobile,))
    user_data = cursor.fetchone()
    conn.close()
    
    # Clear OTP after use
    if req.mobile in OTP_CACHE:
        del OTP_CACHE[req.mobile]
        
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Login successful", 
        "user_id": user_data["id"], 
        "username": user_data["username"]
    }

@app.post("/auth/register")
def register(user: UserRegister):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (mobile, password, username, city, state, crop, language) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (user.mobile, user.password, user.username or user.mobile, user.city, user.state, user.crop, user.language))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    finally:
        conn.close()

@app.post("/auth/login")
def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (user.mobile,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data or user_data["password"] != user.password:
         raise HTTPException(status_code=401, detail="Invalid credentials")
         
    return {
        "message": "Login successful", 
        "user_id": user_data["id"], 
        "username": user_data["username"]
    }

# --- Prediction Endpoints ---

@app.post("/predict")
async def predict(file: UploadFile = File(...), user_id: int = Form(...)):
    try:
        # Read image
        image_data = await file.read()
        
        # Convert to CV2 format
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             return {"error": "Could not decode image"}

        # Analyze using the new engine
        # We pass the filename for logging purposes in the engine
        analysis_result = plant_detector.analyze_image(img, image_name=file.filename)
        
        # Extract keys for API response/DB
        # The engine returns a rich structure. We default to:
        # result='Healthy' or Disease Name
        # confidence=float
        
        diseases = analysis_result.get("disease_diagnosis", [])
        plant_type = analysis_result.get("plant_identification", {}).get("identified_as", "Unknown")
        
        primary_disease = "Unknown"
        confidence = 0.0
        
        if diseases:
             primary_disease = diseases[0]['name']
             # Confidence might be a string "High"/"Medium" or float depending on engine logic
             # Engine logic: confidence: "High" or "Medium". 
             # Let's map it to float for DB compatibility if needed, or keep string?
             # Old DB expected confidence as REAL (float).
             # Let's try to parse or just assign 0.9 for High, 0.5 for Medium
             
             conf_str = diseases[0].get('confidence', 'Low')
             if conf_str == 'High': confidence = 0.95
             elif conf_str == 'Medium': confidence = 0.75
             elif conf_str == 'Low': confidence = 0.40
             elif isinstance(conf_str, (int, float)): confidence = float(conf_str)
             else: confidence = 0.5
        else:
             primary_disease = "Healthy"
             confidence = 0.99
             
        # Save to DB (Legacy table for compatibility with history)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_results (user_id, test_type, result, confidence) VALUES (?, ?, ?, ?)",
            (user_id, 'disease', primary_disease, confidence)
        )
        conn.commit()
        conn.close()

        # We return the simple response as before, OR the full rich response?
        # The frontend likely expects {disease, confidence}.
        # But we can also return everything if the frontend can handle it.
        # Let's return the old keys + a 'details' key with full report.
        
        return {
            "disease": primary_disease, 
            "confidence": confidence,
            "plant": plant_type,
            "details": analysis_result
        }
            
    except Exception as e:
        print(f"Error in prediction: {e}")
        return {"error": str(e)}

@app.post("/predict_soil")
async def predict_soil(
    file: UploadFile = File(...), 
    user_id: int = Form(...),
    lat: float = Form(None),
    lon: float = Form(None)
):
    if not soil_engine:
        return {"error": "Soil Engine not initialized."}
        
    try:
        # Read image
        image_data = await file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             return {"error": "Could not decode image"}

        # Process using Soil Engine
        result = soil_engine.process(img, lat, lon)
        
        soil_type = result['soil_type']
        confidence = result['confidence']

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_results (user_id, test_type, result, confidence) VALUES (?, ?, ?, ?)",
            (user_id, 'soil', soil_type, confidence)
        )
        conn.commit()
        conn.close()
        
        return result
    except Exception as e:
        print(f"Error in soil prediction: {e}")
        return {"error": str(e)}

@app.get("/recommend_fertilizer")
def recommend_fertilizer(crop: str, soil_type: str):
    from logic.fertilizer import recommend_fertilizer_logic
    recommendations = recommend_fertilizer_logic(crop, soil_type)
    return {"recommendations": recommendations}

@app.get("/get_user_advice/{user_id}")
def get_user_advice(user_id: int, lat: float = None, lon: float = None, language: str = "en"):
    # Import locally to avoid circular deps if any (though not expected here)
    from ai_advice import AgriAdvisor
    from weather_engine import WeatherEngine

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # --- Fetch History for "Past" vs "Present" comparison ---
    # We want the 2 most recent DISTINCT results for disease
    cursor.execute("""
        SELECT result, timestamp 
        FROM test_results 
        WHERE user_id = ? AND test_type = 'disease' 
        ORDER BY timestamp DESC LIMIT 2
    """, (user_id,))
    disease_rows = cursor.fetchall()
    
    # We want the 2 most recent DISTINCT results for soil
    cursor.execute("""
        SELECT result, timestamp 
        FROM test_results 
        WHERE user_id = ? AND test_type = 'soil' 
        ORDER BY timestamp DESC LIMIT 2
    """, (user_id,))
    soil_rows = cursor.fetchall()
    
    cursor.execute("""
        SELECT crop FROM users WHERE id = ?
    """, (user_id,))
    user_data_row = cursor.fetchone()
    user_crop = user_data_row["crop"] if user_data_row and user_data_row["crop"] else "Wheat"
    
    conn.close()
    
    # --- Prepare Input Data for AI ---
    
    # Defaults
    present_plant_condition = "Unknown"
    past_plant_condition = "Unknown"
    present_soil_type = "Unknown"
    past_soil_type = "Unknown"
    
    # Parse Disease
    if disease_rows:
        present_plant_condition = disease_rows[0]["result"]
        if len(disease_rows) > 1:
            past_plant_condition = disease_rows[1]["result"]
        else:
            # If only 1 record, assume past was same or unknown. Let's say Unknown to trigger "New condition" logic maybe?
            # Or just set same. Let's set 'Unknown' to imply no history.
            past_plant_condition = "Unknown" 

    # Parse Soil
    if soil_rows:
        present_soil_type = soil_rows[0]["result"]
        if len(soil_rows) > 1:
            past_soil_type = soil_rows[1]["result"]
        else:
             past_soil_type = "Unknown"

    # --- Fetch Real Weather if Location Provided ---
    present_weather = "Sunny, 25°C" # Default Fallback
    if lat is not None and lon is not None:
        try:
            weather_data = WeatherEngine.get_weather(lat, lon)
            # Format: "Condition, Temp°C" e.g., "Cloudy, 24°C"
            present_weather = f"{weather_data['condition']}, {weather_data['temperature']}°C"
        except Exception as e:
            print(f"Error fetching weather for advice: {e}")

    # Crop from User Profile
    crop = user_crop 

    input_data = {
        "past_soil_type": past_soil_type,
        "past_plant_condition": past_plant_condition,
        "present_soil_type": present_soil_type,
        "present_plant_condition": present_plant_condition,
        "present_weather": present_weather,
        "crop": crop,
        "language": language
    }
    
    # --- Check for Missing Data ---
    missing_fields = []
    if present_plant_condition == "Unknown":
        missing_fields.append("disease")
    if present_soil_type == "Unknown":
        missing_fields.append("soil")

    if missing_fields:
        return {
            "status": "incomplete",
            "missing": missing_fields,
            "disease": present_plant_condition,
            "soil": present_soil_type
        }

    # --- Generate Advice ---
    advice_output = AgriAdvisor.generate_advice(input_data)
    
    # Enrich with metadata for frontend display (Cleaned)
    advice_output["disease"] = present_plant_condition.replace("___", " ").replace("_", " ")
    advice_output["soil"] = present_soil_type.replace("___", " ").replace("_", " ")
    advice_output["status"] = "complete" 
    
    return advice_output


    return advice_output

@app.get("/api/weather")
def get_weather(lat: float, lon: float):
    from weather_engine import WeatherEngine
    return WeatherEngine.get_weather(lat, lon)

@app.get("/")
def read_root():
    return {"message": "FarmX Disease Detection API is running"}
