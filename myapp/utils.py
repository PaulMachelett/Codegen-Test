"""
Hilfsfunktionen und Authentifizierung
"""
import re
from functools import wraps
from flask import request, jsonify
from .crud import SessionService

# Validierungsfunktionen
def validate_email(email):
    """Validiert E-Mail-Format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validiert Passwort-Stärke (mindestens 6 Zeichen)"""
    return len(password) >= 6

# Authentifizierungs-Decorators
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
        
        user = SessionService.get_user_from_session(token)
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
        
        user = SessionService.get_user_from_session(token)
        if not user:
            return jsonify({'error': 'Ungültiges oder abgelaufenes Token'}), 401
        
        if not user.admin:
            return jsonify({'error': 'Admin-Rechte erforderlich'}), 403
        
        # Benutzer-Informationen an die Route weitergeben
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Hilfsfunktion um den aktuellen Benutzer zu erhalten"""
    return getattr(request, 'current_user', None)

# Weitere Hilfsfunktionen
def sanitize_input(text, max_length=None):
    """Bereinigt Benutzereingaben"""
    if not text:
        return text
    
    # Grundlegende Bereinigung
    text = text.strip()
    
    # Länge begrenzen falls angegeben
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def format_error_response(message, status_code=400):
    """Formatiert Fehlerantworten einheitlich"""
    return jsonify({'error': message}), status_code

def format_success_response(message, data=None, status_code=200):
    """Formatiert Erfolgsantworten einheitlich"""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code

