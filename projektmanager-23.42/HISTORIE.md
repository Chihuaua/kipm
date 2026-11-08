# HISTORIE · Adventshaus · Leitstand

Chronologische Entwicklungsgeschichte dieses Werkzeugs. **Wird beim Bearbeiten
ergänzt** – jede KI-Sitzung hängt ihre Änderungen hier an (neuestes Datum oben
unter „Neueste Änderungen“, falls gewünscht, oder chronologisch unten).

---

## 0 · Ausgangslage
- Ausgangsstand: eine leere React/Vite/Tailwind-Vorlage in der Sandbox, **nicht** das Adventshaus-Repository.
- Auftrag: ein **Leitstand** – ein Fenster, das dem Besitzer sagt, wo der Stand
  steht und was als Nächstes zu tun ist. Eigenständig, **außerhalb** des Repos,
  kein Patch darauf. Nur lesen, bis eine Aufgabe kommt.

## 1 · Technische Richtungsentscheidung
- Statt React/Vite bewusst **frameworkfrei**: `index.html` + `style.css` + `leitstand.js`.
  Begründung: nur Python 3 als Voraussetzung auf dem Desktop, kein Node-Build,
  Dateien direkt auslieferbar und reparierbar, nichts zu „verstehen“ für spätere KIs.
- **Dunkles Design**, Ablenkung reduziert: Ampel oben, Stationsstraße
  ① Aufgabe → ② KI baut → ③ Übernehmen → ④ Sichern, genau ein großer Knopf
  für den nächsten Schritt, 9 Handlungsknöpfe mit Bedeutungsfarbe + Symbol.

## 2 · Etappe 1 (nur lesend, Demo-Daten)
- Ampel (grün/gelb/rot), Stationsstraße, großer Knopf, Denkanzeige mit laufenden
  Punktezeilen, „genauer Befehl“ und Protokoll eingeklappt, Abbrechen,
  Reiter (Ablauf / So funktioniert’s / Protokoll / Einstellungen), Fußzeile mit Pfaden.
- Alle Daten simuliert; schreibende Knöpfe als „kommt in Etappe 2“ markiert.
- **ZIP-Download** in der Fußzeile (später: eingebettete Bytes, s. u.).

## 3 · Größen- und Layoutänderungen (nach Bewertung durch den Besitzer)
- Kompakter: feste Höhe 720×500 (≈ halbe Fläche von 980×760).
- **Korrektur:** feste Höhe für eine HTML-Seite sinnlos → **Breite bleibt 720 px,
  Höhe wächst mit dem Inhalt**; intern scrollen nur die Zeilen, die Seite selbst
  scrollt bei Bedarf. Alle „overflow: auto“-Kästen entfernt.
- Knöpfe verkleinert, Überschriften verkleinert, Platz neu berechnet.

## 4 · Etappe 2 (schreibende Aktionen + Python-Helfer)
- **Bestätigungs-Dialog** vor jeder schreibenden Aktion (Vorschautext + „Ausführen“),
  danach sichtbarer Fortschritt in der Denkanzeige, Abbrechen bei Leseprüfungen.
- **`leitstand.py`**: lokaler Helfer, nur `127.0.0.1`, **feste Aktionsliste**
  (status, pruefen, ablegen, uebernehmen, sichern, token, spiel, spiel-stop),
  kein freies Kommando aus dem Browser. Token wird nur hier gelesen, nie
  angezeigt, in jeder Ausgabe gefiltert (`Authorization: ***`, `gh***`).
- **Token** in `~/.config/adventshaus/gist-token` (Rechte 600), speicherbar über
  die GUI (`/api/token`).
- **Start/Beenden:** `start.sh`, `install-desktop.sh` (zwei Desktop-Icons),
  `stop.sh` mit PID-Datei.
- **Übergabedatei:** „Stand sichern“ erzeugt `docs/UEBERGABE.md` neu und erhält
  die HAND-Notiz unter der Marke `<!-- HAND: … -->`.
- **Versionsprüfung:** Helfer meldet `version`, GUI vergleicht mit `GUI_VERSION`.

## 5 · Fehler und ihre Behebungen (Entwicklungsverlauf)
1. **Zweites Modul (`zipdata.js`) brach die GUI** in der Vorschau – der
   Zusammenführungs-Build lieferte die Logik nicht mehr. → zurück zu **einem**
   Modul; ZIP-Bytes direkt in `leitstand.js`.
2. **`file://` blockiert ES-Module** → Doppelklick auf `index.html` zeigte eine
   tote GUI. → portable Version mit **inline klassischem Skript** (kein `type="module"`).
3. **Download lieferte HTML statt ZIP** (Vorschau kannte die nebenliegende Datei
   nicht) → „Not a zip archive“. → **eingebettete Bytes** (`data:`-Link) in der GUI.
4. **Desktop-Eintrag mit Pfad-Raten** (3 feste Orte) → „Ordner nicht gefunden“.
   → `install-desktop.sh` schreibt den **tatsächlichen** Pfad, `start.sh`
   findet seinen Ordner selbst, Ausführbit nicht nötig (`bash`-Aufruf).
5. **Browser öffnete nicht zuverlässig** (`webbrowser.open` reicht nicht) →
   Kaskade `xdg-open`/`open` + Adresse groß ausgeben + manuellen Hinweis.
6. **„unbekannte Aktion“** = laufender Helfer mit **alter Version** im Speicher
   (Code wird beim Start geladen). → Versionsnummer + roter Balken
   „Helfer ist zu alt – bitte neu starten“ + Übersetzung der Meldung.
7. **„Fehler: Stand gesichert.“** (Misleitung) → echte Ursachen benennen
   (Sicherung nicht gefunden / fetch fehlgeschlagen).
8. **GitHub-main-Check lief im falschen Ordner** (`origin` unbekannt) → `cwd=projekt`.
9. **Port des Spiels ist dynamisch** (Vite wählt 5174, 5175 …) → Port-Suche
   5173–5200 + 3000/4173/5000/8000/8080 mit Titel-Erkennung.
10. **Vite bindet nur auf `[::1]` (IPv6)** – Suche prüfte nur `127.0.0.1` und
    fand den laufenden Server nie. → **beide Adressen** pro Port geprüft.
11. **„Spiel ansehen“ startete nichts** → startet jetzt selbst `npm run dev`
    (wartet bis 25 s, Log bei Fehlern), zweiter Klick beendet Tab **und** Spiel
    (nur wenn der Leitstand es gestartet hat).
12. **`stop.sh` traf den eigenen Prozess** (`pgrep -f` matchte den Aufruf).
    → Trüger-Muster `leitst[a]nd[.]py` **plus** Prüfung: nur **Python**-Prozesse
    werden beendet (geschützt: Terminals, Editoren, dieser Aufruf selbst).
13. **`stop.sh` ohne Feedback** (Icon läuft ohne Fenster) → Meldungsfenster:
    `zenity` → `kdialog` → `xmessage` → Terminal, sonst Text auf stdout.

## 6 · Offene Punkte (bewusst nicht gebaut)
- **Postfach-Prüfung ohne Token** wird übersprungen („kein Token“) – erst mit
  Token vollständig.
- **Alter Patch** (Basis `2aecf78` ≠ main `b5fdb26`) wird beim nächsten
  „Patch ablegen“ automatisch überschrieben; bis dahin blockiert ihn die Basis-Prüfung.
- **Git-/Gist-Abläufe** (`ablegen`, `uebernehmen`, `sichern`) sind als Referenz
  gebaut und **einmal real durchzutesten** (Repo + Token des Besitzers).
