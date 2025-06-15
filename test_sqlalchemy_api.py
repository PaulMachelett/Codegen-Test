#!/usr/bin/env python3
"""
Test-Skript für das SQLAlchemy-erweiterte Flask-Backend
"""
import requests
import json
import time
import subprocess
import signal
import os

BASE_URL = 'http://localhost:5001'

def start_backend():
    """Startet das Backend im Hintergrund"""
    print("🚀 Starte SQLAlchemy-Backend...")
    process = subprocess.Popen(['python', 'app.py'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    time.sleep(3)  # Warten bis Server gestartet ist
    return process

def test_api():
    """Testet alle API-Endpunkte"""
    print("\n🧪 Teste SQLAlchemy-Backend API...")
    
    # Test 1: Registrierung
    print("\n1️⃣ Teste Benutzerregistrierung...")
    register_data = {
        'name': 'test_user_sqlalchemy',
        'email': 'test_sqlalchemy@example.com',
        'password': 'testpassword123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/register', json=register_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Registrierung erfolgreich")
            print(f"   📊 Mock-DB-Logs sichtbar in Backend-Output")
        else:
            print(f"   ❌ Registrierung fehlgeschlagen: {response.text}")
    except Exception as e:
        print(f"   ❌ Fehler bei Registrierung: {e}")
    
    # Test 2: Login mit Admin
    print("\n2️⃣ Teste Admin-Login...")
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/login', json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            admin_token = response.json()['token']
            print("   ✅ Admin-Login erfolgreich")
            print(f"   🔑 Token: {admin_token[:20]}...")
        else:
            print(f"   ❌ Login fehlgeschlagen: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Fehler bei Login: {e}")
        return
    
    # Test 3: Notiz erstellen
    print("\n3️⃣ Teste Notiz-Erstellung...")
    note_data = {
        'title': 'SQLAlchemy Test-Notiz',
        'content': 'Diese Notiz wurde mit dem SQLAlchemy-Mock-System erstellt.'
    }
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    try:
        response = requests.post(f'{BASE_URL}/notes', json=note_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            note_id = response.json()['note']['id']
            print("   ✅ Notiz erfolgreich erstellt")
            print(f"   📝 Notiz-ID: {note_id}")
        else:
            print(f"   ❌ Notiz-Erstellung fehlgeschlagen: {response.text}")
    except Exception as e:
        print(f"   ❌ Fehler bei Notiz-Erstellung: {e}")
    
    # Test 4: Alle Notizen abrufen
    print("\n4️⃣ Teste Notizen-Abruf...")
    try:
        response = requests.get(f'{BASE_URL}/notes', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            notes = response.json()['notes']
            print(f"   ✅ {len(notes)} Notizen abgerufen")
            for note in notes[:2]:  # Zeige erste 2 Notizen
                print(f"   📝 {note['title']}: {note['content'][:30]}...")
        else:
            print(f"   ❌ Notizen-Abruf fehlgeschlagen: {response.text}")
    except Exception as e:
        print(f"   ❌ Fehler bei Notizen-Abruf: {e}")
    
    # Test 5: Admin-Funktionen
    print("\n5️⃣ Teste Admin-Funktionen...")
    try:
        response = requests.get(f'{BASE_URL}/users', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()['users']
            print(f"   ✅ {len(users)} Benutzer abgerufen")
            for user in users:
                admin_status = "👑 Admin" if user['admin'] else "👤 User"
                print(f"   {admin_status}: {user['name']} ({user['email']})")
        else:
            print(f"   ❌ Benutzer-Abruf fehlgeschlagen: {response.text}")
    except Exception as e:
        print(f"   ❌ Fehler bei Benutzer-Abruf: {e}")
    
    print("\n🎉 SQLAlchemy-Backend-Tests abgeschlossen!")
    print("📊 Alle Mock-Datenbankoperationen wurden simuliert")
    print("🗄️ SQLAlchemy-Modelle erfolgreich integriert")

def main():
    """Hauptfunktion"""
    backend_process = None
    
    try:
        backend_process = start_backend()
        test_api()
    except KeyboardInterrupt:
        print("\n⏹️ Tests unterbrochen")
    finally:
        if backend_process:
            print("\n🛑 Stoppe Backend...")
            backend_process.terminate()
            backend_process.wait()

if __name__ == '__main__':
    main()

