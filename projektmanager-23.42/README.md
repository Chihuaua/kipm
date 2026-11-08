# Projektmanager (Adventshaus) — Version 23.42.03

Eigenständiges Projektmanager-Fenster für den KI-Ablauf am Adventshaus.
Die GUI funktioniert ohne Node-Build und ohne externe CDN-Skripte; der Python-Helfer
lauscht nur auf 127.0.0.1, verlangt ein Sitzungstoken und führt ausschließlich feste Aktionen aus.

## Inhalt des ZIP
- index.html: aktuelle GUI, inline CSS/JS, funktioniert auch per Doppelklick
- style.css: dieselbe Gestaltung als Referenzdatei
- projektmanager.js: dieselbe Aktionslogik als Referenzdatei
- projektmanager.py: lokaler Helfer mit fester API, Sitzungstoken und Git-/Gist-Aktionen
- start.sh / stop.sh / neustart.sh / install-desktop.sh: Start, sicheres Beenden, Neustart (Incident-Hilfe), Desktop-Icon
- einstellungen.json: Projektpfade, Kennung, Port, Spiel-Adresse
- README.md und HISTORIE.md: Anleitung und vollständiger Änderungsverlauf

## Start ohne Terminal-Befehle
1. ZIP vollständig entpacken. Die Dateien müssen zusammen in einem Ordner liegen.
2. Einmalig install-desktop.sh ausführen. Danach gibt es zwei Desktop-Knöpfe.
3. „Projektmanager“ doppelklicken. Es öffnet sich das Projektmanager-Fenster
   (ohne Adressleiste, falls Chromium/Chrome installiert ist; sonst Browser-Tab).
   Beenden und „Neu starten" laufen über die **Werkzeugleiste** oben in der GUI.

Alternativ: bash start.sh oder python3 projektmanager.py im entpackten Ordner.
Voraussetzung: Python 3; für Spiel/Build zusätzlich Node/npm, für Pull Requests gh.

## Token-Sicherheit (nur Postfach-Zugriff)
- Der Token wird im Reiter „Einstellungen“ eingegeben und außerhalb von GUI und
  Projektordner unter ~/.config/adventshaus/gist-token (Rechte 600) gespeichert.
- Minimalrechte: ausschließlich „gist“ (kein „repo“-Zugriff auf das Projekt-Repository!).
- Mit „Echt testen“ prüft der Helfer direkt die GitHub-Gist-API und warnt, falls zu
  weite Rechte (z. B. repo) vergeben wurden. Über „Entfernen“ wird der Token lokal gelöscht.

## Demo und Echtbetrieb
Doppelklick auf index.html ohne Helfer: gelber Demo-Banner, nur Simulation.
Mit Helfer: grüner Banner mit Version und Ordner; die Knöpfe rufen die echte API.
Nach jedem Dateiaustausch Helfer beenden und neu starten. Versionsnummer prüfen.
