"""
Cloudburst Real-Time Prediction Script
=====================================
Uses trained model + rule-based logic
"""

import pandas as pd
import numpy as np
import pickle

class CloudburstPredictor:

    def __init__(self):
        self.feature_names = [
            "rainfall_intensity",
            "rainfall_rate_change",
            "humidity",
            "temperature",
            "pressure",
            "pressure_drop"
        ]
        self.alert_threshold = 0.8
        self.model = None
        
        # Try to load model if it exists
        try:
            with open("cloudburst_model.pkl", "rb") as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            print("[WARNING] Model file not found. Using rule-based prediction only.")

    def rule_based_cloudburst(self, row):
        return (
            row["rainfall_intensity"] > 80
            and row["rainfall_rate_change"] > 10
            and row["humidity"] > 85
            and row["pressure_drop"] > 2
        )

    def ml_probability(self, row):
        if self.model is None:
            return 0.0  # Return 0 probability if model not loaded
        X = np.array([[row[f] for f in self.feature_names]])

        proba = self.model.predict_proba(X)[0]

        # If model was trained on a single class, predict_proba
        # returns a single probability (size 1). In that case,
        # treat the cloudburst probability as 0.0 if the only
        # class is "no cloudburst" (0), or 1.0 otherwise.
        if proba.shape[0] == 1:
            only_class = self.model.classes_[0]
            return 1.0 if only_class == 1 else 0.0

        # Binary case: probability of class "1" (cloudburst)
        return proba[1]

    def hybrid_predict(self, row):
        rule_triggered = self.rule_based_cloudburst(row)
        ml_prob = self.ml_probability(row)
        cloudburst = rule_triggered or (ml_prob >= self.alert_threshold)
        
        return {
            "cloudburst": cloudburst,
            "rule_triggered": rule_triggered,
            "ml_probability": ml_prob
        }


if __name__ == "__main__":

    df = pd.read_csv("cloudburst_input_only.csv")
    predictor = CloudburstPredictor()

    print("\nCLOUDBURST DETECTION RESULTS\n")

    for i, row in df.iterrows():
        result = predictor.hybrid_predict(row)
        alert = result["cloudburst"]
        prob = result["ml_probability"]

        status = "[ALERT] CLOUDBURST" if alert else "[OK] NORMAL"

        print(
            f"Row {i:4d} | "
            f"Rain={row['rainfall_intensity']:.1f} | "
            f"Humidity={row['humidity']:.1f} | "
            f"PressureDrop={row['pressure_drop']:.2f} | "
            f"ML={prob:.2%} | {status}"
        )
