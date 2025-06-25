# /run.py

from app import create_app, db
from app.models import User, Device, SensorData

# Create the Flask app instance using our factory
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    This function allows you to work with the database and models
    in an interactive shell without needing to import them every time.
    You can start it with the `flask shell` command.
    """
    return {'db': db, 'User': User, 'Device': Device, 'SensorData': SensorData}

if __name__ == '__main__':
    # This makes the app accessible on your local network,
    # so the Raspberry Pi can send data to it.
    # `debug=True` enables the debugger and auto-reloads the server on code changes.
    app.run(host='0.0.0.0', port=5000, debug=True)