#!/usr/bin/env bash
# Neustart: beendet ALLE Projektmanager-Helfer (auch aus anderen Ordnern) und startet den aus diesem Ordner.
HERE="$(cd "$(dirname "$0")" && pwd)"
bash "$HERE/stop.sh"
cd "$HERE" || exit 1
exec bash "$HERE/start.sh"
