import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# -----------------------------
# Load and prepare dataset
# -----------------------------
raw_df = pd.read_csv("cloudburst_rainfall_intensity_dataset.csv")

# Map raw columns to the feature schema expected by CloudburstPredictor
df = pd.DataFrame()
df["rainfall_intensity"] = raw_df["rainfall_intensity_mm_hr"]
df["humidity"] = raw_df["humidity"]
df["temperature"] = raw_df["temperature"]
df["pressure"] = raw_df["pressure"]

# Engineer rainfall_rate_change as absolute change between consecutive readings
df["rainfall_rate_change"] = df["rainfall_intensity"].diff().fillna(0).abs()

# Engineer pressure_drop as positive drop since previous reading (else 0)
pressure_delta = df["pressure"].shift(1) - df["pressure"]
df["pressure_drop"] = pressure_delta.clip(lower=0).fillna(0)

# Derive a proxy cloudburst label using the original rule:
# rainfall_intensity > 80 AND rainfall_rate_change > 10 AND humidity > 85 AND pressure_drop > 2
df["cloudburst"] = (
    (df["rainfall_intensity"] > 80)
    & (df["rainfall_rate_change"] > 10)
    & (df["humidity"] > 85)
    & (df["pressure_drop"] > 2)
).astype(int)

features = [
    "rainfall_intensity",
    "rainfall_rate_change",
    "humidity",
    "temperature",
    "pressure",
    "pressure_drop"
]

X = df[features]
y = df["cloudburst"]

# -----------------------------
# Train / Test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# Train Random Forest model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# Evaluate model
# -----------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy*100:.2f}%")

# -----------------------------
# Save trained model
# -----------------------------
with open("cloudburst_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as cloudburst_model.pkl")