- **Protokoll-Rotation** (max. 7 Dateien unter `protokoll/`) nicht umgesetzt.
- **Pfad-Assistent** (Fehlende automatisch suchen/nachfragen) nicht umgesetzt –
  Pfade nur in `einstellungen.json`.
- **Handnotiz-Vorbelegung** (drei Zeilen) – Feld ist da, Vorbelegung nur als
  `NOTIZ_DEFAULT` im Code.
- **Postfach-Übernahme ohne vorhandenen Knopf** nutzt den Referenz-Ablauf
  (`git am`, `tsc`, `build`, `gh pr create`) – der vorhandene Desktop-Knopf
  hat Vorrang, falls da.

## 7 · Grundregeln dieses Werkzeugs (unverhandelbar)
1. Der Leitstand **verändert das Spielprojekt nicht** von selbst; schreibende
   Aktionen fragen vorher und nennen, was passiert.
2. Das **Token verlässt nie** den Helfer und steht nie in einem Log oder einer Meldung.
3. Der Helfer lauscht **nur auf 127.0.0.1** und führt **nur feste Aktionen** aus.
4. **Keine neuen npm-Pakete**, kein Node-Baufschritt für den Desktop-Betrieb.
5. Meldungen immer **ehrlich**: lieber „Sicherung nicht gefunden: <pfad>“ als
   ein Erfolg, der keiner ist.
6. Nach jeder Änderung: `node --check leitstand.js`, `python3 -m py_compile
   leitstand.py`, `bash -n *.sh`, `npm run build`, ZIP neu packen.
7. **Helfer immer neu starten** nach dem Austausch von Dateien – sonst läuft
   die alte Version weiter (Ursache vieler „unbekannt“-Meldungen).
8. **HISTORIE.md bei jeder Änderung fortschreiben** (Abschnitt 8 unten, neueste
   zuerst). **Die Entwickler-Info muss bei jeder Ausgabe den gesamten Quellcode
   aller Komponenten und die gesamte HISTORIE.md enthalten.** Diese Anweisung
   bleibt dauerhaft bestehen; unvollständige oder erfundene Exporte sind nicht
   zulässig. Fehlende Dateien werden ausdrücklich als fehlend benannt.

---

## 8 · Änderungsprotokoll (neueste zuerst)

**16.11.2026 – Version 23.34: vollständiges Funktionspaket, Linien vereinheitlicht, Ecken vergrößert**
- Auf Wunsch des Besitzers wurden die abgeschrägten Ecken aller Knöpfe vergrößert:
  Handlungsknöpfe von 8 px auf 10 px, der große „Jetzt dran“-Knopf von 10 px auf
  12 px; die inneren Fasen jeweils passend dazu (9 px bzw. 11 px), damit die
  schräge Kante optisch dieselbe Stärke wie die 2-px-Rahmen behält.
- Auftrag des Besitzers: Das ZIP darf nicht nur eine Demo-GUI enthalten, sondern
  muss **vollständig funktionsfähig mit Python-Helfer** sein. Alle Komponenten
  sind jetzt als Textquellen in `index.html` eingebettet und werden beim Download
  als echte Dateien geschrieben: `index.html`, `style.css`, `leitstand.js`,
  `leitstand.py`, `start.sh`, `stop.sh`, `install-desktop.sh`,
  `einstellungen.json`, `README.md` und `HISTORIE.md`.
- Die ZIP-Erzeugung arbeitet ohne Server und ohne Node-Paket. Sie schreibt ein
  echtes ZIP mit UTF-8-Dateinamen, CRC32, Zentralverzeichnis und Abschlussprüfung.
  Auch die entpackte GUI kann das vollständige Paket erneut erzeugen.
- **Echte Helfer-Anbindung:** `/api/status` unterscheidet Demo und Echtbetrieb.
  Prüfbericht, Projektdiagnose, Patch eintragen (Text/Datei/Adresse), Patch zu
  GitHub, lokales Speichern, Postfach, Sicherung, Postfach leeren, Basis
  korrigieren, Spiel starten/beenden und Token-Verwaltung rufen die festen
  Endpunkte auf. Schreibende Aktionen fragen weiterhin vorher.
- **Banner:** Demo bleibt gelb, Echtbetrieb grün. Der Banner nennt Version,
  GUI-Version, Ordner und Betriebsart. Ein Versionsunterschied wird mit der
  richtigen Richtung („Helfer älter“ / „GUI älter“) gemeldet.
- **Bekannte Codefehler behoben:** Ergebnisobjekt `j` wird nicht mehr außerhalb
  seines Gültigkeitsbereichs verwendet; der Übergabe-Export verwendet `%s` für
  Versionszeichenketten; die Projektdiagnose initialisiert `fehlen` immer;
  große Patches werden nicht mehr auf 4000 Zeichen gekürzt; statische Dateien
  werden nur aus einer festen Liste ausgeliefert.
- **Linien:** Alle Rahmen und Trennlinien verwenden `--rahmen: 2px`, gemessen an
  der Gruppe Wartung. Gefaste Ecken wurden auf dieselbe optische Strichstärke
  gerechnet. Doppelte angrenzende Linien (Kopf/Banner) wurden entfernt.
- **Layout:** Die Oberkante des „Jetzt dran“-Knopfes liegt durch die gemeinsame
  feste Kopfhöhe exakt auf Höhe der ersten Knöpfe in 01 und 02. Alle Knöpfe
  innerhalb einer Gruppe haben dieselbe Höhe und Breite.
- **Entwickler-Info:** Enthält jetzt auch ohne laufenden Helfer den vollständigen
  Quellcode aller eingebetteten Komponenten und diese gesamte HISTORIE. Regel 8
  wurde entsprechend verschärft und bleibt dauerhaft in jeder Ausgabe erhalten.
- **Nicht als getestet behauptet:** Reale Git-/Gist-/Build-Läufe müssen am
  Projekt des Besitzers durchgeführt werden. Die statische Paketprüfung ersetzt
  keinen echten Funktionstest mit Repository und Token.

**05.11.2026 – Übernahme durch KI-A: drei Fehler behoben, Version 23.26**
Auslöser: Der Besitzer bat KI-A, den Leitstand zu übernehmen (KI-B lieferte seit
~17 Uhr nichts mehr). KI-A lagen alle Dateien vor und wurden gegengeprüft.

- **Fehler 1 (wichtigster) – Sanduhr dreht weiter, keine Meldung:** In
  `runWrite()` wurde `const infoFall = !!(j && j.info);` benutzt, obwohl `j`
  nur **innerhalb** des `if (REAL_MODE)`-Blocks existierte. Jede **erfolgreiche**
  Aktion im echten Modus brach damit ab: die Abschlussmeldung fehlte, der große
  Knopf sprang **nicht** auf den nächsten Schritt, Ampel und Straße blieben
  stehen. → Fix: `let j = null;` **vor** den Block gesetzt.
- **Fehler 2 – falsche „Helfer ist zu alt“-Meldung:** `GUI_VERSION` stand auf
  **23.21**, `HELPER_VERSION` auf **23.25** – weil die letzten vier Änderungen
  nur den Helfer hochgezählt hatten. Das Banner behauptete „Helfer ist zu alt“,
  obwohl der Helfer **neuer** war. → Fix: beide auf **23.26** gesetzt; das
  Banner prüft jetzt die **Richtung**.
- **Fehler 3 – Editier-Unfall:** Der Kommentar hinter `GUI_VERSION` war rund
  **40-mal wiederholt**. → Aufgeräumt auf einen einzigen Kommentar.
- **Nebenbei geprüft:** Alle 13 `fetch("/api/…")`-Pfade der GUI gegen die
  `ACTIONS`-Liste des Helfers → **vollständige Deckung**.
