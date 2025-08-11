# Videoflix Backend - Schritt-für-Schritt Anleitung

> [!IMPORTANT]
> **Lies diese Anleitung vollständig durch, bevor du beginnst!**

Dieses Repository enthält den Backend-Teil der Videoflix-Anwendung. 

Das zugehörige Frontend findest du hier: [Videoflix-frontend](https://github.com/Philipp-Loetzsch/videoflix_frontend)

## Inhaltsverzeichnis

<!-- TOC -->

- [Videoflix - Docker Setup](#videoflix---docker-setup)
  - [Table of Contents](#table-of-contents)
  - [Voraussetzungen](#voraussetzungen)
  - [Quickstart](#quickstart)
  - [Usage](#usage)
    - [Environment Variablen](#environment-variablen)
    - [Migrations im Docker Container](#migrations-im-docker-container)
    - [requirements.txt](#requirementstxt)
  - [Troubleshooting](#troubleshooting)

<!-- /TOC -->

---

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass du Folgendes installiert hast:

### 1. Docker Desktop

- **Windows/Mac**: Lade [Docker Desktop](https://www.docker.com/products/docker-desktop/) herunter und installiere es
- **Linux**: Folge der [Docker Engine Installation](https://docs.docker.com/engine/install/)
- **WICHTIG**: Nach der Installation musst du Docker Desktop starten!
- **Test**: Öffne ein Terminal und führe aus:
  ```bash
  docker --version
  docker-compose --version
  ```
  Beide Befehle sollten eine Versionsnummer anzeigen.

### 2. Git

- Lade Git von [git-scm.com](https://git-scm.com/downloads) herunter und installiere es
- **Test**: Öffne ein Terminal und führe aus:
  ```bash
  git --version
  ```
  Der Befehl sollte eine Versionsnummer anzeigen.

### 3. Code Editor

- Empfohlen: [Visual Studio Code](https://code.visualstudio.com/)
- **WICHTIG**: Stelle in VS Code sicher, dass die Datei `backend.entrypoint.sh` mit "LF" (nicht CRLF) Zeilenenden gespeichert ist!

---

## Installation & Setup

> [!CAUTION]
> ### ⚠️ WICHTIGE REGELN - BITTE BEACHTEN ⚠️
> 
> 1. **NICHT VERÄNDERN:**
>    - `backend.Dockerfile`
>    - `docker-compose.yml`
>    - `backend.entrypoint.sh`
>    - Die grundlegende Konfiguration in `settings.py`
>
> 2. **VORSICHT BEI:**
>    - `.env` Datei: Du kannst Werte ändern, aber **NICHT** existierende Variablen löschen
>    - `settings.py`: Nur neue Einstellungen hinzufügen, bestehende nicht ändern
>
> 3. **ERLAUBT UND ERFORDERLICH:**
>    - Neue Packages installieren
>    - `requirements.txt` regelmäßig aktualisieren
>    - Neue Einstellungen in `settings.py` hinzufügen

### Schritt 1: Projekt klonen

1. Öffne ein Terminal
2. Navigiere zu deinem gewünschten Projektordner
3. Führe aus:
   ```bash
   git clone https://github.com/Philipp-Loetzsch/videoflix_backend.git
   cd videoflix_backend
   ```

### Schritt 2: Umgebungsvariablen einrichten

1. Öffne das Projekt in VS Code:
   ```bash
   code .
   ```

2. Erstelle und konfiguriere die Umgebungsvariablen:
   ```bash
   # Kopiere die Vorlage für Umgebungsvariablen
   cp .env.template .env

   # Öffne die Datei in VS Code
   code .env
   ```

3. Passe die Werte in der `.env` Datei an:
   - Setze ein sicheres Admin-Passwort
   - Konfiguriere die Datenbank-Zugangsdaten
   - Stelle die E-Mail-Einstellungen ein
   - Speichere die Datei

### Schritt 3: Docker Container starten

1. **WICHTIG**: Stelle sicher, dass Docker Desktop läuft!

2. Terminal öffnen und im Projektordner ausführen:
   ```bash
   docker compose up --build
   ```
   
   Falls dieser Befehl nicht funktioniert, versuche stattdessen:
   ```bash
   docker-compose up --build
   ```

3. Warte, bis alle Container gestartet sind. Du siehst viele Log-Ausgaben - das ist normal!

4. Teste die Anwendung:
   - Öffne [localhost:8000](http://localhost:8000) im Browser
   - Du solltest die API-Oberfläche sehen

> [!TIP]
> Um die Container zu stoppen, drücke `Strg+C` im Terminal
> 
> Um sie wieder zu starten (ohne neu zu bauen), verwende:
> ```bash
> docker compose up
> ```

---

## Konfiguration & Nutzung

### Environment Variablen (.env)

> [!IMPORTANT]
> - **NICHT** die Variablennamen in der `.env` ändern
> - **NICHT** existierende Variablen löschen
> - Du **DARFST** die Werte der Variablen anpassen
> - Du **DARFST** neue Variablen hinzufügen

#### Automatischer Admin-Benutzer

Die `backend.entrypoint.sh` erstellt automatisch einen Administrator mit diesen Zugangsdaten:

```env
DJANGO_SUPERUSER_USERNAME=admin    # Standard: "admin"
DJANGO_SUPERUSER_PASSWORD=xxxxx    # Wähle ein sicheres Passwort!
DJANGO_SUPERUSER_EMAIL=xxx@xxx.xx  # Deine E-Mail-Adresse
```

#### Wichtige Konfigurationen

| Name | Type | Description | Default | Mandatory |
| :--- | :---: | :---------- | :----- | :---: |
| **DJANGO_SUPERUSER_USERNAME** | str | Benutzername für das Django-Admin-Superuser-Konto. Dieser Benutzer wird automatisch erstellt wenn er nicht existiert. | `admin` |   |
| **DJANGO_SUPERUSER_PASSWORD** | str |  Passwort für das Django-Admin-Superuser-Konto. Achte darauf, dass es sicher ist. | `adminpassword` |   |
| **DJANGO_SUPERUSER_EMAIL** | str |  E-Mail-Adresse für das Django-Admin-Superuser-Konto. Wird für die Wiederherstellung des Kontos und für Benachrichtigungen verwendet. | `admin@example.com` |   |
| **SECRET_KEY** | str | Ein geheimer Schlüssel für die Kryptografie in Django. Dieser sollte eine lange, zufällige Zeichenfolge sein und vertraulich behandelt werden. |   | x |
| **DEBUG** | bool | Aktiviert oder deaktiviert den Debug-Modus. Sollte in der Produktion auf False gesetzt werden, um die Offenlegung sensibler Informationen zu verhindern. | `True` |   |
| **ALLOWED_HOSTS** | List[str] | Eine Liste von Strings, die die Host-/Domainnamen darstellen, die diese Django-Site bedienen kann. Wichtig für die Sicherheit. | `[localhost]` |   |
| **CSRF_TRUSTED_ORIGINS** | List[str] | Cors-Headers allowed origins. | `[http://localhost:4200]` |   |
| **DB_NAME** | str | Name der PostgreSQL-Datenbank, zu der eine Verbindung hergestellt werden soll. Wichtig für Datenbankoperationen. | `your_database_name` | x |
| **DB_USER** | str | Benutzername für die Authentifizierung bei der PostgreSQL-Datenbank. | `your_database_user` | x |
| **DB_PASSWORD** | str | Passwort für den PostgreSQL-Datenbankbenutzer. | `your_database_password` | x |
| **DB_HOST** | str | Host-Adresse der PostgreSQL-Datenbank. Normalerweise localhost oder der Dienstname in Docker. | `db` |   |
| **DB_PORT** | int | Portnummer für die Verbindung zur PostgreSQL-Datenbank. | `5432` |   |
| **REDIS_LOCATION** | str | Redis location | `redis://redis:6379/1` |   |
| **REDIS_HOST** | str | Redis host | `redis` |   |
| **REDIS_PORT** | int | Redis port | `6379` |   |
| **REDIS_DB** | int | Redis DB | `0` |   |
| **EMAIL_HOST** | str | SMTP-Server-Adresse für den Versand von E-Mails. | `smtp.example.com` | x |
| **EMAIL_PORT** | int | Portnummer für den SMTP-Server. | `587` |   |
| **EMAIL_USE_TLS** | bool | Aktiviert TLS für den E-Mail-Versand. Empfohlen für die Sicherheit. | `True` |   |
| **EMAIL_USE_SSL** | bool | E-Mail verwendet SSL | `False` |   |
| **EMAIL_HOST_USER** | str | Benutzername für das E-Mail-Konto, das zum Senden von E-Mails verwendet wird. | `your_email_user` | x |
| **EMAIL_HOST_PASSWORD** | str | Passwort für das E-Mail-Konto. Achte auf die Sicherheit. | `your_email_password` | x |
| **DEFAULT_FROM_EMAIL** | str | E-Mailadresse die von Django verwendet wird | `EMAIL_HOST_USER` |   |

### Datenbankmigrationen durchführen

Wenn du Änderungen an den Models gemacht hast, musst du diese auf die Datenbank anwenden.

#### Methode 1: Migration im laufenden Container (EMPFOHLEN)

1. Migrations-Dateien erstellen:
   ```bash
   docker compose exec web python manage.py makemigrations
   ```

2. Migrations ausführen:
   ```bash
   docker compose exec web python manage.py migrate
   ```

#### Methode 2: Container neu bauen (NICHT EMPFOHLEN)

Nur wenn Methode 1 nicht funktioniert:

1. Container stoppen mit `Strg+C`
2. Neu bauen und starten:
   ```bash
   docker compose up --build
   ```

### Python-Packages verwalten

#### requirements.txt aktualisieren

1. Füge neue Packages in `requirements.txt` hinzu
2. Container neu bauen:
   ```bash
   docker compose up --build
   ```

#### Installierte Packages anzeigen

Nur Hauptpackages (ohne Abhängigkeiten):
```bash
docker compose exec web pip list --not-required
```

Alle installierten Packages:
```bash
docker compose exec web pip list
```

## Fehlerbehebung

### ❌ "Docker Desktop" Fehler
```bash
unable to get image 'postgres:latest': error during connect:
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.48/images/postgres:latest/json":
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

✅ **Lösung:**
1. Docker Desktop öffnen
2. Warten bis es vollständig gestartet ist
3. Erneut versuchen

### ❌ "entrypoint.sh" Fehler
```bash
videoflix_backend   | exec ./backend.entrypoint.sh: no such file or directory
videoflix_backend exited with code 255
```

✅ **Lösung:**
1. VS Code öffnen
2. `backend.entrypoint.sh` öffnen
3. Unten rechts in der Statusleiste auf "CRLF" klicken
4. "LF" auswählen
5. Datei speichern
6. Docker Container neu starten

### ❌ Datenbank-Fehler
```bash
django.db.utils.OperationalError: FATAL: database "xxx" does not exist
```

✅ **Lösung:**
1. Container stoppen (`Strg+C`)
2. Docker Volumes löschen:
   ```bash
   docker compose down -v
   ```
3. Container neu starten:
   ```bash
   docker compose up --build
   ```

### ❌ Permission Denied
```bash
permission denied while trying to connect to the Docker daemon socket
```

✅ **Lösung:**
- **Windows/Mac**: Docker Desktop neu starten
- **Linux**: Führe die Befehle mit `sudo` aus oder füge deinen Benutzer zur Docker-Gruppe hinzu:
  ```bash
  sudo usermod -aG docker $USER
  ```
  (Danach abmelden und wieder anmelden)

---
