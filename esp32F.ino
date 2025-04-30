#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>
#include <ArduinoJson.h>
const float pin5 = 5;  
// Replace with your network credentials
const char* ssid = "Beemoon";
const char* password = "Tetapilmupadi";

// Flask server endpoints
const char* humidityURL = "https://personalflask.tunnelconnect.cfd/send";
const char* errorURL    = "https://personalflask.tunnelconnect.cfd/send_error";
const char* getFuzzyURL = "https://personalflask.tunnelconnect.cfd/get_fuzzy";

// Pin connected to the humidity sensor
const float sensorPin = 34;

// PWM output pin for the motor driver
const float pwmPin = 25;
const float pwmChannel = 0;
const float pwmFreq = 5000;
const float pwmResolution = 8;

// Control variables
float target = 25.01;
float error, prevError = 0;
float derror;
float controlfuzzy;

// Timing variables
unsigned long lastResetTime = 0;
const unsigned long resetInterval = 3600000;
const unsigned long loopInterval = 1000;
unsigned long lastLoopTime = 0;

// Moving Average Variables
const float numReadings = 10;
float readings[(int)numReadings];
float readIndex = 0;
float total = 0;
float averageHumidity = 0;
float initialLoops = 0;
const float warmupLoops = 100;
float latestHumidity = 0; // Stores the latest sensor reading

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  pinMode((int)pin5, OUTPUT);

  if (!ledcAttach((int)pwmPin, (int)pwmFreq, (int)pwmResolution)) {
    Serial.println("Error: Failed to configure PWM with ledcAttach");
    while (true);
  }

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  lastResetTime = millis();

  for (int i = 0; i < numReadings; i++) {
    readings[i] = 0;
  }
}

void sendData(const char* url, const String &payload) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.print("Data sent to ");
      Serial.print(url);
      Serial.println(" successfully");
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.print("Error sending data to ");
      Serial.print(url);
      Serial.print(", HTTP code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Error: WiFi not connected");
  }
}

void sendHumidityData(float humidity) {
  String payload = "{\"humidity\": " + String(humidity) + "}";
  sendData(humidityURL, payload);
}

void sendErrorData(float error, float derror) {
  String payload = "{\"error\": " + String(error) + ", \"derror\": " + String(derror, 4) + "}";
  sendData(errorURL, payload);
}

float getControlFuzzy() {
  float controlValue = 0;
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(getFuzzyURL);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("GET /get_fuzzy response: ");
      Serial.println(response);
      
      const size_t capacity = JSON_OBJECT_SIZE(1) + 60;
      DynamicJsonDocument doc(capacity);

      DeserializationError err = deserializeJson(doc, response);
      if (!err) {
        controlValue = doc["output"].as<float>();
      } else {
        Serial.print("JSON parse error: ");
        Serial.println(err.c_str());
      }
    } else {
      Serial.print("Error in GET request, HTTP code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected for GET /get_fuzzy");
  }
  return controlValue;
}

void updateSensorReading() {
  digitalWrite((int)pin5, HIGH);
  float sensorValue = analogRead((int)sensorPin);
  latestHumidity = (0.00004 * pow(sensorValue, 2)) - (0.185 * sensorValue) + 207.76;
  latestHumidity = constrain(latestHumidity, 0, 100);
}

void loop() {
  updateSensorReading();
  total = total - readings[(int)readIndex] + latestHumidity;
  readings[(int)readIndex] = latestHumidity;
  readIndex = fmod((readIndex + 1), numReadings);
  averageHumidity = total / numReadings;

  if (millis() - lastLoopTime >= loopInterval) {
    lastLoopTime = millis();

    if (initialLoops < warmupLoops) {
      initialLoops++;
      return; // Skip sending data and control actions during warm-up
    }

    error = averageHumidity - target;
    derror = (error - prevError) / (loopInterval / 1000.0);

    Serial.print("Filtered Humidity: ");
    Serial.print(averageHumidity);
    Serial.print("%, Error: ");
    Serial.print(error);
    Serial.print(", dError: ");
    Serial.println(derror);

    sendHumidityData(averageHumidity);
    sendErrorData(error, derror);

    prevError = error;

    
    if (controlfuzzy != 0) {
      ledcWrite((int)pwmPin, 255);
      Serial.println("PWM Output set to 255 for 1 second");
      delay(100);  // Hold at max output for 1 second
      ledcWrite((int)pwmPin, 0);
    }
    controlfuzzy = getControlFuzzy();
    Serial.print("Control Fuzzy: ");
    Serial.println(controlfuzzy);
    ledcWrite((int)pwmPin, (int)controlfuzzy);
    delay(100);
    ledcWrite((int)pwmPin, 0);
    Serial.print("PWM Output (channel ");
    Serial.print(pwmChannel);
    Serial.print(") set to: ");
    Serial.println(controlfuzzy);
  }

  if (millis() - lastResetTime >= resetInterval) {
    Serial.println("One hour has passed. Restarting...");
    ESP.restart();
  }
}
