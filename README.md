# Flask Web-Backend

Ein funktionales Web-Backend mit Python Flask für Benutzerverwaltung und Notizen-System.

## Funktionen

- Benutzerregistrierung und -anmeldung
- Session-basierte Authentifizierung
- CRUD-Operationen für Notizen
- Administrator-Funktionen
- REST-API mit JSON-Kommunikation

## Installation

```bash
pip install -r requirements.txt
```

## Ausführung

```bash
python app.py
```

Die Anwendung läuft standardmäßig auf `http://localhost:5000`

## API-Endpunkte

### Authentifizierung
- `POST /register` - Benutzerregistrierung
- `POST /login` - Benutzeranmeldung
- `POST /logout` - Abmeldung

### Notizen
- `GET /notes` - Alle eigenen Notizen abrufen
- `POST /notes` - Neue Notiz erstellen
- `GET /notes/<id>` - Einzelne Notiz abrufen
- `PUT /notes/<id>` - Notiz bearbeiten
- `DELETE /notes/<id>` - Notiz löschen

### Administration
- `GET /users` - Alle Benutzer auflisten (nur Admin)
- `DELETE /users/<id>` - Benutzer löschen (nur Admin)

