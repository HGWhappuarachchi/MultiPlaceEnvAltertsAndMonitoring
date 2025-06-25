# Intelligent Environmental Monitoring System

A web-based platform for real-time monitoring and alerting of critical server room environments. This system tracks temperature, humidity, AC voltage, and water leaks, providing live dashboards, alert logs, and device/user management for administrators.

---

## Features

- **Live Dashboard:** View real-time sensor data and alert status for all assigned devices.
- **Historical Data:** Visualize and export historical sensor readings.
- **Alerting:** Email notifications for temperature, humidity, voltage, and water leak events.
- **User Management:** Admins can add, edit, and assign devices to users.
- **Device Management:** Provision new devices, set alert thresholds, and edit device details.
- **Role-Based Access:** Admin and regular user roles with appropriate permissions.
- **REST API:** Devices can POST sensor data to the `/api/ingest` endpoint.

---

## Project Structure

```
environmental_monitoring/
├── app/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── email.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── layout.html
│       ├── index.html
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── devices.html
│       │   ├── add_device.html
│       │   ├── edit_device.html
│       │   ├── users.html
│       │   ├── add_user.html
│       │   ├── edit_user.html
│       │   └── alerts.html
│       ├── history.html
│       └── login.html
├── config.py
├── run.py
├── app.db
└── migrations/
```

---

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd environmental_monitoring
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set environment variables (optional, for email alerts):**
   ```
   set MAIL_USERNAME=your_email@example.com
   set MAIL_PASSWORD=your_password
   set MAIL_DEFAULT_SENDER=alerts@yourdomain.com
   ```
**Admin**: admin@example.com
***password***: adminpass
**User**:  user@example.com
***passowrd***: userpass

5. **Initialize the database:**
   ```sh
   flask db upgrade
   ```

6. **Run the server:**
   ```sh
   python run.py
   ```

7. **Access the app:**
   Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- **Login:** Use the login page to access your dashboard.
- **Admin Panel:** Admins can manage users and devices from the admin dashboard.
- **Device API:** Devices should POST sensor data to `/api/ingest` with JSON payload:
  ```json
  {
    "device_id": "DEVICE_UNIQUE_ID",
    "data": {
      "temperature": 25.3,
      "humidity": 45.2,
      "ac_voltage": 230.1,
      "water_detected": false
    }
  }
  ```

---

## Technologies Used

- Python 3, Flask, Flask-Login, Flask-Migrate, SQLAlchemy
- SQLite (default, can be changed)
- HTML/CSS (Jinja2 templates)
- Chart.js for data visualization

---

## License

This project is licensed under the MIT License.

---

## Credits

Developed by Ghapuarachchi.
