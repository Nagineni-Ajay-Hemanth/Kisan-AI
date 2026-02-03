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
from utils import calculate_distance

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
    user_type: str = "farmer"

class UserLogin(BaseModel):
    mobile: str
    password: str

# Marketplace Models
class ProductCreate(BaseModel):
    name: str
    category: str = None
    price: float
    unit: str = "kg"
    quantity_available: float
    description: str = None
    image_url: str = None

class OrderCreate(BaseModel):
    product_id: int
    quantity: float
    customer_lat: float = None
    customer_lon: float = None

class OrderAccept(BaseModel):
    farmer_lat: float
    farmer_lon: float

class PaymentProcess(BaseModel):
    order_id: int
    payment_method: str  # 'cod' or 'full'
    amount: float


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
        "username": user_data["username"],
        "user_type": user_data["user_type"] if "user_type" in user_data.keys() else "farmer"
    }

@app.post("/auth/register")
def register(user: UserRegister):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Validate user_type
        if user.user_type not in ['farmer', 'customer']:
            raise HTTPException(status_code=400, detail="Invalid user_type. Must be 'farmer' or 'customer'")
        
        cursor.execute("INSERT INTO users (mobile, password, username, city, state, crop, language, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (user.mobile, user.password, user.username or user.mobile, user.city, user.state, user.crop, user.language, user.user_type))
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
        "username": user_data["username"],
        "user_type": user_data["user_type"] if "user_type" in user_data.keys() else "farmer"
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
             if conf_str == 'High': confidence = 0.50
             elif conf_str == 'Medium': confidence = 0.45
             elif conf_str == 'Low': confidence = 0.40
             elif isinstance(conf_str, (int, float)): confidence = float(conf_str)
             else: confidence = 0.42
        else:
             primary_disease = "Healthy"
             confidence = 0.48
             
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

# ===========================
# MARKETPLACE ENDPOINTS
# ===========================

# --- Products ---
@app.post("/products/create")
def create_product(product: ProductCreate, user_id: int):
    """Farmer creates a new product"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (farmer_id, name, category, price, unit, quantity_available, description, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, product.name, product.category, product.price, product.unit, 
              product.quantity_available, product.description, product.image_url))
        conn.commit()
        product_id = cursor.lastrowid
        return {"message": "Product created successfully", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/products/list")
def list_products(category: str = None):
    """List all available products"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if category:
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.status = 'available' AND p.category = ?
            ORDER BY p.created_at DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.status = 'available'
            ORDER BY p.created_at DESC
        """)
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"products": products}

@app.get("/products/farmer/{farmer_id}")
def get_farmer_products(farmer_id: int):
    """Get all products for a specific farmer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE farmer_id = ? ORDER BY created_at DESC", (farmer_id,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"products": products}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductCreate, user_id: int):
    """Update product details"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Verify ownership
        cursor.execute("SELECT farmer_id FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()
        if not result or result["farmer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cursor.execute("""
            UPDATE products 
            SET name=?, category=?, price=?, unit=?, quantity_available=?, description=?, image_url=?
            WHERE id=?
        """, (product.name, product.category, product.price, product.unit, 
              product.quantity_available, product.description, product.image_url, product_id))
        conn.commit()
        return {"message": "Product updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/products/{product_id}")
def delete_product(product_id: int, user_id: int):
    """Delete a product"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Verify ownership
        cursor.execute("SELECT farmer_id FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()
        if not result or result["farmer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cursor.execute("UPDATE products SET status='deleted' WHERE id=?", (product_id,))
        conn.commit()
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# --- Orders ---
@app.post("/orders/create")
def create_order(order: OrderCreate, user_id: int):
    """Customer creates an order"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get product details
        cursor.execute("SELECT * FROM products WHERE id = ?", (order.product_id,))
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product["quantity_available"] < order.quantity:
            raise HTTPException(status_code=400, detail="Insufficient quantity available")
        
        # Calculate product price
        product_price = product["price"] * order.quantity
        
        # Create order (delivery charge will be calculated when farmer accepts)
        cursor.execute("""
            INSERT INTO orders (customer_id, product_id, farmer_id, quantity, product_price, 
                              total_price, customer_lat, customer_lon, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (user_id, order.product_id, product["farmer_id"], order.quantity, 
              product_price, product_price, order.customer_lat, order.customer_lon))
        
        conn.commit()
        order_id = cursor.lastrowid
        return {"message": "Order created successfully", "order_id": order_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/orders/customer")
def get_customer_orders(user_id: int):
    """Get all orders for a customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, p.name as product_name, p.unit, u.username as farmer_name, u.mobile as farmer_mobile
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.farmer_id = u.id
        WHERE o.customer_id = ?
        ORDER BY o.created_at DESC
    """, (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"orders": orders}

@app.get("/orders/farmer")
def get_farmer_orders(user_id: int, status: str = None):
    """Get all orders for a farmer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.unit, u.username as customer_name, u.mobile as customer_mobile
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON o.customer_id = u.id
            WHERE o.farmer_id = ? AND o.status = ?
            ORDER BY o.created_at DESC
        """, (user_id, status))
    else:
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.unit, u.username as customer_name, u.mobile as customer_mobile
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON o.customer_id = u.id
            WHERE o.farmer_id = ?
            ORDER BY o.created_at DESC
        """, (user_id,))
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"orders": orders}

@app.post("/orders/{order_id}/accept")
def accept_order(order_id: int, accept_data: OrderAccept, user_id: int):
    """Farmer accepts an order and provides location"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get order details
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order["farmer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Calculate distance and delivery charge
        distance = calculate_distance(
            order["customer_lat"], order["customer_lon"],
            accept_data.farmer_lat, accept_data.farmer_lon
        )
        delivery_charge = distance * 15  # ₹15 per km
        total_price = order["product_price"] + delivery_charge
        
        # Update order
        cursor.execute("""
            UPDATE orders 
            SET status='accepted', farmer_lat=?, farmer_lon=?, distance_km=?, 
                delivery_charge=?, total_price=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (accept_data.farmer_lat, accept_data.farmer_lon, distance, 
              delivery_charge, total_price, order_id))
        
        conn.commit()
        return {
            "message": "Order accepted successfully",
            "distance_km": distance,
            "delivery_charge": delivery_charge,
            "total_price": total_price
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/orders/{order_id}/reject")
def reject_order(order_id: int, user_id: int):
    """Farmer rejects an order"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute("SELECT farmer_id FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        if not result or result["farmer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cursor.execute("UPDATE orders SET status='rejected', updated_at=CURRENT_TIMESTAMP WHERE id=?", (order_id,))
        conn.commit()
        return {"message": "Order rejected"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/orders/{order_id}/details")
def get_order_details(order_id: int, user_id: int):
    """Get detailed order information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, p.name as product_name, p.unit, p.description,
               c.username as customer_name, c.mobile as customer_mobile,
               f.username as farmer_name, f.mobile as farmer_mobile
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users c ON o.customer_id = c.id
        JOIN users f ON o.farmer_id = f.id
        WHERE o.id = ? AND (o.customer_id = ? OR o.farmer_id = ?)
    """, (order_id, user_id, user_id))
    
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"order": dict(order)}

# --- Payments ---
@app.post("/payments/process")
def process_payment(payment: PaymentProcess, user_id: int):
    """Process payment (simulated)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get order
        cursor.execute("SELECT * FROM orders WHERE id = ?", (payment.order_id,))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order["customer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate simulated transaction ID
        import random
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        
        # Determine payment type
        if payment.payment_method == 'cod':
            payment_type = 'delivery_charge'
            # For COD, only delivery charge is paid now
            if payment.amount != order["delivery_charge"]:
                raise HTTPException(status_code=400, detail="Invalid payment amount for COD")
        else:
            payment_type = 'full_payment'
            # For full payment, total amount is paid
            if payment.amount != order["total_price"]:
                raise HTTPException(status_code=400, detail="Invalid payment amount")
        
        # Create payment record
        cursor.execute("""
            INSERT INTO payments (order_id, amount, payment_type, status, transaction_id)
            VALUES (?, ?, ?, 'completed', ?)
        """, (payment.order_id, payment.amount, payment_type, transaction_id))
        
        # Update order payment status
        if payment.payment_method == 'cod':
            cursor.execute("""
                UPDATE orders 
                SET payment_method='cod', payment_status='partial', status='confirmed', updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (payment.order_id,))
        else:
            cursor.execute("""
                UPDATE orders 
                SET payment_method='full', payment_status='paid', status='confirmed', updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (payment.order_id,))
        
        conn.commit()
        return {
            "message": "Payment processed successfully",
            "transaction_id": transaction_id,
            "payment_type": payment_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/payments/order/{order_id}")
def get_payment_status(order_id: int, user_id: int):
    """Get payment status for an order"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify user is part of the order
    cursor.execute("SELECT customer_id, farmer_id FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order or (order["customer_id"] != user_id and order["farmer_id"] != user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC", (order_id,))
    payments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"payments": payments}

# ===========================
# COMMUNITY ENDPOINTS
# ===========================
from community_endpoints import register_community_endpoints
register_community_endpoints(app, get_db_connection, HTTPException)
