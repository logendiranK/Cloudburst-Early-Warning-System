import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from cloudburst_training import CloudburstPredictor
from sms_alert import send_sms_alert
from streamlit_autorefresh import st_autorefresh
from database import init_db, save_alert
import sqlite3
import os
import requests

# ---------------------------------
# Initialize database
# ---------------------------------
init_db()

# ---------------------------------
# Auto refresh every 10 seconds
# ---------------------------------
st_autorefresh(interval=10000, key="cloudburst_refresh")

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(page_title="Cloudburst Prediction Dashboard", layout="wide")

st.markdown(
    "<h1 style='text-align:center;'>🌧 Cloudburst Anomaly Detection Dashboard</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>IoT Sensors • Random Forest • Hybrid Rule-Based System</p>",
    unsafe_allow_html=True
)

# ---------------------------------
# Load live data from Firebase
# ---------------------------------
def load_data():

    try:
        base_url = os.getenv(
            "FIREBASE_DB_URL",
            "https://cloudburst-system-ba415-default-rtdb.asia-southeast1.firebasedatabase.app",
        )
        resp = requests.get(f"{base_url}/sensor.json", timeout=5)
        resp.raise_for_status()
        data = resp.json() or {}

        if isinstance(data, dict) and data and isinstance(next(iter(data.values())), dict):
            latest_key = sorted(data.keys())[-1]
            latest = data.get(latest_key, {}) or {}
        else:
            latest = data or {}

        row = {
            "timestamp": pd.Timestamp.utcnow(),
            "humidity": float(latest.get("humidity", 0)),
            "pressure": float(latest.get("pressure", 0)),
            "rain_raw": float(latest.get("rain", 0)),
            "soil_moisture": float(latest.get("soil", 0)),
            "temperature": float(latest.get("temperature", 0)),
        }

        # Convert sensor value → rainfall intensity (0–100 scale)
        # 0  = no rain, 4095 = maximum rain
        row["rainfall_intensity"] = (4095.0 - row["rain_raw"]) * 100.0 / 4095.0

        new_df = pd.DataFrame([row])

        history = st.session_state.get("history_df")

        if history is None or history.empty:
            history = new_df
        else:
            cols = ["humidity","pressure","rainfall_intensity","soil_moisture","temperature"]
            last = history.iloc[[-1]][cols].reset_index(drop=True)
            current = new_df[cols].reset_index(drop=True)

            if not last.equals(current):
                history = pd.concat([history,new_df],ignore_index=True).tail(500)

        history["rainfall_rate_change"] = history["rainfall_intensity"].diff().fillna(0).abs()

        pressure_delta = history["pressure"].shift(1) - history["pressure"]
        history["pressure_drop"] = pressure_delta.clip(lower=0).fillna(0)

        st.session_state["history_df"] = history

        return history

    except Exception:
        st.error("⚠ Live sensor data unavailable (Firebase).")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.stop()

# ---------------------------------
# Load predictor
# ---------------------------------
predictor = CloudburstPredictor()

# ---------------------------------
# Sidebar
# ---------------------------------
st.sidebar.header("⚙️ Controls")

if len(df) <= 1:
    row_index = 0
else:
    row_index = st.sidebar.slider("Select Sensor Record",0,len(df)-1,len(df)-1)

row = df.iloc[row_index]

# ---------------------------------
# Prediction
# ---------------------------------
result = predictor.hybrid_predict(row)

confidence = result["ml_probability"] * 100

# ---------------------------------
# Severity Logic
# ---------------------------------
rain = float(row["rainfall_intensity"])

if rain >= 76:
    severity = "CRITICAL"
elif rain >= 56:
    severity = "HIGH"
elif rain >= 36:
    severity = "MEDIUM"
else:
    severity = "LOW"

WINDOW = 10
recent_rain = df["rainfall_intensity"].tail(WINDOW)

if len(recent_rain) == WINDOW:

    if (recent_rain >= 76).all():
        severity = "CRITICAL"

    elif (recent_rain >= 56).all() and severity != "CRITICAL":
        severity = "HIGH"

    elif (recent_rain >= 36).all() and severity not in ["CRITICAL","HIGH"]:
        severity = "MEDIUM"

if result.get("cloudburst"):
    severity = "CRITICAL"


# ---------------------------------
# 🔔 Trigger Hardware Alarm
# ---------------------------------
firebase_alarm_url = "https://cloudburst-system-ba415-default-rtdb.asia-southeast1.firebasedatabase.app/alarm.json"

try:
    if severity in ["HIGH","CRITICAL"]:
        resp = requests.put(firebase_alarm_url,json=1)
    else:
        resp = requests.put(firebase_alarm_url,json=0)
    # Simple debug so you can confirm the buzzer path is being updated
    st.write("Alarm update:", severity, "→", resp.status_code)
except:
    st.warning("⚠ Unable to update alarm status")


# ---------------------------------
# Emergency Banner
# ---------------------------------
if severity in ["HIGH","CRITICAL"]:
    st.error("🚨 EMERGENCY WEATHER ALERT 🚨")

# ---------------------------------
# Sensor Analytics
# ---------------------------------
st.subheader("📡 Live Sensor Analytics")

col1,col2,col3 = st.columns(3)

with col1:
    st.metric("🌧 Rainfall Intensity (mm/hr)",f"{row['rainfall_intensity']:.1f}")
    st.bar_chart(df["rainfall_intensity"].tail(10))

with col2:
    st.metric("🧭 Air Pressure (hPa)",f"{row['pressure']:.1f}")
    st.line_chart(df["pressure"].tail(10))

with col3:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row["humidity"],
        title={"text":"💧 Humidity Level"},
        gauge={
            "axis":{"range":[0,100]},
            "steps":[
                {"range":[0,40],"color":"green"},
                {"range":[40,70],"color":"yellow"},
                {"range":[70,100],"color":"red"}
            ]
        }
    ))
    st.plotly_chart(fig,use_container_width=True)

# Extra sensor readings as gauges (like humidity)
col4,col5 = st.columns(2)

with col4:
    temp_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row["temperature"],
        title={"text": "🌡 Temperature (°C)"},
        gauge={
            "axis": {"range": [0, 60]},
            "steps": [
                {"range": [0, 20], "color": "lightblue"},
                {"range": [20, 35], "color": "green"},
                {"range": [35, 45], "color": "orange"},
                {"range": [45, 60], "color": "red"},
            ],
        },
    ))
    st.plotly_chart(temp_gauge, use_container_width=True)

with col5:
    soil_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row["soil_moisture"],
        title={"text": "🌱 Soil Moisture"},
        gauge={
            "axis": {"range": [0, 4095]},
            "steps": [
                {"range": [0, 1000], "color": "saddlebrown"},
                {"range": [1000, 2500], "color": "yellowgreen"},
                {"range": [2500, 4095], "color": "forestgreen"},
            ],
        },
    ))
    st.plotly_chart(soil_gauge, use_container_width=True)

# ---------------------------------
# Prediction Result
# ---------------------------------
st.subheader("🚨 Cloudburst Risk Assessment")

if severity in ["HIGH","CRITICAL"]:
    st.error(f"🚨 {severity} RISK")
elif severity == "MEDIUM":
    st.warning("⚠ MEDIUM RISK")
else:
    st.success("🟢 LOW RISK")

st.write(f"**ML Probability:** {confidence:.2f}%")

# ---------------------------------
# Historical Trends
# ---------------------------------
st.subheader("📈 Historical Sensor Trends")

st.line_chart(df[["rainfall_intensity","pressure_drop","humidity"]])