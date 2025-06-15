"""
API-Routen und Endpunkte
"""
from flask import Blueprint, request, jsonify
from .crud import UserService, NoteService, SessionService
from .utils import (
    validate_email, validate_password, require_auth, require_admin, 
    get_current_user, sanitize_input, format_error_response, format_success_response
)

# Blueprint für API-Routen erstellen
api = Blueprint('api', __name__)

# Fehlerbehandlung
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpunkt nicht gefunden'}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interner Serverfehler'}), 500

# Authentifizierungs-Endpunkte
@api.route('/registe', methods=['POST'])
def register():
    """Benutzerregistrierung"""
    try:
        data = request.get_json()
        if not data:
            return format_error_response('JSON-Daten erforderlich')
        
        # Erforderliche Felder prüfen
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return format_error_response(f'Feld "{field}" ist erforderlich')
        
        name = sanitize_input(data['name'])
        email = sanitize_input(data['email']).lower()
        password = data['password']
        
        # Validierung
        if not validate_email(email):
            return format_error_response('Ungültiges E-Mail-Format')
        
        if not validate_password(password):
            return format_error_response('Passwort muss mindestens 6 Zeichen lang sein')
        
        # Eindeutigkeit prüfen
        if UserService.get_user_by_email(email):
            return format_error_response('E-Mail bereits registriert', 409)
        
        if UserService.get_user_by_name(name):
            return format_error_response('Benutzername bereits vergeben', 409)
        
        # Benutzer erstellen
        user = UserService.create_user(name, email, password)
        
        return format_success_response(
            'Benutzer erfolgreich registriert',
            {'user': user.to_dict()},
            201
        )
        
    except Exception as e:
        return format_error_response('Fehler bei der Registrierung', 500)

@api.route('/login', methods=['POST'])
def login():
    """Benutzeranmeldung"""
    try:
        data = request.get_json()
        if not data:
            return format_error_response('JSON-Daten erforderlich')
        
        email = sanitize_input(data.get('email', '')).lower()
        password = data.get('password', '')
        
        if not email or not password:
            return format_error_response('E-Mail und Passwort erforderlich')
        
        # Benutzer authentifizieren
        user = UserService.authenticate_user(email, password)
        if not user:
            return format_error_response('Ungültige Anmeldedaten', 401)
        
        # Session erstellen
        token = SessionService.create_session(user.id)
        
        return format_success_response(
            'Erfolgreich angemeldet',
            {
                'token': token,
                'user': user.to_dict()
            }
        )
        
    except Exception as e:
        return format_error_response('Fehler bei der Anmeldung', 500)

@api.route('/logout', methods=['POST'])
def logout():
    """Benutzerabmeldung"""
    try:
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if token and SessionService.invalidate_session(token):
            return format_success_response('Erfolgreich abgemeldet')
        else:
            return format_error_response('Fehler beim Abmelden')
        
    except Exception as e:
        return format_error_response('Fehler beim Abmelden', 500)

# Notizen-Endpunkte
@api.route('/notes', methods=['GET'])
@require_auth
def get_notes():
    """Alle eigenen Notizen abrufen"""
    try:
        user = get_current_user()
        notes = NoteService.get_notes_by_owner(user.id)
        notes_data = [note.to_dict() for note in notes]
        return jsonify({'notes': notes_data}), 200
        
    except Exception as e:
        return format_error_response('Fehler beim Abrufen der Notizen', 500)

@api.route('/notes', methods=['POST'])
@require_auth
def create_note():
    """Neue Notiz erstellen"""
    try:
        data = request.get_json()
        if not data:
            return format_error_response('JSON-Daten erforderlich')
        
        title = sanitize_input(data.get('title', ''), 200)
        content = sanitize_input(data.get('content', ''), 5000)
        
        if not title:
            return format_error_response('Titel ist erforderlich')
        
        if not content:
            return format_error_response('Inhalt ist erforderlich')
        
        user = get_current_user()
        note = NoteService.create_note(title, content, user.id)
        
        return format_success_response(
            'Notiz erfolgreich erstellt',
            {'note': note.to_dict()},
            201
        )
        
    except Exception as e:
        return format_error_response('Fehler beim Erstellen der Notiz', 500)

