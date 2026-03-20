import sqlite3
from datetime import datetime

DB_NAME = "alerts.db"

# Create table
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rainfall REAL,
            humidity REAL,
            pressure REAL,
            soil_moisture REAL,
            severity TEXT,
            confidence REAL
        )
    """)

    conn.commit()
    conn.close()


# Save alert
def save_alert(rainfall, humidity, pressure, soil_moisture, severity, confidence):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts
        (timestamp, rainfall, humidity, pressure, soil_moisture, severity, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rainfall,
        humidity,
        pressure,
        soil_moisture,
        severity,
        confidence
    ))

    conn.commit()
    conn.close()