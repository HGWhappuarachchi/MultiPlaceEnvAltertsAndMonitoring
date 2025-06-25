# /app/routes.py

from flask import render_template, request, jsonify, Blueprint
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from app import db
from app.models import Device, SensorData, AlertLog
from app.email import send_alert_email

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
     return render_template('index.html')

def check_and_send_alerts(device, sensor_readings):
    """Stateful helper function to check all alert conditions."""
    alert_recipients = [user.email for user in device.users]
    if not alert_recipients:
        return

    # Check High Temperature
    temp = sensor_readings.get('temperature')
    if device.temp_threshold_high is not None and temp is not None:
        is_in_alert = temp > device.temp_threshold_high
        if is_in_alert and not device.temp_alert_status:
            device.temp_alert_status = True
            message = f"High Temperature Alert for device '{device.name}': Current temp ({temp}°C) exceeded threshold ({device.temp_threshold_high}°C)."
            db.session.add(AlertLog(device_id=device.id, alert_type='High Temperature', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"ALERT: High Temperature on {device.name}", message)
        elif not is_in_alert and device.temp_alert_status:
            device.temp_alert_status = False
            message = f"Temperature Returned to Normal for device '{device.name}': Current temp is {temp}°C."
            db.session.add(AlertLog(device_id=device.id, alert_type='Temperature Normal', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"OK: Temperature Normal on {device.name}", message)

    # Check Humidity
    humidity = sensor_readings.get('humidity')
    if humidity is not None:
        is_in_hum_alert = (device.humidity_threshold_low is not None and humidity < device.humidity_threshold_low) or \
                          (device.humidity_threshold_high is not None and humidity > device.humidity_threshold_high)
        if is_in_hum_alert and not device.humidity_alert_status:
            device.humidity_alert_status = True
            alert_type = "Low Humidity" if (device.humidity_threshold_low and humidity < device.humidity_threshold_low) else "High Humidity"
            message = f"{alert_type} Alert for device '{device.name}': Current humidity is {humidity}%."
            db.session.add(AlertLog(device_id=device.id, alert_type=alert_type, message=message))
            for email in alert_recipients:
                send_alert_email(email, f"ALERT: Humidity Issue on {device.name}", message)
        elif not is_in_hum_alert and device.humidity_alert_status:
            device.humidity_alert_status = False
            message = f"Humidity Returned to Normal for device '{device.name}': Current humidity is {humidity}%."
            db.session.add(AlertLog(device_id=device.id, alert_type='Humidity Normal', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"OK: Humidity Normal on {device.name}", message)

    # --- NEW: Check AC Voltage ---
    voltage = sensor_readings.get('ac_voltage')
    if voltage is not None:
        is_in_volt_alert = (device.voltage_threshold_low is not None and voltage < device.voltage_threshold_low) or \
                           (device.voltage_threshold_high is not None and voltage > device.voltage_threshold_high)
        if is_in_volt_alert and not device.voltage_alert_status:
            device.voltage_alert_status = True
            alert_type = "Low Voltage" if (device.voltage_threshold_low and voltage < device.voltage_threshold_low) else "High Voltage"
            message = f"{alert_type} Alert for device '{device.name}': Current voltage is {voltage}V."
            db.session.add(AlertLog(device_id=device.id, alert_type=alert_type, message=message))
            for email in alert_recipients:
                send_alert_email(email, f"ALERT: Voltage Issue on {device.name}", message)
        elif not is_in_volt_alert and device.voltage_alert_status:
            device.voltage_alert_status = False
            message = f"Voltage Returned to Normal for device '{device.name}': Current voltage is {voltage}V."
            db.session.add(AlertLog(device_id=device.id, alert_type='Voltage Normal', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"OK: Voltage Normal on {device.name}", message)

    # Check Water Leak
    water_detected = sensor_readings.get('water_detected', False)
    if device.alert_on_water:
        if water_detected and not device.water_alert_status:
            device.water_alert_status = True
            message = f"CRITICAL: Water Leak Detected for device '{device.name}'."
            db.session.add(AlertLog(device_id=device.id, alert_type='Water Leak', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"CRITICAL: Water Leak on {device.name}", message)
        elif not water_detected and device.water_alert_status:
            device.water_alert_status = False
            message = f"Water Leak Cleared for device '{device.name}'."
            db.session.add(AlertLog(device_id=device.id, alert_type='Water Leak Cleared', message=message))
            for email in alert_recipients:
                send_alert_email(email, f"OK: Water Leak Cleared on {device.name}", message)

@bp.route('/api/ingest', methods=['POST'])
def ingest_data():
    req_data = request.get_json()
    if not req_data:
        return jsonify({"error": "Invalid JSON"}), 400
    device_hardware_id = req_data.get('device_id')
    sensor_readings = req_data.get('data')
    if not device_hardware_id or not sensor_readings:
        return jsonify({"error": "Missing 'device_id' or 'data' in payload"}), 400
    device = Device.query.filter_by(unique_hardware_id=device_hardware_id).first()
    if not device:
        return jsonify({"error": f"Device with ID '{device_hardware_id}' is not registered."}), 403
    new_data_log = SensorData(
        device_id=device.id,
        temperature=sensor_readings.get('temperature'),
        humidity=sensor_readings.get('humidity'),
        ac_voltage=sensor_readings.get('ac_voltage'),
        water_detected=sensor_readings.get('water_detected', False)
    )
    db.session.add(new_data_log)
    check_and_send_alerts(device, sensor_readings)
    db.session.commit()
    return jsonify({"status": "success", "message": "Data logged successfully"}), 200

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Renders the main dashboard, including live alert status for each device,
    respecting user-device assignments.
    """
    assigned_devices = current_user.devices.all()
    assigned_device_ids = [device.id for device in assigned_devices]
    
    latest_logs_with_status = []
    if assigned_device_ids:
        subquery = db.session.query(
            SensorData.device_id,
            db.func.max(SensorData.timestamp).label('max_timestamp')
        ).filter(SensorData.device_id.in_(assigned_device_ids)).group_by(SensorData.device_id).subquery()

        results = db.session.query(SensorData, Device).join(
            subquery,
            db.and_(
                SensorData.device_id == subquery.c.device_id,
                SensorData.timestamp == subquery.c.max_timestamp
            )
        ).join(Device, SensorData.device_id == Device.id).all()
        
        for log, device in results:
            latest_logs_with_status.append({
                'log': log,
                'device': device
            })

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    return render_template(
        'dashboard.html', 
        items=latest_logs_with_status,
        last_updated=current_time
    )

@bp.route('/history')
@login_required
def history():
    assigned_devices = current_user.devices.all()
    assigned_device_ids = [d.id for d in assigned_devices]
    end_date_str = request.args.get('end_date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    start_date_str = request.args.get('start_date', (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d'))
    selected_device_id = request.args.get('device_id', 'all')
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
    historical_data = []
    if assigned_device_ids:
        query = SensorData.query.filter(SensorData.device_id.in_(assigned_device_ids), SensorData.timestamp >= start_date, SensorData.timestamp < end_date)
        if selected_device_id != 'all':
            query = query.filter(SensorData.device_id == int(selected_device_id))
        historical_data = query.order_by(SensorData.timestamp.asc()).all()
    chart_data = {
        'labels': [d.timestamp.isoformat() for d in historical_data],
        'temperatures': [d.temperature for d in historical_data],
        'humidities': [d.humidity for d in historical_data],
        'ac_voltages': [d.ac_voltage for d in historical_data]
    }
    return render_template('history.html', data=historical_data, chart_data=chart_data, start_date=start_date_str, end_date=end_date_str, devices=assigned_devices, selected_device_id=selected_device_id)

@bp.route('/alerts')
@login_required
def alerts():
    assigned_device_ids = [device.id for device in current_user.devices.all()]
    user_alerts = []
    if assigned_device_ids:
        user_alerts = AlertLog.query.filter(AlertLog.device_id.in_(assigned_device_ids)).order_by(AlertLog.timestamp.desc()).all()
    return render_template('alerts.html', alerts=user_alerts)
