"""
Flask Web-Backend mit Benutzer- und Notizen-Verwaltung
"""
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
import re

# Lokale Imports
from models import (
    create_user, get_user_by_email, get_user_by_name, get_user_by_id,
    delete_user, get_all_users,
    create_note, get_note_by_id, get_notes_by_owner,
    update_note, delete_note
)
from auth import (
    authenticate_user, create_session, invalidate_session,
    require_auth, require_admin, get_current_user
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Hilfsfunktionen für Validierung
def validate_email(email):
    """Validiert E-Mail-Format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validiert Passwort-Stärke (mindestens 6 Zeichen)"""
    return len(password) >= 6

# Fehlerbehandlung
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpunkt nicht gefunden'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interner Serverfehler'}), 500

# Authentifizierungs-Endpunkte
@app.route('/register', methods=['POST'])
def register():
    """Benutzerregistrierung"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        # Erforderliche Felder prüfen
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Feld "{field}" ist erforderlich'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validierung
        if not validate_email(email):
            return jsonify({'error': 'Ungültiges E-Mail-Format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Passwort muss mindestens 6 Zeichen lang sein'}), 400
        
        # Eindeutigkeit prüfen
        if get_user_by_email(email):
            return jsonify({'error': 'E-Mail bereits registriert'}), 409
        
        if get_user_by_name(name):
            return jsonify({'error': 'Benutzername bereits vergeben'}), 409
        
        # Benutzer erstellen
        password_hash = generate_password_hash(password)
        user = create_user(name, email, password_hash)
        
        # Antwort ohne Passwort-Hash
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            'message': 'Benutzer erfolgreich registriert',
            'user': user_response
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Fehler bei der Registrierung'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Benutzeranmeldung"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'E-Mail und Passwort erforderlich'}), 400
        
        # Benutzer authentifizieren
        user = authenticate_user(email, password)
        if not user:
            return jsonify({'error': 'Ungültige Anmeldedaten'}), 401
        
        # Session erstellen
        token = create_session(user['id'])
        
        # Antwort ohne Passwort-Hash
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            'message': 'Erfolgreich angemeldet',
            'token': token,
            'user': user_response
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler bei der Anmeldung'}), 500

@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Benutzerabmeldung"""
    try:
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if token and invalidate_session(token):
            return jsonify({'message': 'Erfolgreich abgemeldet'}), 200
        else:
            return jsonify({'error': 'Fehler beim Abmelden'}), 400
            
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abmelden'}), 500

# Notizen-Endpunkte
@app.route('/notes', methods=['GET'])
@require_auth
def get_notes():
    """Alle eigenen Notizen abrufen"""
    try:
        user = get_current_user()
        notes = get_notes_by_owner(user['id'])
        return jsonify({'notes': notes}), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Notizen'}), 500

@app.route('/notes', methods=['POST'])
@require_auth
def create_note_endpoint():
    """Neue Notiz erstellen"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({'error': 'Titel ist erforderlich'}), 400
        
        if not content:
            return jsonify({'error': 'Inhalt ist erforderlich'}), 400
        
        user = get_current_user()
        note = create_note(title, content, user['id'])
        
        return jsonify({
            'message': 'Notiz erfolgreich erstellt',
            'note': note
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Erstellen der Notiz'}), 500

@app.route('/notes/<int:note_id>', methods=['GET'])
@require_auth
def get_note(note_id):
    """Einzelne Notiz abrufen"""
    try:
        note = get_note_by_id(note_id)
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        user = get_current_user()
        if note['owner_id'] != user['id']:
            return jsonify({'error': 'Zugriff verweigert'}), 403
        
        return jsonify({'note': note}), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Notiz'}), 500

@app.route('/notes/<int:note_id>', methods=['PUT'])
@require_auth
def update_note_endpoint(note_id):
    """Notiz bearbeiten"""
    try:
        note = get_note_by_id(note_id)
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        user = get_current_user()
        if note['owner_id'] != user['id']:
            return jsonify({'error': 'Zugriff verweigert'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        title = data.get('title', '').strip() if 'title' in data else None
        content = data.get('content', '').strip() if 'content' in data else None
        
        # Mindestens ein Feld muss aktualisiert werden
        if title is None and content is None:
            return jsonify({'error': 'Titel oder Inhalt muss angegeben werden'}), 400
        
        # Leere Werte verhindern
        if title is not None and not title:
            return jsonify({'error': 'Titel darf nicht leer sein'}), 400
        
        if content is not None and not content:
            return jsonify({'error': 'Inhalt darf nicht leer sein'}), 400
        
        updated_note = update_note(note_id, title, content)
        
        return jsonify({
            'message': 'Notiz erfolgreich aktualisiert',
            'note': updated_note
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Aktualisieren der Notiz'}), 500

@app.route('/notes/<int:note_id>', methods=['DELETE'])
@require_auth
def delete_note_endpoint(note_id):
    """Notiz löschen"""
    try:
        note = get_note_by_id(note_id)
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        user = get_current_user()
        if note['owner_id'] != user['id']:
            return jsonify({'error': 'Zugriff verweigert'}), 403
        
        if delete_note(note_id):
            return jsonify({'message': 'Notiz erfolgreich gelöscht'}), 200
        else:
            return jsonify({'error': 'Fehler beim Löschen der Notiz'}), 500
            
    except Exception as e:
        return jsonify({'error': 'Fehler beim Löschen der Notiz'}), 500

# Admin-Endpunkte
@app.route('/users', methods=['GET'])
@require_admin
def get_users():
    """Alle Benutzer auflisten (nur Admin)"""
    try:
        users = get_all_users()
        return jsonify({'users': users}), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Benutzer'}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user_endpoint(user_id):
    """Benutzer löschen (nur Admin)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'Benutzer nicht gefunden'}), 404
        
        current_user = get_current_user()
        if user_id == current_user['id']:
            return jsonify({'error': 'Admin kann sich nicht selbst löschen'}), 400
        
        if delete_user(user_id):
            return jsonify({'message': 'Benutzer erfolgreich gelöscht'}), 200
        else:
            return jsonify({'error': 'Fehler beim Löschen des Benutzers'}), 500
            
    except Exception as e:
        return jsonify({'error': 'Fehler beim Löschen des Benutzers'}), 500

# Informations-Endpunkt
@app.route('/', methods=['GET'])
def index():
    """API-Informationen"""
    return jsonify({
        'message': 'Flask Web-Backend API',
        'version': '1.0.0',
        'endpoints': {
            'auth': ['/register', '/login', '/logout'],
            'notes': ['/notes', '/notes/<id>'],
            'admin': ['/users', '/users/<id>']
        }
    }), 200

@app.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Aktuelle Benutzerinformationen abrufen"""
    try:
        user = get_current_user()
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        return jsonify({'user': user_response}), 200
        
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Benutzerinformationen'}), 500

if __name__ == '__main__':
    print("🚀 Flask Web-Backend wird gestartet...")
    print("📋 Verfügbare Dummy-Benutzer:")
    print("   Admin: admin@example.com / admin123")
    print("   User1: john@example.com / password123")
    print("   User2: jane@example.com / mypassword")
    print("🌐 Server läuft auf: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