- **Stop-Skript:** `stop.sh` lag vollständig vor und wurde unverändert
  übernommen (PID-Datei zuerst, `leitst[a]nd`-Muster, Feedback-Kaskade).

**15.11.2026 – Analyse von KI-A übernommen: Übergabedatei-Rest verdrängte den Arbeits-Patch**

**14.11.2026 – Vertrauensprüfung der Info-Meldung (Frage des Besitzers)**
„Wie vertrauenswürdig ist diese Aussage?“ („GitHub ist bereits aktuell –
der Patch enthielt nur Dateien, die es bei dir schon gibt …“)

- **Geprüft und vertrauenswürdig:** Die Behauptung „nur vorhandene
  Dateien“ – der Filter arbeitet mit konkreten Dateipfaden und
  `os.path.exists`; wenn nach dem Filter kein Diff mehr übrig ist, war
  tatsächlich nichts Neues im Patch. Echter neuer Inhalt wäre ein Diff
  geblieben und hätte `apply --check` durchlaufen.
- **Zu stark behauptet:** „GitHub ist bereits aktuell“ – in diesem
  Prüfzweig wird der GitHub-/Lokal-Stand **nicht** verglichen (das passiert
  nur in der Basis-Prüfung). Die Meldung verkaufte mehr, als sie weiß.
- **Korrigiert (23.4):** Sie sagt nur noch, was geprüft wurde:
  „Der Patch enthielt nur Dateien, die es bei dir schon gibt: … – nichts
  Neues zu übernehmen. Keine Handlung nötig.“ – **plus** der lokal-voraus-
  Hinweis, falls zutreffend.
- **Grenzen weiterhin offengelegt:** Die Meldung sagt nicht „dein Stand ist
  GitHub gleich“ und nicht „der Patch wäre anwendbar gewesen“ – nur: in
  diesem Patch steckte nichts Neues.
- **Version auf 23.4 erhöht.**

**14.11.2026 – Knopf „Basis korrigieren“ (nach der Analyse von KI-A)**
- **Situation nach Version 23.2:** Banner und lokaler-Commits-Hinweis
  funktionierten, aber die `aktuell.json` trug als Basis **586e3c5**, während
  GitHub-main auf **82b1629** stand → echter „veraltet“-Fall.
- **Neue Helfer-Aktion `basis-korrigieren`** (POST `/api/basis-korrigieren`):
  liest `aktuell.json`, setzt `basis` auf den **aktuellen origin/main** und
  schreibt die json zurück – **Patch-Inhalt und Prüfsumme bleiben
  unverändert**. Meldung nennt alte und neue Basis.
- **GUI:** Beim Basis-Fehler erscheint im Denkfenster-Fuß der grüne Knopf
  **„Basis korrigieren“**. Nach Erfolg springt der große Knopf automatisch
  wieder auf **„Patch übernehmen“**.
- Sicherheit: Die Prüfsumme wird vorher geprüft, danach entscheidet weiterhin
  `apply --check` über echte Inhaltskonflikte.
- **Version auf 23.3 erhöht.**

**14.11.2026 – Basis-Prüfung korrigiert: origin/main statt lokalem HEAD
(Analyse von KI-A übernommen)**
KI-A fand die Ursache der „veraltet“-Meldung: Der Patch-Basis wurde mit dem
**lokalen `HEAD`** verglichen, aber KIs bauen auf **`origin/main`**.

- **Befund:** Lokale Commits, die nirgends auf GitHub sind, ließen den
  lokalen `HEAD` vom GitHub-Stand abweichen → jede Prüfung meldete fälschlich
  „veraltet“, obwohl der Patch zum GitHub-Stand passte.
- **Fix:** Neue Hilfsfunktion `_origin_main_kurz()` (`git ls-remote
  origin refs/heads/main`, Offline-Fallback: lokaler HEAD). Die
  **Basis-Prüfung vergleicht jetzt gegen origin/main**.
- **Neuer Info-Hinweis:** Wenn der lokale Stand GitHub voraus ist, steht in
  der Meldung: *„Hinweis: Dein lokaler Stand (X) ist GitHub (Y) voraus –
  deine lokalen Commits sind noch nicht auf GitHub.“*
- Beide Hinweise (lokale Commits + entfernte Dateien) werden jetzt
  **verkettet** (nicht überschrieben).
- **Version auf 23.2 erhöht.**

**14.11.2026 – Versions-Nachweis für den Download und den Start (Diagnose)**
Rückmeldung: „Bin bei 23.1 – habe aber wieder die alte Meldung.“ Der
Screenshot-Banner zeigte **keinen** Versions-/Ordner-Zusatz und es gab
**keinen** Versionsbalken → belegt: GUI **und** Helfer laufen mit der
gleichen alten Datei.

- **ZIP-Downloadname enthält jetzt die Version:**
  `adventshaus-leitstand-23.1.zip`.
- **`start.sh` meldet beim Start die Version + den Ordner.**
- **Diagnose-Weg ohne Rätseln:** `leitstand.py` im Texteditor öffnen →
  Strg+F „23.1“ → nicht gefunden = alte Datei; gefunden = Start-Pfad
  zeigt auf eine andere Kopie.
- **Version weiter 23.1.**

**14.11.2026 – „Nichts Neues“ ist keine Fehlermeldung (Feinschliff)**
- Wenn der Patch ausschließlich Dateien enthält, die es schon gibt, ist das
  **kein Fehler, sondern ein Zustand** – keine Handlung nötig.
- **Geändert in beiden Aktionen** (eintragen und übernehmen):
  - vorher: `ok: false` mit Lösung (rot)
  - jetzt: **`ok: true, info: true`** → grüne Info-Zeile, keine Lösungszeile,
    kein Wechsel des großen Knopfes, kein Ampel-/Straßen-Umschalten.
- Echte Konflikte bleiben **Fehler mit Lösung**.
- **Version auf 23.1 erhöht.**

**14.11.2026 – Doppelte Prüfung des Filters (Auftrag: „doppelt und dreifach prüfen“)**
- **Prüfung 1 – Reihenfolge in `act_uebernehmen`:** sha256 am *Original*
  (vor dem Filter) → Basis-Prüfung → **Filter** → `apply --check` → `git am`.
  Korrekt: die Prüfsumme beschreibt das Postfach-Dokument, nicht den
  gefilterten Text. ✓
- **Prüfung 2 – ZWEITE LÜCKE GEFUNDEN und behoben:** Der Filter prüfte nur
  **neue Dateien** (`--- /dev/null`). Wenn `docs/UEBERGABE.md` im Patch als
  **Änderung** stand, griff er **nicht**.
- **Filter erweitert:** `docs/UEBERGABE.md` wird **immer** entfernt – egal
  ob neu oder als Änderung. Andere Dateien weiterhin nur, wenn *neu + existiert schon*.
- **Prüfung 3 – vier Fälle getestet:**
  - A: Übergabedatei als *Änderung* + echte neue Datei → Übergabedatei
    entfernt, neue Datei bleibt ✓
  - B: nur Übergabedatei → Early-Return ✓
  - C: ganz neue Datei, die es nicht gibt → **unverändert** ✓
  - D: neue Datei, die es schon gibt → entfernt ✓
- **Hinweis zu „Version 23/24 sind weg“:** Die Versionen 19–27 gehörten
  zum **verworfenen Redesign** und wurden mit auf `ref-gui` zurückgesetzt.
- **Version auf 23 erhöht.**

**14.11.2026 – Diagnose: Version und Ordner jetzt immer sichtbar**
- **Beweis für alte Version:** Die Meldung enthielt keinen Filter-Hinweis.
  Da **kein** roter Versionsbalken erschien, waren GUI und Helfer *gleich alt*.