@api.route('/notes/<int:note_id>', methods=['GET'])
@require_auth
def get_note(note_id):
    """Einzelne Notiz abrufen"""
    try:
        note = NoteService.get_note_by_id(note_id)
        if not note:
            return format_error_response('Notiz nicht gefunden', 404)
        
        user = get_current_user()
        if note.owner_id != user.id:
            return format_error_response('Zugriff verweigert', 403)
        
        return jsonify({'note': note.to_dict()}), 200
        
    except Exception as e:
        return format_error_response('Fehler beim Abrufen der Notiz', 500)

@api.route('/notes/<int:note_id>', methods=['PUT'])
@require_auth
def update_note(note_id):
    """Notiz bearbeiten"""
    try:
        note = NoteService.get_note_by_id(note_id)
        if not note:
            return format_error_response('Notiz nicht gefunden', 404)
        
        user = get_current_user()
        if note.owner_id != user.id:
            return format_error_response('Zugriff verweigert', 403)
        
        data = request.get_json()
        if not data:
            return format_error_response('JSON-Daten erforderlich')
        
        title = data.get('title')
        content = data.get('content')
        
        # Validierung nur wenn Werte gesetzt sind
        if title is not None:
            title = sanitize_input(title, 200)
            if not title:
                return format_error_response('Titel darf nicht leer sein')
        
        if content is not None:
            content = sanitize_input(content, 5000)
            if not content:
                return format_error_response('Inhalt darf nicht leer sein')
        
        updated_note = NoteService.update_note(note_id, title, content)
        
        return format_success_response(
            'Notiz erfolgreich aktualisiert',
            {'note': updated_note.to_dict()}
        )
        
    except Exception as e:
        return format_error_response('Fehler beim Aktualisieren der Notiz', 500)

@api.route('/notes/<int:note_id>', methods=['DELETE'])
@require_auth
def delete_note(note_id):
    """Notiz löschen"""
    try:
        note = NoteService.get_note_by_id(note_id)
        if not note:
            return format_error_response('Notiz nicht gefunden', 404)
        
        user = get_current_user()
        if note.owner_id != user.id:
            return format_error_response('Zugriff verweigert', 403)
        
        if NoteService.delete_note(note_id):
            return format_success_response('Notiz erfolgreich gelöscht')
        else:
            return format_error_response('Fehler beim Löschen der Notiz', 500)
        
    except Exception as e:
        return format_error_response('Fehler beim Löschen der Notiz', 500)

# Admin-Endpunkte
@api.route('/users', methods=['GET'])
@require_admin
def get_users():
    """Alle Benutzer auflisten (nur Admin)"""
    try:
        users = UserService.get_all_users()
        users_data = [user.to_dict() for user in users]
        return jsonify({'users': users_data}), 200
        
    except Exception as e:
        return format_error_response('Fehler beim Abrufen der Benutzer', 500)

@api.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Benutzer löschen (nur Admin)"""
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return format_error_response('Benutzer nicht gefunden', 404)
        
        current_user = get_current_user()
        if user_id == current_user.id:
            return format_error_response('Admin kann sich nicht selbst löschen')
        
        if UserService.delete_user(user_id):
            return format_success_response('Benutzer erfolgreich gelöscht')
        else:
            return format_error_response('Fehler beim Löschen des Benutzers', 500)
        
    except Exception as e:
        return format_error_response('Fehler beim Löschen des Benutzers', 500)

# Benutzer-Info-Endpunkte
@api.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Aktuelle Benutzerinformationen abrufen"""
    try:
        user = get_current_user()
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return format_error_response('Fehler beim Abrufen der Benutzerinformationen', 500)

