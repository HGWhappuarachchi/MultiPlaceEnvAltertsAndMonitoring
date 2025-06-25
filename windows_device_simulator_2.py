# /windows_device_simulator_2.py

import requests
import json
import time
import random

# --- Configuration ---
# A NEW, UNIQUE ID for our second device.
DEVICE_ID = "RPI_LAB_BENCH_02" 

# The server is still running on your own machine (localhost)
SERVER_URL = "http://127.0.0.1:5000/api/ingest" 

def generate_fake_sensor_data():
    """Generates random data to simulate a second, different device."""
    # Use slightly different ranges to distinguish it from the first device
    data = {
        "temperature": round(random.uniform(18.0, 22.0), 2), # Cooler environment
        "humidity": round(random.uniform(40.0, 50.0), 2), # Drier environment
        "ac_voltage": round(random.uniform(235.0, 240.0), 2), # Slightly higher voltage
        # This device will rarely have a water leak
        "water_detected": random.choice([False] * 10 + [True]) 
    }
    return data

def send_to_server(payload):
    """Sends the data payload to the server's ingestion endpoint."""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"SUCCESS (Device 2): Sent payload: {payload}")
        else:
            print(f"FAIL (Device 2): Status Code {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR (Device 2): Could not connect to server: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    print("Starting Windows Device Simulator 2...")
    while True:
        sensor_data = generate_fake_sensor_data()
        
        payload = {
            "device_id": DEVICE_ID,
            "data": sensor_data
        }
        
        send_to_server(payload)
        
        # Send data at a slightly different interval
        print("Waiting for 15 seconds...\n")
        time.sleep(15)
