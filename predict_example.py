"""
Real-Time Cloudburst Prediction Script
=====================================
Uses trained hybrid ML + rule-based model
with input-only ESP32 sensor CSV data.
"""

import pandas as pd
from cloudburst_training import CloudburstPredictor


def main():

    print("=" * 70)
    print("REAL-TIME CLOUDBURST PREDICTION SYSTEM")
    print("=" * 70)

    # Initialize predictor (model loading is handled in __init__)
    try:
        predictor = CloudburstPredictor()
        if predictor.model is not None:
            print("[OK] Trained model loaded successfully\n")
        else:
            print("[WARNING] Model not found. Using rule-based prediction only.\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize predictor: {e}")
        return

    # Load input-only CSV (NO cloudburst column)
    try:
        df = pd.read_csv("cloudburst_input_only.csv")
        print(f"[OK] Input data loaded: {len(df)} rows\n")
    except FileNotFoundError:
        print("[ERROR] cloudburst_input_only.csv not found")
        return

    print("=" * 70)
    print("PROCESSING SENSOR DATA")
    print("=" * 70)

    alerts = []

    for idx, row in df.iterrows():

        result = predictor.hybrid_predict(row)

        status = "🚨 CLOUDBURST ALERT" if result["cloudburst"] else "✅ NORMAL"

        print(
            f"Row {idx:4d} | "
            f"Rain={row['rainfall_intensity']:.1f} | "
            f"Humidity={row['humidity']:.1f} | "
            f"PressureDrop={row['pressure_drop']:.2f} | "
            f"ML={result['ml_probability']:.2%} | "
            f"Rule={result['rule_triggered']} | "
            f"{status}"
        )

        if result["cloudburst"]:
            alerts.append(idx)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Rows Processed : {len(df)}")
    print(f"Cloudburst Alerts    : {len(alerts)}")

    if alerts:
        print(f"Alert Triggered At Rows: {alerts[:10]}{'...' if len(alerts) > 10 else ''}")
    else:
        print("No cloudburst detected")

    print("\nSYSTEM READY FOR LIVE ESP32 STREAMING 🚀")


if __name__ == "__main__":
    main()