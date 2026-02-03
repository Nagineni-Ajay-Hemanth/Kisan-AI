
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
def list_products(category: str = None, search: str = None):
    """List all available products"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if category and search:
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.status = 'available' AND p.category = ? AND p.name LIKE ?
            ORDER BY p.created_at DESC
        """, (category, f"%{search}%"))
    elif category:
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.status = 'available' AND p.category = ?
            ORDER BY p.created_at DESC
        """, (category,))
    elif search:
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.status = 'available' AND p.name LIKE ?
            ORDER BY p.created_at DESC
        """, (f"%{search}%",))
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

@app.get("/products/{product_id}")
def get_product_details(product_id: int):
    """Get single product details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
        FROM products p
        JOIN users u ON p.farmer_id = u.id
        WHERE p.id = ?
    """, (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product

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
