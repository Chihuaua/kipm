(function(){
"use strict";
/* ============================================================
   Adventshaus · Projektmanager: Oberfläche mit Demo- und Echtbetrieb
   ============================================================ */

var GUI_VERSION = "23.42.09";
var EROEFFNUNG = "# KI-START – Little Computer Luni · Das Adventshaus\n\n**Die einzige Pflicht-Lektüre für jede KI-Sitzung.** Schlank gehalten; README,\nBerater-Info, Spielkonzept und Merkzettel nur bei Bedarf. Diese Datei ist die führende\nQuelle; der Eröffnungstext der Projektmanager-GUI wird daraus erzeugt.\n\n- **Repo:** https://github.com/Chihuaua/adventshaus\n- **Basis:** neuester Commit auf `main`. Kein Tag, außer ausdrücklich genannt (Tags hinken hinterher).\n- **Eröffnungstext:** nur im Projektmanager („Eröffnungstext kopieren“). Im Spiel gibt es keine Übergabe-Leiste mehr.\n\n## Projekt in einem Satz\nRuhiges Beobachtungsspiel im Stil von *Little Computer People* (1985). Luni lebt in\neinem Haus (4 Ebenen) in Echtzeit (Europe/Berlin). Web ist der Prototyp, **Wii ist das\nEndziel**. Zielbild (Adventskalender, zwei Hunde, Nikolaus/Postbote, Silvester) ist noch\nnicht gebaut.\n\n## Die vier Grundsätze (nicht verhandelbar)\n1. **Zuschauen statt gewinnen** – keine Punkte, Balken, Game Over, Belohnungsschleifen.\n2. **Echtzeit** – echte Uhr/Kalender (Europe/Berlin); Türchen nachholbar, nicht vorziehbar.\n3. **Drei Zielplattformen** – PC-Browser, Handy (Touch), Wii; nichts bauen, was auf der Wii nicht nachbaubar ist.\n4. **Alles handgezeichnet, keine Assets** – prozedural (Canvas 2D, WebAudio); keine Bild-, Font-, Audiodateien im Spiel.\n\n## Plattformregeln\n- Nur Canvas-Primitive in der 960×600-Bühne; kein DOM/HTML-Text/CSS in der Spielwelt.\n- Keine Browser-Spezialitäten in `src/game/` (kein fetch, keine Web-Fonts/Bild-URLs/externen Dienste).\n- Jede Interaktion ohne Maus: Zeiger **und** Durchschalten + Bestätigen; Ziele sind benannte Stationen in `STATIONS`; sichtbarer Fokus-Ring.\n- Fernsehtauglich: Klickziele ≥ 24×24, Schrift ≥ 10 Einheiten, keine Info nur über Hover.\n- **Wii: 4:3 UND 16:9 müssen beide unterstützt werden.** Nichts Wichtiges in den äußeren 10 % links/rechts (4:3-Beschnitt), äußere 5 % frei (Overscan).\n- Speicherung als Schlüssel/Wert (SD-Karten-fähig); Audio nur synthetisch.\n\n## Verbindliche Oberfläche im Spiel (nur diese Elemente)\n- Kopfzeile (`LUNIS HAUS`, Untertitel, `LUNI-STUDIO →`, Tonknopf) · Monitorrahmen (Canvas 8:5, max. 1140 px) · Hintergrund `.bg-room .grid-floor`.\n- **Keine Übergabe-Leiste im Spiel.** Eröffnungstext, Postfach und Freigaben liegen im Projektmanager.\n- **Verboten:** Spielbeschreibung darüber, Steuerungserklärung/Fußzeile darunter, Footer/Credits/Versionszeile, zusätzliche Panels/Karten, neue Komponenten ums Spiel, Änderungen an `.bezel`/`.screen-glass`/`.bg-room`/Canvas-Größe.\n- **Hovertexte im Canvas exakt:** `600 11px \"Space Grotesk\"`, Text `#eef7f2`, Hintergrund `rgba(8,20,26,.88)`, Boxhöhe 20, Radius 5, Innenabstand 8 – nicht vergrößern, nicht durch HTML ersetzen.\n\n## Regel 0 – Nichts Ungefragtes\nKlonen und ausführen, nicht nachbauen. Layout, Texte, Schriftgrößen, Hover-Labels,\nRahmen, Buttons bleiben exakt. Geändert wird nur, was die Aufgabe ausdrücklich verlangt.\nVerbesserungen nur als Frage im Chat, nicht als Tat. Nichts löschen oder umbenennen ohne Auftrag.\n\n## Arbeitsablauf / Postfach\n- **Kein Token im Chat, Screenshot oder Repo.** Kein Token anfordern. Der Besitzer legt die Patch-Dateien selbst ins Postfach. Die KI liefert den Patch als Datei/ZIP.\n- Basis = neuester `main`-Commit, kein Tag.\n- Ablauf: klonen → bauen → zeigen → „ja“ → Patch als Datei/ZIP → Besitzer legt ins Postfach → Knopf → PR-Merge im Browser → Knopf (nachziehen + spiegeln).\n- `main` ist geschützt (PR-Pflicht, keine Force-Pushes); Tags nie verschieben.\n- Nur eine KI gleichzeitig ins Postfach; im Battle-Modus nur die benannte. Kennung KI-A/KI-B, jede Antwort mit Kennung; Umbenennung nur durch ausdrückliche Besitzer-Nachricht. Ist die Kennung unklar, vor Dateiänderungen fragen.\n\n## Vor der Arbeit / Abnahme\n- `git fetch origin && git log --oneline -1 origin/main`\n- `ADVENTS_PROJ=\"$PWD\" bash tools/check.sh | tail -4`\n- **FEHLT** = Funktion weg → echter Fehler, anhalten und melden. **OFFEN** = geplante Aufgabe noch offen → Normalzustand, weiterarbeiten.\n- Hartes Kriterium: **`Fehlt: 0`**. `Offen: 0` nur, wenn die Aufgabe genau diese offenen Punkte erledigt.\n- Nach der Änderung erneut `check.sh | tail -4` und `git diff --stat` zeigen: nur die beauftragten Dateien, keine zusätzlichen.\n- Ist eine Funktion scheinbar weg, zuerst Aufruf und Tageszeit prüfen, bevor sie als fehlend gemeldet wird.\n\n## Prüfen und zeigen\n- `./node_modules/.bin/tsc --noEmit && npm run build` fehlerfrei. **Niemals `npx tsc`.**\n- Dev-Server in der Sandbox-Wurzel starten; `curl -s http://localhost:5173 | grep -o '<title>[^<]*</title>'` erwartet `Little Computer Luni · Das Adventshaus`, nicht `Ready to build`.\n- Laufende Szene zeigen und Klicks im Browser prüfen. Arbeite klein: ein Schritt, eine Prüfung; Antworten/Ausgaben kurz (tail/head), keine kompletten Protokolle.\n- Keine Dateiinhalte zum Abtippen, sondern einen Patch. Bilder aus dem Chat sind Anhänge, keine Projektdateien; nichts davon ins Repository legen.\n\n## Technik-Schutzplanken (dauerhaft)\n- Config nicht ohne Absprache: `package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts` (kein `npm install`, kein `npm audit fix`).\n- `resize()`-Fix in `house.ts` nicht anfassen.\n- Entfernte Altlasten nicht zurückholen: Kamin, PDF-Download, `engine.ts`, `Hud.tsx`, `Overlays.tsx`, `TouchControls.tsx`.\n- Spiellogik in `src/game/`, React nur in `src/components/`; `House` weiß nichts von React.\n- Deutsch in Kommentaren, Labels, Commit-Messages.\n- Alle anderen Dateien sind im Rahmen der Aufgabe änderbar.\n\n## Kommunikation mit dem Besitzer\n- Besitzer ist kein Programmierer; keine Code-Lesekenntnisse voraussetzen – Prüfungen sind Befehle mit Zahlen.\n- Nie auf frühere Nachrichten verweisen; alles Nötige steht an Ort und Stelle.\n- Immer Ort (Terminal/Editor/Browser/Schreibtisch) + erwartetes Ergebnis nennen; ein Schritt pro Nachricht bei Überforderung.\n- Vorschau muss aus der Sandbox-Wurzel laufen (nicht Unterordner), sonst zeigt Arena das leere Template.\n\n## Ausdrücklich abgelehnt\nZugangsdaten in Chat/Screenshot/Repo · ungenaue Anweisungen · mehrere parallele Projektordner · Überschreiben großer Dateien durch KI · ungefragte „Verbesserungen“.\n\nAufgabe: Noch keine. Klone den Stand, zeig ihn mir unverändert – dann sage ich dir, was zu tun ist.";

function versionsVergleich(a,b){
  var links=String(a||"").split("."),rechts=String(b||"").split(".");
  for(var i=0;i<Math.max(links.length,rechts.length);i++){
    var x=parseInt(links[i]||"0",10),y=parseInt(rechts[i]||"0",10);
    if(!isFinite(x)||!isFinite(y)) return 0;
    if(x>y) return 1;
    if(x<y) return -1;
  }
  return 0;
}

var API = {
  pruefbericht:{method:"GET", pfad:"/api/pruefen"},
  pruefen:{method:"GET", pfad:"/api/projekt-diagnose"},
  eintragen:{method:"POST", pfad:"/api/patch-einfuegen"},
  zugit:{method:"POST", pfad:"/api/uebernehmen"},
  speichern:{method:"POST", pfad:"/api/offene-speichern"},
  aktualisieren:{method:"POST", pfad:"/api/aktualisieren"},
  zweige:{method:"POST", pfad:"/api/zweige"},
  postfach:{method:"POST", pfad:"/api/ablegen"},
  nachhause:{method:"POST", pfad:"/api/sichern"},
  entfernen:{method:"POST", pfad:"/api/postfach-leeren"},
  spiel:{method:"POST", pfad:"/api/spiel"},
  spielstop:{method:"POST", pfad:"/api/spiel-stop"}
};

var $  = function(s,r){ return (r||document).querySelector(s); };
var $$ = function(s,r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };

function csrfToken(){
  var m = document.querySelector('meta[name="projektmanager-csrf"]');
  return m ? (m.getAttribute("content") || "") : "";
}
function apiHeaders(extra){
  var h = {"X-Projektmanager-Token": csrfToken()};
  if (extra) Object.keys(extra).forEach(function(k){ h[k] = extra[k]; });
  return h;
}

/* ---------- Aktionen (Titel, Symbole, Art) ---------- */
var AKTEN = {
  eroeffnung:{
    label:"Eröffnungstext kopieren", sym:"✎", art:"read", mark:"lokal", gruppe:"01",
    sub:"Starttext für die KI",
    tip:"Legt den Eröffnungstext (Anleitung für die neue KI-Sitzung) in die Zwischenablage – nur lesend.",
    vorschau:"Lese die Übergabedatei docs/UEBERGABE.md und kopiere den Abschnitt „Eröffnungstext“ in die Zwischenablage.\nEs wird keine Datei verändert."
  },
  pruefbericht:{
    label:"Projekt Prüfbericht holen", sym:"⧉", art:"read", mark:"lokal", gruppe:"01",
    sub:"Projektstand prüfen",
    tip:"Prüft Projektordner, Git-Stand und Basis – erzeugt den Prüfbericht zum Weitergeben an die KI. Liest nur.",
    vorschau:"Lese Projektordner, git status und die Basis (origin/main) und stelle den Prüfbericht zusammen.\nEs wird nichts verändert."
  },
  eintragen:{
    label:"Patch holen", sym:"⇥", art:"write", mark:"online", gruppe:"01",
    sub:"KI-Patch ins Postfach",
    tip:"Legt den Patch der KI ins Postfach (GitHub-Gist). Prüft vorher die Basis und filtert docs/UEBERGABE.md.",
    vorschau:"Schreibe den übergebenen Patch-Text ins Postfach (GitHub-Gist) als aktuell.patch + aktuell.json.\nDer Postfach-Inhalt wird dabei überschrieben."
  },
  zugit:{
    label:"Patch zu GitHub", sym:"⇧", art:"write", mark:"online", gruppe:"01",
    sub:"Prüfen und Freigabe",
    tip:"Holt den Patch aus dem Postfach, prüft ihn, baut ihn lokal, eröffnet eine Pull Request auf GitHub und wechselt zurück auf main.",
    vorschau:"Lese das Postfach, prüfe Prüfsumme und Basis, wende den Patch auf einem eigenen Zweig an,\nbaue das Projekt, eröffne eine Pull Request (Freigabe) auf GitHub und kehre auf main zurück."
  },
  speichern:{
    label:"Offene Änderungen speichern", sym:"◎", art:"write", mark:"lokal", gruppe:"02",
    sub:"Commit, kein Upload",
    tip:"Prüft auf versehentliche Geheimdateien und speichert offene Änderungen als lokalen Commit. Es wird nichts hochgeladen.",
    vorschau:"Prüfe auf sensible Dateien (.env, Schlüssel), melde ignorierte Dateien ehrlich und führe git add + git commit im Projektordner aus.\nEs wird nichts hochgeladen – der lokale Stand wird nur festgehalten."
  },
  postfach:{
    label:"Ins Postfach legen", sym:"⇪", art:"write", mark:"online", gruppe:"02",
    sub:"Deinen Stand ablegen",
    tip:"Prüft ob das Postfach frei ist, bündelt alle lokalen Commits seit origin/main als Patch und legt ihn ins Postfach.",
    vorschau:"Prüfe das Postfach auf unübernommene Patches, baue aus allen lokalen Commits einen Patch,\nberechne die Prüfsumme und schreibe ihn ins Postfach (GitHub-Gist)."
  },
  aktualisieren:{
    label:"Lokal aktualisieren", sym:"↻", art:"write", mark:"online", gruppe:"02",
    sub:"GitHub-Stand nach main holen",
    tip:"Führt git pull --ff-only aus: übernimmt neue GitHub-Commits in deinen Arbeitsordner – nur bei sauberem Stand, bei Divergenz ehrlicher Abbruch statt automatischem Zusammenführen.",
    vorschau:"Prüfe auf offene Änderungen und führe git pull --ff-only origin main aus.\nNeue GitHub-Commits kommen in deinen lokalen Arbeitsordner; bei Divergenz wird ehrlich abgebrochen."
  },
  nachhause:{
    label:"Patch lokal nach Hause", sym:"⇩", art:"write", mark:"lokal", gruppe:"02",
    sub:"Sicherung und Übergabe",
    tip:"Holt den Stand von GitHub in die lokale Sicherung und erneuert die Übergabedatei (HAND-Notiz bleibt erhalten).",
    vorschau:"Hole den Stand von GitHub, aktualisiere die lokale Sicherung und schreibe docs/UEBERGABE.md neu\n(die HAND-Notiz unter <!-- HAND: … --> bleibt erhalten)."
  },
  pruefen:{
    label:"Stand prüfen", sym:"✓", art:"read", mark:"lokal", gruppe:"03",
    sub:"Diagnose",
    tip:"Prüft den Stand des Projekts, offene Dateien, den Abgleich lokal vs. GitHub (identisch / voraus / hinter / Divergenz) und den Postfach-Inhalt. Liest nur.",
    vorschau:"Lese git status, die Basis (origin/main) und den Postfach-Inhalt und berichte den Stand.\nEs wird nichts verändert."
  },
  spiel:{
    label:"Spiel ansehen", sym:"▶", art:"write", mark:"lokal", gruppe:"03",
    sub:"Spiel im Browser öffnen",
    tip:"Startet das Spiel frisch aus dem aktuellen Projektordner und öffnet es; fremde oder alte Server werden nicht geöffnet.",
    vorschau:"Beendet ein vom Projektmanager gestartetes Spiel und startet einen frischen Dev-Server auf einem freien Port.\nDie Adresse wird mit Cache-Bruch geöffnet; fremde Server werden nicht geöffnet."
  },
  zweige:{
    label:"Zweige aufräumen", sym:"⎇", art:"write", mark:"lokal", gruppe:"04",
    sub:"gemergte ki/*-Zweige löschen",
    tip:"Räumt Git-Zweige auf: löscht NUR Zweige ki/*, deren Commits bereits in main gemerged sind (lokal und auf GitHub). Noch nicht gemergte Zweige werden nur aufgelistet, nie berührt.",
    vorschau:"Führe git fetch --prune aus und entferne gemergte ki/*-Zweige lokal (-d) und remote (--delete).\nNoch nicht gemergte Zweige bleiben unverändert."
  },
  entfernen:{
    label:"Alten Patch entfernen", sym:"⌫", art:"write", mark:"online", gruppe:"04",
    sub:"Postfach leeren",
    tip:"Entfernt nur aktuell.patch und aktuell.json aus dem Postfach. Übrige Gist-Dateien bleiben unangetastet.",
    vorschau:"Prüfe den Gist-Inhalt und lösche daraus nur aktuell.patch und aktuell.json.\nÜbrige Dateien im Gist werden nicht angerührt."
  },
  abbrechen:{
    label:"Vorgang abbrechen", sym:"⊘", art:"read", mark:"lokal", gruppe:"04",
    sub:"Laufenden Vorgang stoppen",
    tip:"Bricht eine laufende Prüfung sofort ab. Bei schreibenden Aktionen läuft der Helfer seine geprüften Schritte zu Ende, damit nichts halb bleibt.",
    vorschau:"Keine Datei wird verändert – es wird nur der laufende Vorgang beendet."
  },
  spielstop:{
    label:"Spiel beenden", sym:"■", art:"write", mark:"lokal", gruppe:"04",
    sub:"Vom Projektmanager gestartet",
    tip:"Beendet ein Spiel, das der Projektmanager selbst gestartet hat. Ehrliche Meldung, falls keins lief.",
    vorschau:"Beende nur einen Spiel-Server, den der Projektmanager selbst gestartet hat."
  }
};

var GRUPPEN = [
  {id:"01", titel:"Übergabe an die KI", klein:"prüfen → Starttext → Bericht", farbe:"blau", aktionen:["pruefen","eroeffnung","pruefbericht"]},
  {id:"02", titel:"Sichern des Projektes", klein:"Stand sichern · KI-Patch → GitHub", farbe:"violett", aktionen:["pruefen","speichern","eintragen","postfach","zugit","aktualisieren","nachhause"]},
  {id:"03", titel:"Status", klein:"prüfen → Spiel ansehen", farbe:"tuerkis", aktionen:["pruefen","spiel"]},
  {id:"04", titel:"Wartung", klein:"entfernen → Zweige → abbrechen → beenden", farbe:"grau", aktionen:["entfernen","zweige","abbrechen","spielstop"]}
];

var GRUPPEN_FARBE = {blau:"var(--blau)", violett:"var(--violett)", tuerkis:"var(--tuerkis)", grau:"var(--grau)"};

/* ---------- Ablauf (Simulationsschritte) ---------- */
var ABLauf = {
  eroeffnung:[
    ["Lese Einstellungen (einstellungen.json)","info"],
    ["Übergabedatei gefunden: docs/UEBERGABE.md","ok"],
    ["Abschnitt „Eröffnungstext“ kopiert","ok"]
  ],
  pruefbericht:[
    ["Prüfe Projektordner …","info"],
    ["git status: 1 offene Änderung (docs/UEBERGABE.md)","warn"],
    ["Basis: 82b1629 (origin/main) – passt","ok"],
    ["Prüfsumme des Postfachs: stimmt","ok"]
  ],
  pruefen:[
    ["Lese Status (nur lesend) …","info"],
    ["Projektordner gefunden","ok"],
    ["Basis-Prüfung gegen origin/main: ok","ok"]
  ],
  eintragen:[
    ["Prüfe Patch-Text (Prüfsumme wird im Helfer berechnet)","info"],
    ["Filter: docs/UEBERGABE.md entfernt – Datei existiert schon","warn"],
    ["Basis vorhanden: 82b1629","ok"],
    ["Schreibe ins Postfach (GitHub-Gist) …","info"]
  ],
  zugit:[
    ["Gist lesen …","info"],
    ["Prüfsumme stimmt","ok"],
    ["Basis passt (82b1629)","ok"],
    ["git apply --check: in Ordnung","ok"],
    ["Zweig ki/thema angelegt, Patch angewendet","ok"],
    ["tsc + Build: ohne Fehler","ok"],
    ["Pull Request (Freigabe) eröffnet · zurück auf main","ok"]
  ],
  speichern:[
    ["git status --porcelain -uall (Geheimnis-Check ok)","info"],
    ["git add + git commit – lokal, kein Push","ok"]
  ],
  postfach:[
    ["Postfach auf unübernommene Patches prüfen …","info"],
    ["Stand aus lokalen Commits als Patch bauen …","info"],
    ["Prüfsumme berechnen","ok"],
    ["Gist schreiben (aktuell.patch + aktuell.json)","ok"]
  ],
  aktualisieren:[
    ["Prüfe: Arbeitsbaum sauber …","info"],
    ["git pull --ff-only origin main …","info"],
    ["Lokal = GitHub-Stand","ok"]
  ],
  nachhause:[
    ["GitHub-Stand holen (fetch)","ok"],
    ["Sicherung aktualisieren (Bare-Spiegel)","ok"],
    ["docs/UEBERGABE.md neu schreiben (HAND-Notiz bleibt)","ok"]
  ],
  zweige:[
    ["git fetch --prune …","info"],
    ["Gemergte ki/*-Zweige suchen …","info"],
    ["Gemergte Zweige lokal und remote entfernen","ok"]
  ],
  entfernen:[
    ["Postfach-Inhalt prüfen (Gist)","info"],
    ["aktuell.patch entfernt","ok"],
    ["aktuell.json entfernt","ok"]
  ],
  spiel:[
    ["Starte frischen Dev-Server im aktuellen Projektordner …","info"],
    ["Frischer Dev-Server bereit; Adresse wird geöffnet","ok"]
  ],
  spielstop:[
    ["Prüfe, ob der Projektmanager das Spiel gestartet hat …","info"],
    ["Kein selbst gestartetes Spiel gefunden","warn"]
  ]
};

var ENDBUND = {
  eroeffnung:{txt:"Eröffnungstext liegt in der Zwischenablage – du kannst die KI starten.",art:"info",lampe:"gelb"},
  pruefbericht:{txt:"Prüfbericht ist fertig – „Bericht kopieren“ unten rechts nimmt ihn mit.",art:"info",lampe:"gelb"},
  pruefen:{txt:"Stand geprüft: alles lesend, nichts verändert.",art:"ok",lampe:"gruen"},
  eintragen:{txt:"Patch liegt im Postfach – weiter mit „Patch zu GitHub“.",art:"ok",lampe:"gelb"},
  zugit:{txt:"Pull Request eröffnet – im Browser auf „Freigabe“ klicken.",art:"ok",lampe:"gelb"},
  speichern:{txt:"Änderungen lokal gespeichert – es wurde nichts hochgeladen.",art:"ok",lampe:"gruen"},
  postfach:{txt:"Dein Stand liegt im Postfach (online).",art:"ok",lampe:"gelb"},
  aktualisieren:{txt:"Lokaler Stand = GitHub-Stand (main ist aktuell).",art:"ok",lampe:"gruen"},
  nachhause:{txt:"Stand gesichert und Übergabedatei erneuert.",art:"ok",lampe:"gruen"},
  zweige:{txt:"Gemergte ki/*-Zweige aufgeräumt; nicht gemergte Zweige unverändert.",art:"ok",lampe:"gruen"},
  entfernen:{txt:"Alter Patch entfernt – der nächste Patch kann geliefert werden.",art:"ok",lampe:"gelb"},
  spiel:{txt:"Spiel läuft – der Tab wurde geöffnet.",art:"ok",lampe:"gelb"},
  spielstop:{txt:"Kein vom Projektmanager gestartetes Spiel – es wurde nichts beendet.",art:"warn",lampe:"gelb"}
};

var ZUSTAND = {
  modus:"demo", helperVersion:null, ordner:null, tokenVorhanden:false, githubMain:"",
  cfg:{projekt:"~/projekte/adventshaus", sicherung:"~/sicherung/adventshaus.git", kennung:"KI-B", spiel_url:"http://localhost:5173/"},
  kette:null, erledigt:{}, laeuft:false, token:0, override:null, versionKonflikt:false,
  log:[], ampel:"gelb", bericht:null, controller:null, patchHinweis:"", patchArchiv:null
};

/* Logische Reihenfolge: prüfen -> lokal speichern -> Postfach -> KI-Übergabe -> PR -> nach Hause -> Spiel */
var STANDARD_KETTE = ["pruefen","speichern","postfach","eroeffnung","pruefbericht","eintragen","zugit","aktualisieren","nachhause","spiel"];

/* ============================================================
   Aufbau der Knöpfe
   ============================================================ */
function baueKnöpfe(){
  GRUPPEN.forEach(function(g){
    var ziel = $("#kn-"+g.id);
    ziel.textContent = "";
    g.aktionen.forEach(function(id){
      var a = AKTEN[id];
      var b = document.createElement("button");
      b.className = "knopf " + (a.mark==="lokal" ? "lokal" : "online");
      b.setAttribute("data-act", id);
      b.setAttribute("data-gruppe", g.id);
      b.setAttribute("title", a.tip);
      b.innerHTML =
        '<span class="sym">' + a.sym + '</span>' +
        '<span class="txt">' +
          '<span class="z1">' + a.label + '</span>' +
          '<span class="z2"><span class="badge ' + a.mark + '">' + a.mark + '</span>' + a.sub + '</span>' +
        '</span>';
      b.addEventListener("click", function(){ klickAktion(id, b); });
      ziel.appendChild(b);
    });
  });
}

/* ============================================================
   Denkfenster
   ============================================================ */
function denkZeile(text, art){
  var li = document.createElement("li");
  li.className = art || "info";
  var m = {ok:"✓", info:"›", warn:"!", err:"✕"}[art || "info"] || "›";
  var symbol = document.createElement("span");
  var inhalt = document.createElement("span");
  symbol.className = "m";
  symbol.textContent = m;
  inhalt.textContent = text;
  li.appendChild(symbol);
  li.appendChild(inhalt);
  $("#denkListe").appendChild(li);
  var b = $("#denkBody"); b.scrollTop = b.scrollHeight;
}
function denkAktuell(text){ $("#denkAktuell").textContent = text; }
function denkStatus(text, laeuft){
  $("#denkStatusText").textContent = text;
  $("#denkStatus").classList.toggle("laeuft", !!laeuft);
  var sb = $("#denkFortschritt");
  if (sb) sb.classList.toggle("laeuft", !!laeuft);
}
function protokolle(text){
  ZUSTAND.log.push(text);
  $("#protokollText").textContent = ZUSTAND.log.slice(-120).join("\n");
  var rl = $("#rasterLog"); if (rl) rl.textContent = ZUSTAND.log.slice(-200).join("\n");
}

/* ============================================================
   Ampel & Stationsstraße
   ============================================================ */
function setAmpel(zustand, text){
  ZUSTAND.ampel = zustand;
  $("#lampeRot").classList.toggle("aktiv", zustand==="rot");
  $("#lampeGelb").classList.toggle("aktiv", zustand==="gelb");
  $("#lampeGruen").classList.toggle("aktiv", zustand==="gruen");
  $("#ampelText").textContent = text || ({gruen:"alles in Ordnung", gelb:"es wartet etwas", rot:"Fehler"}[zustand]);
}
function markiereStation(id){
  var map = {eroeffnung:"1", pruefbericht:"1", pruefen:"1", eintragen:"2", postfach:"2", zugit:"3", speichern:"4", aktualisieren:"4", nachhause:"4", zweige:"4"};
  var nr = map[id] || "";
  $$("#strasse .str-schritt").forEach(function(el){
    el.classList.toggle("aktiv", !!nr && el.getAttribute("data-schritt") === nr);
  });
}

/* ============================================================
   Großer Knopf / Kette
   ============================================================ */
function naechsterSchritt(){
  if (!ZUSTAND.kette && ZUSTAND.override) return ZUSTAND.override;
  if (ZUSTAND.kette){
    var g = gruppeVon(ZUSTAND.kette.gruppe);
    var liste = g.aktionen;
    if (ZUSTAND.kette.index < liste.length) return liste[ZUSTAND.kette.index];
    return null;
  }
  for (var i=0;i<STANDARD_KETTE.length;i++){
    if (!ZUSTAND.erledigt[STANDARD_KETTE[i]]) return STANDARD_KETTE[i];
  }
  return null;
}
function gruppeVon(id){
  for (var i=0;i<GRUPPEN.length;i++) if (GRUPPEN[i].id===id) return GRUPPEN[i];
  return GRUPPEN[0];
}
function aktualisiereGrossenKnopf(){
  var id = naechsterSchritt();
  var knopf = $("#grossKnopf");
  var echt = ZUSTAND.modus === "echt";
  $$(".knopf").forEach(function(b){ b.classList.remove("markiert"); });
  if (!id){
    $("#grossSymbol").textContent = "✓";
    $("#grossLabel").textContent = echt ? "Ablauf durchlaufen" : "Vorschau durchlaufen";
    $("#grossSub").textContent = "Eine Überschrift startet eine neue Kette.";
    knopf.setAttribute("title","Alle Schritte wurden durchlaufen.");
    $("#grossKette").innerHTML = "";
    return;
  }
  var a = AKTEN[id];
  $(".g-mitte").style.setProperty("--c", GRUPPEN_FARBE[gruppeVon(a.gruppe).farbe]);
  $("#grossSymbol").textContent = a.sym;
  $("#grossLabel").textContent = a.label;
  $("#grossSub").textContent = (echt ? "Nächster Schritt · " : "Vorschau · ") + a.sub;
  knopf.setAttribute("title", (echt ? "" : "Vorschau: ") + a.tip);
  markiereStation(id);
  var k = $("#grossKette");
  k.textContent = "";
  if (ZUSTAND.kette){
    var g = gruppeVon(ZUSTAND.kette.gruppe);
    var name = document.createElement("span");
    name.className = "kette-name";
    name.textContent = g.titel + " · Schritt " + (ZUSTAND.kette.index + 1) + "/" + g.aktionen.length;
    var fortschritt = document.createElement("span");
    fortschritt.className = "kette-fortschritt";
    fortschritt.setAttribute("aria-hidden", "true");
    g.aktionen.forEach(function(x,i){
      var strich = document.createElement("i");
      if (i <= ZUSTAND.kette.index) strich.className = "aktiv";
      fortschritt.appendChild(strich);
    });
    k.appendChild(name);
    k.appendChild(fortschritt);
  } else {
    k.textContent = "Kette über eine Überschrift starten";
  }
  $$('.knopf[data-act="'+id+'"]').forEach(function(z){ z.classList.add("markiert"); });
}
function ketteStarten(gruppeId){
  if (ZUSTAND.laeuft){
    denkZeile("Ein Vorgang läuft noch. Bitte zuerst abbrechen oder abwarten.", "warn");
    return;
  }
  var g = gruppeVon(gruppeId);
  var echt = ZUSTAND.modus === "echt";
  ZUSTAND.override = null;
  ZUSTAND.kette = {gruppe:gruppeId, index:0};
  denkAktuell((echt ? "Kette „" : "Vorschau der Kette „")+g.titel+"“: "+AKTEN[g.aktionen[0]].label+" ist als Nächstes dran.");
  denkZeile((echt ? "Kette: " : "Vorschau: ") + g.aktionen.map(function(x){return AKTEN[x].label;}).join(" → "), "info");
  protokolle("Kette gestartet: " + g.titel);
  setAmpel("gelb", echt ? "Kette aktiv" : "Vorschau");
  aktualisiereGrossenKnopf();
  aktualisiereKettenAnzeige();
}
function ketteWeiter(id){
  if (!ZUSTAND.kette) return false;
  var g = gruppeVon(ZUSTAND.kette.gruppe);
  var pos = g.aktionen.indexOf(id);
  return pos === ZUSTAND.kette.index;
}
function aktualisiereKettenAnzeige(){
  var aktivId = ZUSTAND.kette ? ZUSTAND.kette.gruppe : null;
  var wkStart = $("#wkStart"), wkNeustart = $("#wkNeustart"), wkBeenden = $("#wkBeenden"), wkJa = $("#wkJa"), wkNein = $("#wkNein");
  if (wkStart) wkStart.addEventListener("click", function(){ werkzeugAktion("start"); });
  if (wkNeustart) wkNeustart.addEventListener("click", function(){ werkzeugConfirm = "neustart"; zeigeWerkzeugLeiste(); });
  if (wkBeenden) wkBeenden.addEventListener("click", function(){ werkzeugConfirm = "beenden"; zeigeWerkzeugLeiste(); });
  if (wkJa) wkJa.addEventListener("click", function(){ var a = werkzeugConfirm; werkzeugConfirm = null; zeigeWerkzeugLeiste(); if (a) werkzeugAktion(a); });
  if (wkNein) wkNein.addEventListener("click", function(){ werkzeugConfirm = null; zeigeWerkzeugLeiste(); denkZeile("Abgebrochen – nichts geändert.", "info"); });

  $$(".kl-chip").forEach(function(c){
    c.classList.toggle("aktiv", c.getAttribute("data-kette") === aktivId);
  });
  $$(".kette-start").forEach(function(b){
    var on = b.getAttribute("data-kette") === aktivId;
    b.classList.toggle("aktiv", on);
    var h = b.querySelector(".kette-hinweis");
    if (!h) return;
    if (on){
      var g = gruppeVon(b.getAttribute("data-kette"));
      h.textContent = "läuft · Schritt " + Math.min(ZUSTAND.kette.index + 1, g.aktionen.length) + "/" + g.aktionen.length;
    } else {
      h.textContent = "Start →";
    }
  });
  var st = $("#klStatus");
  if (st){
    if (aktivId){
      var g2 = gruppeVon(aktivId);
      st.textContent = "Kette „" + g2.titel + "“ aktiv · Schritt " + Math.min(ZUSTAND.kette.index + 1, g2.aktionen.length) + "/" + g2.aktionen.length;
      st.className = "kl-status aktiv";
    } else {
      st.textContent = "keine Kette aktiv – hier oder per Gruppenüberschrift starten";
      st.className = "kl-status";
    }
  }
}

/* ============================================================
   Aktionen
   ============================================================ */
function klickAktion(id, knopfEl){
  if (id === "abbrechen" && ZUSTAND.laeuft){
    abbrechen();
    return;
  }
  if (ZUSTAND.laeuft){
    denkZeile("Es läuft gerade ein Vorgang – erst „Abbrechen“ drücken.", "warn");
    return;
  }
  var a = AKTEN[id];
  if (id !== ZUSTAND.override) ZUSTAND.override = null;
  var inKette = ketteWeiter(id);
  var kettenHinweis = "";
  if (ZUSTAND.kette && !inKette){
    kettenHinweis = "Kette beendet, weil du einen anderen Schritt gewählt hast.";
    ZUSTAND.kette = null;
    denkZeile(kettenHinweis, "warn");
    protokolle(kettenHinweis);
    aktualisiereGrossenKnopf();
    aktualisiereKettenAnzeige();
  }
  if (id === "abbrechen"){
    abbrechen();
    return;
  }
  if (id === "eintragen"){
    patchOeffnen(kettenHinweis);
    return;
  }
  if (a.art === "write"){
    dialogOeffnen(id, kettenHinweis);
  } else {
    starteAktion(id, kettenHinweis);
  }
}

function starteAktion(id, kettenHinweis){
  if (id === "eroeffnung"){ eroeffnungKopieren(kettenHinweis); return; }
  if (ZUSTAND.modus === "echt"){ starteEcht(id, kettenHinweis); return; }

  var a = AKTEN[id];
  var schritte = ABLauf[id] || [];
  var ende = ENDBUND[id] || {txt:"Vorschau beendet.", art:"ok", lampe:"gruen"};
  var token = ++ZUSTAND.token;

  ZUSTAND.laeuft = true;
  $("#denkListe").innerHTML = "";
  $("#btnBericht").classList.add("hidden");
  hideSolution();
  denkStatus("Simulation", true);
  denkAktuell("Vorschau: " + a.label + " …");
  $("#befehlText").textContent = a.vorschau;
  if (kettenHinweis) denkZeile(kettenHinweis, "warn");
  protokolle("Simulation gestartet: " + a.label);

  var i = 0;
  function weiter(){
    if (token !== ZUSTAND.token) return;
    if (i < schritte.length){
      var s = schritte[i++];
      denkZeile(s[0], s[1]);
      setTimeout(weiter, 320);
      return;
    }
    denkZeile(ende.txt, ende.art);
    denkZeile("Nur eine Simulation. Es wurde nichts geprüft oder verändert.", "info");
    denkAktuell("Simulation beendet. Keine echten Projektdaten wurden verwendet.");
    denkStatus("simuliert", false);
    ZUSTAND.laeuft = false;
    ZUSTAND.erledigt[id] = true;
    setAmpel("gelb", "Vorschau");
    protokolle("Simulation beendet: " + a.label);
    if (id === "pruefbericht" || id === "pruefen"){
      $("#btnBericht").classList.remove("hidden");
    }
    if (ZUSTAND.kette){
      var g = gruppeVon(ZUSTAND.kette.gruppe);
      var pos = g.aktionen.indexOf(id);
      if (pos >= 0){
        ZUSTAND.kette.index = pos + 1;
        if (ZUSTAND.kette.index >= g.aktionen.length){
          denkZeile("Die Vorschau der Kette „"+g.titel+"“ ist fertig.", "ok");
          protokolle("Vorschau der Kette fertig: " + g.titel);
          ZUSTAND.kette = null;
        }
      }
    }
    aktualisiereKettenAnzeige();
    aktualisiereGrossenKnopf();
    setTimeout(function(){ if (token===ZUSTAND.token) denkStatus("bereit", false); }, 900);
  }
  weiter();
}
function anfrageKiKopieren(){
  var t = [];
  t.push("LIEFERFORMAT FÜR DEN PATCH – bitte exakt so:");
  t.push("1) Gib mir den Patch als TXT-Datei mit Code in der Vorschau, damit ich den Inhalt in „Patch holen“ einfügen kann.");
  t.push("2) Biete mir zusätzlich die Patch-Dateien als ZIP-Datei zum Download an.");
  t.push("Die ZIP muss enthalten:");
  t.push('   - aktuell.patch  (vollständiger Patch, erste Zeile beginnt mit "diff --git")');
  t.push('   - aktuell.json   ({"datei":"aktuell.patch","sha256":"…","titel":"…","basis":"…"})');
  t.push("   sha256 = erste 16 Hex-Zeichen der SHA-256-Prüfsumme des Patch-Textes.");
  t.push("   basis  = 7-stelliger Kurz-Hash von origin/main im Projekt");
  if (ZUSTAND.githubMain){
    t.push("   (aktueller GitHub-main: " + ZUSTAND.githubMain + ")");
  } else {
    t.push("   (aktueller GitHub-main: aus der Zeile „GitHub-main:“ des zuletzt kopierten Prüfberichts übernehmen)");
  }
  kopiereText(t.join("\n")).then(function(ok){
    var info = $("#patchInfo");
    info.textContent = ok ? "Anfrage für KI ist jetzt im Zwischenspeicher. mit STRG+V in den Chat kopieren." : "Kopieren nicht möglich – Zwischenablage unverändert.";
    info.className = "paste-info " + (ok ? "ok" : "bad");
  });
}
function kopiereText(text){
  function fallback(){
    return new Promise(function(resolve){
      var feld=document.createElement("textarea");
      feld.value=text; feld.style.position="fixed"; feld.style.left="-9999px";
      document.body.appendChild(feld); feld.select();
      var ok=false;
      try{ ok=document.execCommand("copy"); }catch(e){ ok=false; }
      feld.remove(); resolve(ok);
    });
  }
  if (navigator.clipboard && navigator.clipboard.writeText){
    return navigator.clipboard.writeText(text).then(function(){return true;},fallback);
  }
  return fallback();
}
function aktionFortschritt(id){
  ZUSTAND.erledigt[id]=true;
  if (ZUSTAND.kette){
    var g=gruppeVon(ZUSTAND.kette.gruppe), pos=g.aktionen.indexOf(id);
    if (pos>=0){
      ZUSTAND.kette.index=pos+1;
      if (ZUSTAND.kette.index>=g.aktionen.length){
        denkZeile("Kette „"+g.titel+"“ ist fertig.","ok");
        ZUSTAND.kette=null;
      }
    }
  }
  aktualisiereKettenAnzeige();
  var folge={
    pruefen:"speichern",
    speichern:"postfach",
    postfach:"eroeffnung",
    eroeffnung:"pruefbericht",
    pruefbericht:"eintragen",
    eintragen:"zugit",
    zugit:"aktualisieren",
    aktualisieren:"nachhause",
    entfernen:"postfach",
    nachhause:"pruefen"
  }[id] || null;
  ZUSTAND.override=folge;
  aktualisiereGrossenKnopf();
}
function eroeffnungKopieren(hinweis){
  if (hinweis) denkZeile(hinweis,"warn");
  denkAktuell("Kopiere den Eröffnungstext …");
  kopiereText(EROEFFNUNG).then(function(ok){
    denkZeile(ok ? "Eröffnungstext kopiert – mit STRG+V in den Chat einfügen." : "Kopieren nicht möglich; die Zwischenablage wurde nicht geändert.",ok?"ok":"err");
    denkAktuell(ok ? "Eröffnungstext ist in der Zwischenablage." : "Kopieren fehlgeschlagen.");
    protokolle(ok ? "Eröffnungstext kopiert" : "Eröffnungstext: Kopieren fehlgeschlagen");
    if (ok) aktionFortschritt("eroeffnung");
  });
}
function showSolution(url,text){
  var a=$("#solveLink");
  if (!url || !/^https?:\/\//i.test(url)){ a.classList.add("hidden"); return; }
  a.href=url; a.textContent=text || "Öffnen"; a.classList.remove("hidden");
}
function hideSolution(){
  $("#solveLink").classList.add("hidden");
  $("#btnBasis").classList.add("hidden");
  var ov = $("#btnOverwrite");
  if (ov) ov.classList.add("hidden");
}
function prLinkZeigen(url){
  var a=$("#solveLink");
  if (!url || !/^https:\/\/[^/\s]+\/[^/\s]+\/[^/\s]+\/pull\/\d+$/.test(url)){ a.classList.add("hidden"); return false; }
  a.href=url; a.textContent="PR öffnen"; a.title="Pull Request im Browser öffnen"; a.target="_blank"; a.rel="noopener"; a.classList.remove("hidden"); return true;
}

function echtenBericht(id,j){
  var l=["Projektmanager – Prüfbericht","Zeit: "+new Date().toLocaleString("de-DE"),"Modus: Echtbetrieb · GUI "+GUI_VERSION+" · Helfer "+(ZUSTAND.helperVersion || "?")];
  if (id==="pruefbericht"){
    (j.steps || []).forEach(function(s){ l.push("· "+(s.name||"Schritt")+": "+(s.out||"")+(s.loesung?" | Lösung: "+s.loesung:"")); });
  } else {
    (j.zeilen || []).forEach(function(z){ l.push("· "+z); });
    if (j.out) l.push("· "+j.out);
  }
  l.push("Kennung: "+(ZUSTAND.cfg.kennung || "–"));
  return l.join("\n");
}
async function starteEcht(id,kettenHinweis,extra){
  if (ZUSTAND.versionKonflikt){
    denkZeile("Aktion blockiert: GUI und Helfer haben unterschiedliche Versionen. Helfer neu starten und Seite aktualisieren.","err");
    return;
  }
  var a=AKTEN[id], spec=API[id];
  if (!spec){ denkZeile("Kein echter Endpunkt für "+id,"err"); return; }
  extra=extra || {};
  var token=++ZUSTAND.token;
  ZUSTAND.laeuft=true;
  ZUSTAND.controller=typeof AbortController==="function" ? new AbortController() : null;
  $("#denkListe").innerHTML="";
  $("#btnBericht").classList.add("hidden");
  hideSolution();
  denkStatus("Helfer läuft",true);
  denkAktuell("Helfer: "+a.label+" …");
  $("#befehlText").textContent=(extra.pfad || spec.pfad)+" · "+spec.method+"\n"+a.vorschau;
  if (kettenHinweis) denkZeile(kettenHinweis,"warn");
  protokolle("Echte Aktion: "+a.label);
  try{
    var headers = apiHeaders(extra.daten ? {"Content-Type":"application/json"} : null);
    var optionen={method:spec.method,cache:"no-store",headers:headers};
    if (ZUSTAND.controller) optionen.signal=ZUSTAND.controller.signal;
    if (extra.daten){
      optionen.body=JSON.stringify(extra.daten);
    }
    var r=await fetch(extra.pfad || spec.pfad,optionen);
    var j=await r.json();
    if (token!==ZUSTAND.token) return;
    if (j && j.github_main) ZUSTAND.githubMain = j.github_main;
    if (!r.ok && !j.out) throw new Error("HTTP "+r.status);
    if (id==="pruefbericht"){
      var schritte=j.steps || [];
      if (!schritte.length) denkZeile(j.out || "Keine Prüfdaten erhalten.",j.ok?"info":"err");
      schritte.forEach(function(s){
        denkZeile((s.name||"Schritt")+(s.out?": "+s.out:""),s.ok?"ok":"warn");
        if (s.loesung) denkZeile("Lösung: "+s.loesung,"warn");
        if (s.link) showSolution(s.link,s.linkText);
      });
      ZUSTAND.bericht=echtenBericht(id,j);
      $("#btnBericht").classList.remove("hidden");
    } else if (id==="pruefen"){
      (j.zeilen || []).forEach(function(z){denkZeile(z,"info");});
      ZUSTAND.bericht=echtenBericht(id,j);
      $("#btnBericht").classList.remove("hidden");
    }
    var erfolg=(id==="spiel") ? !!j.url : !!j.ok;
    var ton=erfolg ? (j.info?"info":"ok") : (id==="spielstop"?"warn":"err");
    if (id!=="pruefbericht" && id!=="pruefen") denkZeile(j.out || (erfolg?"Erledigt.":"Keine Erfolgsmeldung erhalten."),ton);
    else if (j.out && id==="pruefen") denkZeile(j.out,ton);
    if (j.sha_info) denkZeile(j.sha_info,"info");
    if (j.loesung) denkZeile("Lösung: "+j.loesung,"warn");
    if (j.link) showSolution(j.link,j.linkText);
    if (j.basisfehler) $("#btnBasis").classList.remove("hidden");
    if (j.ueberschreiben && $("#btnOverwrite")) $("#btnOverwrite").classList.remove("hidden");
    if (j.detail){ $("#befehlText").textContent += "\n\n"+j.detail; }
    if (id==="spiel" && j.url){
      var fenster=window.open(j.url,"_blank");
      denkZeile(fenster?"Spiel-Adresse geöffnet: "+j.url:"Browser hat das neue Fenster blockiert. Adresse: "+j.url,fenster?"ok":"warn");
      if (!fenster) showSolution(j.url,"Spiel öffnen");
    }
    var prBereit = j.pr_url ? prLinkZeigen(j.pr_url) : false;
    if (id==="zugit" && prBereit){
      var prFenster=window.open(j.pr_url,"_blank");
      if (!prFenster) denkZeile("PR nicht automatisch geöffnet – Knopf „PR öffnen“ verwenden.","warn");
    }
    denkAktuell(j.out || (erfolg?a.label+" abgeschlossen.":a.label+" fehlgeschlagen."));
    denkStatus(erfolg?"fertig":"Fehler",false);
    var neueLampe=erfolg?"gruen":(id==="spielstop"?"gelb":"rot");
    var lampenText=erfolg?(j.info?"keine Handlung nötig":"alles ok"):(id==="spielstop"?"kein Spiel beendet":"Fehler");
    setAmpel(neueLampe,lampenText);
    protokolle((erfolg?"✓ ":"✕ ")+(j.out || a.label));
    if (erfolg && !j.info) aktionFortschritt(id);
    else aktualisiereGrossenKnopf();
  }catch(e){
    if (token!==ZUSTAND.token) return;
    var msg=(e && e.name==="AbortError") ? "Anzeige abgebrochen; der Helfer kann seine geprüften Schritte zu Ende führen." : "Helfer nicht erreichbar oder Aktion fehlgeschlagen: "+e.message;
    denkZeile(msg,"err"); denkAktuell(msg); denkStatus("Fehler",false);
    setAmpel("rot","Fehler"); protokolle(msg);
  }finally{
    if (token===ZUSTAND.token){ ZUSTAND.laeuft=false; ZUSTAND.controller=null; }
  }
}
async function basisKorrigieren(){
  if (ZUSTAND.modus!=="echt"){ denkZeile("Basis korrigieren ist nur mit Helfer möglich.","warn"); return; }
  $("#btnBasis").classList.add("hidden");
  denkAktuell("Prüfe Prüfsumme und korrigiere die Basis …");
  try{
    var r=await fetch("/api/basis-korrigieren",{method:"POST",headers:apiHeaders()}),j=await r.json();
    denkZeile(j.out || "Unbekannte Antwort.",j.info?"info":j.ok?"ok":"err");
    denkAktuell(j.out || "Basis-Korrektur beendet.");
    if (j.ok && j.bereits_uebernommen){ ZUSTAND.override=null; hideSolution(); aktualisiereGrossenKnopf(); setAmpel("gelb","bereits übernommen"); }
    else if (j.ok){ ZUSTAND.override="zugit"; aktualisiereGrossenKnopf(); setAmpel("gruen","Basis korrigiert"); }
    else setAmpel("rot","Fehler");
  }catch(e){ denkZeile("Basis korrigieren fehlgeschlagen: "+e.message,"err"); }
}
function postfachUeberschreiben(){
  if (ZUSTAND.modus!=="echt") return;
  if ($("#btnOverwrite")) $("#btnOverwrite").classList.add("hidden");
  starteEcht("postfach","Überschreiben des vorhandenen Postfach-Patches bestätigt.",{daten:{force:true}});
}
function abbrechen(){
  if (!ZUSTAND.laeuft){
    denkZeile("Hinweis: Es läuft gerade kein Vorgang – „Abbrechen“ ist hier wirkungslos.", "warn");
    denkAktuell("Es läuft gerade keine Aktion.");
    return;
  }
  var echt=ZUSTAND.modus==="echt";
  if (ZUSTAND.controller){ try{ZUSTAND.controller.abort();}catch(e){} }
  ZUSTAND.controller=null;
  ZUSTAND.token++;
  ZUSTAND.laeuft = false;
  denkStatus("bereit", false);
  var abbruchText=echt ? "Anzeige abgebrochen. Der Helfer kann seine geprüften Schritte zu Ende führen; das ist kein Server-Abbruch." : "Simulation abgebrochen. Es wurde nichts verändert.";
  denkZeile(abbruchText, "warn");
  denkAktuell(abbruchText);
  protokolle(abbruchText);
  setAmpel("gelb", "abgebrochen");
  aktualisiereGrossenKnopf();
}

/* ============================================================
   Patch holen: Text, Datei oder Adresse
   ============================================================ */
function patchPruefe(){
  var patch=$("#patchText").value, meta=$("#patchMeta").value;
  var hatDiff=/(^|\n)diff --git /.test(patch), basis="";
  try{basis=String(JSON.parse(meta).basis || "").trim();}catch(e){basis="";}
  var voll=(hatDiff && !!basis) || !!ZUSTAND.patchArchiv, info=$("#patchInfo");
  info.className="paste-info "+(voll?"ok":"bad");
  if (ZUSTAND.patchArchiv) info.textContent="Patch-ZIP bereit: wird beim Eintragen binärgenau geprüft.";
  else if (!patch.trim() && !meta.trim()) info.textContent="Noch nichts eingefügt.";
  else info.textContent=(hatDiff?"Patch-Format erkannt ✓":"Es fehlt „diff --git“ am Zeilenanfang")+" · "+(basis?"Basis "+basis+" ✓":"json mit lesbarer Basis fehlt (Pflicht)");
  $("#patchOk").disabled=!voll;
}
function patchOeffnen(hinweis){
  ZUSTAND.patchHinweis=hinweis || "";
  ZUSTAND.patchArchiv=null;
  $("#patchText").value=""; $("#patchMeta").value=""; $("#patchUrl").value="";
  $("#patchDateiName").textContent="keine Datei gewählt";
  $("#patchModus").textContent=ZUSTAND.modus==="echt" ? "Echtbetrieb: Der Helfer prüft und schreibt ins GitHub-Gist. Das Token bleibt lokal." : "Demo: Eingabe wird geprüft, aber nur simuliert – es wird nichts ins Postfach geschrieben.";
  $("#patchOk").textContent=ZUSTAND.modus==="echt" ? "Ins Postfach legen" : "Simulation starten";
  patchPruefe();
  $("#patchDialog").classList.remove("hidden");
  $("#patchText").focus();
}
function patchSchliessen(){ $("#patchDialog").classList.add("hidden"); }
function patchSenden(){
  if ($("#patchOk").disabled) return;
  var daten=ZUSTAND.patchArchiv?{archiv:ZUSTAND.patchArchiv}:{patch:$("#patchText").value,meta:$("#patchMeta").value},hinweis=ZUSTAND.patchHinweis;
  patchSchliessen();
  if (ZUSTAND.modus==="echt") starteEcht("eintragen",hinweis,{daten:daten});
  else starteAktion("eintragen",hinweis);
}
function patchHolen(){
  var url=$("#patchUrl").value.trim();
  if (!url){ $("#patchInfo").textContent="Bitte zuerst eine Adresse einfügen."; $("#patchInfo").className="paste-info bad"; return; }
  if (ZUSTAND.modus!=="echt"){
    $("#patchInfo").textContent="„Von dort holen“ braucht den Helfer; in der Demo wird keine Adresse geladen.";
    $("#patchInfo").className="paste-info bad"; return;
  }
  var hinweis=ZUSTAND.patchHinweis;
  patchSchliessen();
  starteEcht("eintragen",hinweis,{pfad:"/api/patch-von-url",daten:{url:url}});
}

/* ============================================================
   Bestätigungs-Dialog
   ============================================================ */
var dialogZiel = null;
var dialogHinweis = "";
var dialogAusloeser = null;
function dialogOeffnen(id, kettenHinweis){
  var a = AKTEN[id];
  dialogZiel = id;
  dialogHinweis = kettenHinweis || "";
  dialogAusloeser = document.activeElement;
  var echt = ZUSTAND.modus === "echt";
  $("#dialogTitel").textContent = echt ? "Aktion bestätigen" : "Simulation bestätigen";
  $("#dialogWarn").textContent = echt ? "Diese Aktion verändert Daten. Der Helfer führt nur die gezeigte feste Aktion aus." : "Nur Vorschau: Es werden keine Dateien oder Online-Dienste verändert.";
    $("#dialogText").textContent = (echt ? "Ausführen: „" : "So würde „") + a.label + "“ (" + a.mark + ")" + (echt ? ":" : " im echten Projektmanager ablaufen:");
  $("#dialogVorschau").textContent = a.vorschau;
  $("#dialogVersion").textContent = GUI_VERSION;
  $("#dialogOk").textContent = echt ? "Ausführen" : "Simulation starten";
  $("#dialog").classList.remove("hidden");
  $("#dialogOk").focus();
}
function dialogSchliessen(){
  $("#dialog").classList.add("hidden");
  dialogZiel = null;
  dialogHinweis = "";
  if (dialogAusloeser && document.contains(dialogAusloeser)) dialogAusloeser.focus();
  dialogAusloeser = null;
}

/* ============================================================
   Reiter
   ============================================================ */
var REITER = {
  ablauf:function(){
    return '<h3>Ablauf – die vier Bereiche</h3>' +
      '<ol>' +
      '<li><b>01 · Übergabe an die KI</b> (oben links, zwingend) – was die KI von dir braucht: Stand prüfen, Eröffnungstext, Prüfbericht.</li>' +
      '<li><b>02 · Sichern des Projektes</b> (oben rechts, zwingend) – Reihenfolge: prüfen, speichern, Patch holen, Ins Postfach legen, Patch zu GitHub, Lokal aktualisieren, nach Hause.</li>' +
      '<li><b>03 · Status</b> – Diagnose und Spiel ansehen.</li>' +
      '<li><b>04 · Wartung</b> – alten Patch entfernen, Zweige aufräumen, abbrechen, beenden.</li>' +
      '</ol>' +
      '<h4>Der große Knopf</h4>' +
      '<p>Er zeigt <b>immer den Schritt, der gerade dran ist</b>. Willst du eine Kette ablaufen lassen, wählst du sie oben in der <b>Kette-Leiste</b> (oder per Gruppenüberschrift 01–04) – die aktive Kette leuchtet überall, und der große Knopf springt von selbst zum nächsten Schritt. Ein erneuter Klick auf die aktive Kette beendet sie.</p>' +
      '<h4>Stationsstraße</h4>' +
      '<p><code>① Aufgabe</code> → <code>② KI baut</code> → <code>③ Übernehmen</code> → <code>④ Sichern</code></p>';
  },
  so:function(){
    return '<h3>So funktioniert’s</h3>' +
      '<h4>Sicherheitsmodell: Nur Postfach-Zugriff für KI</h4>' +
      '<p>Der gespeicherte GitHub-Token besitzt <b>ausschließlich Gist-Rechte (<code>gist</code>)</b> und <b>keinen Schreibzugriff auf dein Projekt-Repository</b>. So kann weder eine KI-Sitzung noch das Gist-Postfach deinen Hauptzweig <code>main</code> direkt verändern.</p>' +
      '<h4>Der Weg eines Patches</h4>' +
      '<ol>' +
      '<li>Eigener Stand: <b>Offene Änderungen speichern</b> → <b>Ins Postfach legen</b> (bündelt alle lokalen Commits seit <code>origin/main</code>, warnt vor Überschreiben).</li>' +
      '<li>Im Dialog „Patch holen" → <b>KI-Anfrage kopieren</b> → STRG+V in den KI-Chat → KI liefert Patch (TXT mit Code + ZIP zum Download) → <b>Patch holen</b> (ins Postfach).</li>' +
      '<li><b>Patch zu GitHub</b>: Gist lesen → Prüfsumme → Basis → <code>git apply --check</code> → Zweig → Build → Pull Request (Freigabe) → zurück auf <code>main</code>.</li>' +
      '<li>Im Browser auf <b>Freigabe</b> (Merge) klicken, danach <b>Patch lokal nach Hause</b>.</li>' +
      '</ol>' +
      '<h4>Grundregeln (unverhandelbar)</h4>' +
      '<ol>' +
      '<li>Schreibende Aktionen müssen vorher bestätigt werden.</li>' +
      '<li>Das Token verlässt nie den lokalen Helfer (<code>~/.config/adventshaus/gist-token</code>, Rechte 600) und wird in allen Ausgaben gefiltert.</li>' +
      '<li>Der Helfer lauscht nur auf <code>127.0.0.1</code>, prüft Sitzungstoken und führt nur feste Aktionen aus.</li>' +
      '</ol>';
  },
  protokoll:function(){
    return '<h3>Protokoll</h3><div class="raster-log" id="rasterLog">' +
      (ZUSTAND.log.length ? ZUSTAND.log.slice(-200).join("\n") : "Noch nichts protokolliert.") + '</div>';
  },
  einstellungen:function(){
    var c=ZUSTAND.cfg;
    return '<h3>Einstellungen</h3>' +
      '<div class="pfad-raster">' +
      '<label class="k" for="cfgProjekt">Projektordner</label><input class="v cfg-inp" id="cfgProjekt" type="text" value="'+htmlEsc(c.projekt)+'">' +
      '<label class="k" for="cfgSicherung">Sicherung</label><input class="v cfg-inp" id="cfgSicherung" type="text" value="'+htmlEsc(c.sicherung)+'">' +
      '<label class="k" for="cfgKennung">Kennung</label><input class="v cfg-inp" id="cfgKennung" type="text" value="'+htmlEsc(c.kennung)+'">' +
      '<label class="k" for="cfgSpiel">Spiel-Adresse</label><input class="v cfg-inp" id="cfgSpiel" type="text" value="'+htmlEsc(c.spiel_url)+'">' +
      '<span class="k">Modus</span><span class="v">'+(ZUSTAND.modus==="echt"?"Echtbetrieb · Helfer "+htmlEsc(ZUSTAND.helperVersion):"Demo · kein Helfer")+'</span>' +
      '<span class="k">Helfer-Ordner</span><span class="v">'+htmlEsc(ZUSTAND.ordner || "nicht verbunden")+'</span>' +
      '</div>' +
      '<div class="token-zeile"><button class="mini ok" id="btnCfgSave">Pfade &amp; Einstellungen speichern</button><span id="cfgState" class="paste-info"></span></div>' +
      '<h4>GitHub-Token (nur Gist-Recht – kein Projektzugriff)</h4>' +
      '<div class="token-zeile">' +
        '<input id="inpToken" type="password" placeholder="ghp_… oder github_pat_…" autocomplete="off" spellcheck="false">' +
        '<button class="mini ok" id="btnTokenSave">Speichern</button>' +
        '<button class="mini" id="btnTokenTest">Echt testen</button>' +
        '<button class="mini abbruch" id="btnTokenDelete">Entfernen</button>' +
      '</div>' +
      '<p id="tokenState">Wird außerhalb von GUI und Projektordner in <code>~/.config/adventshaus/gist-token</code> (Rechte 600) gespeichert. Erneuern oder widerrufen unter <a href="https://github.com/settings/tokens" target="_blank" rel="noopener">github.com/settings/tokens</a>.</p>';
  }
};
var offenerReiter = null;
function zeigeReiter(name){
  offenerReiter = offenerReiter === name ? null : name;
  $$("#reiter button").forEach(function(b){
    var aktiv = b.getAttribute("data-reiter") === offenerReiter;
    b.classList.toggle("aktiv", aktiv);
    b.setAttribute("aria-expanded", String(aktiv));
  });
  var inhalt = $("#reiterInhalt");
  inhalt.classList.toggle("hidden", !offenerReiter);
  inhalt.innerHTML = offenerReiter ? REITER[offenerReiter]() : "";
  if (offenerReiter==="einstellungen") verdrahteEinstellungen();
}
function htmlEsc(s){
  return String(s == null ? "" : s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});
}
function aktualisiereFussPfade(){
  $("#pfadProjekt").textContent = ZUSTAND.cfg.projekt;
  $("#pfadSicherung").textContent = ZUSTAND.cfg.sicherung;
  var pf = $("#pfadPostfach");
  if (pf){
    if (ZUSTAND.modus !== "echt") pf.textContent = "nicht verbunden";
    else pf.textContent = ZUSTAND.tokenVorhanden ? "verbunden (Token bereit)" : "kein Token hinterlegt";
  }
}
function verdrahteEinstellungen(){
  var speichern=$("#btnTokenSave"), testen=$("#btnTokenTest"), loeschen=$("#btnTokenDelete"), cfgSave=$("#btnCfgSave");
  if (cfgSave) cfgSave.addEventListener("click", async function(){
    var st=$("#cfgState");
    if (ZUSTAND.modus!=="echt"){ st.textContent="Nur mit laufendem Helfer speicherbar."; return; }
    var daten={
      projekt:$("#cfgProjekt").value.trim(),
      sicherung:$("#cfgSicherung").value.trim(),
      kennung:$("#cfgKennung").value.trim(),
      spiel_url:$("#cfgSpiel").value.trim()
    };
    try{
      var r=await fetch("/api/einstellungen",{method:"POST",headers:apiHeaders({"Content-Type":"application/json"}),body:JSON.stringify(daten)}),j=await r.json();
      st.textContent=j.out || "Unbekannte Antwort.";
      st.className="paste-info "+(j.ok?"ok":"bad");
      if (j.ok && j.cfg){
        Object.keys(j.cfg).forEach(function(k){ ZUSTAND.cfg[k]=j.cfg[k]; });
        aktualisiereFussPfade();
      }
    }catch(e){ st.textContent="Fehler: "+e.message; st.className="paste-info bad"; }
  });
  if (speichern) speichern.addEventListener("click",async function(){
    var wert=$("#inpToken").value.trim(),status=$("#tokenState");
    if (!wert){status.textContent="Bitte Token einfügen.";return;}
    if (ZUSTAND.modus!=="echt"){status.textContent="Token speichern ist nur mit laufendem Helfer möglich; in der Demo wird nichts gespeichert.";return;}
    try{
      var r=await fetch("/api/token",{method:"POST",headers:apiHeaders({"Content-Type":"application/json"}),body:JSON.stringify({token:wert})}),j=await r.json();
      status.textContent=j.out || "Unbekannte Antwort.";
      if (j.ok){
        $("#inpToken").value="";
        ZUSTAND.tokenVorhanden=true;
        aktualisiereFussPfade();
      }
    }catch(e){status.textContent="Token nicht gespeichert: "+e.message;}
  });
  if (testen) testen.addEventListener("click",async function(){
    var status=$("#tokenState");
    if (ZUSTAND.modus!=="echt"){status.textContent="Kein Helfer verbunden – Tokenstatus kann nicht geprüft werden.";return;}
    status.textContent="Prüfe Token direkt gegen GitHub-Gist-API …";
    try{
      var r=await fetch("/api/token-test",{method:"POST",headers:apiHeaders()}),j=await r.json();
      status.textContent=(j.out || "Unbekannte Antwort.") + (j.loesung ? " " + j.loesung : "");
      ZUSTAND.tokenVorhanden=!!j.ok;
      aktualisiereFussPfade();
    }catch(e){status.textContent="Token-Test fehlgeschlagen: "+e.message;}
  });
  if (loeschen) loeschen.addEventListener("click",async function(){
    var status=$("#tokenState");
    if (ZUSTAND.modus!=="echt"){status.textContent="Kein Helfer verbunden.";return;}
    try{
      var r=await fetch("/api/token-loeschen",{method:"POST",headers:apiHeaders()}),j=await r.json();
      status.textContent=(j.out || "Entfernt.") + (j.loesung ? " " + j.loesung : "");
      if (j.ok){
        $("#inpToken").value="";
        ZUSTAND.tokenVorhanden=false;
        aktualisiereFussPfade();
      }
    }catch(e){status.textContent="Entfernen fehlgeschlagen: "+e.message;}
  });
}

/* ============================================================
   Helfer-Erkennung und Banner (Demo gelb, Echtbetrieb grün)
   ============================================================ */
function bannerCode(s){ var c = document.createElement("code"); c.textContent = s; return c; }
function bannerFett(s){ var b = document.createElement("b"); b.textContent = s; return b; }
function setzeBanner(modus, info){
  info = info || {};
  var b = $("#modusBanner"), t = $("#modusText");
  b.className = "banner " + (modus === "echt" ? "modus-echt" : modus === "fehler" ? "fehler" : "modus-demo");
  t.textContent = "";
  function txt(s){ t.appendChild(document.createTextNode(s)); }
  if (modus === "echt"){
    t.appendChild(bannerFett("Echter Modus"));
    txt(" – Helfer verbunden (" + (info.host || location.host) + ") · ");
    t.appendChild(bannerFett("Version " + (info.helfer || "?")));
    txt(" (GUI " + GUI_VERSION + ")");
    if (info.ordner){ txt(" · Ordner: "); t.appendChild(bannerCode(info.ordner)); }
    txt(". Die Knöpfe führen echte git-/Postfach-Schritte aus.");
    $("#modusVersion").textContent = "Echtbetrieb";
  } else if (modus === "fehler"){
    t.appendChild(bannerFett(info.richtung || "Versionen passen nicht"));
    txt(" – Helfer " + (info.helfer || "?") + ", GUI " + GUI_VERSION + ". Bitte Helfer beenden und neu starten; danach Version und Ordner prüfen.");
    $("#modusVersion").textContent = "kein Echtbetrieb";
  } else {
    t.appendChild(bannerFett("Demo-Modus"));
    txt(" – reine Simulation, es wird nichts verändert · ");
    t.appendChild(bannerFett("Version " + GUI_VERSION));
    txt(" · Ordner: "); t.appendChild(bannerCode("nicht verbunden"));
    txt(". Für echten Betrieb: Helfer starten (");
    t.appendChild(bannerCode("./start.sh"));
    txt(") und "); t.appendChild(bannerCode("http://127.0.0.1:8790/")); txt(" öffnen.");
    $("#modusVersion").textContent = "kein Echtbetrieb";
  }
}
async function detecteModus(){
  $("#versionAnzeige").textContent="GUI "+GUI_VERSION;
  setzeBanner("demo");
  ZUSTAND.modus="demo";
  aktualisiereFussPfade();
  if (location.protocol==="file:" || typeof fetch!=="function") return;
  var controller=typeof AbortController==="function" ? new AbortController() : null;
  var timer=controller ? setTimeout(function(){controller.abort();},1600) : null;
  try{
    var optionen={cache:"no-store",headers:apiHeaders()}; if (controller) optionen.signal=controller.signal;
    var r=await fetch("/api/status",optionen);
    if (!r.ok) throw new Error("HTTP "+r.status);
    var j=await r.json();
    if (!j || j.helfer!==true) throw new Error("kein Projektmanager-Helfer");
    ZUSTAND.modus="echt";
    ZUSTAND.helperVersion=String(j.version || "?");
    ZUSTAND.ordner=j.ordner || "";
    ZUSTAND.tokenVorhanden=!!j.token;
    ZUSTAND.versionKonflikt=ZUSTAND.helperVersion!==GUI_VERSION;
    if (j.cfg) Object.keys(ZUSTAND.cfg).forEach(function(k){if (j.cfg[k]!=null) ZUSTAND.cfg[k]=j.cfg[k];});
    aktualisiereFussPfade();
    if (ZUSTAND.versionKonflikt){
      var neuer=versionsVergleich(ZUSTAND.helperVersion,GUI_VERSION);
      var richtung=neuer>0?"Die GUI ist älter als der Helfer":neuer<0?"Der Helfer ist älter als die GUI":"Versionsangaben unterscheiden sich";
      setzeBanner("fehler",{helfer:ZUSTAND.helperVersion,richtung:richtung});
    }else{
      setzeBanner("echt",{helfer:ZUSTAND.helperVersion,ordner:ZUSTAND.ordner,host:location.host});
    }
    setAmpel("gelb","noch nicht geprüft");
    aktualisiereGrossenKnopf();
    protokolle("Helfer verbunden: "+ZUSTAND.helperVersion+" · "+ZUSTAND.ordner);
  }catch(e){
    ZUSTAND.modus="demo";
    setzeBanner("demo");
    aktualisiereFussPfade();
  }finally{
    if (timer) clearTimeout(timer);
  }
}

/* ============================================================
    Portables ZIP: aktuelle HTML-Vorschau samt eigener ZIP-Erzeugung.
   ============================================================ */
function portableHTML(){
  var kopie = document.documentElement.cloneNode(true);
  function c(id){ return kopie.querySelector("#" + id); }
  kopie.querySelectorAll('meta[name="projektmanager-csrf"]').forEach(function(m){ m.remove(); });
  kopie.querySelectorAll("style:not(#appStyles)").forEach(function(stil){ stil.remove(); });
  ["kn-01","kn-02","kn-03","kn-04"].forEach(function(id){ c(id).textContent = ""; });
  kopie.querySelector(".g-mitte").removeAttribute("style");
  kopie.querySelectorAll(".kl-chip.aktiv, .kette-start.aktiv").forEach(function(el){ el.classList.remove("aktiv"); });
  kopie.querySelectorAll(".kette-hinweis").forEach(function(h){ h.textContent = "Start →"; });
  if (c("klStatus")){ c("klStatus").textContent = "keine Kette aktiv – hier oder per Gruppenüberschrift starten"; c("klStatus").className = "kl-status"; }
  if (c("wkBestaetigung")) c("wkBestaetigung").classList.add("hidden");
  if (c("wkNormal")) c("wkNormal").classList.remove("hidden");
  c("grossSymbol").textContent = "✓";
  c("grossLabel").textContent = "Stand prüfen";
  c("grossSub").textContent = "Vorschau · Diagnose";
  c("grossKette").textContent = "Kette über eine Überschrift starten";
  c("denkAktuell").textContent = "Bereit für deinen nächsten Schritt.";
  c("denkListe").innerHTML = '<li class="info"><span class="m">›</span><span>Hinweise und Prüfschritte erscheinen hier.</span></li>';
  c("denkStatus").classList.remove("laeuft");
  if (c("denkFortschritt")) c("denkFortschritt").classList.remove("laeuft");
  c("denkStatusText").textContent = "bereit";
  c("abschnittBefehl").classList.add("hidden");
  c("abschnittProtokoll").classList.add("hidden");
  c("protokollText").textContent = "–";
  c("befehlText").textContent = "–";
  ["btnBefehl","btnProtokoll"].forEach(function(id){
    c(id).classList.remove("aktiv");
    c(id).setAttribute("aria-expanded", "false");
  });
  c("btnBericht").classList.add("hidden");
  c("btnBasis").classList.add("hidden");
  if (c("btnOverwrite")) c("btnOverwrite").classList.add("hidden");
  c("solveLink").classList.add("hidden");
  c("patchDialog").classList.add("hidden");
  c("modusBanner").className="banner modus-demo";
  c("modusText").innerHTML='<b>Demo-Modus</b> – reine Simulation, es wird nichts verändert · <b>Version '+GUI_VERSION+'</b> · Ordner: <code>nicht verbunden</code>. Für echten Betrieb: Helfer starten (<code>./start.sh</code>) und <code>http://127.0.0.1:8790/</code> öffnen.';
  c("modusVersion").textContent="kein Echtbetrieb";
  c("versionAnzeige").textContent="GUI "+GUI_VERSION;
  c("pfadProjekt").textContent="~/projekte/adventshaus";
  c("pfadSicherung").textContent="~/sicherung/adventshaus.git";
  if (c("pfadPostfach")) c("pfadPostfach").textContent="nicht verbunden";
  c("reiterInhalt").classList.add("hidden");
  c("reiterInhalt").textContent = "";
  kopie.querySelectorAll("#reiter button").forEach(function(b){
    b.classList.remove("aktiv");
    b.setAttribute("aria-expanded", "false");
  });
  c("dialog").classList.add("hidden");
  ["dialogWarn","dialogText","dialogVorschau","dialogVersion"].forEach(function(id){ c(id).textContent = ""; });
  c("ampelText").textContent = "Vorschau";
  kopie.querySelectorAll(".lampe").forEach(function(l){ l.classList.remove("aktiv"); });
  c("lampeGelb").classList.add("aktiv");
  return "<!DOCTYPE html>\n" + kopie.outerHTML + "\n";
}

var CRC_TABELLE = (function(){
  var t = new Uint32Array(256);
  for (var n=0;n<256;n++){
    var c=n;
    for (var k=0;k<8;k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
    t[n]=c >>> 0;
  }
  return t;
})();
function crc32(bytes){
  var c=0xffffffff;
  for (var i=0;i<bytes.length;i++) c=CRC_TABELLE[(c ^ bytes[i]) & 255] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function zipSpeichern(dateien){
  var encoder=new TextEncoder();
  var eintraege=dateien.map(function(datei){
    var name=encoder.encode(datei.name);
    var daten=encoder.encode(datei.text);
    if (name.length > 65535 || daten.length > 0xffffffff) throw new Error("Datei zu groß für ZIP.");
    return {name:name, daten:daten, crc:crc32(daten), offset:0};
  });
  var jetzt=new Date();
  var zeit=(jetzt.getHours()<<11)|(jetzt.getMinutes()<<5)|(jetzt.getSeconds()>>1);
  var datum=((Math.max(1980,jetzt.getFullYear())-1980)<<9)|((jetzt.getMonth()+1)<<5)|jetzt.getDate();
  var teile=[], position=0;
  function anfuegen(bytes){ teile.push(bytes); position+=bytes.length; }
  function header(laenge){ var bytes=new Uint8Array(laenge); return {bytes:bytes, view:new DataView(bytes.buffer)}; }
  eintraege.forEach(function(e){
    e.offset=position;
    var h=header(30+e.name.length),v=h.view;
    v.setUint32(0,0x04034b50,true); v.setUint16(4,20,true);
    v.setUint16(6,0x0800,true); v.setUint16(8,0,true);
    v.setUint16(10,zeit,true); v.setUint16(12,datum,true);
    v.setUint32(14,e.crc,true); v.setUint32(18,e.daten.length,true);
    v.setUint32(22,e.daten.length,true); v.setUint16(26,e.name.length,true);
    h.bytes.set(e.name,30); anfuegen(h.bytes); anfuegen(e.daten);
  });
  var zentralStart=position;
  eintraege.forEach(function(e){
    var h=header(46+e.name.length),v=h.view;
    v.setUint32(0,0x02014b50,true); v.setUint16(4,20,true);
    v.setUint16(6,20,true); v.setUint16(8,0x0800,true);
    v.setUint16(10,0,true); v.setUint16(12,zeit,true);
    v.setUint16(14,datum,true); v.setUint32(16,e.crc,true);
    v.setUint32(20,e.daten.length,true); v.setUint32(24,e.daten.length,true);
    v.setUint16(28,e.name.length,true); v.setUint32(42,e.offset,true);
    h.bytes.set(e.name,46); anfuegen(h.bytes);
  });
  var zentralLaenge=position-zentralStart;
  var ende=header(22),v=ende.view;
  v.setUint32(0,0x06054b50,true);
  v.setUint16(8,eintraege.length,true); v.setUint16(10,eintraege.length,true);
  v.setUint32(12,zentralLaenge,true); v.setUint32(16,zentralStart,true);
  anfuegen(ende.bytes);
  var zip=new Uint8Array(position), at=0;
  teile.forEach(function(teil){ zip.set(teil,at); at+=teil.length; });
  var pruef=new DataView(zip.buffer);
  if (pruef.getUint32(position-22,true)!==0x06054b50 ||
      pruef.getUint32(position-6,true)!==zentralStart ||
      pruef.getUint16(position-12,true)!==eintraege.length) throw new Error("ZIP-Abschluss ungültig.");
  var zentral=zentralStart;
  eintraege.forEach(function(e){
    var start=e.offset, datenStart=start+30+e.name.length;
    if (pruef.getUint32(start,true)!==0x04034b50 ||
        pruef.getUint32(start+14,true)!==crc32(zip.subarray(datenStart,datenStart+e.daten.length)) ||
        pruef.getUint32(start+18,true)!==e.daten.length ||
        pruef.getUint32(zentral,true)!==0x02014b50 ||
        pruef.getUint32(zentral+42,true)!==start ||
        pruef.getUint32(zentral+16,true)!==e.crc) throw new Error("ZIP-Eintrag ungültig.");
    zentral+=46+e.name.length;
  });
  if (zentral!==position-22) throw new Error("ZIP-Verzeichnis unvollständig.");
  return zip;
}
function quell(id){
  var n=document.getElementById(id);
  if (!n) throw new Error("Eingebettete Quelle fehlt: "+id);
  return n.textContent.replace(/^\n/,"");
}
function paketDateien(){
  var dateien=[
    {name:"index.html",text:portableHTML()},
    {name:"style.css",text:quell("appStyles")},
    {name:"projektmanager.js",text:quell("appScript")},
    {name:"projektmanager.py",text:quell("src-python")},
    {name:"start.sh",text:quell("src-start")},
    {name:"stop.sh",text:quell("src-stop")},
    {name:"neustart.sh",text:quell("src-neustart")},
    {name:"install-desktop.sh",text:quell("src-install")},
    {name:"einstellungen.json",text:quell("src-einstellungen")},
    {name:"README.md",text:quell("src-readme")},
    {name:"HISTORIE.md",text:quell("src-historie")}
  ];
  dateien.forEach(function(d){
    if (!d.text || !d.text.trim()) throw new Error("Leere Paketdatei: "+d.name);
  });
  return dateien;
}
function zipLaden(){
  try{
    var dateien=paketDateien();
    var zip=zipSpeichern(dateien);
    var url=URL.createObjectURL(new Blob([zip],{type:"application/zip"}));
    var link=document.createElement("a");
    link.href=url;
    link.download="projektmanager-"+GUI_VERSION+".zip";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function(){URL.revokeObjectURL(url);},60000);
    var msg="Vollständiges ZIP erstellt: "+link.download+" – "+dateien.length+" Dateien, inklusive projektmanager.py, Start-/Stop-Skripten, Konfiguration und HISTORIE.";
    denkZeile(msg,"ok"); denkAktuell(msg); protokolle(msg);
  }catch(err){
    denkZeile("ZIP konnte nicht erstellt werden: "+err.message,"err");
  }
}
function textDatei(name, text){
  var blob = new Blob([text], {type:"text/plain;charset=utf-8"});
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a); a.click();
  a.remove();
  setTimeout(function(){ try { URL.revokeObjectURL(a.href); } catch (e) {} }, 60000);
}
function entwicklerInfo(){
  try{
    var dateien=paketDateien();
    var t=["PROJEKTMANAGER (ADVENTSHAUS) – ENTWICKLER-INFO (vollständig)",
      "Erzeugt: "+new Date().toLocaleString("de-DE")+" · GUI/Helfer-Paket "+GUI_VERSION,
      "Modus beim Export: "+(ZUSTAND.modus==="echt"?"Echtbetrieb":"Demo – Quellen trotzdem vollständig"),"",
      "ZWECK: Stand und nächster Schritt für den KI-Ablauf; kein Teil des Spiels.",
      "SICHERHEIT: Helfer nur 127.0.0.1, Sitzungstoken, feste Aktionen, Token nur im Helfer.",
      "REGEL: Diese Entwickler-Info enthält den gesamten Quellcode aller Komponenten",
      "und die gesamte HISTORIE.md. Diese Anweisung bleibt bei jeder Änderung bestehen.",
      "HISTORIE.md ist bei jeder Änderung fortzuschreiben.","",
      "DATEIEN: "+dateien.map(function(d){return d.name;}).join(", "),""];
    dateien.forEach(function(d){
      t.push("================================================================================");
      t.push("BEGIN DATEI: "+d.name);
      t.push("================================================================================");
      t.push(d.text.replace(/\s+$/,""));
      t.push("END DATEI: "+d.name); t.push("");
    });
    t.push("ENDE DER ENTWICKLER-INFO");
    var text=t.join("\n");
    textDatei("Projektmanager-Entwicklerinfo.txt",text);
    var kb=Math.max(1,Math.round(new TextEncoder().encode(text).length/1024));
    denkZeile("Entwickler-Info heruntergeladen: "+kb+" KB – vollständiger Quellcode aller "+dateien.length+" Komponenten und gesamte HISTORIE.","ok");
    protokolle("Entwickler-Info vollständig erzeugt: "+kb+" KB");
  }catch(e){denkZeile("Entwickler-Info fehlgeschlagen: "+e.message,"err");}
}

function beispielberichtKopieren(){
  var echt=ZUSTAND.modus==="echt" && ZUSTAND.bericht;
  var text=echt ? ZUSTAND.bericht : ["ADVENTSHAUS - BEISPIELBERICHT", "Nur Demo. Keine echten Projektdaten wurden geprüft.", ""]
    .concat(ABLauf.pruefbericht.map(function(s){ return "Beispiel: " + s[0]; })).join("\n");
  kopiereText(text).then(function(ok){
    denkZeile(ok ? (echt?"Echter Prüfbericht kopiert.":"Beispielbericht kopiert – ausdrücklich keine echten Projektdaten.") : "Kopieren nicht möglich; Zwischenablage unverändert.",ok?"ok":"warn");
    if (ok) protokolle(echt?"Prüfbericht kopiert":"Beispielbericht kopiert");
  });
}

/* ============================================================
   Werkzeugleiste (Start / Neu starten / Beenden)
   ============================================================ */
var werkzeugConfirm = null;
function zeigeWerkzeugLeiste(){
  var norm = $("#wkNormal"), best = $("#wkBestaetigung"), txt = $("#wkBestaetigungText");
  if (!norm || !best) return;
  if (werkzeugConfirm){
    norm.classList.add("hidden");
    best.classList.remove("hidden");
    if (txt) txt.textContent = (werkzeugConfirm === "neustart" ? "„Neu starten“" : "„Beenden“") + " – wirklich?";
  } else {
    norm.classList.remove("hidden");
    best.classList.add("hidden");
  }
}
function werkzeugAktion(akt){
  if (akt === "start"){
    if (ZUSTAND.modus === "echt"){
      denkZeile("Helfer läuft bereits (Version " + ZUSTAND.helperVersion + ").", "info");
    } else {
      denkZeile("Kein Helfer verbunden. Start: bash start.sh im Helfer-Ordner oder Desktop-Knopf.", "info");
    }
    return;
  }
  if (ZUSTAND.modus !== "echt"){ denkZeile("Nur mit laufendem Helfer möglich.", "info"); return; }
  if (ZUSTAND.laeuft){ denkZeile("Erst den laufenden Vorgang abwarten oder abbrechen.", "warn"); return; }
  if (akt === "neustart"){
    denkZeile("Helfer wird neu gestartet … die Seite lädt automatisch neu.", "info");
    setzeBanner("demo");
    fetch("/api/neustart", {method: "POST", headers: apiHeaders()}).then(function(r){ return r.json(); }).then(function(j){
      denkZeile(j.out || "Neustart …", "info");
      setTimeout(function(){ location.reload(); }, 2600);
    }).catch(function(e){
      denkZeile("Neustart-Auslösung fehlgeschlagen: " + e.message, "err");
      setTimeout(function(){ location.reload(); }, 1600);
    });
  } else if (akt === "beenden"){
    denkZeile("Helfer wird beendet …", "warn");
    fetch("/api/beenden", {method: "POST", headers: apiHeaders()}).then(function(r){ return r.json(); }).then(function(j){
      denkZeile(j.out || "Helfer beendet.", "warn");
      ZUSTAND.modus = "demo";
      setzeBanner("demo");
      setAmpel("gelb", "Helfer beendet");
      denkStatus("Helfer beendet", false);
      ZUSTAND.tokenVorhanden = false;
      aktualisiereFussPfade();
      aktualisiereKettenAnzeige();
      denkZeile("Neu starten über „Neu starten“ (nach Neustart des Helfers) oder Desktop-Knopf.", "info");
    }).catch(function(e){ denkZeile("Beenden fehlgeschlagen: " + e.message, "err"); });
  }
}

/* ============================================================
   Start
   ============================================================ */
function init(){
  baueKnöpfe();

  $("#grossKnopf").addEventListener("click", function(){
    var id = naechsterSchritt();
    if (!id){ denkZeile("Es ist nichts offen. Klicke eine Überschrift 01–04, um eine Kette zu starten.", "info"); return; }
    klickAktion(id);
  });

  $$(".kette-start").forEach(function(b){
    b.addEventListener("click", function(){ ketteStarten(b.getAttribute("data-kette")); });
  });

  $$(".kl-chip").forEach(function(c){
    c.addEventListener("click", function(){
      var gid = c.getAttribute("data-kette");
      if (ZUSTAND.kette && ZUSTAND.kette.gruppe === gid){
        ZUSTAND.kette = null;
        denkZeile("Kette „" + gruppeVon(gid).titel + "“ beendet (erneuter Klick).", "info");
        protokolle("Kette beendet: " + gruppeVon(gid).titel);
      } else {
        ketteStarten(gid);
      }
      aktualisiereKettenAnzeige();
    });
  });

  $("#btnAbbruch").addEventListener("click", abbrechen);
  $("#btnBefehl").addEventListener("click", function(){
    var a = $("#abschnittBefehl");
    a.classList.toggle("hidden");
    $("#btnBefehl").classList.toggle("aktiv", !a.classList.contains("hidden"));
    $("#btnBefehl").setAttribute("aria-expanded", String(!a.classList.contains("hidden")));
    if (!a.classList.contains("hidden")) $("#denkBody").scrollTop = $("#denkBody").scrollHeight;
  });
  $("#btnProtokoll").addEventListener("click", function(){
    var a = $("#abschnittProtokoll");
    a.classList.toggle("hidden");
    $("#btnProtokoll").classList.toggle("aktiv", !a.classList.contains("hidden"));
    $("#btnProtokoll").setAttribute("aria-expanded", String(!a.classList.contains("hidden")));
    if (!a.classList.contains("hidden")) $("#denkBody").scrollTop = $("#denkBody").scrollHeight;
  });
  $("#btnBericht").addEventListener("click", beispielberichtKopieren);
  $("#btnBasis").addEventListener("click", basisKorrigieren);
  if ($("#btnOverwrite")) $("#btnOverwrite").addEventListener("click", postfachUeberschreiben);
  $("#patchAnfrage").addEventListener("click", anfrageKiKopieren);
  $("#patchOk").addEventListener("click", patchSenden);
  $("#patchAbbrechen").addEventListener("click", patchSchliessen);
  $("#patchHolen").addEventListener("click", patchHolen);
  $("#patchText").addEventListener("input", patchPruefe);
  $("#patchMeta").addEventListener("input", patchPruefe);
  $("#patchDateiKnopf").addEventListener("click", function(){$("#patchDatei").click();});
  $("#patchDatei").addEventListener("change", function(e){
    var f=e.target.files && e.target.files[0]; if (!f) return;
    var name=String(f.name||"").toLowerCase();
    if (name.endsWith(".zip") || f.type==="application/zip" || f.type==="application/x-zip-compressed"){
      if (f.size>16*1024*1024){ $("#patchDateiName").textContent="ZIP zu groß (maximal 16 MiB)."; return; }
      var zr=new FileReader();
      zr.onload=function(){
        try{
          var bytes=new Uint8Array(zr.result), bin="";
          for(var i=0;i<bytes.length;i+=8192){ bin+=String.fromCharCode.apply(null, bytes.subarray(i,i+8192)); }
          ZUSTAND.patchArchiv=btoa(bin);
          $("#patchText").value=""; $("#patchMeta").value="";
          $("#patchDateiName").textContent="ZIP gelesen: "+f.name;
          patchPruefe();
        }catch(err){ $("#patchDateiName").textContent="ZIP konnte nicht gelesen werden."; }
      };
      zr.onerror=function(){$("#patchDateiName").textContent="ZIP konnte nicht gelesen werden.";};
      zr.readAsArrayBuffer(f); e.target.value=""; return;
    }
    ZUSTAND.patchArchiv=null;
    var fr=new FileReader();
    fr.onload=function(){
      var text=String(fr.result || "");
      if (text.trim().startsWith("{")) $("#patchMeta").value=text;
      else $("#patchText").value=text;
      $("#patchDateiName").textContent="Datei gelesen: "+f.name;
      patchPruefe();
    };
    fr.onerror=function(){$("#patchDateiName").textContent="Datei konnte nicht gelesen werden.";};
    fr.readAsText(f); e.target.value="";
  });
  $("#patchDialog").addEventListener("click",function(e){if(e.target===this)patchSchliessen();});

  $("#dialogOk").addEventListener("click", function(){
    var id = dialogZiel;
    var hinweis = dialogHinweis;
    dialogSchliessen();
    if (id) starteAktion(id, hinweis);
  });
  $("#dialogAbbrechen").addEventListener("click", function(){
    denkZeile("Abgebrochen – es wurde nichts verändert.", "warn");
    dialogSchliessen();
  });
  $("#dialog").addEventListener("click", function(e){ if (e.target === this) dialogSchliessen(); });

  $$("#reiter button").forEach(function(b){
    b.addEventListener("click", function(){ zeigeReiter(b.getAttribute("data-reiter")); });
  });

  $("#btnZip").addEventListener("click", zipLaden);
  $("#btnInfo").addEventListener("click", entwicklerInfo);

  document.addEventListener("keydown", function(e){
    var dialogOffen = !$("#dialog").classList.contains("hidden");
    if (e.key === "Tab" && dialogOffen){
      var erster = $("#dialogAbbrechen");
      var letzter = $("#dialogOk");
      if (e.shiftKey && (document.activeElement === erster || !$("#dialog").contains(document.activeElement))){
        e.preventDefault(); letzter.focus();
      } else if (!e.shiftKey && document.activeElement === letzter){
        e.preventDefault(); erster.focus();
      }
    }
    if (e.key === "Escape"){
      if (!$("#patchDialog").classList.contains("hidden")) patchSchliessen();
      else if (dialogOffen) dialogSchliessen();
      else abbrechen();
    }
  });

  aktualisiereGrossenKnopf();
  aktualisiereKettenAnzeige();
  setAmpel("gelb", "Vorschau");
  detecteModus();
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
})();