- **Fix (Version 22):** Der Modus-Banner zeigt jetzt **immer** Version des
  Helfers und der GUI sowie den Ordner (`/api/status` liefert `HERE`).
- **Ablauf zum Aktualisieren:** Beenden-Knopf → neueste ZIP holen → Ordner
  überschreiben → Start-Knopf → Version und Ordner im Banner prüfen.
- **Version auf 22 erhöht.**

**14.11.2026 – Filter auch beim ÜBERNEHMEN**
- **Ursache:** Der Patch lag noch in alter Fassung im Postfach. Der Filter
  griff nur beim Eintragen, beim Übernehmen gab es ihn nicht.
- **Fix:** `act_uebernehmen` filtert jetzt **vor** `git apply --check`,
  inklusive Early-Return, wenn der Patch nur Doppelungen enthält.
- **Damit ist der aktuelle Postfach-Patch sofort übernehmbar.**
- **Version auf 21 erhöht.**

**14.11.2026 – Veraltete Etappe-1/2-Meldungen bereinigt**
- Die Meldung war eine statische Fußnote im Einstellungen-Reiter und wurde
  mit dem Referenzstand unverändert übernommen.
- **Alle sichtbaren Relikte bereinigt:** Einstellungs-Fußnote, Pfade-Kleintext,
  etaBadge, Start-Protokoll, Dateikopf- und Abschnittskommentare.
- **Version auf 20 erhöht.**

**14.11.2026 – „Betroffen: docs/UEBERGABE.md“ – Ursache behoben**
- **Ursache:** Die KI erzeugt `docs/UEBERGABE.md` und packt sie in den Patch.
  Beim Besitzer existiert die Datei schon. Der Patch führt sie als *neu* ein
  → `apply --check` scheitert.
- **Verhinderung eingebaut (`_filtere_bereits_vorhandene`):** Diff-Blöcke für
  Dateien, die der Patch als neu einführt und die es im Projekt schon gibt,
  werden entfernt – mit sichtbarem Hinweis.
- **Regel für künftige KI-Sitzungen:** `docs/UEBERGABE.md` gehört **nie in
  einen Patch**.
- **Version auf 19 erhöht.**

**13.11.2026 – REDesign verworfen: Zurücksetzung auf die Referenz `ref-gui`**
- **Das gesamte Cyberpunk-/Kreis-Redesign (Versionen 19–27) ist verworfen**:
  Hülle, Neon-Farbwelt, Scanlines, Keil-Menü, HUD-Ringe, Bänder-Kreis,
  Fächer-Icons, Denkfenster-Neuordnung.
- **Wurzel und Klon `gui`** stehen wieder auf `ref-gui`.
- **Diese HISTORIE bleibt erhalten**, damit der gesamte Entwicklungsweg
  dokumentiert bleibt.
- **Version steht wieder auf 18.**

**12.11.2026 – Kreis maximal groß, dicke Bänder, Fächer-Icons**
- **Ehrliche Grenzen:** langer Text ist auf Bögen kaum lesbar; die Mitte war
  zu groß, dadurch die Ringzone schmal.
- **Kreis jetzt maximal groß:** Stage von 560 → **680 px**, Innen-Disc von
  r118 → **r86**, Ringzone von 72 → **98 px**.
- **Bänder deutlich dicker:** Höhe 8 → **13**, Abstand 2.4 → **3**.
- **Icons fächerförmig statt als Säule:** Jedes Knopf-Band bekommt seinen
  eigenen Winkel-Offset.
- **Denkfenster wandert unter den Kreis** (breit, mit internem Scroll).
- **Version auf 27 erhöht.**

**12.11.2026 – Quadranten mit dünnen Bändern (Vorlage „Bild 2“)**
- **Neue Segment-Generierung:** Jeder Quadrant wird aus **dünnen Bändern**
  aufgebaut, radial bündig von innen nach außen.
- **Pro Quadrant mindestens 6 Bänder:** die **Knöpfe belegen die inneren
  Bänder**, die restlichen Bänder sind Deko-Bänder.
- **Höhe und Breite variabel** über Konstanten (`BAND_DICK`, `BAND_LUECKE`).
- **Icons** zentriert auf den Knopf-Bändern, Hover hebt das Band hervor.
- **„ODER“-Gabelung** als radialer Versatz mit ODER-Label.
- **Neu:** Der nächste große Knopf markiert sein Band (`markiereNaechstes`).
- **Version auf 26 erhöht.**

**11.11.2026 – Die GUI WIRD das Kreismenü**
- **Neue Hauptfläche `stage`:** Innen-Disc, **vier Gruppen-Ringe**,
  **Statusring außen**.
- **Jeder Ring = eine Gruppe, jedes Segment = ein Knopf** mit individuellen
  Segmentbreiten und Gruppenfarben.
- **„ODER“-Gabelung** im Sichern-Ring.
- **Segmente tragen echte Icons**, Hover-Texte und `[data-act]` bleiben.
- **Mitte:** runder Hauptknopf und eckiges Denkfenster.
- **Bewahrt:** Kopf, Modus-/Referenz-Banner, Stationsstraße, Reiter,
  Fußzeile, alle Reiter-Inhalte und Endpunkte.
- **Version auf 25 erhöht.**

**11.11.2026 – Kreisform korrigiert**
- **Ursache:** Rundung als absolute Pixel (`160px / 92px`), bei wachsender
  Höhe nur gerundete Ecken statt Oval.
- **Fix:** prozentuale Kreisform `border-radius: 50% / 26%`.
- **Version auf 24 erhöht.**

**Offene Diagnose „Patch zu GitHub“**
- „Patch eintragen/ablegen“ schreibt **nur ins Postfach**; „Patch zu GitHub“
  führt **sechs Prüfungen/Schritte** aus (Gist lesen → Prüfsumme → Basis →
  `apply --check` → git-Zweig/Anwenden → tsc+Build → PR eröffnen).
- Häufigste Ursachen: Basis/`apply --check`, Projekt-Pfad kein Repository,
  `gh` fehlt für die PR-Eröffnung.
- **Vom Besitzer erbeten:** konkreter Fehler-Text oder Screenshot.

**10.11.2026 – Gesamtes GUI als Kreisform**
- **Hülle kreisförmig** (`border-radius: 160px / 92px`).
- **Außenring als Kennzeichnung:** Demo gelb, echter Modus Cyan.
- **Mittelteil in der Mitte:** großer Knopf und Denkfenster vertikal zentriert.
- **Version auf 23 erhöht.**

**10.11.2026 – Echtes Kreismenü als SVG-Keile**
- Vier **keilförmige Segmente** als SVG-Annulus-Pfade, mit Lücken, Nummern
  und Namen im Segment.
- **Jeder Keil trägt seine Gruppenfarbe**; gewählter Keil glüht.
- **Mitte:** Ampelpunkt und Hinweistext.
- **Aufteilung:** links Kreismenü, Mitte Aktion + Denkfenster, rechts Knöpfe.
- **Version auf 22 erhöht.**

**10.11.2026 – HUD-Aufteilung nach den Ring-Bildern**
- **Neue Aufteilung (drei Spalten):** links Vorbereitung/Status, Mitte HUD
  mit großem Knopf und Denkfenster, rechts Sichern/Wartung.
- **Nummern 01–04 an den Labels.**
- **Radialmenü entfällt funktional**, Kreis-Idee lebt in der Aufteilung weiter.
- **Version auf 21 erhöht.**

**09.11.2026 – Futuristisches Panel mit Radialmenü**
- **Radialmenü** als linke Spalte, vier Hauptbereiche als Kreis, Ampelpunkt
  in der Mitte.
- **Klick auf ein Segment** zeigt genau diese Gruppe mit ihren Knöpfen.
- **Automatische Folge:** Nach jeder Aktion springt das Menü auf den Bereich
  des nächsten Schritts.
