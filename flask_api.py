from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

CSV_FILE = "cloudburst_input_only.csv"

@app.route("/sensor-data", methods=["POST"])
def receive_sensor_data():
    data = request.json

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    return jsonify({"status": "success", "message": "Sensor data received"})

if __name__ == "__main__":
    app.run(debug=True)
