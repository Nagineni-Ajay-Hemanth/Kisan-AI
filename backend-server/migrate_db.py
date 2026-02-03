import sqlite3
import os

# Path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "farmx.db")

print(f"Migrating database at: {DB_PATH}")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check if user_type column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'user_type' not in columns:
        print("Adding user_type column...")
        cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'farmer'")
        conn.commit()
        print("✓ user_type column added successfully")
        
        # Update existing users to be farmers
        cursor.execute("UPDATE users SET user_type = 'farmer' WHERE user_type IS NULL")
        conn.commit()
        print("✓ Existing users set to 'farmer' type")
    else:
        print("✓ user_type column already exists")
        
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("Migration complete!")