- **Layout neu (drei Spalten):** Radial links · Denkanzeige Mitte · Gruppen rechts.
- **Version auf 20 erhöht.**

**09.11.2026 – Cyberpunk-Redesign umgesetzt**
- **Farbwelt:** tiefes Schwarz mit Scanlines, Cyan als Haupt-Neon, Violett
  als Sekundärschimmer.
- **Klammerähnliche Symbole entfernt**, Neon-Konturen beim Hover.
- **Gruppen** mit Neon-Rahmen, Labels in Monospace.
- **Keine Funktion angefasst:** Hover-Texte, Ampel, Prüfungen, Haken,
  Reihenfolge, „oder“-Trennlinie, Badges, Endpunkte bleiben.
- **Version auf 19 erhöht.**

**08.11.2026 – Referenz `ref-gui` gesichert, Klon `gui` angelegt**
- **Ordner `ref-gui/`** = eingefrorener Referenzstand.
- **Ordner `gui/`** = Klon für künftige Weiterarbeitung.
- **Referenz-Banner** in der Vorschau.
- **Offener Auftrag nach Go:** Redesign auf „edlen futuristischen Look“.
- **Version auf 18 erhöht.**

**08.11.2026 – Gruppen als Karten mit Gruppenfarbe**
- **Jede Gruppe** bekommt einen dünnen Rahmen in ihrer Gruppenfarbe.
- **Farben innerhalb einer Gruppe einheitlich** an Rahmen und Symbol.
- **Gruppenüberschriften heller** und hellere Rahmenlinie darunter.
- **Version auf 17 erhöht.**

**07.11.2026 – „oder“-Trennlinie in der Gruppe Sichern**
- Zwischen **Patch eintragen** und **Offene Änderungen speichern** steht eine
  Trennlinie mit „oder“ – zwei alternative Eingänge.
- Beide Wege münden bei `Patch zu GitHub → Patch lokal nach Hause`.
- **Version auf 16 erhöht.**

**07.11.2026 – Zurück zu normalen Hover-Texten**
- Das eigene Tooltip-Fenster wurde **wieder entfernt**: alle `data-tip`
  zurück auf `title`, Tooltip-Logik und CSS entfernt.
- **Version auf 15 erhöht.**

**07.11.2026 – Eigenes Tooltip-Fenster statt Browser-Popover**
- **Alle 27 Hover-Texte** von `title` auf `data-tip` umgestellt.
- **Eigene Tooltip-Logik** mit Verzögerung und Umklappen am Bildschirmrand.
- **Gewinn:** HTML-Tip mit farbigen Wortmarken.
- **Version auf 14 erhöht.**

**07.11.2026 – Wortmarken ohne Rahmen**
- Die Wortmarken „Ins Postfach legen“ und „Patch zu GitHub“ stehen nur noch
  als **farbige fette Schrift** – Rahmen und Hintergrund entfernt.
- **Version auf 13 erhöht.**

**07.11.2026 – Speichern-Knopf in die Gruppe Sichern, farbige Wortmarken**
- **„Offene Änderungen speichern“ wandert** direkt unter „Patch eintragen“
  in die Gruppe *Sichern*.
- **Vorbereitung** enthält: Eröffnungstext kopieren, Projekt Prüfbericht holen.
- **Hovertext des Speichern-Knopfs** erklärt lokalen Commit ohne Upload.
- **Farbige Wortmarken** in der sichtbaren Unterzeile.
- **Version auf 12 erhöht.**

**07.11.2026 – „Stand prüfen“ → „Projekt Prüfbericht holen“**
- **Umbenennung und Versetzung** an Platz 2 der Vorbereitung.
- **Handlungs-Knopf „Bericht kopieren“ entfernt** (war doppelt). Der
  Kopier-Knopf in der Denkanzeige blendet sich nach erfolgreicher Prüfung ein.
- **Version auf 11 erhöht.**

**07.11.2026 – „Spiel beenden“, Pull-Request-Erklärung, Gist-Formulierung**
- **Neuer Knopf „Spiel beenden“** in Wartung: beendet nur ein vom Helfer
  gestartetes Spiel, schließt den Tab und meldet ehrlich, falls keins lief.
- **Mouseover „Patch zu GitHub“** erklärt Pull Request als **Freigabe**.
- **Version auf 10 erhöht.**

**07.11.2026 – Mouseover radikal gekürzt**
- Alle Handlungs-Mouseover auf **zwei Sätze** gekürzt, mit **Ort in Klammern**.
- Kein `title` mehr als 180 Zeichen.
- **Ablauf im Fenster dokumentiert:** KI schickt Patch → Patch eintragen →
  Patch zu GitHub → Patch lokal nach Hause.
- **Version auf 9 erhöht.**

**06.11.2026 – Umbenennung, Schwarz/Grau-Design, Reihenfolge**
- **„Fremden Patch ablegen“ → „Patch eintragen“**.
- **Design auf Schwarz/Grautöne**, Ausnahmen: grüne Haken, farbige Umrandungen,
  farbige Symbole; funktionale Ampel-/Statusfarben bleiben.
- **Reihenfolge Gruppe Sichern getauscht:** zuerst Patch eintragen, dann Ins
  Postfach legen.
- **Mouseover** erklärt main-Stand und lokalen Commit ohne Upload.
- **Version auf 8 erhöht.**

**06.11.2026 – „Fremden Patch ablegen“ + Gruppen-Neustruktur**
- **Neuer Knopf** mit Textfeld UND „Datei wählen“, Live-Prüfung von diff,
  betroffenen Dateien, json und Basis. json mit Basis ist Pflicht.
- **Endpunkt `patch-einfuegen`**, Prüfsumme im Helfer selbst berechnet.
- **Gruppen-Neustruktur:** Vorbereitung (blau), Status (türkis), Sichern
  (violett), Wartung (grau).
- **lokal/online sichtbar:** Badge und Knopfform (lokal rund, online eckig).
- **Version auf 7 erhöht.**

**06.11.2026 – Doppelte Meldung bereinigt**
- Das Präfix „Der Patch passt nicht zu deinem Stand“ stand zusätzlich zum
  Klartext von `git_klar()` → Satz doppelt. Beide Stellen liefern jetzt nur
  noch einen sauberen Satz.
- **Version auf 6 erhöht.**

**04.11.2026 – Versionsregel nachgeholt**
- **Befund:** `HELPER_VERSION`/`GUI_VERSION` blieben seit vielen Änderungen
  gleich; der Abgleich erkannte gleich alte Kopien nicht.
- **Regel:** Bei **jeder** Änderung an `leitstand.py` oder `leitstand.js`
  werden beide Versionen gemeinsam erhöht.
- **Version auf 5 erhöht.**

**04.11.2026 – Übersetzungstabelle erweitert**
- **Fix in `git_klar()`:** Muster für deutsche und englische Git-Fehler,
  betroffene Dateien automatisch nennen, Hinweis-Kaskaden abschneiden.
- **Getestet** mit Screenshot-Text und weiteren Fällen.

**04.11.2026 – Jeder Knopf erklärt sich + Handlungen gruppiert**
- **Mouseover (`title`) an allen Knöpfen/Links** – kurz, Sinn + Funktion.
- **Handlungen nach Nutzungsreihenfolge gruppiert und sortiert**.
- `check.sh`-Ausgabe bleibt bewusst lang.

**04.11.2026 – „Abbrechen“ → „Vorgang abbrechen“**
- Beide Abbrechen-Knöpfe einheitlich benannt, gleiche Funktion, ein Name.
- **Mouseover** erklärt: Prüfungen stoppen sofort; schreibende Aktionen
  beenden ihre geprüften Schritte, damit nichts halb bleibt.
