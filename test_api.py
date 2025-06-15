"""
Test-Skript für die Flask-API
Dieses Skript demonstriert die Verwendung aller API-Endpunkte
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_api():
    """Testet alle API-Endpunkte systematisch"""
    print("🧪 API-Tests werden gestartet...\n")
    
    # 1. API-Info abrufen
    print("1. API-Informationen abrufen:")
    response = requests.get(f'{BASE_URL}/')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # 2. Neuen Benutzer registrieren
    print("2. Neuen Benutzer registrieren:")
    new_user_data = {
        'name': 'test_user',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    response = requests.post(f'{BASE_URL}/register', json=new_user_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # 3. Mit Admin anmelden
    print("3. Admin-Login:")
    admin_login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    response = requests.post(f'{BASE_URL}/login', json=admin_login_data)
    admin_token = None
    if response.status_code == 200:
        admin_token = response.json()['token']
        print(f"   Status: {response.status_code}")
        print(f"   Admin-Token erhalten: {admin_token[:20]}...\n")
    else:
        print(f"   Fehler beim Admin-Login: {response.json()}\n")
    
    # 4. Mit normalem Benutzer anmelden
    print("4. Benutzer-Login:")
    user_login_data = {
        'email': 'john@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/login', json=user_login_data)
    user_token = None
    if response.status_code == 200:
        user_token = response.json()['token']
        print(f"   Status: {response.status_code}")
        print(f"   User-Token erhalten: {user_token[:20]}...\n")
    else:
        print(f"   Fehler beim User-Login: {response.json()}\n")
    
    if not user_token:
        print("❌ Kann ohne User-Token nicht fortfahren")
        return
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # 5. Aktuelle Benutzerinformationen abrufen
    print("5. Aktuelle Benutzerinformationen:")
    response = requests.get(f'{BASE_URL}/me', headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # 6. Eigene Notizen abrufen
    print("6. Eigene Notizen abrufen:")
    response = requests.get(f'{BASE_URL}/notes', headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # 7. Neue Notiz erstellen
    print("7. Neue Notiz erstellen:")
    new_note_data = {
        'title': 'Test-Notiz',
        'content': 'Das ist eine Test-Notiz, die über die API erstellt wurde.'
    }
    response = requests.post(f'{BASE_URL}/notes', json=new_note_data, headers=headers)
    new_note_id = None
    if response.status_code == 201:
        new_note_id = response.json()['note']['id']
        print(f"   Status: {response.status_code}")
        print(f"   Neue Notiz erstellt mit ID: {new_note_id}\n")
    else:
        print(f"   Fehler beim Erstellen der Notiz: {response.json()}\n")
    
    # 8. Einzelne Notiz abrufen
    if new_note_id:
        print("8. Einzelne Notiz abrufen:")
        response = requests.get(f'{BASE_URL}/notes/{new_note_id}', headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # 9. Notiz bearbeiten
        print("9. Notiz bearbeiten:")
        update_data = {
            'title': 'Aktualisierte Test-Notiz',
            'content': 'Der Inhalt wurde über die API aktualisiert.'
        }
        response = requests.put(f'{BASE_URL}/notes/{new_note_id}', json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
    
    # 10. Admin-Funktionen testen (falls Admin-Token verfügbar)
    if admin_token:
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        print("10. Alle Benutzer auflisten (Admin):")
        response = requests.get(f'{BASE_URL}/users', headers=admin_headers)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}\n")
    
    # 11. Notiz löschen
    if new_note_id:
        print("11. Notiz löschen:")
        response = requests.delete(f'{BASE_URL}/notes/{new_note_id}', headers=headers)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}\n")
    
    # 12. Abmelden
    print("12. Abmelden:")
    response = requests.post(f'{BASE_URL}/logout', headers=headers)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.json()}\n")
    
    print("✅ API-Tests abgeschlossen!")

if __name__ == '__main__':
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Fehler: Kann keine Verbindung zum Server herstellen.")
        print("   Stellen Sie sicher, dass der Flask-Server läuft (python app.py)")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")

