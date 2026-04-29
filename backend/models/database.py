# database.py - Sets up SQLite database and creates all tables
# SQLite is a lightweight database that stores everything in a single file

import sqlite3
import os

# Database file will be created in the backend folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "internmitra.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    """Creates all tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table to store internship tracker entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            notes TEXT,
            applied_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table to store chat session history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table to store AI evaluation logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eval_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            question TEXT NOT NULL,
            expected TEXT NOT NULL,
            got TEXT NOT NULL,
            score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")