"""
Datenbankverbindung und Mock-Schicht für SQLite-Simulation
"""
from .models import db, User, Note
import uuid

# Mock-Schicht für SQLite-Simulation
class MockDatabase:
    """
    Mock-Schicht, die das Verhalten einer echten SQLite-Datenbank mit SQLAlchemy simuliert
    """
    def __init__(self):
        self.users = []
        self.notes = []
        self.user_id_counter = 1
        self.note_id_counter = 1
        self.sessions = {}  # Session-Token-Speicher
        self._init_dummy_data()
    
    def _init_dummy_data(self):
        """Initialisiert Dummy-Daten"""
        # Dummy-Users erstellen
        admin_user = User('admin', 'admin@example.com', 'admin123', admin=True)
        admin_user.id = self.user_id_counter
        self.user_id_counter += 1
        
        user1 = User('john_doe', 'john@example.com', 'password123')
        user1.id = self.user_id_counter
        self.user_id_counter += 1
        
        user2 = User('jane_smith', 'jane@example.com', 'mypassword')
        user2.id = self.user_id_counter
        self.user_id_counter += 1
        
        self.users.extend([admin_user, user1, user2])
        
        # Dummy-Notes erstellen
        note1 = Note('Erste Notiz', 'Das ist meine erste Notiz im System.', 2)
        note1.id = self.note_id_counter
        self.note_id_counter += 1
        
        note2 = Note('Einkaufsliste', 'Milch, Brot, Eier, Käse', 2)
        note2.id = self.note_id_counter
        self.note_id_counter += 1
        
        note3 = Note('Meeting-Notizen', 'Wichtige Punkte aus dem heutigen Meeting: 1. Projekt-Timeline, 2. Budget-Planung', 3)
        note3.id = self.note_id_counter
        self.note_id_counter += 1
        
        note4 = Note('Ideen für das Wochenende', 'Wandern, Kino, Freunde treffen', 3)
        note4.id = self.note_id_counter
        self.note_id_counter += 1
        
        self.notes.extend([note1, note2, note3, note4])
    
    # User CRUD-Operationen (simuliert SQLAlchemy Query-Interface)
    def create_user(self, name, email, password, admin=False):
        """Simuliert User.create() mit SQLAlchemy"""
        # Eindeutigkeit prüfen
        if self.get_user_by_email(email) or self.get_user_by_name(name):
            return None
        
        user = User(name, email, password, admin)
        user.id = self.user_id_counter
        self.user_id_counter += 1
        self.users.append(user)
        return user
    
    def get_user_by_id(self, user_id):
        """Simuliert User.query.get(id)"""
        return next((user for user in self.users if user.id == user_id), None)
    
    def get_user_by_email(self, email):
        """Simuliert User.query.filter_by(email=email).first()"""
        return next((user for user in self.users if user.email == email), None)
    
    def get_user_by_name(self, name):
        """Simuliert User.query.filter_by(name=name).first()"""
        return next((user for user in self.users if user.name == name), None)
    
    def get_all_users(self):
        """Simuliert User.query.all()"""
        return self.users.copy()
    
    def delete_user(self, user_id):
        """Simuliert User.delete() mit Cascade-Delete für Notes"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Cascade-Delete: Alle Notes des Users löschen
        self.notes = [note for note in self.notes if note.owner_id != user_id]
        
        # User löschen
        self.users = [u for u in self.users if u.id != user_id]
        return True
    
    # Note CRUD-Operationen
    def create_note(self, title, content, owner_id):
        """Simuliert Note.create() mit SQLAlchemy"""
        # Prüfen ob Owner existiert (Foreign Key Constraint)
        if not self.get_user_by_id(owner_id):
            return None
        
        note = Note(title, content, owner_id)
        note.id = self.note_id_counter
        self.note_id_counter += 1
        self.notes.append(note)
        return note
    
    def get_note_by_id(self, note_id):
        """Simuliert Note.query.get(id)"""
        return next((note for note in self.notes if note.id == note_id), None)
    
    def get_notes_by_owner(self, owner_id):
        """Simuliert Note.query.filter_by(owner_id=owner_id).all()"""
        return [note for note in self.notes if note.owner_id == owner_id]
    
    def update_note(self, note_id, title=None, content=None):
        """Simuliert Note.update() mit SQLAlchemy"""
        note = self.get_note_by_id(note_id)
        if not note:
            return None
        
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        
        # Updated timestamp aktualisieren
        from datetime import datetime
        note.updated_at = datetime.utcnow()
        
        return note
    
    def delete_note(self, note_id):
        """Simuliert Note.delete() mit SQLAlchemy"""
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        
        self.notes = [n for n in self.notes if n.id != note_id]
        return True
    
    # Session-Management
    def create_session(self, user_id):
        """Erstellt eine neue Session"""
        token = str(uuid.uuid4())
        self.sessions[token] = {
            'user_id': user_id,
            'created_at': __import__('datetime').datetime.utcnow()
        }
        return token
    
    def get_session(self, token):
        """Ruft Session-Informationen ab"""
        return self.sessions.get(token)
    
    def invalidate_session(self, token):
        """Invalidiert eine Session"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

# Globale Mock-Datenbankinstanz
mock_db = MockDatabase()

def init_db(app):
    """Initialisiert die Datenbank mit der Flask-App"""
    db.init_app(app)
    print("🗄️ SQLAlchemy-Mock-Datenbank initialisiert")
    print("📊 Simuliert echte SQLite-Datenbankoperationen")
    return db

