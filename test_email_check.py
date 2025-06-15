"""
Tests für die E-Mail-Existenz-Prüfung Route
"""
import pytest
import json
from unittest.mock import patch
from main import create_app
from myapp.crud import UserService
from myapp.models import User

class TestEmailCheckRoute:
    """Test-Klasse für /check-email Route"""
    
    @pytest.fixture
    def app(self):
        """Flask-App für Tests erstellen"""
        return create_app()
    
    @pytest.fixture
    def client(self, app):
        """Test-Client erstellen"""
        return app.test_client()
    
    def test_check_email_exists_true(self, client):
        """Test: E-Mail existiert - sollte true zurückgeben"""
        mock_user = User(name="Test User", email="test@example.com", password="testpass", admin=False)
        mock_user.id = 1  # ID nach der Erstellung setzen
        
        with patch.object(UserService, 'get_user_by_email', return_value=mock_user):
            response = client.get('/check-email?email=test@example.com')
            
            assert response.status_code == 200
            assert response.get_json() == True
    
    def test_check_email_exists_false(self, client):
        """Test: E-Mail existiert nicht - sollte false zurückgeben"""
        with patch.object(UserService, 'get_user_by_email', return_value=None):
            response = client.get('/check-email?email=nonexistent@example.com')
            
            assert response.status_code == 200
            assert response.get_json() == False
    
    def test_check_email_case_insensitive(self, client):
        """Test: E-Mail-Prüfung ist case-insensitive"""
        mock_user = User(name="Test User", email="test@example.com", password="testpass", admin=False)
        mock_user.id = 1  # ID nach der Erstellung setzen
        
        with patch.object(UserService, 'get_user_by_email', return_value=mock_user):
            # Test mit Großbuchstaben
            response = client.get('/check-email?email=TEST@EXAMPLE.COM')
            assert response.status_code == 200
            assert response.get_json() == True
            
            # Test mit gemischter Schreibweise
            response = client.get('/check-email?email=Test@Example.Com')
            assert response.status_code == 200
            assert response.get_json() == True
    
    def test_check_email_with_whitespace(self, client):
        """Test: E-Mail mit Leerzeichen wird korrekt behandelt"""
        mock_user = User(name="Test User", email="test@example.com", password="testpass", admin=False)
        mock_user.id = 1  # ID nach der Erstellung setzen
        
        with patch.object(UserService, 'get_user_by_email', return_value=mock_user):
            response = client.get('/check-email?email= test@example.com ')
            
            assert response.status_code == 200
            assert response.get_json() == True
    
    def test_check_email_invalid_format(self, client):
        """Test: Ungültiges E-Mail-Format - sollte false zurückgeben"""
        response = client.get('/check-email?email=invalid-email')
        
        assert response.status_code == 200
        assert response.get_json() == False
    
    def test_check_email_no_parameter(self, client):
        """Test: Kein E-Mail-Parameter - sollte false zurückgeben"""
        response = client.get('/check-email')
        
        assert response.status_code == 200
        assert response.get_json() == False
    
    def test_check_email_empty_parameter(self, client):
        """Test: Leerer E-Mail-Parameter - sollte false zurückgeben"""
        response = client.get('/check-email?email=')
        
        assert response.status_code == 200
        assert response.get_json() == False
    
    def test_check_email_exception_handling(self, client):
        """Test: Exception-Behandlung - sollte false zurückgeben"""
        with patch.object(UserService, 'get_user_by_email', side_effect=Exception("Database error")):
            response = client.get('/check-email?email=test@example.com')
            
            assert response.status_code == 200
            assert response.get_json() == False
    
    def test_check_email_with_existing_dummy_users(self, client):
        """Test: Mit den vorhandenen Dummy-Benutzern"""
        # Test mit existierenden Dummy-Benutzern (ohne Mocking)
        response = client.get('/check-email?email=admin@example.com')
        assert response.status_code == 200
        assert response.get_json() == True
        
        response = client.get('/check-email?email=john@example.com')
        assert response.status_code == 200
        assert response.get_json() == True
        
        response = client.get('/check-email?email=jane@example.com')
        assert response.status_code == 200
        assert response.get_json() == True
        
        # Test mit nicht existierender E-Mail
        response = client.get('/check-email?email=notfound@example.com')
        assert response.status_code == 200
        assert response.get_json() == False
