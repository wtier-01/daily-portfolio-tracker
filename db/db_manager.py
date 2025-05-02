# db/db_manager.py

import sqlite3
from pathlib import Path
from datetime import date

# Path to the SQLite database file
DB_PATH = Path("data/portfolio.db")

def init_db():
    """Create the snapshots table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                date TEXT PRIMARY KEY,
                value REAL
            );
        """)
        conn.commit()

def insert_snapshot(value):
    """Insert or update today's portfolio value."""
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO snapshots (date, value)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET value = excluded.value;
        """, (today, value))
        conn.commit()

def fetch_snapshots():
    """Fetch all historical portfolio snapshots as a DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        df = conn.execute("SELECT date, value FROM snapshots ORDER BY date").fetchall()
    return df

def get_latest_snapshots(n=2):
    """Fetch the last `n` snapshots as a list of (date, value)."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT date, value FROM snapshots ORDER BY date DESC LIMIT ?", (n,))
        rows = cur.fetchall()
    return rows[::-1]  # Return in ascending order (oldest → newest)
