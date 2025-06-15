"""
Datenmodelle und In-Memory-Speicher für das Flask-Backend
"""
from werkzeug.security import generate_password_hash

# In-Memory-Datenspeicher
users = []
notes = []

# ID-Zähler für neue Einträge
user_id_counter = 1
note_id_counter = 1

def init_dummy_data():
    """Initialisiert Dummy-Daten für Entwicklung und Tests"""
    global user_id_counter, note_id_counter
    
    # Dummy-Benutzer erstellen
    dummy_users = [
        {
            'id': 1,
            'name': 'admin',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('admin123'),
            'admin': True
        },
        {
            'id': 2,
            'name': 'john_doe',
            'email': 'john@example.com',
            'password_hash': generate_password_hash('password123'),
            'admin': False
        },
        {
            'id': 3,
            'name': 'jane_smith',
            'email': 'jane@example.com',
            'password_hash': generate_password_hash('mypassword'),
            'admin': False
        }
    ]
    
    # Dummy-Notizen erstellen
    dummy_notes = [
        {
            'id': 1,
            'title': 'Erste Notiz',
            'content': 'Das ist meine erste Notiz im System.',
            'owner_id': 2
        },
        {
            'id': 2,
            'title': 'Einkaufsliste',
            'content': 'Milch, Brot, Eier, Käse',
            'owner_id': 2
        },
        {
            'id': 3,
            'title': 'Meeting-Notizen',
            'content': 'Wichtige Punkte aus dem heutigen Meeting: 1. Projekt-Timeline, 2. Budget-Planung',
            'owner_id': 3
        },
        {
            'id': 4,
            'title': 'Ideen für das Wochenende',
            'content': 'Wandern, Kino, Freunde treffen',
            'owner_id': 3
        }
    ]
    
    users.extend(dummy_users)
    notes.extend(dummy_notes)
    user_id_counter = 4
    note_id_counter = 5

# User CRUD-Operationen
def create_user(name, email, password_hash, admin=False):
    """Erstellt einen neuen Benutzer"""
    global user_id_counter
    user = {
        'id': user_id_counter,
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'admin': admin
    }
    users.append(user)
    user_id_counter += 1
    return user

def get_user_by_id(user_id):
    """Findet einen Benutzer anhand der ID"""
    return next((user for user in users if user['id'] == user_id), None)

def get_user_by_email(email):
    """Findet einen Benutzer anhand der E-Mail"""
    return next((user for user in users if user['email'] == email), None)

def get_user_by_name(name):
    """Findet einen Benutzer anhand des Namens"""
    return next((user for user in users if user['name'] == name), None)

def delete_user(user_id):
    """Löscht einen Benutzer und alle seine Notizen"""
    global users, notes
    users = [user for user in users if user['id'] != user_id]
    notes = [note for note in notes if note['owner_id'] != user_id]
    return True

def get_all_users():
    """Gibt alle Benutzer zurück (ohne Passwort-Hashes)"""
    return [{k: v for k, v in user.items() if k != 'password_hash'} for user in users]

# Notes CRUD-Operationen
def create_note(title, content, owner_id):
    """Erstellt eine neue Notiz"""
    global note_id_counter
    note = {
        'id': note_id_counter,
        'title': title,
        'content': content,
        'owner_id': owner_id
    }
    notes.append(note)
    note_id_counter += 1
    return note

def get_note_by_id(note_id):
    """Findet eine Notiz anhand der ID"""
    return next((note for note in notes if note['id'] == note_id), None)

def get_notes_by_owner(owner_id):
    """Gibt alle Notizen eines Benutzers zurück"""
    return [note for note in notes if note['owner_id'] == owner_id]

def update_note(note_id, title=None, content=None):
    """Aktualisiert eine Notiz"""
    note = get_note_by_id(note_id)
    if note:
        if title is not None:
            note['title'] = title
        if content is not None:
            note['content'] = content
        return note
    return None

def delete_note(note_id):
    """Löscht eine Notiz"""
    global notes
    initial_length = len(notes)
    notes = [note for note in notes if note['id'] != note_id]
    return len(notes) < initial_length

def get_all_notes():
    """Gibt alle Notizen zurück"""
    return notes

# Initialisierung der Dummy-Daten beim Import
init_dummy_data()

