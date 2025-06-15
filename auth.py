"""
Authentifizierungs- und Autorisierungssystem
"""
import uuid
from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash
from models import get_user_by_email, get_user_by_id

# In-Memory-Session-Speicher
active_sessions = {}

def generate_session_token():
    """Generiert ein eindeutiges Session-Token"""
    return str(uuid.uuid4())

def create_session(user_id):
    """Erstellt eine neue Session für einen Benutzer"""
    token = generate_session_token()
    active_sessions[token] = user_id
    return token

def get_user_from_session(token):
    """Gibt den Benutzer für ein Session-Token zurück"""
    if token in active_sessions:
        user_id = active_sessions[token]
        return get_user_by_id(user_id)
    return None

def invalidate_session(token):
    """Invalidiert ein Session-Token"""
    if token in active_sessions:
        del active_sessions[token]
        return True
    return False

def authenticate_user(email, password):
    """Authentifiziert einen Benutzer mit E-Mail und Passwort"""
    user = get_user_by_email(email)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def require_auth(f):
    """Decorator für Endpunkte, die Authentifizierung erfordern"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization header fehlt'}), 401
        
        # Bearer Token Format unterstützen
        if token.startswith('Bearer '):
            token = token[7:]
        
        user = get_user_from_session(token)
        if not user:
            return jsonify({'error': 'Ungültiges oder abgelaufenes Token'}), 401
        
        # Benutzer-Informationen an die Route weitergeben
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator für Endpunkte, die Admin-Rechte erfordern"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization header fehlt'}), 401
        
        # Bearer Token Format unterstützen
        if token.startswith('Bearer '):
            token = token[7:]
        
        user = get_user_from_session(token)
        if not user:
            return jsonify({'error': 'Ungültiges oder abgelaufenes Token'}), 401
        
        if not user.get('admin', False):
            return jsonify({'error': 'Admin-Rechte erforderlich'}), 403
        
        # Benutzer-Informationen an die Route weitergeben
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Hilfsfunktion um den aktuellen Benutzer zu erhalten"""
    return getattr(request, 'current_user', None)

