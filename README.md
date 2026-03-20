# Cloudburst Early Warning System - ML Model

## Overview
This project implements a supervised machine learning classification model to predict cloudburst events using IoT sensor data from ESP32 devices.

## Features
- Random Forest Classifier optimized for non-linear weather patterns
- Comprehensive model evaluation (Accuracy, Precision, Recall, F1-score, Confusion Matrix)
- Feature importance analysis
- Real-time prediction function for ESP32 sensor inputs
- Alert system (triggers when probability > 0.8)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Training the Model
```bash
python cloudburst_training.py
```

This will:
1. Load and explore the dataset
2. Preprocess the data (handle missing values, scale features)
3. Split data into training (80%) and testing (20%) sets
4. Train a Random Forest Classifier
5. Evaluate the model with multiple metrics
6. Display feature importance
7. Save the model as `cloudburst_model.pkl` and scaler as `scaler.pkl`
8. Demonstrate the prediction function

### Using the Trained Model

```python
from cloudburst_training import CloudburstPredictor

# Load saved model
predictor = CloudburstPredictor()
predictor.load_saved_model()

# Make prediction from ESP32 sensor data
result = predictor.predict_cloudburst(
    rainfall_intensity=120.0,    # mm/min
    rainfall_rate_change=25.0,
    humidity=95.0,                # %
    temperature=20.0,             # °C
    pressure=980.0,               # hPa
    pressure_drop=20.0            # hPa
)

print(result['message'])
# Output: ⚠️ CLOUDBURST ALERT! Probability: 85.23%
```

## Dataset
- File: `cloudburst_dataset.csv`
- Features: rainfall_intensity, rainfall_rate_change, humidity, temperature, pressure, pressure_drop
- Target: cloudburst (0 = No, 1 = Yes)

## Model Output
- `cloudburst_model.pkl`: Trained Random Forest model
- `scaler.pkl`: Feature scaler for preprocessing

## Alert Threshold
The system triggers an alert when cloudburst probability exceeds 80% (configurable via `alert_threshold` parameter).