- Der Abbrechen-Knopf im Bestätigungs-Dialog bleibt „Abbrechen“.

**04.11.2026 – Redundanter Knopf entfernt + Abbrechen-Hinweis**
- **„Erneut versuchen“ entfernt**, identisch mit „Stand prüfen“.
- **„Abbrechen“ ohne laufende Aktion:** erklärende Zeile direkt in der
  Denkanzeige statt leicht zu übersehendem Toast.

**04.11.2026 – Knopf und Export in „Entwickler-Info“ umbenannt**
- „Übergabe (TXT)“ → **„Entwickler-Info (TXT)“**, einschließlich Dateiname,
  Denkanzeige, Protokoll, Toast und Export-Markierungen.
- Endpunkt `/api/uebergabe` bleibt unverändert.

**Diagnosehilfe für „Meldung trotz Update noch roh“:**
- Die Alt-Meldung existiert im aktuellen Code nicht mehr. Wer sie sieht,
  läuft mit einer alten `leitstand.py`. Suchprobe: `git_klar`.

**04.11.2026 – Gutachter-Bericht umgesetzt (Punkte 1–5)**
1. **Git-Meldungen übersetzen** (`git_klar()`): Mapping typischer Fehler →
   Klartext + Lösung, Kaskaden abschneiden.
2. **`git apply --check` VOR `git am` + Rollback:** Bei Nicht-Anwendbarkeit
   keine Veränderung; bei `am`-Fehlschlag `--abort` und Rückkehr zum Ausgangs-Branch.
3. **`git_geraeumig()`** räumt Reste eines gesteckten `git am` auf.
   Identitäts-Fallback auch für `am --abort` und Commit.
4. **Doppelte Fehlerzeile behoben** (`runWrite`): nur noch eine Abschlusszeile.
5. **Prüfung schon beim Ablegen** gezielt für die Übergabedatei, ohne legitime
   neue Dateien allgemein zu blockieren.

**04.11.2026 – „Alles per Knopf, kein Terminal“**
- **Neuer Knopf „Offene Änderungen speichern“:** alle offenen Änderungen als
  **lokalen Commit**, ausdrücklich kein Push/Upload, mit Bestätigungsdialog.
- **„Stand sichern“ speichert die Übergabedatei selbst** (add + commit),
  wodurch der Zirkel „sichern → nicht sauber“ entfällt.
- **Lösungsmeldungen ohne Terminal** verweisen auf den Knopf.

**04.11.2026 – Zirkel „Stand sichern → nicht sauber“**
- **Fehlerbild:** „Patch ablegen“ meldete genau die Datei als offen, die
  „Stand sichern“ selbst erzeugt hatte.
- **Meldung selbsterklärend**, nennt konkreten Pfad und Lösung.
- **Bug behoben:** `git status --porcelain` jetzt mit `-uall`, damit echte
  Dateipfade statt zusammengefasster Ordner gemeldet werden.

**04.11.2026 – Endpunkt-Mismatch „unbekannte Aktion“**
- **Ursache:** GUI rief `/api/leeren`, Helfer kannte nur `postfach-leeren`.
- **Fix 1:** Mapping `API_KEY` in `leitstand.js`.
- **Fix 2:** `helferHint` unterscheidet gleiche Version (zweite Kopie?) und
  Versionsunterschied (neu starten).
- **Regressionstest:** Abgleich aller `fetch("/api/…")`-Pfade gegen ACTIONS.

**04.11.2026 – Knopf „Alten Patch entfernen“**
- Alle Handlungen bleiben aktiv; der große Knopf ist die nächste Aktion.
- **Neue Helfer-Aktion `postfach-leeren`:** löscht nur `aktuell.patch` +
  `aktuell.json`, nie die Knopf-Dateien, prüft vorher den Gist-Inhalt.
- Lösungsmeldung beim veralteten Patch verweist auf diesen Knopf.

**04.11.2026 – Fehlermeldungen erklären sich selbst**
- Jede Fehlermeldung nennt **Bedeutung** und **Lösung**, plus klickbaren Link
  wo sinnvoll.
- Fälle: nicht sauber, veralteter Patch, Prüfsumme falsch, Token fehlt,
  Repo fehlt.
- **Bug behoben:** Fehlgeschlagener `git status` wird nicht mehr als offene
  Datei ausgegeben; Porcelain-Pfade korrekt abgetrennt.

**04.11.2026 – Übergabe-Knopf (TXT-Export)**
- Neuer Knopf **„Übergabe (TXT)“** in der Fußzeile.
- Erzeugt Zweck, Sicherheitshinweise, Stand, Historie und **vollständigen
  Code** aller Dateien (ZIP-Bytes maskiert). Endpunkt `/api/uebergabe`.
- **Regel ergänzt:** HISTORIE.md bei jeder Änderung fortschreiben.

**04.11.2026 – Fixes im Zug des Übergabe-Knopfes**
- Schreibfehler in der Überschrift korrigiert (`SICHEITSHINWEISE` →
  `SICHERHEITSHINWEISE`).
- **Signal-Handler-Deadlock behoben:** kein `httpd.shutdown()` aus demselben
  Thread; Aufräumen + direktes Beenden.

**04.11.2026 – „Stand sichern“ an Bare-Spiegeln**
- **Ursache:** Der Spiegel ist ein **Bare-Repository** ohne Arbeitsverzeichnis;
  `git reset --hard` scheitert dort.
- **Fix:** `act_sichern` erkennt bare und aktualisiert per
  `fetch origin +refs/heads/main:refs/heads/main`.
- Fehlende Sicherung und „kein Git-Repository“ werden sauber benannt,
  `docs/` wird beim Schreiben angelegt.
- **Getestet** an einem echten Bare-Spiegel: `ok: True`, „Stand gesichert“.

---

**07.11.2026 – Version 23.35 · Sicherheits- & Zuverlässigkeits-Überarbeitung (Prioritäten 1–4)**
- **Priorität 1 (Datenverlust & Überschreibschutz):**
  - `act_ablegen`: prüft vor dem Schreiben, ob bereits ein `aktuell.patch` im Gist liegt, und fragt über den neuen Knopf „Trotzdem überschreiben“ (`force: true`) explizit nach. Bündelt außerdem alle lokalen Commits seit `origin/main` (`git format-patch origin/main..HEAD`) statt nur `-1`.
  - `act_offene_speichern`: blockiert `git add -A`, falls ungetrackte/geänderte Geheimdateien (`.env*`, `*token*`, `*.pem`, `*.key`, `credentials.json`) im Arbeitsverzeichnis liegen.
  - `act_sichern`: prüft nicht-bare Spiegel vor `git reset --hard` auf ungespeicherte Änderungen und meldet lokale Commits vor `origin/main`.
- **Priorität 2 (Netzwerkfehler & echter Token-Test):**
  - Einheitlicher `_gist_request`-Wrapper fängt `HTTPError` (401/403/404 mit Klartext-Lösung), `URLError` (Offline) und `TimeoutError` sauber ab, statt HTTP-500-Ausnahmen zu werfen.
  - Neuer Endpunkt `POST /api/token-test` prüft den Token live gegen die GitHub-Gist-API und warnt bei unnötigen `repo`-Scopes; `POST /api/token-loeschen` entfernt den Token lokal.
- **Priorität 3 (Token-Maskierung, CSRF-Schutz & Offline-GUI):**
  - `scrub()` maskiert neben `gh[pousr]_` jetzt auch Fine-Grained PATs (`github_pat_…`) sowie das Sitzungstoken und wird an alle `run()`-Aufrufe durchgereicht.
  - `Handler` erzwingt `Host`-/`Origin`-Prüfung sowie ein pro Start erzeugtes `X-Leitstand-Token` (`<meta name="leitstand-csrf">`); `spiel` und `spiel-stop` auf `POST` umgestellt.
  - Ungenutztes externes Tailwind-CDN-Skript aus `index.html` entfernt.
