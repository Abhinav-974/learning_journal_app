import sqlite3

DB_NAME = "learning.db"


def get_connection():
    """Return a SQLite connection."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    """Initialize database and required tables."""
    conn = get_connection()
    cur = conn.cursor()

    # Table to ensure one row per calendar day
    cur.execute("""
        CREATE TABLE IF NOT EXISTS days (
            date TEXT PRIMARY KEY,
            miss_reason TEXT
        )
    """)

    # Table to store multiple learning entries per day
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            entry_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(date) REFERENCES days(date)
        )
    """)

    conn.commit()
    conn.close()