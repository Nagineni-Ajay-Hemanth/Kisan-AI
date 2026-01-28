from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from torchvision import models, transforms, datasets
import torch.nn as nn
from PIL import Image
import torch.nn.functional as F
import io
import sqlite3
import os
from datetime import datetime

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

class UserLogin(BaseModel):
    mobile: str
    password: str

# --- Paths ---
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "PlantVillage")
MODEL_PATH = os.path.join(BASE_DIR, "models", "plant_disease_model.pth")
SOIL_DATASET_PATH = os.path.join(BASE_DIR, "datasets", "Soil Types")
SOIL_MODEL_PATH = os.path.join(BASE_DIR, "models", "soil_type_model.pth")

# --- Disease Model Setup ---
# Load dataset to get class names (Cached globally)
try:
    dataset = datasets.ImageFolder(DATASET_PATH)
    class_names = dataset.classes
except Exception as e:
    print(f"Warning: Could not load dataset from {DATASET_PATH}. Error: {e}")
    class_names = [] # Handle gracefully or crash if critical

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Load Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.efficientnet_b0(weights=None)
if class_names:
    num_classes = len(class_names)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("Model not fully initialized due to missing class names.")

# --- Soil Model Setup ---
try:
    soil_dataset = datasets.ImageFolder(SOIL_DATASET_PATH)
    soil_class_names = soil_dataset.classes
except Exception as e:
    print(f"Warning: Could not load soil dataset from {SOIL_DATASET_PATH}. Error: {e}")
    soil_class_names = []

soil_model = models.efficientnet_b0(weights=None)
if soil_class_names:
    num_soil_classes = len(soil_class_names)
    soil_model.classifier[1] = nn.Linear(soil_model.classifier[1].in_features, num_soil_classes)
    
    try:
        soil_model.load_state_dict(torch.load(SOIL_MODEL_PATH, map_location=device))
        soil_model.to(device)
        soil_model.eval()
        print("Soil Model loaded successfully.")
    except Exception as e:
        print(f"Error loading soil model: {e}")
else:
    print("Soil Model not fully initialized due to missing class names.")


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
        cursor.execute("INSERT INTO users (mobile, password, username) VALUES (?, ?, ?)", 
                       (user.mobile, user.password, user.username or user.mobile))
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
    if not class_names:
        return {"error": "Class names not loaded. Check server logs."}
        
    try:
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        img = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            out = model(img)
            probs = F.softmax(out, dim=1)
            conf, pred = torch.max(probs, 1)

        disease = class_names[pred.item()]
        confidence = conf.item()

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_results (user_id, test_type, result, confidence) VALUES (?, ?, ?, ?)",
            (user_id, 'disease', disease, confidence)
        )
        conn.commit()
        conn.close()

        return {"disease": disease, "confidence": confidence}
    except Exception as e:
        print(f"Error in prediction: {e}")
        return {"error": str(e)}

@app.post("/predict_soil")
async def predict_soil(file: UploadFile = File(...), user_id: int = Form(...)):
    if not soil_class_names:
        return {"error": "Soil class names not loaded. Check server logs."}
        
    try:
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        img = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            out = soil_model(img)
            probs = F.softmax(out, dim=1)
            conf, pred = torch.max(probs, 1)

        soil_type = soil_class_names[pred.item()]
        confidence = conf.item()

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_results (user_id, test_type, result, confidence) VALUES (?, ?, ?, ?)",
            (user_id, 'soil', soil_type, confidence)
        )
        conn.commit()
        conn.close()
        
        return {"soil_type": soil_type, "confidence": confidence}
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

    # crop would ideally come from user profile or selected in frontend. Defaulting to general.
    crop = "Wheat" 

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
