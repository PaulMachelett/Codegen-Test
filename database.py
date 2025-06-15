"""
SQLAlchemy Datenbankmodelle und Mock-Schicht für SQLite-Simulation
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# SQLAlchemy-Instanz
db = SQLAlchemy()

class User(db.Model):
    """SQLAlchemy User-Modell"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship zu Notes
    notes = relationship('Note', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, email, password, admin=False):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = admin
    
    def check_password(self, password):
        """Überprüft das Passwort"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_password=False):
        """Konvertiert User zu Dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'admin': self.admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data
    
    def __repr__(self):
        return f'<User {self.name}>'

class Note(db.Model):
    """SQLAlchemy Note-Modell"""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content, owner_id):
        self.title = title
        self.content = content
        self.owner_id = owner_id
    
    def to_dict(self):
        """Konvertiert Note zu Dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Note {self.title}>'

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
        """Simuliert db.session.delete(user) + CASCADE DELETE"""
        user = self.get_user_by_id(user_id)
        if user:
            # Cascade delete - alle Notizen des Users löschen
            self.notes = [note for note in self.notes if note.owner_id != user_id]
            self.users = [u for u in self.users if u.id != user_id]
            return True
        return False
    
    # Note CRUD-Operationen (simuliert SQLAlchemy Query-Interface)
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
    
    def get_all_notes(self):
        """Simuliert Note.query.all()"""
        return self.notes.copy()
    
    def update_note(self, note_id, title=None, content=None):
        """Simuliert SQLAlchemy Update-Operation"""
        note = self.get_note_by_id(note_id)
        if note:
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            note.updated_at = datetime.utcnow()
            return note
        return None
    
    def delete_note(self, note_id):
        """Simuliert db.session.delete(note)"""
        initial_length = len(self.notes)
        self.notes = [note for note in self.notes if note.id != note_id]
        return len(self.notes) < initial_length
    
    # Session-Management (simuliert echte Session-Tabelle)
    def create_session(self, user_id):
        """Erstellt Session-Token"""
        token = str(uuid.uuid4())
        self.sessions[token] = {
            'user_id': user_id,
            'created_at': datetime.utcnow()
        }
        return token
    
    def get_user_from_session(self, token):
        """Holt User aus Session"""
        if token in self.sessions:
            user_id = self.sessions[token]['user_id']
            return self.get_user_by_id(user_id)
        return None
    
    def invalidate_session(self, token):
        """Invalidiert Session"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

# Globale Mock-Database-Instanz
mock_db = MockDatabase()