- **Priorität 4 (UI-Bereinigung, Ablauf, Live-Einstellungen & Altlasten):**
  - Korrupte Beschriftungen in `index.html` korrigiert; Fußzeile `#pfadPostfach` dynamisch aktualisiert; `STANDARD_KETTE` und Folgeschritte auf den logischen Ablauf (`prüfen → lokal speichern → Postfach → KI-Übergabe → PR → nach Hause`) ausgerichtet; `act_uebernehmen` wechselt nach PR-Erstellung wieder auf `main` zurück.
  - Live-Speichern der Pfade/Einstellungen (`POST /api/einstellungen`) im Reiter „Einstellungen“ ergänzt.
  - Altlasten entfernt (`KNOPF`-Hook `~/adventshaus-knopf.sh`, ungenutztes Feld `ablage`, tote JS-Funktion `entwicklerInfoOhneHelfer`, keine `.pid`-Datei im Paket).

---

**07.11.2026 – Version 23.36 · Ehrliche Meldung bei git-ignorierten Dateien (Live-Test-Nachbesserung)**
- **Gefunden im gemeinsamen Live-Test:** Eine git-ignorierte Datei (z. B. `.env.test`) ist im normalen `git status` unsichtbar; „Offene Änderungen speichern" meldete irreführend „Alles gespeichert – keine offenen Änderungen", obwohl die Datei auf der Platte lag.
- **Fix in `act_offene_speichern`:** Bei leerem Git-Status zusätzlich `git status --porcelain --ignored` prüfen; liegen ignorierte Dateien vor, wird das ehrlich gemeldet („Git sieht keine speicherbaren Änderungen. N ignorierte Datei(en) liegen bewusst unverfolgt im Projektordner: …").
- Der Geheimnis-Schutz (Blockade von `.env*`, `*token*`, `*.pem`, `*.key` …) bleibt für alle git-sichtbaren Dateien bestehen.

---

**07.11.2026 – Version 23.37 · Beendigungsfenster im Leitstand-Design (Live-Test-Nachbesserung)**
- Das Beendigungsfenster von stop.sh (zenity/kdialog/xmessage) wird jetzt im Leitstand-Look angezeigt: dunkler Hintergrund (#151619), heller Text (#ececee), abgerundeter dunkler OK-Knopf, schmalere Breite (280 statt 340 px) – falls das GTK-Frontend CSS unterstützt, sonst unverändert.
- Doppel-Popups bei ESC behoben: zenity, kdialog und xmessage zeigen je genau ein Fenster (vorher fiel ein ESC-Abbruch in das nächste Frontend durch).

---

**07.11.2026 – Version 23.38 · Kette-Auswahl oben + logische Gruppenreihenfolge (Dopplungen erlaubt)**
- **Neue Kette-Leiste oben** (unter dem Modus-Banner): die vier Ketten „Übergabe / Sicherung / Prüfung / Wartung" lassen sich per Chip wählen; die aktive Kette ist **oben UND an der Gruppenüberschrift** markiert (inkl. „läuft · Schritt X/Y"). Ein zweiter Klick auf die aktive Kette beendet sie.
- **Gruppenreihenfolge** in jeder Gruppe jetzt exakt der Arbeitsfluss, Dopplungen erlaubt: „Stand prüfen" beginnt die Ketten 01, 02 und 03; „Alten Patch entfernen" schließt die Kette 01 ab (Duplikat aus 04).
- **Denkfenster-Farben** neu: positiv = grün, Hinweise = blau, Warnungen/Fehler = rot.
- **JETZT-DRAN-Logik unverändert** (zeigt immer den nächsten Schritt der aktiven Kette bzw. der Standardreihenfolge); Bestätigungs-Dialoge vor schreibenden Aktionen bleiben bestehen.

---

**07.11.2026 – Version 23.39 · „Lokal aktualisieren" – Tagesablauf ohne Terminal**
- **Neuer Knopf „Lokal aktualisieren"** (Gruppe 02, zwischen „Ins Postfach legen" und „Patch lokal nach Hause"):
  `git pull --ff-only origin main` – übernimmt neue GitHub-Commits (z. B. nach Merge eines PRs)
  in den lokalen Arbeitsordner. Nur bei sauberem Stand (sonst Hinweis: erst speichern);
  bei Divergenz ehrlicher Abbruch statt automatischem Zusammenführen.
- In die Standardreihenfolge und in Kette 02 eingebunden: … → zu GitHub → **lokal aktualisieren** → nach Hause.
- Damit ist der gesamte Tagesablauf (prüfen → speichern → Postfach → KI → PR → Merge im Browser
  → **lokal aktualisieren** → nach Hause) vollständig ohne Terminal möglich.

---

**07.11.2026 – Version 23.40 · „Zweige aufräumen", „Neu starten"-Knopf, Abgleich in „Stand prüfen"**
- **Neuer Knopf „Zweige aufräumen"** (Gruppe 04): `git fetch --prune`; löscht NUR gemergte
  ki/*-Zweige (lokal mit -d, remote mit --delete); nicht gemergte Zweige werden nur
  aufgelistet, nie berührt → kein Datenverlust möglich. Damit ist A1 (Zweig-Aufräumen)
  komplett ohne Terminal möglich.
- **Neuer Desktop-Knopf „Adventshaus · Leitstand neu starten"** (neustart.sh): beendet
  ALLE Helfer (auch Zombies aus gelöschten Ordnern) und startet den aus dem Paket-Ordner.
  Damit ist der A2-Incident („start.sh startet nicht" / JSON statt GUI) ohne Terminal
  beherrschbar. install-desktop.sh legt jetzt drei Icons an.
- **„Stand prüft" zeigt zusätzlich den Abgleich lokal vs. GitHub** (git fetch +
  rev-list --left-right --count) mit Lesart: „(0 0) identisch", „(0 N) lokal N vor",
  „(N 0) lokal N hinter (→ Lokal aktualisieren)", „(N M) DIVERGENZ – nichts pushen".
  Damit ist A3 (Stand-Check bei Zweifeln) im GUI-Knopf enthalten.

---

**07.11.2026 – Version 23.41 · Statusbalken statt drehendem Symbol**
- Im Denkfenster ersetzt ein animierter **Statusbalken** (gestreift, türkis, läuft
  während jeder Aktion und blendet danach aus) das bisherige drehende Spinner-Symbol.
  Status-Text und Ampel bleiben unverändert.

---

**07.11.2026 – Version 23.42 · Werkzeugleiste (Start/Neu starten/Beenden) statt 3 Desktop-Icons**
- Neue **Werkzeugleiste** oben in der GUI (unter der Kette-Leiste): kompakte Leiste mit
  den drei System-Knöpfen „▶ Starten" (Status-Hinweis), „↻ Neu starten" und „■ Beenden"
  – jeweils mit Inline-Bestätigung („Wirklich? Ja/Nein") vor den schreibenden Aktionen.
- Neue Helfer-Endpunkte: POST /api/beenden (sauberer Ausstieg, PID-Datei aufgeräumt) und
  POST /api/neustart (startet den Helfer aus dem Paket-Ordner neu, Seite lädt selbst neu).
- **install-desktop.sh legt jetzt genau EIN Icon** an und entfernt die alten
  „beenden"/„neustart"-Icons (Aufräumen geschehen).
- start.sh öffnet das Fenster bevorzugt **ohne Browser-Chrome** (chromium/google-chrome
  --app, falls vorhanden), sonst wie bisher über den Standardsbrowser.

---

**07.11.2026 – 23.42 (Namensänderung):** Die GUI heißt fortan **„Projektmanager"**
(Fenster-Titel, Kopfzeile, Dialoge, Desktop-Icon, Meldungen). Dateinamen, Ordner,
ZIP-Name und der Projektordner des Spiels bleiben unverändert.
Hinweis: Mit Librewolf/Firefox als Browser bleibt die Browser-Menüleiste sichtbar
(kein App-Modus); Chromium/Chrome/Edge/Brave/Vivaldi daneben installiert →
sauberes Fenster ohne Menüleiste, automatisch erkannt.

---

**07.11.2026 – 23.42 (Umbenennung „Leitstand" → „kipm"/„Projektmanager"):**
Dateien: kipm.py, kipm.js, kipm.pid · Header: X-Kipm-Token · CSRF-Name: kipm-csrf ·
User-Agent: Adventshaus-Kipm · Desktop-Icon: kipm.desktop · ZIP: adventshaus-kipm-<Version>.zip.
GUI-Name: „Projektmanager". Die historische Bezeichnung „Leitstand" bleibt in dieser
Chronik als Geschichte erhalten — im produktiven Code und in allen Namen nicht mehr.

---

**07.11.2026 – 23.42 (Edge-Case-Fix „Ins Postfach legen"):** Lag der lokale Stand
gleich mit GitHub (0 Commits voraus), wurde zuvor der HEAD-Commit als Patch exportiert —
bei einem Merge-Commit ohne Diff-Teile blieb ein leerer „0-Dateien"-Patch im Briefkasten.
Jetzt meldet der Helfer stattdessen: „Nichts abgelegt – lokal liegt nichts vor GitHub".

---

**07.11.2026 – 23.42 (Layout: Knöpfe in Bedienreihenfolge):** Die vier Spalten folgen
jetzt der logischen Bedienfolge im Leserauftritt (oben links → oben rechts → unten
links → unten rechts): 01 Sichern des Projektes (prüfen → speichern → Postfach),
02 Übergabe an die KI (Starttext → Bericht → Patch holen → zu GitHub),
03 Abschluss und Status (aktualisieren → nach Hause → Spiel ansehen),
04 Wartung (entfernen → Zweige → abbrechen → beenden). Der JETZT-DRAN-Knopf und die
Ketten bleiben unverändert — der Nutzer wählt zwischen großem Knopf und Spalten-Klick.

---

**07.11.2026 – 23.42 (Korrektur, ZWANG des Besitzers bis auf Widerruf):**
Übergabe an die KI = oben LINKS (blau), Sichern des Projektes = oben RECHTS (violett).
„Patch holen" gehört in Sichern (KI-Liefer-Moment, nicht in die Übergabe). Reihenfolge
Sichern wie besprochen: prüfen → speichern → Ins Postfach legen → Patch holen →
Patch zu GitHub → Lokal aktualisieren → Patch lokal nach Hause.
01 Übergabe: prüfen → Eröffnungstext → Bericht. 03 Status: prüfen → Spiel ansehen.
04 Wartung unverändert.

---

**07.11.2026 – 23.42 (Umbenennung kipm → projektmanager):** Ordner `projektmanager-23.42`,
Dateien `projektmanager.py`/`projektmanager.js`/`projektmanager.pid`, Header
`X-Projektmanager-Token`, CSRF-Name `projektmanager-csrf`, User-Agent
`Adventshaus-Projektmanager`, Desktop-Icon `projektmanager.desktop` (räumt alle
älteren Icons automatisch auf), ZIP `projektmanager-23.42.zip`. GUI-Name bleibt
„Projektmanager". Regel: Ordner niemals umbenennen/verschieben, während der Helfer
läuft (sonst: „index.html nicht gefunden") — erst `pkill -f projektmanager.py`.


## 23.42 · Arbeitsrevision pfad-diagnose.1 (nicht auf GitHub veröffentlicht)

Ausgangspunkt: Chihuaua/kipm, Commit 379c824217ac3ac5d7059cfef740f6d30eefd0e1.
Der GitHub-Referenzklon bleibt unverändert. Keine Änderungen an GUI-Anordnung,
Knopfbeschriftungen, Aktionsreihenfolge, CSS, JavaScript oder Dateinamen.

- Der Helfer prüft index.html vor dem Binden am eigenen Dateiordner.
- Fehlende GUI-Dateien werden mit vollständigem erwartetem Pfad und Prozess-PID gemeldet.
- Ein belegter Port wird nicht mehr als erfolgreicher Helferstart ausgegeben.
- Andere Bindefehler werden ehrlich gemeldet; kein Browser wird fehlgeleitet.
- Der Status enthält GUI-Pfad, Verfügbarkeit und Arbeitsrevision; GUI/Helfer bleiben 23.42.
- Ein bereits laufender alter Prozess übernimmt diese Korrekturen erst nach einem Neustart.
- Die sichtbare GUI und projektmanager.js bleiben bytegleich zur GitHub-Vorlage.


## 23.42 · Arbeitsrevision uebergabe-pruefung.1 (nicht auf GitHub veröffentlicht)

- Exakte Patch-Prüfsummen; keine stille Neuberechnung und kein Beschneiden der Patch-Bytes.
- Vollständiges Nachladen abgeschnittener Gist-Dateien über raw_url; Upload wird zurückgelesen.
- Keine stillen Dateifilter; Mail-Patches und Plain-Diffs werden passend verarbeitet.
- Basisprüfung mit kurzen und vollständigen Hashes gegen den tatsächlich entfernten main-Stand.
- Keine Zweig-Überschreibung; Buildfehler ohne Push; PR-Fehler ohne falsche Erfolgsmeldung.
- Neue Patch-Dateien werden in der Diagnose als neu vorgesehen statt als Projektfehler gemeldet.
- Übergabenotiz ist idempotent und erzeugt keinen automatischen Commit mehr.
- Direkter HTTPS-Import von Patch-ZIPs und Raw-Patches mit Größen- und Adressprüfung.
- Offline-Regressionstests mit lokalen Repositories und simuliertem gh; keine echten GitHub-Schreibzugriffe.


## 23.42.03 — fortlaufende Versionsnummer und geprüfte Übergabe

- Aktive Versionierung beginnt bei 23.42.01; weitere Änderungen folgen als 23.42.02, 23.42.03 usw.
- GUI_VERSION, HELPER_VERSION und GUI_HINT zeigen dieselbe aktive Version.
- Versionsvergleich prüft alle Nummernsegmente statt parseFloat.
- Der bestehende Installationsordner projektmanager-23.42 bleibt bewusst stabil.
- Enthält die zuvor offline geprüften Pfad- und Übergabekorrekturen; keine echten GitHub-Schreibzugriffe bei der Prüfung.


## 23.42.02 — lokale Patch-ZIPs und Bereits-Enthalten-Diagnose

- Datei wählen akzeptiert zusätzlich .zip und übermittelt das Archiv binärgenau als Base64.
- Der Helfer extrahiert genau aktuell.patch und aktuell.json ohne Textumwandlung.
- Bereits in GitHub-main enthaltene Plain-Diffs werden erkannt und nicht erneut eingetragen.


## 23.42.03 — identische Postfach-Patches erkennen

- Vor dem Ablegen/Eintragen wird der vorhandene Postfach-Patch bytegenau verglichen.
- Identischer Patch mit gleicher Basis: Hinweis „liegt bereits im Postfach“, keine Schreibaktion.
- Anderer Patch: Blockade mit alter/neuer Prüfsumme und Basis statt pauschaler Belegt-Meldung.
