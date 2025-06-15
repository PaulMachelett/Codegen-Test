"""
SQLAlchemy Datenbankmodelle
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# SQLAlchemy-Instanz wird in db.py initialisiert und hier importiert
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
    
    # Relationship zu Notes - mise à jour pour utiliser user_id
    notes = relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
    # Changement: owner_id renommé en user_id pour une meilleure cohérence
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content, user_id):
        # Constructeur mis à jour pour utiliser user_id au lieu d'owner_id
        self.title = title
        self.content = content
        self.user_id = user_id
    
    def to_dict(self):
        """Konvertiert Note zu Dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            # Retour du nouveau nom d'attribut user_id
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Note {self.title}>'
