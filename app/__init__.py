# /app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login = LoginManager()
# If a user who is not logged in tries to access a protected page,
# Flask-Login will redirect them to the login view.
login.login_view = 'auth.login' 

def create_app(config_class=Config):
    """
    Application factory function. Configures and returns the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind extensions to the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login.init_app(app)

    # --- Register Blueprints ---
    # We import here to avoid circular dependencies.
    
    # Main application routes (dashboard, data ingestion)
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Authentication routes (login, logout)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp) # url_prefix removed as requested

    # Admin routes (user and device management)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    # This import ensures that the models are registered with SQLAlchemy
    # before any database operations are performed.
    from app import models

    return app
