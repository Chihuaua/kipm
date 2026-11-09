#!/usr/bin/env bash
# Einmalig installieren: ein Desktop-Knopf mit dem tatsächlichen Ordnerpfad.
# (Beenden/Neu starten sind jetzt in der Werkzeugleiste der GUI.)
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.config/adventshaus" 2>/dev/null
if [ ! -f "$HOME/.config/adventshaus/gist-token" ]; then
  touch "$HOME/.config/adventshaus/gist-token" 2>/dev/null
  chmod 600 "$HOME/.config/adventshaus/gist-token" 2>/dev/null
fi
DESK="$HOME/Schreibtisch"
[ -d "$DESK" ] || DESK="$HOME/Desktop"
mkdir -p "$DESK" 2>/dev/null
rm -f "$DESK/Adventshaus-Leitstand.desktop" "$DESK/Adventshaus-Leitstand-beenden.desktop" "$DESK/Adventshaus-Leitstand-neustart.desktop" "$DESK/Adventshaus-Kipm.desktop" "$DESK/kipm.desktop" 2>/dev/null
FILE="$DESK/projektmanager.desktop"
cat > "$FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Projektmanager
GenericName=KI-Übergabe
Comment=Startet den Projektmanager (Helfer + Fenster) – nur lokal
Exec=bash "$HERE/start.sh"
Icon=applications-system
Terminal=false
Categories=Utility;
EOF
chmod +x "$FILE" 2>/dev/null
if command -v gio >/dev/null 2>&1; then
  for F in "$FILE"; do
    gio set "$F" metadata::trusted true 2>/dev/null || true
    gio set "$F" kde::trusted true 2>/dev/null || true
  done
fi
echo "==> Fertig. Ein Icon auf dem Schreibtisch (Ordner: $HERE)"
echo "Beenden und Neu starten laufen über die Werkzeugleiste in der GUI."
