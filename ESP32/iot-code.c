#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT11.h>

// WIFI
const char* ssid = "KL";
const char* password = "05080805";

// FIREBASE URL
String firebaseURL = "https://cloudburst-system-ba415-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json";
String alarmURL = "https://cloudburst-system-ba415-default-rtdb.asia-southeast1.firebasedatabase.app/alarm.json";

// PINS
#define RAIN_PIN 34
#define SOIL_PIN 35
#define DHTPIN 5
#define BUZZER_PIN 26

#define SDA_PIN 21
#define SCL_PIN 22

Adafruit_BMP280 bmp;
DHT11 dht11(DHTPIN);

// Buzzer state
bool toneActive = false;

void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting sensors...");

  Wire.begin(SDA_PIN, SCL_PIN);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 not detected!");
  } 
  else {
    Serial.println("BMP280 detected");
  }

  WiFi.begin(ssid, password);

  Serial.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
}

void loop() {

  // ----------------------
  // Read Sensors
  // ----------------------

  int rainValue = analogRead(RAIN_PIN);
  int soilValue = analogRead(SOIL_PIN);

  int temperature = 0;
  int humidity = 0;

  dht11.readTemperatureHumidity(temperature, humidity);

  float pressure = bmp.readPressure() / 100.0;

  Serial.println("---- SENSOR DATA ----");

  Serial.print("Rain: ");
  Serial.println(rainValue);

  Serial.print("Soil: ");
  Serial.println(soilValue);

  Serial.print("Temperature: ");
  Serial.println(temperature);

  Serial.print("Humidity: ");
  Serial.println(humidity);

  Serial.print("Pressure: ");
  Serial.println(pressure);

  Serial.println("---------------------");

  // ----------------------
  // Send data to Firebase
  // ----------------------

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    http.begin(firebaseURL);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";
    jsonData += "\"rain\":" + String(rainValue) + ",";
    jsonData += "\"soil\":" + String(soilValue) + ",";
    jsonData += "\"temperature\":" + String(temperature) + ",";
    jsonData += "\"humidity\":" + String(humidity) + ",";
    jsonData += "\"pressure\":" + String(pressure) + ",";
    jsonData += "\"timestamp\":" + String(millis());
    jsonData += "}";

    int httpResponseCode = http.POST(jsonData);

    Serial.print("Firebase Response: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  // ----------------------
  // Check Alarm Status
  // ----------------------

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient httpAlarm;

    httpAlarm.begin(alarmURL);

    int httpCode = httpAlarm.GET();

    if (httpCode > 0) {

      String payload = httpAlarm.getString();

      payload.replace("\"", "");
      payload.trim();

      Serial.print("Alarm payload: ");
      Serial.println(payload);

      int alarmValue = payload.toInt();

      if (alarmValue == 1) {

        Serial.println("BUZZER ON");

        if (!toneActive) {
          tone(BUZZER_PIN, 1000);
          toneActive = true;
        }

      } 
      else {

        Serial.println("BUZZER OFF");

        if (toneActive) {
          noTone(BUZZER_PIN);
          toneActive = false;
        }

      }

    } 
    else {
      Serial.println("Failed to read alarm");
    }

    httpAlarm.end();
  }

  delay(5000);
}