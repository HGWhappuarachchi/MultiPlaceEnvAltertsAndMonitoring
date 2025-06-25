# /app/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth import admin_required
# Ensure all necessary models are imported
from app.models import User, Device, AlertLog, SensorData 
from app import db
from app.email import send_alert_email
# Import datetime and timedelta for checking online status
from datetime import datetime, timedelta 

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Renders the admin-only dashboard with live system stats."""
    
    # --- GATHER SYSTEM STATISTICS ---
    
    # Count total users and devices
    user_count = User.query.count()
    device_count = Device.query.count()
    
    # Determine Online/Offline status of devices
    # A device is considered offline if it hasn't sent data in the last 5 minutes
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    # Subquery to find the latest timestamp for each device
    subquery = db.session.query(
        SensorData.device_id,
        db.func.max(SensorData.timestamp).label('max_timestamp')
    ).group_by(SensorData.device_id).subquery()
    
    # Left outer join to include devices that have never sent data
    latest_device_logs = db.session.query(Device, subquery.c.max_timestamp).outerjoin(
        subquery, Device.id == subquery.c.device_id
    ).all()
    
    online_devices = 0
    offline_devices = 0
    for device, max_timestamp in latest_device_logs:
        # A device is online if it has a timestamp that is more recent than 5 minutes ago
        if max_timestamp and max_timestamp > five_minutes_ago:
            online_devices += 1
        else:
            offline_devices += 1

    # Get the 10 most recent alerts for the activity feed
    recent_alerts = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        user_count=user_count,
        device_count=device_count,
        online_devices=online_devices,
        offline_devices=offline_devices,
        recent_alerts=recent_alerts
    )

# --- User Management Routes ---

@bp.route('/users')
@login_required
@admin_required
def users():
    """Show a list of all users."""
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Handles adding a new user."""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        role = request.form.get('role')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash(f'User with email {email} already exists.', 'error')
            return redirect(url_for('admin.add_user'))

        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            role=role
        )
        if password:
            new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        subject = "Welcome to the Environmental Monitoring System"
        body = f"Hello {full_name},\n\nAn account has been created for you. You can now log in."
        send_alert_email(recipient=new_user.email, subject=subject, body=body)

        flash(f'User {full_name} has been created successfully!')
        return redirect(url_for('admin.users'))

    return render_template('admin/add_user.html')


@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Handles editing an existing user and their device assignments."""
    user_to_edit = User.query.get_or_404(user_id)
    all_devices = Device.query.all()

    if request.method == 'POST':
        user_to_edit.full_name = request.form.get('full_name')
        user_to_edit.email = request.form.get('email')
        user_to_edit.phone_number = request.form.get('phone_number')
        user_to_edit.role = request.form.get('role')
        
        password = request.form.get('password')
        if password:
            user_to_edit.set_password(password)

        assigned_device_ids = request.form.getlist('devices')
        user_to_edit.devices = [device for device in all_devices if str(device.id) in assigned_device_ids]

        db.session.commit()
        flash(f'User {user_to_edit.full_name} updated successfully!')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', user=user_to_edit, devices=all_devices)


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Handles deleting a user."""
    user_to_delete = User.query.get_or_404(user_id)
    
    if user_to_delete.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
        
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'User {user_to_delete.full_name} has been deleted.')
    return redirect(url_for('admin.users'))

# --- Device Management Routes ---

@bp.route('/devices')
@login_required
@admin_required
def devices():
    """Show a list of all devices."""
    all_devices = Device.query.all()
    return render_template('admin/devices.html', devices=all_devices)

@bp.route('/devices/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_device():
    if request.method == 'POST':
        new_device = Device(
            name=request.form.get('name'),
            unique_hardware_id=request.form.get('unique_hardware_id'),
            category=request.form.get('category'),
            temp_threshold_high=float(request.form.get('temp_threshold_high')) if request.form.get('temp_threshold_high') else None,
            humidity_threshold_low=float(request.form.get('humidity_threshold_low')) if request.form.get('humidity_threshold_low') else None,
            humidity_threshold_high=float(request.form.get('humidity_threshold_high')) if request.form.get('humidity_threshold_high') else None,
            voltage_threshold_low=float(request.form.get('voltage_threshold_low')) if request.form.get('voltage_threshold_low') else None,
            voltage_threshold_high=float(request.form.get('voltage_threshold_high')) if request.form.get('voltage_threshold_high') else None,
            alert_on_water=request.form.get('alert_on_water') == 'on'
        )
        db.session.add(new_device)
        db.session.commit()
        flash(f'Device {new_device.name} has been added successfully!')
        return redirect(url_for('admin.devices'))
    return render_template('admin/add_device.html')

@bp.route('/devices/edit/<int:device_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_device(device_id):
    device_to_edit = Device.query.get_or_404(device_id)
    if request.method == 'POST':
        device_to_edit.name = request.form.get('name')
        device_to_edit.unique_hardware_id = request.form.get('unique_hardware_id')
        device_to_edit.category = request.form.get('category')
        device_to_edit.temp_threshold_high = float(request.form.get('temp_threshold_high')) if request.form.get('temp_threshold_high') else None
        device_to_edit.humidity_threshold_low = float(request.form.get('humidity_threshold_low')) if request.form.get('humidity_threshold_low') else None
        device_to_edit.humidity_threshold_high = float(request.form.get('humidity_threshold_high')) if request.form.get('humidity_threshold_high') else None
        device_to_edit.voltage_threshold_low = float(request.form.get('voltage_threshold_low')) if request.form.get('voltage_threshold_low') else None
        device_to_edit.voltage_threshold_high = float(request.form.get('voltage_threshold_high')) if request.form.get('voltage_threshold_high') else None
        device_to_edit.alert_on_water = request.form.get('alert_on_water') == 'on'
        db.session.commit()
        flash(f'Device {device_to_edit.name} updated successfully!')
        return redirect(url_for('admin.devices'))
    return render_template('admin/edit_device.html', device=device_to_edit)

@bp.route('/devices/delete/<int:device_id>', methods=['POST'])
@login_required
@admin_required
def delete_device(device_id):
    """Handles deleting a device."""
    device_to_delete = Device.query.get_or_404(device_id)
    db.session.delete(device_to_delete)
    db.session.commit()
    flash(f'Device {device_to_delete.name} has been deleted.')
    return redirect(url_for('admin.devices'))

# --- Alert Management Route ---

@bp.route('/alerts')
@login_required
@admin_required
def alerts():
    """Shows a list of all alerts in the system for admin users."""
    all_alerts = AlertLog.query.order_by(AlertLog.timestamp.desc()).all()
    return render_template('admin/alerts.html', alerts=all_alerts)
@bp.route('/maintenance', methods=['GET', 'POST'])
@login_required
@admin_required
def maintenance():
    # ... logic is correct
    return render_template('admin/maintenance.html')

