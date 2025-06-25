# /app/email.py

from flask_mail import Message
from app import mail # We will create this 'mail' object in the next step
from flask import current_app

def send_alert_email(recipient, subject, body):
    """Sends an email alert."""
    msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.body = body
    try:
        mail.send(msg)
        print(f"Alert email sent successfully to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")