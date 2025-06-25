# /app/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
# We need to import the 'login' manager and the 'User' model
from app import db, login
from app.models import User
from functools import wraps
from flask_login import current_user
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# This is the function we moved from models.py
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

bp = Blueprint('auth', __name__)

# --- No changes to the login or logout routes ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... keep existing code ...
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))