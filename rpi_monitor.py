import time
import requests
import board
import adafruit_dht
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json

# --- Configuration ---
# TODO: Replace with your device's unique ID and Server URL
DEVICE_ID = "RPI_SERVER_ROOM_A_01" 
SERVER_URL = "http://<YOUR_SERVER_IP>:5000/api/ingest" # This will be the IP of your computer running the Flask app

# --- Sensor Initialization ---
# Initialize DHT22 Temperature/Humidity Sensor
# TODO: Update the pin if you use a different one (e.g., board.D18)
dht_sensor = adafruit_dht.DHT22(board.D4)

# Initialize I2C bus for the ADC
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115 ADC
try:
    ads = ADS.ADS1115(i2c)
    # Define the analog input channel for the ZMPT101B voltage sensor
    # TODO: Update the channel if you use a different one (e.g., ADS.P1)
    zmpt101b_channel = AnalogIn(ads, ADS.P0) 
    print("ADS1115 ADC initialized successfully.")
except Exception as e:
    print(f"Error initializing ADS1115 ADC: {e}")
    ads = None
    zmpt101b_channel = None

# TODO: Initialize RainDrop Sensor (assuming digital for now on pin D5)
# If using analog, connect to another ADC channel. For this example, we'll simulate a digital read.
import RPi.GPIO as GPIO
RAIN_SENSOR_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(RAIN_SENSOR_PIN, GPIO.IN)


# --- Functions ---
def read_sensors():
    """Reads data from all connected sensors and returns a dictionary."""
    data = {
        "temperature": None,
        "humidity": None,
        "ac_voltage": None,
        "water_detected": False
    }

    # Read Temperature and Humidity
    try:
        data["temperature"] = dht_sensor.temperature
        data["humidity"] = dht_sensor.humidity
    except RuntimeError as error:
        # Errors happen often with DHT sensors, just print it and continue
        print(f"DHT22 Read error: {error.args[0]}")
    
    # Read AC Voltage from ZMPT101B via ADS1115
    if zmpt101b_channel:
        try:
            # This is a raw value. You will need to calibrate this to get an accurate voltage reading.
            # This involves measuring actual voltage with a multimeter and finding the formula.
            # For now, we'll just send the raw value.
            raw_adc_value = zmpt101b_channel.value
            # Placeholder for calibration - replace with your formula
            data["ac_voltage"] = raw_adc_value * 0.0001875 # Example calibration factor
        except Exception as e:
            print(f"ADS1115 Read error: {e}")

    # Read Water Leak Sensor
    try:
        # If input is LOW (0), it means water is detected
        if GPIO.input(RAIN_SENSOR_PIN) == GPIO.LOW:
            data["water_detected"] = True
        else:
            data["water_detected"] = False
    except Exception as e:
        print(f"Rain Sensor Read error: {e}")
        
    return data

def send_to_server(payload):
    """Sends the data payload to the server's ingestion endpoint."""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("Data sent successfully.")
        else:
            print(f"Failed to send data. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to server: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    print("Starting Server Room Monitoring System...")
    while True:
        print("Reading sensor data...")
        sensor_data = read_sensors()
        
        payload = {
            "device_id": DEVICE_ID,
            "data": sensor_data
        }
        
        print(f"Payload: {payload}")
        
        print("Sending data to server...")
        send_to_server(payload)
        
        print("Waiting for 60 seconds...")
        time.sleep(60)