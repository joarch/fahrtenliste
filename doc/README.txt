Fahrtenliste Webapplikation basierend auf Django Webframework.

Starten mit start.bat (z.B. Doppelklick).

Es wird ein Webserver im Hintergrund gestartet.

Im Start Skript sollte der Standard Browser mit der richtigen URL automatisch geöffnet werden.
Alternativ kann die Anwendung im Browser mit "http://127.0.0.1:8000" aufgerufen werden.

Einloggen mit Administrator
Benutzername: admin
Passwort: admin

Unter FAHRTENLISTE stehen die Einzelnen Tabellen zur Eingabe der Fahrten zur Verfügung
- Adressen: hiermit können die Adressen eingesehen und gepflegt werden
- Kunden: hiermit können die Kunden eingesehen und gepflegt werden
- Fahrten: hiermit werden die Fahrten eingegeben
           - auf der Seite oben rechts mit "FAHRT HINZUFÜGEN" können neue Fahrten hinzugefügt werden usw.
		   - während der neuen Erfassung einer Fahrt können Kunden auch direkt neu erfasst werden mit "+" neben "Kunde:"
		   - bei neuer Eingabe des Kunden kann wiederum mit "+" neben der "Adresse:" direkt neue Adressen erfasst werden
           - ein einfacher HTML Report kann mit dem Button "Report" aufgerufen werden, als Zeitraum wird der Zeitraum des
             Filters aus der Fahrtentabelle übernommen

Benutzer können unter Benutzer verwaltet werden.
Wichtig für den Anfang, wenn neue Benutzer eingegeben werden muss nach dem Speichern unter "Berechtigungen" zusätzlich noch
- "Mitarbeiter-Status" und
- "Administrator-Status"
angeklickt werden, damit sich der neue Benutzer auf der Seite anmelden kann und alle Tabellen bearbeiten kann

Zum Beenden einfach die Browserseite schließen und das CMD Fenster was im Hintergrund geöffnet wurde schließen.

Als Backup reicht es aus die Datenbank Datei unter "db.sqlite3" zu kopieren und wegzuspeichern.

Technik:
- Die Programmiersprache ist Python 3.8
- Als Webframework wird Django verwendet
- Die Datenbank liegt unter: db.sqlite3
- Die Programm Dateien (eigener Sourcecode) liegt unter src\fahrtenliste_main\*
- Die Programm Einstellungen (Django Settings) liegt unter src\fahrtenliste\settings.py

Neue Datenbank erstellen bzw. neu aufsetzen:
- umbenennen (löschen) von "db.sqlite3"
- im Command Prompt (cmd):
-- cd [Installations Verzeichnis]
-- python38\python.exe src\manage.py migrate
-- python38\python.exe src\manage.py createsuperuser
