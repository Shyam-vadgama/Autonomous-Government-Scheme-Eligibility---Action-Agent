import sqlite3
import os
from typing import Optional, Dict, Any

# Ensure DB_PATH is absolute and relative to this script file
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_user_db():
    """Initialize the users database with the required table and ensure schema is up to date."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create table if it doesn't exist (basic schema)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        
        # Check and add missing columns (Schema Migration)
        required_columns = {
            "address": "TEXT DEFAULT ''",
            "state": "TEXT DEFAULT ''",
            "district": "TEXT DEFAULT ''",
            "occupation": "TEXT DEFAULT ''",
            "annual_income": "TEXT DEFAULT ''",
            "education_level": "TEXT DEFAULT ''",
            "caste_category": "TEXT DEFAULT ''"
        }
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        for col, col_def in required_columns.items():
            if col not in existing_columns:
                print(f"Migrating DB: Adding column '{col}'")
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_def}")
                except Exception as e:
                    print(f"Error adding column {col}: {e}")
                    
        conn.commit()

def create_user(name, email, phone, password) -> bool:
    """Create a new user. Returns True if successful, False if email exists."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:  # Added timeout
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                (name, email, phone, password)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(email, password) -> Optional[Dict[str, Any]]:
    """Verify user credentials. Returns user dict if valid, None otherwise."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Select all columns to be safe, or specify carefully
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
