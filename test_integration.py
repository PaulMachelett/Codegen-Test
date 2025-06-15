#!/usr/bin/env python3
"""
Integrationstests für das Flask-Backend mit pytest
Testet alle REST-Endpunkte über Test-Client mit gemockter Datenbank
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from main import create_app
from myapp.models import User, Note
from myapp.crud import UserService, NoteService, SessionService


class TestFlaskBackendIntegration:
    """Integrationstests für Flask-Backend REST-API"""
    
    @pytest.fixture
    def app(self):
        """Flask-App für Tests erstellen"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def client(self, app):
        """Test-Client erstellen"""
        return app.test_client()
    
    @pytest.fixture
    def mock_user(self):
        """Mock-User für Tests"""
        user = MagicMock(spec=User)
        user.id = 1
        user.name = 'testuser'
        user.email = 'test@example.com'
        user.admin = False
        user.to_dict.return_value = {
            'id': 1,
            'name': 'testuser',
            'email': 'test@example.com',
            'admin': False,
            'created_at': '2024-01-01T00:00:00'
        }
        user.check_password.return_value = True
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        """Mock-Admin-User für Tests"""
        admin = MagicMock(spec=User)
        admin.id = 2
        admin.name = 'admin'
        admin.email = 'admin@example.com'
        admin.admin = True
        admin.to_dict.return_value = {
            'id': 2,
            'name': 'admin',
            'email': 'admin@example.com',
            'admin': True,
            'created_at': '2024-01-01T00:00:00'
        }
        admin.check_password.return_value = True
        return admin
    
    @pytest.fixture
    def mock_note(self):
        """Mock-Note für Tests"""
        note = MagicMock(spec=Note)
        note.id = 1
        note.title = 'Test Note'
        note.content = 'Test content'
        note.owner_id = 1
        note.to_dict.return_value = {
            'id': 1,
            'title': 'Test Note',
            'content': 'Test content',
            'owner_id': 1,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        return note
    
    @pytest.fixture
    def auth_headers(self):
        """Authorization Headers für authentifizierte Requests"""
        return {'Authorization': 'Bearer test-token-123'}

    # ==================== REGISTRIERUNG TESTS ====================
    
    def test_register_success(self, client, mock_user):
        """Test: Erfolgreiche Benutzerregistrierung"""
        with patch.object(UserService, 'get_user_by_email', return_value=None), \
             patch.object(UserService, 'get_user_by_name', return_value=None), \
             patch.object(UserService, 'create_user', return_value=mock_user):
            
            response = client.post('/register', 
                json={
                    'name': 'testuser',
                    'email': 'test@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Benutzer erfolgreich registriert'
            assert 'user' in data
            assert data['user']['name'] == 'testuser'
            assert data['user']['email'] == 'test@example.com'
    
    def test_register_missing_fields(self, client):
        """Test: Registrierung mit fehlenden Feldern"""
        response = client.post('/register', 
            json={
                'name': 'testuser',
                'email': 'test@example.com'
                # password fehlt
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'password' in data['error']
    
    def test_register_invalid_email(self, client):
        """Test: Registrierung mit ungültiger E-Mail"""
        response = client.post('/register', 
            json={
                'name': 'testuser',
                'email': 'invalid-email',
                'password': 'password123'
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Ungültiges E-Mail-Format'
    
    def test_register_weak_password(self, client):
        """Test: Registrierung mit schwachem Passwort"""
        response = client.post('/register', 
            json={
                'name': 'testuser',
                'email': 'test@example.com',
                'password': '123'  # Zu kurz
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Passwort muss mindestens 6 Zeichen lang sein'
    
    def test_register_duplicate_email(self, client, mock_user):
        """Test: Registrierung mit bereits existierender E-Mail"""
        with patch.object(UserService, 'get_user_by_email', return_value=mock_user):
            response = client.post('/register', 
                json={
                    'name': 'testuser2',
                    'email': 'test@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert data['error'] == 'E-Mail bereits registriert'
    
    def test_register_duplicate_username(self, client, mock_user):
        """Test: Registrierung mit bereits existierendem Benutzernamen"""
        with patch.object(UserService, 'get_user_by_email', return_value=None), \
             patch.object(UserService, 'get_user_by_name', return_value=mock_user):
            
            response = client.post('/register', 
                json={
                    'name': 'testuser',
                    'email': 'test2@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert data['error'] == 'Benutzername bereits vergeben'
    
    def test_register_no_json(self, client):
        """Test: Registrierung ohne JSON-Daten"""
        response = client.post('/register')
        
        assert response.status_code == 400
        # Prüfe ob Response JSON ist
        if response.content_type and 'application/json' in response.content_type:
            data = json.loads(response.data)
            assert data['error'] == 'JSON-Daten erforderlich'
        else:
            # Falls HTML-Response, prüfe Status Code
            assert response.status_code == 400

    # ==================== LOGIN TESTS ====================
    
    def test_login_success(self, client, mock_user):
        """Test: Erfolgreicher Login"""
        with patch.object(UserService, 'authenticate_user', return_value=mock_user), \
             patch.object(SessionService, 'create_session', return_value='test-token-123'):
            
            response = client.post('/login', 
                json={
                    'email': 'test@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Erfolgreich angemeldet'
            assert data['token'] == 'test-token-123'
            assert 'user' in data
            assert data['user']['name'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """Test: Login mit ungültigen Anmeldedaten"""
        with patch.object(UserService, 'authenticate_user', return_value=None):
            response = client.post('/login', 
                json={
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['error'] == 'Ungültige Anmeldedaten'
    
    def test_login_missing_fields(self, client):
        """Test: Login mit fehlenden Feldern"""
        response = client.post('/login', 
            json={
                'email': 'test@example.com'
                # password fehlt
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'E-Mail und Passwort erforderlich'
    
    def test_login_no_json(self, client):
        """Test: Login ohne JSON-Daten"""
        response = client.post('/login')
        
        assert response.status_code == 400
        # Prüfe ob Response JSON ist
        if response.content_type and 'application/json' in response.content_type:
            data = json.loads(response.data)
            assert data['error'] == 'JSON-Daten erforderlich'
        else:
            # Falls HTML-Response, prüfe Status Code
            assert response.status_code == 400

    # ==================== LOGOUT TESTS ====================
    
    def test_logout_success(self, client, auth_headers):
        """Test: Erfolgreicher Logout"""
        with patch.object(SessionService, 'invalidate_session', return_value=True):
            response = client.post('/logout', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Erfolgreich abgemeldet'
    
    def test_logout_invalid_token(self, client, auth_headers):
        """Test: Logout mit ungültigem Token"""
        with patch.object(SessionService, 'invalidate_session', return_value=False):
            response = client.post('/logout', headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Fehler beim Abmelden'

    # ==================== NOTIZEN ERSTELLEN TESTS ====================
    
    def test_create_note_success(self, client, auth_headers, mock_user, mock_note):
        """Test: Erfolgreiche Notiz-Erstellung"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'create_note', return_value=mock_note):
            
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': 'Test Note',
                    'content': 'Test content'
                })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Notiz erfolgreich erstellt'
            assert 'note' in data
            assert data['note']['title'] == 'Test Note'
            assert data['note']['content'] == 'Test content'
    
    def test_create_note_missing_auth(self, client):
        """Test: Notiz-Erstellung ohne Authentifizierung"""
        response = client.post('/notes', 
            json={
                'title': 'Test Note',
                'content': 'Test content'
            })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authorization header fehlt'
    
    def test_create_note_invalid_token(self, client, auth_headers):
        """Test: Notiz-Erstellung mit ungültigem Token"""
        with patch.object(SessionService, 'get_user_from_session', return_value=None):
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': 'Test Note',
                    'content': 'Test content'
                })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['error'] == 'Ungültiges oder abgelaufenes Token'
    
    def test_create_note_missing_title(self, client, auth_headers, mock_user):
        """Test: Notiz-Erstellung ohne Titel"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'content': 'Test content'
                    # title fehlt
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Titel ist erforderlich'
    
    def test_create_note_missing_content(self, client, auth_headers, mock_user):
        """Test: Notiz-Erstellung ohne Inhalt"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': 'Test Note'
                    # content fehlt
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Inhalt ist erforderlich'
    
    def test_create_note_empty_title(self, client, auth_headers, mock_user):
        """Test: Notiz-Erstellung mit leerem Titel"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': '',
                    'content': 'Test content'
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Titel ist erforderlich'
    
    def test_create_note_no_json(self, client, auth_headers, mock_user):
        """Test: Notiz-Erstellung ohne JSON-Daten"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.post('/notes', headers=auth_headers)
            
            assert response.status_code == 400
            # Prüfe ob Response JSON ist
            if response.content_type and 'application/json' in response.content_type:
                data = json.loads(response.data)
                assert data['error'] == 'JSON-Daten erforderlich'
            else:
                # Falls HTML-Response, prüfe Status Code
                assert response.status_code == 400

    # ==================== NOTIZEN ABRUFEN TESTS ====================
    
    def test_get_notes_success(self, client, auth_headers, mock_user, mock_note):
        """Test: Erfolgreicher Abruf aller eigenen Notizen"""
        notes = [mock_note]
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_notes_by_owner', return_value=notes):
            
            response = client.get('/notes', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'notes' in data
            assert len(data['notes']) == 1
            assert data['notes'][0]['title'] == 'Test Note'
            assert data['notes'][0]['content'] == 'Test content'
    
    def test_get_notes_empty(self, client, auth_headers, mock_user):
        """Test: Abruf von Notizen wenn keine vorhanden"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_notes_by_owner', return_value=[]):
            
            response = client.get('/notes', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'notes' in data
            assert len(data['notes']) == 0
    
    def test_get_notes_missing_auth(self, client):
        """Test: Notizen-Abruf ohne Authentifizierung"""
        response = client.get('/notes')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authorization header fehlt'
    
    def test_get_notes_invalid_token(self, client, auth_headers):
        """Test: Notizen-Abruf mit ungültigem Token"""
        with patch.object(SessionService, 'get_user_from_session', return_value=None):
            response = client.get('/notes', headers=auth_headers)
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['error'] == 'Ungültiges oder abgelaufenes Token'

    # ==================== EINZELNE NOTIZ ABRUFEN TESTS ====================
    
    def test_get_single_note_success(self, client, auth_headers, mock_user, mock_note):
        """Test: Erfolgreicher Abruf einer einzelnen Notiz"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note):
            
            response = client.get('/notes/1', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'note' in data
            assert data['note']['title'] == 'Test Note'
            assert data['note']['content'] == 'Test content'
    
    def test_get_single_note_not_found(self, client, auth_headers, mock_user):
        """Test: Abruf einer nicht existierenden Notiz"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=None):
            
            response = client.get('/notes/999', headers=auth_headers)
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['error'] == 'Notiz nicht gefunden'
    
    def test_get_single_note_access_denied(self, client, auth_headers, mock_user, mock_note):
        """Test: Abruf einer fremden Notiz (Zugriff verweigert)"""
        mock_note.owner_id = 999  # Andere User-ID
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note):
            
            response = client.get('/notes/1', headers=auth_headers)
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['error'] == 'Zugriff verweigert'

    # ==================== NOTIZ BEARBEITEN TESTS ====================
    
    def test_update_note_success(self, client, auth_headers, mock_user, mock_note):
        """Test: Erfolgreiche Notiz-Bearbeitung"""
        updated_note = MagicMock(spec=Note)
        updated_note.to_dict.return_value = {
            'id': 1,
            'title': 'Updated Note',
            'content': 'Updated content',
            'owner_id': 1,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T01:00:00'
        }
        
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note), \
             patch.object(NoteService, 'update_note', return_value=updated_note):
            
            response = client.put('/notes/1', 
                headers=auth_headers,
                json={
                    'title': 'Updated Note',
                    'content': 'Updated content'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Notiz erfolgreich aktualisiert'
            assert data['note']['title'] == 'Updated Note'
            assert data['note']['content'] == 'Updated content'
    
    def test_update_note_not_found(self, client, auth_headers, mock_user):
        """Test: Bearbeitung einer nicht existierenden Notiz"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=None):
            
            response = client.put('/notes/999', 
                headers=auth_headers,
                json={
                    'title': 'Updated Note',
                    'content': 'Updated content'
                })
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['error'] == 'Notiz nicht gefunden'

    # ==================== NOTIZ LÖSCHEN TESTS ====================
    
    def test_delete_note_success(self, client, auth_headers, mock_user, mock_note):
        """Test: Erfolgreiche Notiz-Löschung"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note), \
             patch.object(NoteService, 'delete_note', return_value=True):
            
            response = client.delete('/notes/1', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Notiz erfolgreich gelöscht'
    
    def test_delete_note_not_found(self, client, auth_headers, mock_user):
        """Test: Löschung einer nicht existierenden Notiz"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=None):
            
            response = client.delete('/notes/999', headers=auth_headers)
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['error'] == 'Notiz nicht gefunden'

    # ==================== BENUTZER-INFO TESTS ====================
    
    def test_get_current_user_info_success(self, client, auth_headers, mock_user):
        """Test: Erfolgreicher Abruf der eigenen Benutzerinformationen"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.get('/me', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'user' in data
            assert data['user']['name'] == 'testuser'
            assert data['user']['email'] == 'test@example.com'
    
    def test_get_current_user_info_missing_auth(self, client):
        """Test: Benutzer-Info-Abruf ohne Authentifizierung"""
        response = client.get('/me')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authorization header fehlt'

    # ==================== ADMIN TESTS ====================
    
    def test_get_all_users_admin_success(self, client, auth_headers, mock_admin_user, mock_user):
        """Test: Admin kann alle Benutzer abrufen"""
        users = [mock_admin_user, mock_user]
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_admin_user), \
             patch.object(UserService, 'get_all_users', return_value=users):
            
            response = client.get('/users', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'users' in data
            assert len(data['users']) == 2
    
    def test_get_all_users_non_admin_forbidden(self, client, auth_headers, mock_user):
        """Test: Normaler Benutzer kann nicht alle Benutzer abrufen"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
            response = client.get('/users', headers=auth_headers)
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['error'] == 'Admin-Rechte erforderlich'
    
    def test_delete_user_admin_success(self, client, auth_headers, mock_admin_user, mock_user):
        """Test: Admin kann Benutzer löschen"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_admin_user), \
             patch.object(UserService, 'get_user_by_id', return_value=mock_user), \
             patch.object(UserService, 'delete_user', return_value=True):
            
            response = client.delete('/users/1', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Benutzer erfolgreich gelöscht'
    
    def test_delete_user_admin_cannot_delete_self(self, client, auth_headers, mock_admin_user):
        """Test: Admin kann sich nicht selbst löschen"""
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_admin_user), \
             patch.object(UserService, 'get_user_by_id', return_value=mock_admin_user):
            
            response = client.delete('/users/2', headers=auth_headers)  # Admin-ID = 2
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Admin kann sich nicht selbst löschen'

    # ==================== BEARER TOKEN TESTS ====================
    
    def test_bearer_token_format(self, client, mock_user, mock_note):
        """Test: Bearer Token Format wird korrekt verarbeitet"""
        bearer_headers = {'Authorization': 'Bearer test-token-123'}
        
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_notes_by_owner', return_value=[mock_note]):
            
            response = client.get('/notes', headers=bearer_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'notes' in data

    # ==================== ERROR HANDLING TESTS ====================
    
    def test_404_endpoint_not_found(self, client):
        """Test: 404 für nicht existierende Endpunkte"""
        response = client.get('/nonexistent')
        
        assert response.status_code == 404
        # Prüfe ob Response JSON ist
        if response.content_type and 'application/json' in response.content_type:
            data = json.loads(response.data)
            assert data['error'] == 'Endpunkt nicht gefunden'
        else:
            # Falls HTML-Response, prüfe Status Code
            assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
