"""
Haupteinstiegspunkt für das Flask-Backend
"""
from flask import Flask
from myapp.db import init_db
from myapp.routes import api

def create_app():
    """Flask-App-Factory"""
    app = Flask(__name__)
    
    # Konfiguration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_app.db'  # Würde echte DB verwenden
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Datenbank initialisieren
    init_db(app)
    
    # Blueprints registrieren
    app.register_blueprint(api)
    
    return app

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    app = create_app()
    
    print("🚀 Flask Web-Backend wird gestartet...")
    print("📋 Verfügbare Dummy-Benutzer:")
    print("   Admin: admin@example.com / admin123")
    print("   User1: john@example.com / password123")
    print("   User2: jane@example.com / mypassword")
    print("🌐 Server läuft auf: http://localhost:5001")
    
    app.run(debug=False, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()

