# /config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this-secret-key'

    # --- UPDATED DATABASE CONFIGURATION ---
    # We are adding '?timeout=15' to the end of the SQLite URI.
    # This tells SQLite to wait for 15 seconds if the database is locked
    # before giving up. This is usually more than enough time for the other
    # operation to finish.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') + '?timeout=15'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Email Configuration ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'alerts@yourdomain.com'
