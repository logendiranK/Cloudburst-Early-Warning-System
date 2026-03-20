import requests
import os

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
PHONE_NUMBERS = os.getenv("ALERT_PHONE_NUMBERS")

def send_sms_alert(message):
    if not FAST2SMS_API_KEY or not PHONE_NUMBERS:
        print("❌ SMS credentials not configured")
        return False

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "numbers": PHONE_NUMBERS
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print("⚠️ SMS sending failed:", e)
        return False
