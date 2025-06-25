# /app/models.py

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Association table to link users and devices
user_device_association = db.Table('user_device_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'))
)

class User(UserMixin, db.Model):
    """Represents a user in the system."""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(10), default='user', nullable=False)
    
    devices = db.relationship(
        'Device', secondary=user_device_association,
        backref=db.backref('users', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.full_name}>'

class Device(db.Model):
    """Represents a physical monitoring device."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    unique_hardware_id = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(120), default='default')
    
    # --- All Alert Thresholds ---
    temp_threshold_high = db.Column(db.Float)
    humidity_threshold_low = db.Column(db.Float)
    humidity_threshold_high = db.Column(db.Float)
    alert_on_water = db.Column(db.Boolean, default=True)
    # --- NEW VOLTAGE THRESHOLDS ---
    voltage_threshold_low = db.Column(db.Float)
    voltage_threshold_high = db.Column(db.Float)

    # --- All Alert Statuses ---
    temp_alert_status = db.Column(db.Boolean, default=False)
    humidity_alert_status = db.Column(db.Boolean, default=False)
    water_alert_status = db.Column(db.Boolean, default=False)
    # --- NEW VOLTAGE STATUS ---
    voltage_alert_status = db.Column(db.Boolean, default=False)


    # Relationships
    sensor_data = db.relationship('SensorData', backref='device', lazy='dynamic')
    alerts = db.relationship('AlertLog', backref='device', lazy='dynamic')
    
    def __repr__(self):
        return f'<Device {self.name}>'

class SensorData(db.Model):
    """Represents a single data log from a device's sensors."""
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    ac_voltage = db.Column(db.Float)
    water_detected = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return f'<SensorData from Device {self.device_id} at {self.timestamp}>'

class AlertLog(db.Model):
    """Represents a single alert event in the system."""
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return f'<AlertLog for Device {self.device_id} at {self.timestamp}>'
