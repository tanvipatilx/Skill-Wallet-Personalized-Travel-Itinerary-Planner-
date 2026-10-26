"""
database.py - Lightweight SQLite persistence for VoyageAI Trip Management.
Zero external database dependencies for seamless Streamlit Community Cloud deployment.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "trips.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_title TEXT NOT NULL,
            destination TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            budget_level TEXT NOT NULL,
            travel_party TEXT NOT NULL,
            total_cost_usd REAL DEFAULT 0,
            total_cost_inr REAL DEFAULT 0,
            itinerary_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_trip(trip_title: str, destination: str, duration_days: int, 
              budget_level: str, travel_party: str, total_cost_usd: float, 
              total_cost_inr: float, itinerary_data: Dict[str, Any]) -> int:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_trips 
        (trip_title, destination, duration_days, budget_level, travel_party, total_cost_usd, total_cost_inr, itinerary_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip_title,
        destination,
        duration_days,
        budget_level,
        travel_party,
        total_cost_usd,
        total_cost_inr,
        json.dumps(itinerary_data),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trip_id

def get_all_trips() -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_trips ORDER BY id DESC")
    rows = cursor.fetchall()
    trips = []
    for r in rows:
        trips.append({
            "id": r["id"],
            "trip_title": r["trip_title"],
            "destination": r["destination"],
            "duration_days": r["duration_days"],
            "budget_level": r["budget_level"],
            "travel_party": r["travel_party"],
            "total_cost_usd": r["total_cost_usd"],
            "total_cost_inr": r["total_cost_inr"],
            "created_at": r["created_at"],
            "itinerary_data": json.loads(r["itinerary_json"])
        })
    conn.close()
    return trips

def get_trip_by_id(trip_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_trips WHERE id = ?", (trip_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "trip_title": row["trip_title"],
            "destination": row["destination"],
            "duration_days": row["duration_days"],
            "budget_level": row["budget_level"],
            "travel_party": row["travel_party"],
            "total_cost_usd": row["total_cost_usd"],
            "total_cost_inr": row["total_cost_inr"],
            "created_at": row["created_at"],
            "itinerary_data": json.loads(row["itinerary_json"])
        }
    return None

def delete_trip(trip_id: int) -> bool:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_trips WHERE id = ?", (trip_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Ensure DB initialized on module load
init_db()
