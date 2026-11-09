#!/usr/bin/env bash
# Projektmanager (Adventshaus) — Start (nur lokal, 127.0.0.1)
HERE="$(cd "$(dirname "$0")" && pwd)"
for f in projektmanager.py projektmanager.js index.html; do
  if [ ! -f "$HERE/$f" ]; then
    echo "FEHLER: $f fehlt im Ordner $HERE."
    echo "Ursache fast immer: ZIP unvollständig entpackt, doppelter Ordner (…/projektmanager-23.42/projektmanager-23.42/…) oder Ordner wurde verschoben, während der Helfer lief."
    echo "Prüfe: ls $HERE  (müssen 11 Dateien sein, u. a. index.html)"
    exit 1
  fi
done
cd "$HERE" || exit 1
echo "==> Projektmanager-Ordner: $HERE"
if ! command -v python3 >/dev/null 2>&1; then
  echo "FEHLER: Python 3 fehlt. Installieren (Debian/Ubuntu): sudo apt install python3"
  exit 1
fi
mkdir -p "$HOME/.config/adventshaus" 2>/dev/null
if [ ! -f "$HOME/.config/adventshaus/gist-token" ]; then
  touch "$HOME/.config/adventshaus/gist-token" 2>/dev/null
  chmod 600 "$HOME/.config/adventshaus/gist-token" 2>/dev/null
  echo "==> Token-Datei angelegt (leer): ~/.config/adventshaus/gist-token"
fi
VER="$(grep -o 'HELPER_VERSION = "[^"]*"' projektmanager.py | head -1 | sed 's/.*"\(.*\)"/\1/')"
echo "==> Projektmanager-Version: ${VER:-unbekannt}  (Ordner: $HERE)"
echo "==> Starte Helfer … der Browser öffnet sich. Dieses Fenster bleibt offen (Strg+C beendet)."
exec python3 -u projektmanager.py
