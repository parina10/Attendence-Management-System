"""
Authentication module for handling user login and signup
"""
import hashlib
import re
import db
from db import create_user, get_user_by_username

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username (3-20 characters, alphanumeric and underscore)"""
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, ""

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    return True, ""

def signup_user(username, email, password):
    """Handle user signup"""
    # Validate username
    is_valid, message = validate_username(username)
    if not is_valid:
        return False, message

    # Validate email
    if not validate_email(email):
        return False, "Invalid email format"

    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message

    # Hash password and create user
    password_hash = hash_password(password)
    success, message = create_user(username, email, password_hash)

    return success, message

def login_user(username, password):
    """Handle user login"""
    user = get_user_by_username(username)

    if not user:
        return False, None, "Invalid username or password"

    if not verify_password(password, user['password_hash']):
        return False, None, "Invalid username or password"

    return True, user, "Login successful"

def is_authenticated(session_state):
    """Check if user is authenticated"""
    return session_state.get('authenticated', False) and session_state.get('user_id') is not None

def logout_user(session_state):
    """Handle user logout"""
    session_state.authenticated = False
    session_state.user_id = None
    session_state.username = None
    session_state.email = None
    session_state.page = 'login'
