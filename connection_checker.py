# /connection_checker.py

import time
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Device, SensorData, AlertLog
from app.email import send_alert_email

# Create a Flask app instance to work with the database
app = create_app()

# The app_context() is necessary to access the database outside of a web request
with app.app_context():
    
    def check_device_status():
        """
        Checks all devices for connection loss and sends alerts if a device is offline.
        """
        print(f"[{datetime.utcnow()}] Running device status check...")
        
        # Define the time threshold for a device to be considered offline
        offline_threshold = datetime.utcnow() - timedelta(minutes=5)
        
        # Get all devices from the database
        devices = Device.query.all()
        
        for device in devices:
            # Find the most recent sensor log for this device
            latest_log = SensorData.query.filter_by(device_id=device.id).order_by(SensorData.timestamp.desc()).first()
            
            is_offline = False
            if latest_log is None:
                # If a device has never sent data, it's considered offline
                is_offline = True
            elif latest_log.timestamp < offline_threshold:
                # If the latest data point is older than our threshold, it's offline
                is_offline = True

            if is_offline:
                # --- CHECK IF AN OFFLINE ALERT WAS RECENTLY SENT ---
                # This prevents spamming the admin with an email every minute for the same offline device.
                # We check if the last alert for this device in the past 15 minutes was a 'Connection Loss' alert.
                recent_alert_threshold = datetime.utcnow() - timedelta(minutes=15)
                
                last_offline_alert = AlertLog.query.filter(
                    AlertLog.device_id == device.id,
                    AlertLog.alert_type == 'Connection Loss',
                    AlertLog.timestamp > recent_alert_threshold
                ).first()

                if not last_offline_alert:
                    print(f"ALERT: Device '{device.name}' appears to be offline. Sending notification.")
                    
                    message = f"Connection Loss Alert for device '{device.name}'. No data has been received in over 5 minutes."
                    
                    # 1. Log the alert to the database
                    new_alert = AlertLog(
                        device_id=device.id,
                        alert_type='Connection Loss',
                        message=message
                    )
                    db.session.add(new_alert)
                    db.session.commit()
                    
                    # 2. Send an email to the admin
                    # TODO: Make the recipient dynamic in the future
                    admin_email = 'admin@example.com' 
                    subject = f"Device Offline: {device.name}"
                    send_alert_email(recipient=admin_email, subject=subject, body=message)
                else:
                    print(f"INFO: Device '{device.name}' is offline, but an alert was sent recently. Skipping.")

    # --- Main Loop ---
    if __name__ == "__main__":
        print("Starting Connection Loss Checker...")
        while True:
            check_device_status()
            # Wait for 60 seconds before checking again
            print("Check complete. Waiting for 60 seconds...")
            time.sleep(60)


