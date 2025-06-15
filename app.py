import os
import jwt
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
# IMPORTANT: Use a strong, unique secret key in production.
# This key is deliberately made easy to find for demonstration purposes.
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'super-secret-key-for-jwt-signing') 

# Hardcoded users for demonstration
USERS = {
    "user": {"password": "password123", "role": "user"},
    "admin": {"password": "adminpassword", "role": "admin"}
}

# --- JWT Helper Functions ---

def generate_jwt(username, role):
    """Generates a signed JWT for the given user."""
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(minutes=30) # Token expires in 30 minutes
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt(token):
    """Decodes a JWT and returns its payload, or None if invalid."""
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

# --- Decorator for Protected Endpoints ---

def jwt_required(f):
    """
    Decorator to ensure a JWT is present and valid.
    Redirects to login if no token or token is invalid/expired.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            # If no token, redirect to login page
            return redirect(url_for('login'), code=401) 

        data = decode_jwt(token)
        if "error" in data:
            # If token is invalid or expired, return error message
            return jsonify({"message": data["error"]}), 401
        
        # Attach decoded user data to the request object for later use
        request.current_user = data 
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """
    Decorator to ensure the user has 'admin' role.
    Contains the deliberate access-control flaw.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            return redirect(url_for('login'), code=401)

        data = decode_jwt(token)
        if "error" in data:
            return jsonify({"message": data["error"]}), 401

        # --- DELIBERATE ACCESS-CONTROL FLAW STARTS HERE ---
        # The flaw: We *only* check for the presence of 'admin' as a substring in the role.
        # This means a user with role 'user;admin' or 'superadmin' (if such a role existed)
        # could gain access, as 'admin' is a substring of their role.
        # The correct, secure check would be: if data.get('role') != 'admin':
        if 'admin' not in data.get('role', ''):
            return jsonify({"message": "Access Denied: Admin role required."}), 403
        # --- DELIBERATE ACCESS-CONTROL FLAW ENDS HERE ---
        
        request.current_user = data
        return f(*args, **kwargs)
    return decorated


# --- Routes ---

@app.route('/')
def index():
    """Redirects to the login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login and JWT issuance."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = USERS.get(username)
        if user and user['password'] == password:
            # Generate JWT with username and role from hardcoded users
            token = generate_jwt(username, user['role'])
            resp = make_response(redirect(url_for('dashboard')))
            # Set JWT as an httponly cookie. secure=True for production HTTPS.
            resp.set_cookie('jwt_token', token, httponly=True, secure=False) 
            return resp
        else:
            return render_template('login.html', message="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard')
@jwt_required
def dashboard():
    """Routes to the appropriate dashboard based on user role."""
    user_role = request.current_user['role']
    if user_role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/user/dashboard')
@jwt_required
def user_dashboard():
    """User-specific dashboard accessible by any valid user."""
    return render_template('user_dashboard.html', username=request.current_user['username'])

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin-specific dashboard, protected by admin_required decorator."""
    return render_template('admin_dashboard.html', username=request.current_user['username'])

@app.route('/logout')
def logout():
    """Logs out the user by deleting the JWT cookie."""
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('jwt_token', '', expires=0, httponly=True, secure=False)
    return resp

if __name__ == '__main__':
    app.run(debug=True, port=5000)