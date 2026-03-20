from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'
})

ref = db.reference('sensor_data')

@app.route("/sensor-data", methods=["POST"])
def receive_sensor_data():
    data = request.json

    # Add timestamp
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Push to Firebase
    ref.push(data)

    return jsonify({"status": "success", "message": "Sensor data stored in Firebase"})

if __name__ == "__main__":
    app.run(debug=True)