import requests
import random
import time

URL = "http://127.0.0.1:5000/sensor-data"

while True:
    payload = {
        "rainfall_intensity": random.uniform(10, 120),
        "rainfall_rate_change": random.uniform(1, 20),
        "humidity": random.uniform(60, 98),
        "temperature": random.uniform(18, 35),
        "pressure" : random.uniform(990, 1020),
        "pressure_drop": random.uniform(0.5, 5)
    }

    try:
        requests.post(URL, json=payload)
        print("📡 Sensor data sent")
    except:
        print("❌ Flask server not running")

    time.sleep(10)
