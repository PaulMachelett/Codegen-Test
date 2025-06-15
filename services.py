"""
Service-Schicht für Datenbankoperationen mit SQLAlchemy-ähnlicher Syntax
"""
from database import mock_db, User, Note
from werkzeug.security import check_password_hash

class UserService:
    """Service-Klasse für User-Operationen"""
    
    @staticmethod
    def create_user(name, email, password, admin=False):
        """
        Erstellt einen neuen Benutzer
        Simuliert: db.session.add(user) + db.session.commit()
        """
        try:
            user = mock_db.create_user(name, email, password, admin)
            if user:
                print(f"[DB] INSERT INTO users (name, email, password_hash, admin) VALUES ('{name}', '{email}', '[HASH]', {admin})")
                return user
            return None
        except Exception as e:
            print(f"[DB ERROR] Failed to create user: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Findet User by ID
        Simuliert: User.query.get(user_id)
        """
        print(f"[DB] SELECT * FROM users WHERE id = {user_id}")
        return mock_db.get_user_by_id(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """
        Findet User by Email
        Simuliert: User.query.filter_by(email=email).first()
        """
        print(f"[DB] SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        return mock_db.get_user_by_email(email)
    
    @staticmethod
    def get_user_by_name(name):
        """
        Findet User by Name
        Simuliert: User.query.filter_by(name=name).first()
        """
        print(f"[DB] SELECT * FROM users WHERE name = '{name}' LIMIT 1")
        return mock_db.get_user_by_name(name)
    
    @staticmethod
    def get_all_users():
        """
        Holt alle User
        Simuliert: User.query.all()
        """
        print("[DB] SELECT * FROM users")
        return mock_db.get_all_users()
    
    @staticmethod
    def delete_user(user_id):
        """
        Löscht User (mit CASCADE DELETE für Notes)
        Simuliert: db.session.delete(user) + db.session.commit()
        """
        print(f"[DB] DELETE FROM notes WHERE owner_id = {user_id}")
        print(f"[DB] DELETE FROM users WHERE id = {user_id}")
        return mock_db.delete_user(user_id)
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authentifiziert User
        Simuliert: User.query.filter_by(email=email).first() + password check
        """
        print(f"[DB] SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        user = mock_db.get_user_by_email(email)
        if user and user.check_password(password):
            print("[AUTH] Password verification successful")
            return user
        print("[AUTH] Authentication failed")
        return None

class NoteService:
    """Service-Klasse für Note-Operationen"""
    
    @staticmethod
    def create_note(title, content, owner_id):
        """
        Erstellt neue Note
        Simuliert: db.session.add(note) + db.session.commit()
        """
        try:
            note = mock_db.create_note(title, content, owner_id)
            if note:
                print(f"[DB] INSERT INTO notes (title, content, owner_id) VALUES ('{title}', '{content[:20]}...', {owner_id})")
                return note
            return None
        except Exception as e:
            print(f"[DB ERROR] Failed to create note: {e}")
            return None
    
    @staticmethod
    def get_note_by_id(note_id):
        """
        Findet Note by ID
        Simuliert: Note.query.get(note_id)
        """
        print(f"[DB] SELECT * FROM notes WHERE id = {note_id}")
        return mock_db.get_note_by_id(note_id)
    
    @staticmethod
    def get_notes_by_owner(owner_id):
        """
        Holt alle Notes eines Users
        Simuliert: Note.query.filter_by(owner_id=owner_id).all()
        """
        print(f"[DB] SELECT * FROM notes WHERE owner_id = {owner_id}")
        return mock_db.get_notes_by_owner(owner_id)
    
    @staticmethod
    def get_all_notes():
        """
        Holt alle Notes
        Simuliert: Note.query.all()
        """
        print("[DB] SELECT * FROM notes")
        return mock_db.get_all_notes()
    
    @staticmethod
    def update_note(note_id, title=None, content=None):
        """
        Aktualisiert Note
        Simuliert: note.title = new_title + db.session.commit()
        """
        updates = []
        if title is not None:
            updates.append(f"title = '{title}'")
        if content is not None:
            updates.append(f"content = '{content[:20]}...'")
        
        if updates:
            print(f"[DB] UPDATE notes SET {', '.join(updates)} WHERE id = {note_id}")
        
        return mock_db.update_note(note_id, title, content)
    
    @staticmethod
    def delete_note(note_id):
        """
        Löscht Note
        Simuliert: db.session.delete(note) + db.session.commit()
        """
        print(f"[DB] DELETE FROM notes WHERE id = {note_id}")
        return mock_db.delete_note(note_id)

class SessionService:
    """Service-Klasse für Session-Management"""
    
    @staticmethod
    def create_session(user_id):
        """
        Erstellt Session
        Simuliert: INSERT INTO sessions (token, user_id, created_at)
        """
        token = mock_db.create_session(user_id)
        print(f"[DB] INSERT INTO sessions (token, user_id, created_at) VALUES ('{token[:8]}...', {user_id}, NOW())")
        return token
    
    @staticmethod
    def get_user_from_session(token):
        """
        Holt User aus Session
        Simuliert: SELECT users.* FROM users JOIN sessions ON users.id = sessions.user_id WHERE sessions.token = ?
        """
        print(f"[DB] SELECT users.* FROM users JOIN sessions ON users.id = sessions.user_id WHERE sessions.token = '{token[:8]}...'")
        return mock_db.get_user_from_session(token)
    
    @staticmethod
    def invalidate_session(token):
        """
        Invalidiert Session
        Simuliert: DELETE FROM sessions WHERE token = ?
        """
        print(f"[DB] DELETE FROM sessions WHERE token = '{token[:8]}...'")
        return mock_db.invalidate_session(token)

