"""
Authentifizierungs- und Autorisierungssystem mit SQLAlchemy-Integration
"""
from functools import wraps
from flask import request, jsonify
from services import UserService, SessionService

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
