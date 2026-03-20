import time
import random
import requests
from datetime import datetime

FIREBASE_DB_URL = "https://YOUR_PROJECT.firebaseio.com/sensor_data.json"

while True:
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rainfall_intensity": random.uniform(10, 120),
        "rainfall_rate_change": random.uniform(0, 20),
        "humidity": random.uniform(60, 95),
        "temperature": random.uniform(20, 35),
        "pressure": random.uniform(990, 1020),
        "pressure_drop": random.uniform(0, 5),
    }

    requests.put(FIREBASE_DB_URL, json=data)
    print("📡 Sensor data sent:", data)

    time.sleep(10)  # ESP32 sends data every 10 seconds
