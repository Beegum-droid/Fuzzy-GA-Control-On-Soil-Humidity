# 🌱 Fuzzy-GA-Control-On-Soil-Humidity

A smart soil humidity control system that uses **Fuzzy Logic** and **Genetic Algorithms (GA)** to regulate a water pump for maintaining optimal soil moisture. This system includes both simulation tools and real-time integration with an ESP32 microcontroller.

---

## 🔍 Overview

Traditional threshold-based systems may not adapt well to dynamic environments like soil moisture. This project applies fuzzy logic with optimized membership functions to enhance control accuracy and flexibility.

### Key Features
- Manual vs GA-optimized fuzzy membership function comparison
- Real-time soil moisture monitoring and water control
- ESP32 microcontroller integration with HTTP-based communication
- Python-based simulation and tuning tools

---

## 🧠 How It Works

1. **Sensor Input**: The ESP32 reads soil moisture values from a sensor.
2. **Data Transmission**: Sensor data is sent via HTTP to a server (hosted using Flask).
3. **Fuzzy Logic Processing**: The server calculates control output (e.g., pump power level) based on fuzzy rules and membership functions.
4. **Control Output**: The ESP32 receives the result and adjusts the water pump accordingly.

---

## 📁 File Descriptions

| File                  | Description |
|-----------------------|-------------|
| `SimulationFuzzy.py`  | Simulates fuzzy logic control using **manually tuned** membership functions. |
| `SimulationFGA.py`    | Simulates fuzzy logic control using **GA-optimized** membership functions. |
| `MembershipTunerGA.py`| Uses a Genetic Algorithm to **optimize fuzzy membership functions**. |
| `espflask.py`         | Flask-based server to **exchange data** between ESP32, computer, and database using HTTP. |
| `esp32.ino`           | C/C++ code for ESP32 to **read sensor data**, **send it to the server**, and **apply fuzzy control output**. |
| `FuzzyO.py`           | Fuzzy logic function using **manually tuned** membership functions. |
| `FuzzyGA.py`          | Fuzzy logic function using **GA-optimized** membership functions. |

---

## ⚙️ System Requirements

### Hardware
- ESP32 Development Board
- Soil Moisture Sensor
- Relay + Water Pump
- Wi-Fi connection

### Software
- Python 3.x
- Arduino IDE
- Required Python libraries:
  - `numpy`
  - `flask`
  - `scikit-fuzzy`
  - `requests`

---
