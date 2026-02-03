import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "farmx.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            username TEXT,
            city TEXT,
            state TEXT,
            crop TEXT DEFAULT 'Wheat',
            language TEXT DEFAULT 'en',
            user_type TEXT DEFAULT 'farmer'
        )
    ''')
    
    # Test Results Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            test_type TEXT, -- 'disease' or 'soil'
            result TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            unit TEXT DEFAULT 'kg',
            quantity_available REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'available',
            FOREIGN KEY(farmer_id) REFERENCES users(id)
        )
    ''')
    
    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            farmer_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            product_price REAL NOT NULL,
            delivery_charge REAL DEFAULT 0,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            payment_status TEXT DEFAULT 'unpaid',
            customer_lat REAL,
            customer_lon REAL,
            farmer_lat REAL,
            farmer_lon REAL,
            distance_km REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(farmer_id) REFERENCES users(id)
        )
    ''')
    
    # Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_type TEXT,
            status TEXT DEFAULT 'pending',
            transaction_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    ''')
    
    # Community Posts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'question',
            likes_count INTEGER DEFAULT 0,
            replies_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(farmer_id) REFERENCES users(id)
        )
    ''')
    
    # Community Replies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            farmer_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            likes_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            FOREIGN KEY(farmer_id) REFERENCES users(id)
        )
    ''')
    
    # Community Likes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER,
            reply_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            FOREIGN KEY(reply_id) REFERENCES community_replies(id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id),
            UNIQUE(user_id, reply_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
