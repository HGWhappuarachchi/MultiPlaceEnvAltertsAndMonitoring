# /windows_device_simulator.py

import requests
import json
import time
import random

# --- Configuration ---
# Use the same Device ID that you provisioned in the database
DEVICE_ID = "RPI_SERVER_ROOM_A_01" 

# The server is running on your own machine (localhost)
SERVER_URL = "http://127.0.0.1:5000/api/ingest" 

def generate_fake_sensor_data():
    """Generates random data to simulate real sensor readings."""
    data = {
        "temperature": round(random.uniform(22.0, 28.5), 2),
        "humidity": round(random.uniform(55.0, 65.0), 2),
        "ac_voltage": round(random.uniform(228.0, 232.0), 2),
        # Occasionally simulate a water leak
        "water_detected": random.choice([True, False, False, False, False]) 
    }
    return data

def send_to_server(payload):
    """Sends the data payload to the server's ingestion endpoint."""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"SUCCESS: Sent payload: {payload}")
        else:
            print(f"FAIL: Status Code {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to server: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    print("Starting Windows Device Simulator...")
    while True:
        sensor_data = generate_fake_sensor_data()
        
        # The payload structure MUST be identical to the real RPi script
        payload = {
            "device_id": DEVICE_ID,
            "data": sensor_data
        }
        
        send_to_server(payload)
        
        # Send data more frequently for faster testing
        print("Waiting for 10 seconds...\n")
        time.sleep(10)