#!/usr/bin/env bash
# Beendet NUR den Projektmanager-Helfer, nicht das Spiel oder andere Programme.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 1
ist_helfer() {
  [ -r "/proc/$1/cmdline" ] || return 1
  CMD="$(tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null)"
  case "$CMD" in
    *projektmanager.py*) case "$CMD" in python*|*/python*) return 0 ;; *) return 1 ;; esac ;;
    *) return 1 ;;
  esac
}
BEENDET=""
if [ -f projektmanager.pid ]; then
  PID="$(tr -dc '0-9' < projektmanager.pid 2>/dev/null)"
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null && ist_helfer "$PID"; then
    kill "$PID" 2>/dev/null
    i=0; while [ $i -lt 5 ] && kill -0 "$PID" 2>/dev/null; do sleep 1; i=$((i+1)); done
    kill -9 "$PID" 2>/dev/null
    BEENDET="$PID"
  fi
  rm -f projektmanager.pid
fi
for P in $(pgrep -f "projektmanager[.]py" 2>/dev/null); do
  [ "$P" = "$$" ] && continue
  ist_helfer "$P" || continue
  kill "$P" 2>/dev/null
  BEENDET="$BEENDET $P"
done
sleep 1
for P in $(pgrep -f "projektmanager[.]py" 2>/dev/null); do
  [ "$P" = "$$" ] && continue
  ist_helfer "$P" || continue
  kill -9 "$P" 2>/dev/null
done
sleep 1
REST=""
for P in $(pgrep -f "projektmanager[.]py" 2>/dev/null); do
  ist_helfer "$P" && REST="$REST $P"
done
if [ -z "${REST// /}" ]; then
  TEXT="Projektmanager ist beendet. ${BEENDET}"
else
  TEXT="Achtung: der Projektmanager-Helfer läuft noch:$REST"
fi
echo "$TEXT"
if [ -n "${DISPLAY:-}" ]; then
  if command -v zenity >/dev/null 2>&1; then
    if zenity --help 2>/dev/null | grep -q -- '--css'; then
      CSS='*{background-color:#151619;color:#ececee} label{font-size:12px} button{background-image:none;background-color:#1a1b1e;border:2px solid #4a4d52;border-radius:7px;padding:5px 18px;font-size:12px} button:hover{background-color:#232528;border-color:#697581}'
      zenity --info --title="Projektmanager" --width=280 --text="$TEXT" --css="$CSS" 2>/dev/null
    else
      zenity --info --title="Projektmanager" --width=280 --text="$TEXT" 2>/dev/null
    fi
    exit 0
  fi
  if command -v kdialog >/dev/null 2>&1; then
    kdialog --title "Projektmanager" --msgbox "$TEXT" 2>/dev/null
    exit 0
  fi
  if command -v xmessage >/dev/null 2>&1; then
    xmessage -center -timeout 15 "$TEXT" 2>/dev/null
    exit 0
  fi
  for T in gnome-terminal konsole xterm; do
    if command -v "$T" >/dev/null 2>&1; then
      "$T" -- bash -c "printf '%s\n\n' '$TEXT'; read -r -p 'Enter schließt …'" 2>/dev/null \
        || "$T" -e bash -c "printf '%s\n\n' '$TEXT'; read -r -p 'Enter schließt …'" 2>/dev/null
      exit 0
    fi
  done
fi
echo "Hinweis: kein Fenster möglich – Meldung nur hier."
