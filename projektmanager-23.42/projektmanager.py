#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adventshaus · Projektmanager — lokaler Helfer, nur 127.0.0.1, Sitzungstoken und feste Aktionen."""
import json
import os
import re
import time
import subprocess
import hashlib
import webbrowser
import signal
import shutil
import tempfile
import secrets
import hmac
import socket
import threading
import http.server
import socketserver
import urllib.request
import urllib.error
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
TOKEN_PATH = os.path.join(HOME, ".config", "adventshaus", "gist-token")
GIST_ID = "f28cc85bf67f8a7f2fa6251a2092a33c"
GIST_API = "https://api.github.com/gists/" + GIST_ID
GIST_URL = "https://gist.github.com/Chihuaua/" + GIST_ID
REPO_URL = "https://github.com/Chihuaua/adventshaus"
CONFIG = os.path.join(HERE, "einstellungen.json")
PID_FILE = os.path.join(HERE, "projektmanager.pid")
HELPER_VERSION = "23.42"
GUI_HINT = "23.42"
SESSION_TOKEN = secrets.token_hex(24)
GAME_PROC = None
GAME_LOG = os.path.join(tempfile.gettempdir(), "adventshaus-spiel.log")

SENSITIVE_FILE_RE = re.compile(
    r"(^|/)\.env($|\.)|gist-token|id_rsa|id_ed25519|\.pem$|\.key$|\.p12$|credentials\.json|secrets?\.",
    re.I,
)


def load_config():
    d = {
        "projekt": "~/projekte/adventshaus",
        "sicherung": "~/sicherung/adventshaus.git",
        "kennung": "KI-B",
        "port": 8790,
        "spiel_url": "http://localhost:5173/",
    }
    try:
        with open(CONFIG, encoding="utf-8") as f:
            raw = json.load(f)
            for k in ("projekt", "sicherung", "kennung", "port", "spiel_url"):
                if k in raw and raw[k] is not None:
                    d[k] = raw[k]
    except Exception:
        pass
    for k in ("projekt", "sicherung"):
        d[k] = os.path.expanduser(str(d[k]))
    return d


CFG = load_config()


def read_token():
    try:
        with open(TOKEN_PATH, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def scrub(text, token=""):
    text = text if isinstance(text, str) else str(text)
    if token:
        text = text.replace(token, "***")
    if SESSION_TOKEN:
        text = text.replace(SESSION_TOKEN, "***")
    return re.sub(r"(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+)", "gh***", text)


def run(cmd, cwd=None, input_text=None, token="", timeout=180, limit=4000):
    tok = token or read_token()
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = scrub((r.stdout or "") + (r.stderr or ""), tok).strip()
        if limit is not None:
            out = out[:limit]
        return {"ok": r.returncode == 0, "code": r.returncode, "out": out}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "out": "Zeitüberschreitung nach %s s" % timeout}
    except Exception as e:
        return {"ok": False, "code": -1, "out": scrub(str(e), tok)}


def git_klar(text):
    if not text:
        return ""
    t = re.split(r"Hinweis:|hint:|Disable this message", str(text).replace("\n", " "))[0].strip()
    pfade = []
    for p in re.findall(r"[\w./-]+\.(?:md|ts|tsx|js|jsx|json|css|html|py|sh|mjs)", t):
        if p not in pfade:
            pfade.append(p)
    betroffen = (" Betroffen: " + ", ".join(pfade[:3]) + ".") if pfade else ""
    muster = [
        (
            r"bereitgestellt|already (exists|present)|would be overwritten|bereits vorhanden",
            "Der Patch führt eine Datei als neu ein, die es im Projekt schon gibt.",
            "Die KI muss den Patch auf den aktuellen Stand neu aufsetzen.",
        ),
        (
            r"konnte nicht angewendet|nicht angewendet|Anwendung des Patches fehlgeschlagen|does not apply|Patch failed|CONFLICT|Konflikt",
            "Der Patch passt nicht zum aktuellen Stand.",
            "Die KI muss ihn neu aufsetzen.",
        ),
        (
            r"another git am|am process already running|rebase-apply",
            "Es steckt noch ein unvollendeter Patch-Vorgang im Projekt.",
            "„Stand prüfen“ räumt das beim nächsten Aufruf auf.",
        ),
        (
            r"not a git repository|Kein Git-Repository",
            "Der Projektordner ist kein Git-Repository.",
            "Pfad „projekt“ in den Einstellungen prüfen.",
        ),
        (
            r"must be run in a work tree|Arbeitsverzeichnis",
            "Diese Operation braucht ein Arbeitsverzeichnis; der Ordner ist ein Bare-Repository.",
            "Sicherungspfad prüfen.",
        ),
        (r"nothing to commit|nichts zu committen", "Es gibt nichts zu speichern.", ""),
        (r"Permission denied|Zugriff verweigert", "Keine Schreibberechtigung.", "Ordnerrechte prüfen."),
        (r"could not resolve host|Could not resolve", "Kein Internetzugang zu GitHub.", "Verbindung prüfen."),
        (r"timed out|Timeout|Zeitüberschreitung", "Ein Schritt hat zu lange gedauert.", "Verbindung prüfen und erneut versuchen."),
        (r"Authentication failed|could not read Username|403|401", "GitHub-Anmeldung für Git-Push fehlgeschlagen.", "Lokale Git-/gh-Anmeldung prüfen."),
        (r"corrupt patch",
         "Der Patch-Text ist unvollständig oder defekt (typisch: beim Kopieren aus dem Chat abgeschnitten).",
         "KI den Patch komplett neu liefern lassen – am besten als Datei/ZIP („KI-Anfrage kopieren“), nicht als Chat-Text."),
    ]
    for pat, klar, loesung in muster:
        if re.search(pat, t, re.I):
            return klar + betroffen + ((" " + loesung) if loesung else "")
    kurz = re.sub(r"^(?:Fehler|error|fatal):\s*", "", t).strip()
    return "Git meldet: " + kurz[:160] + betroffen


def _git_ident(proj, token=""):
    if run(["git", "config", "user.email"], cwd=proj, token=token)["out"].strip():
        return ["git"]
    return ["git", "-c", "user.email=projektmanager@lokal", "-c", "user.name=Projektmanager"]


def _commit_ident(proj, token=""):
    return _git_ident(proj, token=token) + ["commit"]


def git_geraeumig(proj, token=""):
    try:
        gd = run(["git", "rev-parse", "--git-dir"], cwd=proj, token=token)["out"].strip()
        if not gd:
            return False
        pfad = gd if os.path.isabs(gd) else os.path.join(proj, gd)
        if os.path.isdir(os.path.join(pfad, "rebase-apply")):
            return run(_git_ident(proj, token=token) + ["am", "--abort"], cwd=proj, token=token)["ok"]
    except Exception:
        pass
    return False


def _origin_main_kurz(proj, token=""):
    r = run(["git", "ls-remote", "origin", "refs/heads/main"], cwd=proj, token=token, timeout=20)
    if r["ok"] and r["out"].strip():
        return r["out"].split()[0][:7]
    r_local = run(["git", "rev-parse", "--short", "origin/main"], cwd=proj, token=token)
    if r_local["ok"] and r_local["out"].strip():
        return r_local["out"].strip()
    return ""


class GistRequestError(Exception):
    def __init__(self, out, loesung=""):
        super().__init__(out)
        self.out = out
        self.loesung = loesung


def _http_fehler_detail(e, token=""):
    try:
        detail = e.read().decode(errors="ignore")[:240]
    except Exception:
        detail = ""
    if e.code == 401:
        return (
            "GitHub-Token ungültig oder abgelaufen (HTTP 401).",
            "Reiter Einstellungen → neuen Gist-Token einfügen → Speichern → Testen.",
        )
    if e.code == 403:
        return (
            "Zugriff auf das Postfach verweigert oder Rate-Limit erreicht (HTTP 403).",
            "Prüfe, ob der Token das Recht „gist“ besitzt.",
        )
    if e.code == 404:
        return (
            "Postfach-Gist nicht gefunden (HTTP 404).",
            "Prüfe, ob der Token Zugriff auf geheime Gists hat und die Gist-ID stimmt.",
        )
    return (
        "HTTP %s%s" % (e.code, (": " + scrub(detail, token)) if detail else ""),
        "Verbindung und Postfach-Status prüfen.",
    )


def _gist_request(method, token, payload=None, timeout=45):
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "Adventshaus-Projektmanager",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(GIST_API, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            scopes = resp.headers.get("X-OAuth-Scopes", "")
            body = json.load(resp)
            return body, scopes
    except urllib.error.HTTPError as e:
        out, loesung = _http_fehler_detail(e, token)
        raise GistRequestError(out, loesung)
    except (TimeoutError, socket.timeout):
        raise GistRequestError(
            "Zeitüberschreitung bei der Verbindung zu GitHub.",
            "Internetverbindung prüfen und erneut versuchen.",
        )
    except urllib.error.URLError as e:
        reason = scrub(str(getattr(e, "reason", e)), token)[:120]
        raise GistRequestError(
            "Keine Internetverbindung zu GitHub (%s)." % reason,
            "Netzwerkverbindung prüfen und erneut versuchen.",
        )


def _gist_lesen(token):
    body, _ = _gist_request("GET", token, timeout=45)
    return body


def _gist_schreiben(files, token):
    body, _ = _gist_request("PATCH", token, payload={"files": files}, timeout=60)
    return body


def _token_fehlt():
    return {
        "ok": False,
        "out": "Token fehlt: ~/.config/adventshaus/gist-token.",
        "loesung": "Reiter Einstellungen → Gist-Token einfügen → Speichern.",
    }


def act_status():
    return {
        "helfer": True,
        "version": HELPER_VERSION,
        "token": bool(read_token()),
        "ordner": HERE,
        "cfg": {k: CFG.get(k) for k in ("projekt", "sicherung", "kennung", "spiel_url")},
    }


def act_token_testen():
    token = read_token()
    if not token:
        return _token_fehlt()
    try:
        _, scopes = _gist_request("GET", token, timeout=20)
        scope_list = [s.strip() for s in scopes.split(",") if s.strip()]
        if "repo" in scope_list or "public_repo" in scope_list:
            return {
                "ok": True,
                "out": "Token gültig, aber zu weit berechtigt (Scopes: %s)." % ", ".join(scope_list),
                "loesung": "Empfehlung: Token auf „gist“ begrenzen, damit das Projekt-Repo geschützt bleibt.",
            }
        scope_hinweis = ("Scopes: " + ", ".join(scope_list)) if scope_list else "Fine-Grained / Gist-Zugriff bestätigt"
        return {
            "ok": True,
            "out": "Token gültig · Postfach-Gist erreichbar (%s)." % scope_hinweis,
        }
    except GistRequestError as e:
        return {"ok": False, "out": e.out, "loesung": e.loesung}


def act_token_loeschen():
    try:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write("")
        os.chmod(TOKEN_PATH, 0o600)
        return {
            "ok": True,
            "out": "Token lokal aus ~/.config/adventshaus/gist-token entfernt.",
            "loesung": "Optional zusätzlich unter github.com/settings/tokens widerrufen.",
        }
    except Exception as e:
        return {"ok": False, "out": "Token konnte nicht entfernt werden: " + str(e)}


def act_einstellungen_speichern(payload):
    projekt = str(payload.get("projekt") or "").strip()
    sicherung = str(payload.get("sicherung") or "").strip()
    kennung = str(payload.get("kennung") or "").strip() or "KI-B"
    spiel_url = str(payload.get("spiel_url") or "").strip() or "http://localhost:5173/"
    if not projekt or not sicherung:
        return {"ok": False, "out": "Projektordner und Sicherungspfad dürfen nicht leer sein."}
    if not re.match(r"^https?://", spiel_url, re.I):
        return {"ok": False, "out": "Spiel-Adresse muss mit http:// oder https:// beginnen."}
    neu_disk = {
        "projekt": projekt,
        "sicherung": sicherung,
        "kennung": kennung,
        "port": int(CFG.get("port", 8790)),
        "spiel_url": spiel_url,
    }
    try:
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(neu_disk, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        return {"ok": False, "out": "einstellungen.json nicht schreibbar: " + str(e)}
    CFG["projekt"] = os.path.expanduser(projekt)
    CFG["sicherung"] = os.path.expanduser(sicherung)
    CFG["kennung"] = kennung
    CFG["spiel_url"] = spiel_url
    proj_ok = os.path.isdir(CFG["projekt"])
    sich_ok = os.path.isdir(CFG["sicherung"])
    hinweis = ""
    if not proj_ok or not sich_ok:
        fehlt = []
        if not proj_ok:
            fehlt.append("Projektordner existiert noch nicht")
        if not sich_ok:
            fehlt.append("Sicherungsordner existiert noch nicht")
        hinweis = " Hinweis: " + ", ".join(fehlt) + "."
    return {
        "ok": True,
        "cfg": {k: CFG.get(k) for k in ("projekt", "sicherung", "kennung", "spiel_url")},
        "out": "Einstellungen gespeichert und sofort aktiv.%s" % hinweis,
    }


def postfach_basis_check(token, proj):
    if not token:
        return {"ok": True, "out": "kein Token – Postfach-Prüfung übersprungen"}
    try:
        data = _gist_lesen(token)
        try:
            meta = json.loads(((data.get("files") or {}).get("aktuell.json") or {}).get("content") or "{}")
        except Exception:
            meta = {}
        if not meta.get("basis"):
            return {"ok": True, "out": "kein Patch im Postfach"}
        origin = _origin_main_kurz(proj, token)
        basis = str(meta.get("basis", "")).strip()
        if not origin:
            return {"ok": True, "out": "Basis %s im Postfach (GitHub-main offline nicht prüfbar)" % basis}
        if basis == origin:
            return {"ok": True, "out": "Basis %s passt zu GitHub-main" % basis}
        return {
            "ok": False,
            "out": "Basis %s ≠ GitHub-main %s – Patch veraltet." % (basis, origin),
            "loesung": "Alten Patch entfernen oder Basis korrigieren.",
            "link": GIST_URL,
            "linkText": "Postfach öffnen",
        }
    except GistRequestError as e:
        return {"ok": False, "out": e.out, "loesung": e.loesung}


def act_pruefen():
    proj, token = CFG["projekt"], read_token()
    git_geraeumig(proj, token=token)
    steps = [
        ["git status", run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)],
        ["HEAD", run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)],
    ]
    ls_rem = run(["git", "ls-remote", "origin", "refs/heads/main"], cwd=proj, token=token, timeout=20)
    if ls_rem["ok"] and ls_rem["out"].strip():
        steps.append(["GitHub main", {"ok": True, "out": ls_rem["out"].split()[0][:7]}])
    else:
        steps.append([
            "GitHub main",
            {
                "ok": False,
                "out": "GitHub-main nicht erreichbar (offline oder Remote-Fehler).",
                "loesung": "Internetverbindung prüfen; lokale Arbeit bleibt möglich.",
            },
        ])
    if os.path.isdir(CFG["sicherung"]):
        steps.append(
            ["Sicherung", run(["git", "-C", CFG["sicherung"], "rev-parse", "--short", "refs/heads/main"], token=token)]
        )
    else:
        steps.append(
            [
                "Sicherung",
                {
                    "ok": False,
                    "out": "nicht gefunden: " + CFG["sicherung"],
                    "loesung": "Pfad „sicherung“ in den Einstellungen prüfen.",
                },
            ]
        )
    if os.path.exists(os.path.join(proj, "tools", "check.sh")):
        steps.append(["check.sh", run(["bash", "tools/check.sh"], cwd=proj, token=token)])
    steps.append(["Postfach-Basis", postfach_basis_check(token, proj)])
    return {"ok": all(s[1]["ok"] for s in steps),
            "github_main": (ls_rem["out"].split()[0][:7] if (ls_rem["ok"] and ls_rem["out"].strip()) else ""),
            "steps": [{"name": n, **v} for n, v in steps]}


def _filtere_bereits_vorhandene(patch_text, proj):
    entfernt, rest = [], []
    for b in re.split(r"(?=^diff --git )", patch_text, flags=re.M):
        if not b.strip():
            rest.append(b)
            continue
        m = re.search(r"\+\+\+ b/(\S+)", b)
        if not m:
            rest.append(b)
            continue
        pfad = m.group(1)
        if pfad == "docs/UEBERGABE.md" or ("--- /dev/null" in b and os.path.exists(os.path.join(proj, pfad))):
            entfernt.append(pfad)
        else:
            rest.append(b)
    return "".join(rest), entfernt


def act_ablegen(payload=None):
    payload = payload or {}
    force = bool(payload.get("force"))
    token = read_token()
    if not token:
        return _token_fehlt()
    proj = CFG["projekt"]
    git_geraeumig(proj, token=token)
    st = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    if not st["ok"]:
        return {
            "ok": False,
            "out": "Projekt-Status nicht lesbar: " + git_klar(st["out"]),
            "loesung": "Pfad „projekt“ prüfen – aktuell: " + proj,
        }
    if st["out"].strip():
        zeilen = [z for z in st["out"].splitlines() if z.strip()]
        namen = [z.split(None, 1)[-1] for z in zeilen[:8]]
        return {
            "ok": False,
            "out": "Stand nicht sauber – %d offene Änderung(en): %s" % (len(zeilen), ", ".join(namen)),
            "loesung": "Knopf „Offene Änderungen speichern“ drücken, danach erneut ins Postfach legen.",
        }

    # Postfach-Überschreibschutz: prüfen, ob bereits ein Patch im Gist liegt
    if not force:
        try:
            existing = _gist_lesen(token)
            files = existing.get("files") or {}
            old_patch = ((files.get("aktuell.patch") or {}).get("content") or "").strip()
            if old_patch:
                try:
                    old_meta = json.loads((files.get("aktuell.json") or {}).get("content") or "{}")
                except Exception:
                    old_meta = {}
                alt_titel = str(old_meta.get("titel") or "unbekannt")
                alt_basis = str(old_meta.get("basis") or "?")
                return {
                    "ok": False,
                    "ueberschreiben": True,
                    "out": "Im Postfach liegt bereits ein Patch („%s“, Basis %s)." % (alt_titel, alt_basis),
                    "loesung": "Wähle „Trotzdem überschreiben“ oder entferne zuerst den alten Patch.",
                    "link": GIST_URL,
                    "linkText": "Postfach öffnen",
                }
        except GistRequestError as e:
            return {"ok": False, "out": "Postfach nicht prüfbar: " + e.out, "loesung": e.loesung}

    # Mehr-Commit-Unterstützung: alle lokalen Commits seit origin/main bündeln
    ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=proj, token=token)
    ahead_count = int(ahead["out"].strip()) if ahead["ok"] and ahead["out"].strip().isdigit() else 0
    if ahead_count == 0:
        basis = (run(["git", "rev-parse", "--short", "origin/main"], cwd=proj, token=token)["out"].strip()
                 or run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)["out"].strip())
        return {"ok": True, "info": True,
                "out": "Nichts abgelegt – lokal liegt nichts vor GitHub (Stand %s). "
                       "Erst „Offene Änderungen speichern“ (oder „Lokal aktualisieren“), dann erneut ablegen." % basis}
    patch = run(["git", "format-patch", "origin/main..HEAD", "--stdout"], cwd=proj, token=token, limit=None)
    basis = run(["git", "rev-parse", "--short", "origin/main"], cwd=proj, token=token)["out"].strip()
    commit_info = "%d Commit(s)" % ahead_count

    if not patch["ok"] or not patch["out"]:
        return {"ok": False, "out": "Kein Patch erzeugt: " + git_klar(patch["out"])}
    patch_text = patch["out"]
    entfernt = []
    if not re.search(r"^diff --git ", patch_text, flags=re.M):
        return {
            "ok": True,
            "info": True,
            "out": "Nichts abgelegt – Patch enthält keine Dateiänderungen.",
        }
    sha16 = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()[:16]
    titel = run(["git", "log", "-1", "--pretty=%s"], cwd=proj, token=token)["out"].strip()
    meta = {
        "datei": "aktuell.patch",
        "sha256": sha16,
        "titel": titel,
        "basis": basis,
        "commits": max(1, ahead_count),
    }
    try:
        _gist_schreiben(
            {
                "aktuell.patch": {"content": patch_text},
                "aktuell.json": {"content": json.dumps(meta, ensure_ascii=False)},
            },
            token,
        )
        hinweis = (" Entfernt: " + ", ".join(entfernt)) if entfernt else ""
        return {
            "ok": True,
            "out": "Patch ins Postfach gelegt (%s). Prüfsumme %s, Basis %s.%s" % (commit_info, sha16, basis, hinweis),
        }
    except GistRequestError as e:
        return {"ok": False, "out": "Ablegen fehlgeschlagen: " + e.out, "loesung": e.loesung}


def act_uebernehmen():
    token = read_token()
    if not token:
        return _token_fehlt()
    proj = CFG["projekt"]
    try:
        data = _gist_lesen(token)
    except GistRequestError as e:
        return {"ok": False, "out": "Postfach nicht lesbar: " + e.out, "loesung": e.loesung}
    files = data.get("files") or {}
    original = (files.get("aktuell.patch") or {}).get("content") or ""
    try:
        meta = json.loads((files.get("aktuell.json") or {}).get("content") or "{}")
    except Exception:
        meta = {}
    if not original:
        return {
            "ok": False,
            "out": "Kein aktuell.patch im Postfach.",
            "loesung": "KI-Patch mit „Patch holen“ ablegen.",
        }
    if hashlib.sha256(original.encode("utf-8")).hexdigest()[:16] != meta.get("sha256"):
        return {
            "ok": False,
            "out": "Prüfsumme stimmt nicht – nichts wurde verändert.",
            "loesung": "Patch neu ablegen lassen.",
            "link": GIST_URL,
            "linkText": "Postfach öffnen",
        }
    origin = _origin_main_kurz(proj, token)
    lokal = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)["out"].strip()
    basis = str(meta.get("basis") or "").strip()
    erlaubte_basen = {b for b in (origin, lokal) if b}
    if basis and erlaubte_basen and basis not in erlaubte_basen:
        return {
            "ok": False,
            "basisfehler": True,
            "out": "Veralteter Patch: Basis %s, GitHub-main %s, lokal %s." % (basis, origin or "–", lokal),
            "loesung": "KI um neuen Patch bitten oder geprüft „Basis korrigieren“ verwenden.",
            "link": GIST_URL,
            "linkText": "Postfach öffnen",
        }
    git_geraeumig(proj, token=token)
    patch, vorhanden = _filtere_bereits_vorhandene(original, proj)
    if not re.search(r"^diff --git ", patch, flags=re.M):
        return {
            "ok": True,
            "info": True,
            "out": "Nur bereits vorhandene Dateien im Patch: %s – nichts Neues zu übernehmen." % ", ".join(vorhanden),
        }
    vorab = run(["git", "apply", "--check", "-"], cwd=proj, input_text=patch, token=token)
    if not vorab["ok"]:
        return {
            "ok": False,
            "out": git_klar(vorab["out"]),
            "loesung": "Nichts wurde verändert. Die KI muss den Patch neu aufsetzen.",
            "link": GIST_URL,
            "linkText": "Postfach öffnen",
        }
    thema = re.sub(r"[^a-z0-9]+", "-", str(meta.get("titel") or "patch").lower()).strip("-")[:24] or "patch"
    branch = "ki/" + thema
    ausgang = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=proj, token=token)["out"].strip() or "main"
    if not run(["git", "checkout", "-B", branch], cwd=proj, token=token)["ok"]:
        return {"ok": False, "out": "Zweig konnte nicht erstellt werden: " + branch}
    am = run(["git", "am"], cwd=proj, input_text=patch, token=token)
    if not am["ok"]:
        run(["git", "am", "--abort"], cwd=proj, token=token)
        run(["git", "checkout", ausgang], cwd=proj, token=token)
        return {
            "ok": False,
            "out": git_klar(am["out"]),
            "loesung": "Zurück auf „%s“; die KI muss den Patch neu aufsetzen." % ausgang,
        }
    tsc = run(["./node_modules/.bin/tsc", "--noEmit"], cwd=proj, token=token)
    build = run(["npm", "run", "build"], cwd=proj, token=token)
    if not (tsc["ok"] and build["ok"]):
        run(["git", "checkout", ausgang], cwd=proj, token=token)
        return {
            "ok": False,
            "branch": branch,
            "out": "Patch auf %s angewendet (zurück auf %s), aber Typen %s / Build %s."
            % (branch, ausgang, "OK" if tsc["ok"] else "Fehler", "OK" if build["ok"] else "Fehler"),
            "detail": tsc["out"][-500:] + "\n" + build["out"][-500:],
            "loesung": "Kein PR geöffnet. Buildfehler im Zweig %s prüfen." % branch,
        }
    push = run(["git", "push", "-u", "origin", branch], cwd=proj, token=token, timeout=60)
    # Immer sauber auf Ausgangszweig (z. B. main) zurückkehren
    run(["git", "checkout", ausgang], cwd=proj, token=token)
    if not push["ok"]:
        return {
            "ok": False,
            "branch": branch,
            "out": "Build OK (Zweig %s lokal bereit, zurück auf %s), aber Push fehlgeschlagen: %s"
            % (branch, ausgang, git_klar(push["out"])),
            "loesung": "Falls der Gist-Token absichtlich keine Repo-Rechte hat, Zweig manuell oder über gh pushen.",
        }
    pr = run(["gh", "pr", "create", "--base", "main", "--head", branch, "--fill"], cwd=proj, token=token, timeout=45)
    m = re.search(r"https://\S+?/pull/\d+", pr["out"])
    pr_url = m.group(0) if m else (REPO_URL + "/compare/main..." + urllib.parse.quote(branch, safe=""))
    hinweis = (" Entfernt: " + ", ".join(vorhanden)) if vorhanden else ""
    return {
        "ok": True,
        "branch": branch,
        "pr_url": pr_url,
        "out": "Zweig %s · Typen OK · Build OK · %s (Arbeitsbaum wieder auf %s).%s"
        % (branch, "PR geöffnet" if pr["ok"] else "PR-Vergleich geöffnet", ausgang, hinweis),
        "detail": pr["out"],
    }


def act_beenden():
    def _spaeeter():
        time.sleep(0.4)
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_spaeeter, daemon=True).start()
    return {"ok": True, "out": "Helfer wird beendet (sauberer Ausstieg, PID aufgeräumt)."}


def act_neustart():
    try:
        subprocess.Popen(
            ["bash", "-c", "sleep 1.5; exec bash \"%s\"" % os.path.join(HERE, "start.sh")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
        )
    except Exception as e:
        return {"ok": False, "out": "Neustart fehlgeschlagen: " + str(e)}
    def _spaeeter():
        time.sleep(0.4)
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_spaeeter, daemon=True).start()
    return {"ok": True, "out": "Helfer startet neu – die Seite lädt automatisch neu."}


def act_zweige():
    token = read_token()
    proj = CFG["projekt"]
    fetch = run(["git", "fetch", "--prune", "origin"], cwd=proj, token=token, timeout=30)
    merged_local = run(["git", "branch", "--merged", "main"], cwd=proj, token=token)["out"].splitlines()
    lokal = [b.strip().lstrip("*").strip() for b in merged_local
             if "ki/" in b and b.strip().lstrip("*").strip() != "main"]
    merged_remote = run(["git", "branch", "-r", "--merged", "main"], cwd=proj, token=token)["out"].splitlines()
    remote = [b.strip().replace("origin/", "", 1) for b in merged_remote
              if b.strip().startswith("origin/ki/")]
    gel_lokal, gel_remote = [], []
    for b in sorted(set(lokal)):
        if run(["git", "branch", "-d", b], cwd=proj, token=token)["ok"]:
            gel_lokal.append(b)
    for b in sorted(set(remote)):
        if run(["git", "push", "origin", "--delete", b], cwd=proj, token=token, timeout=30)["ok"]:
            gel_remote.append(b)
    alle_lokal = run(["git", "branch"], cwd=proj, token=token)["out"].splitlines()
    ungel = [b.strip().lstrip("*").strip() for b in alle_lokal
             if "ki/" in b and b.strip().lstrip("*").strip() not in gel_lokal]
    msg = "Zweige geprüft (nur gemergte ki/*-Zweige werden entfernt)."
    if gel_lokal:
        msg += " Lokal gelöscht: " + ", ".join(gel_lokal) + "."
    if gel_remote:
        msg += " Remote gelöscht: " + ", ".join(gel_remote) + "."
    if not gel_lokal and not gel_remote:
        msg += " Keine gemergten Reste gefunden."
    if ungel:
        msg += " Unverändert (noch nicht gemerged): " + ", ".join(ungel) + "."
    if not fetch["ok"]:
        return {"ok": True, "info": True,
                "out": "Offline: " + msg + " (Fetch nicht möglich: " + fetch["out"][:60] + ")"}
    return {"ok": True, "out": msg}


def act_aktualisieren():
    token = read_token()
    proj = CFG["projekt"]
    st = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    if not st["ok"]:
        return {"ok": False, "out": "Projekt nicht lesbar: " + git_klar(st["out"])}
    if st["out"].strip():
        zeilen = [z for z in st["out"].splitlines() if z.strip()]
        namen = [z[3:].strip().strip('"') for z in zeilen[:6]]
        return {
            "ok": False,
            "out": "Nicht aktualisiert – %d offene Änderung(en): %s" % (len(zeilen), ", ".join(namen)),
            "loesung": "Erst „Offene Änderungen speichern“ drücken, dann „Lokal aktualisieren“.",
        }
    vor = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)["out"].strip()
    pull = run(["git", "pull", "--ff-only", "origin", "main"], cwd=proj, token=token, timeout=60)
    if not pull["ok"]:
        return {
            "ok": False,
            "out": "Lokale Aktualisierung fehlgeschlagen: " + git_klar(pull["out"]),
            "loesung": "Eventuell Divergenz (beide Seiten eigene Commits) – „Stand prüfen“ für Details.",
        }
    nach = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)["out"].strip()
    if vor == nach:
        return {"ok": True, "info": True, "out": "Lokal war schon aktuell (main " + vor + ")."}
    return {"ok": True, "out": "Lokal aktualisiert: main " + vor + " → " + nach + " (GitHub-Stand übernommen)."}


def act_sichern():
    token, sicher, proj = read_token(), CFG["sicherung"], CFG["projekt"]
    git_geraeumig(proj, token=token)
    if not os.path.isdir(sicher):
        return {
            "ok": False,
            "out": "Sicherung nicht gefunden: " + sicher,
            "loesung": "Pfad „sicherung“ in den Einstellungen prüfen.",
        }
    if not run(["git", "-C", sicher, "rev-parse", "--git-dir"], token=token)["ok"]:
        return {"ok": False, "out": "Sicherung ist kein Git-Repository: " + sicher}
    fetch = run(["git", "-C", sicher, "fetch", "origin"], token=token, timeout=30)
    if not fetch["ok"]:
        return {"ok": False, "out": "Sicherung nicht aktualisierbar: " + git_klar(fetch["out"])}
    bare = run(["git", "-C", sicher, "rev-parse", "--is-bare-repository"], token=token)["out"].strip() == "true"
    if bare:
        res = run(["git", "-C", sicher, "fetch", "origin", "+refs/heads/main:refs/heads/main"], token=token, timeout=30)
    else:
        dirty = run(["git", "-C", sicher, "status", "--porcelain"], token=token)["out"].strip()
        if dirty:
            return {
                "ok": False,
                "out": "Sicherung hat ungespeicherte lokale Änderungen – kein Überschreiben durchgeführt.",
                "loesung": "Sicherungsordner prüfen oder als Bare-Repository anlegen.",
            }
        res = run(["git", "-C", sicher, "reset", "--hard", "origin/main"], token=token)

    ueber = os.path.join(proj, "docs", "UEBERGABE.md")
    hand = ""
    if os.path.exists(ueber):
        with open(ueber, encoding="utf-8") as fp:
            m = re.search(r"<!--\s*HAND:.*", fp.read(), re.S)
            hand = m.group(0) if m else ""
    main = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)["out"].strip()
    auto = "## Stand (automatisch, %s)\nmain %s · Kennung %s · Prüfung: siehe Projektmanager\n\n" % (
        time.strftime("%d.%m.%Y %H:%M"),
        main,
        CFG["kennung"],
    )
    try:
        os.makedirs(os.path.dirname(ueber), exist_ok=True)
        with open(ueber, "w", encoding="utf-8") as fp:
            fp.write(auto + (hand or "<!-- HAND: ab hier schreibt nur der Besitzer -->\n\n## Als Nächstes\n"))
        ueb_ok = True
    except Exception as e:
        return {"ok": False, "out": "Übergabedatei nicht schreibbar: " + str(e)}
    gespeichert = ""
    if run(["git", "rev-parse", "--git-dir"], cwd=proj, token=token)["ok"]:
        run(["git", "add", "--", ueber], cwd=proj, token=token)
        if not run(["git", "diff", "--cached", "--quiet"], cwd=proj, token=token)["ok"]:
            c = run(_commit_ident(proj, token=token) + ["-m", "docs: Übergabedatei"], cwd=proj, token=token)
            if c["ok"]:
                gespeichert = " und die Übergabedatei gespeichert"

    ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=proj, token=token)
    ahead_count = int(ahead["out"].strip()) if ahead["ok"] and ahead["out"].strip().isdigit() else 0
    lokal_hinweis = (
        " Hinweis: Im Projektordner liegen %d lokale(r) Commit(s) vor origin/main." % ahead_count
        if ahead_count > 0
        else ""
    )
    ok = res["ok"] and ueb_ok
    return {
        "ok": ok,
        "out": (
            "Stand gesichert (Sicherung auf main, Übergabedatei aktualisiert%s).%s"
            % (gespeichert, lokal_hinweis)
        )
        if ok
        else "Sichern unvollständig: " + git_klar(res["out"]),
    }


UEBERGABE_DATEIEN = [
    "index.html",
    "style.css",
    "projektmanager.js",
    "projektmanager.py",
    "start.sh",
    "stop.sh",
    "neustart.sh",
    "install-desktop.sh",
    "einstellungen.json",
    "README.md",
    "HISTORIE.md",
]


def act_uebergabe():
    token = read_token()
    t = [
        "PROJEKTMANAGER (ADVENTSHAUS) – ENTWICKLER-INFO (vollständig)",
        "Erstellt: %s · Helfer %s · GUI %s · Kennung %s"
        % (time.strftime("%d.%m.%Y %H:%M"), HELPER_VERSION, GUI_HINT, CFG.get("kennung", "-")),
        "",
        "ZWECK: Stand und nächster Schritt für den KI-Ablauf, kein Teil des Spiels.",
        "SICHERHEIT: nur 127.0.0.1, Sitzungstoken, feste Aktionen, Token nur im Helfer und immer gefiltert.",
        "REGEL: Diese Info muss den gesamten Quellcode aller Komponenten und die gesamte HISTORIE enthalten.",
        "",
        "AKTUELLER STAND:",
    ]
    for k in ("projekt", "sicherung", "kennung", "port", "spiel_url"):
        t.append("  %s: %s" % (k, CFG.get(k, "-")))
    t += [
        "  token: " + ("vorhanden" if token else "fehlt"),
        "  ordner: " + HERE,
        "",
        "VOLLSTÄNDIGER QUELLCODE EINSCHLIESSLICH HISTORIE:",
    ]
    for name in UEBERGABE_DATEIEN:
        p = os.path.join(HERE, name)
        t += ["", "### DATEI: " + name]
        if not os.path.exists(p):
            t.append("(fehlt im Ordner)")
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as fp:
                inhalt = fp.read()
        except Exception as e:
            inhalt = "(nicht lesbar: %s)" % e
        t += ["```", inhalt.rstrip(), "```"]
    t.append("### ENDE DER ENTWICKLER-INFO")
    text = scrub("\n".join(t), token)
    return {"ok": True, "text": text, "bytes": len(text.encode("utf-8"))}


def act_offene_speichern():
    token = read_token()
    proj = CFG["projekt"]
    git_geraeumig(proj, token=token)
    st = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    if not st["ok"]:
        return {"ok": False, "out": "Projekt nicht lesbar: " + git_klar(st["out"])}
    zeilen = [z for z in st["out"].splitlines() if z.strip()]
    if not zeilen:
        ign = run(["git", "status", "--porcelain", "--ignored"], cwd=proj, token=token)
        ign_namen = [
            z[3:].strip()
            for z in (ign["out"].splitlines() if ign["ok"] else [])
            if z.startswith("!!")
        ]
        if ign_namen:
            return {
                "ok": True,
                "info": True,
                "out": "Git sieht keine speicherbaren Änderungen. %d ignorierte Datei(en) liegen bewusst unverfolgt im Projektordner: %s."
                % (len(ign_namen), ", ".join(ign_namen[:6])),
            }
        return {"ok": True, "info": True, "out": "Alles gespeichert – keine offenen Änderungen."}
    namen = [z[3:].strip().strip('"') for z in zeilen]
    verdaechtig = [n for n in namen if SENSITIVE_FILE_RE.search(n)]
    if verdaechtig:
        return {
            "ok": False,
            "out": "Speichern gestoppt – potenziell geheime Datei(en) erkannt: %s." % ", ".join(verdaechtig[:6]),
            "loesung": "Entferne diese Dateien aus dem Projektordner oder trage sie in .gitignore ein.",
        }
    msg = (
        "docs: Übergabedatei"
        if len(namen) == 1 and namen[0].endswith("UEBERGABE.md")
        else "Projektmanager: %d offene Änderung(en) gespeichert" % len(zeilen)
    )
    if not run(["git", "add", "-A"], cwd=proj, token=token)["ok"]:
        return {"ok": False, "out": "git add fehlgeschlagen."}
    c = run(_commit_ident(proj, token=token) + ["-m", msg], cwd=proj, token=token)
    if not c["ok"]:
        return {"ok": False, "out": "Speichern fehlgeschlagen: " + git_klar(c["out"])}
    return {
        "ok": True,
        "out": "%d Änderung(en) lokal gespeichert („%s“: %s) – nichts hochgeladen."
        % (len(zeilen), msg, ", ".join(namen[:5])),
    }


def act_basis_korrigieren():
    token = read_token()
    if not token:
        return _token_fehlt()
    try:
        data = _gist_lesen(token)
    except GistRequestError as e:
        return {"ok": False, "out": e.out, "loesung": e.loesung}
    files = data.get("files") or {}
    try:
        meta = json.loads((files.get("aktuell.json") or {}).get("content") or "{}")
    except Exception:
        return {"ok": False, "out": "aktuell.json ist nicht lesbar."}
    patch = (files.get("aktuell.patch") or {}).get("content") or ""
    if patch and hashlib.sha256(patch.encode("utf-8")).hexdigest()[:16] != meta.get("sha256"):
        return {"ok": False, "out": "Basis nicht geändert: Die Patch-Prüfsumme stimmt nicht."}
    origin = _origin_main_kurz(CFG["projekt"], token)
    if not origin:
        return {"ok": False, "out": "GitHub-main konnte nicht ermittelt werden."}
    alt = str(meta.get("basis") or "–")
    meta["basis"] = origin
    try:
        _gist_schreiben({"aktuell.json": {"content": json.dumps(meta, ensure_ascii=False)}}, token)
        return {"ok": True, "out": "Basis von %s auf %s gesetzt; Patch und Prüfsumme unverändert." % (alt, origin)}
    except GistRequestError as e:
        return {"ok": False, "out": e.out, "loesung": e.loesung}


def _data_uri_inhalt(html_text):
    import base64

    patch, meta = "", ""
    for m in re.finditer(r"data:[a-z0-9/+.]+;(?:charset=[^;]+;)?base64,([A-Za-z0-9+/=]+)", html_text):
        try:
            roh = base64.b64decode(m.group(1)).decode("utf-8", "ignore")
        except Exception:
            continue
        if "diff --git" in roh and not patch:
            patch = roh
        elif '"basis"' in roh and not meta:
            meta = roh
    return patch, meta


def act_patch_von_url(payload):
    url = (payload.get("url") or "").strip()
    if not url:
        return {"ok": False, "out": "Keine Adresse angegeben."}
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {"ok": False, "out": "Nur http/https-Adressen sind erlaubt."}
    host = (parsed.hostname or "").lower()
    if host not in ("gist.githubusercontent.com", "gist.github.com", "raw.githubusercontent.com", "github.com"):
        return {
            "ok": False,
            "out": "Nicht erlaubte Domain: %s." % (host or "unbekannt"),
            "loesung": "Aus Sicherheitsgründen sind nur GitHub-/Gist-Adressen erlaubt.",
        }
    try:
        r = urllib.request.urlopen(url, timeout=25)
        inhalt = r.read(2_000_000).decode("utf-8", "ignore")
        basis_url = r.geturl().rsplit("/", 1)[0] + "/"
    except Exception as e:
        return {"ok": False, "out": "Adresse nicht erreichbar: " + scrub(str(e), read_token())[:140]}
    patch, meta = "", ""
    for name in ("aktuell.patch", "aktuell.json"):
        try:
            txt = urllib.request.urlopen(basis_url + name, timeout=15).read(2_000_000).decode("utf-8", "ignore")
            if name.endswith("patch"):
                patch = txt
            else:
                meta = txt
        except Exception:
            pass
    if not patch or not meta:
        p2, m2 = _data_uri_inhalt(inhalt)
        patch, meta = patch or p2, meta or m2
    if not patch:
        return {"ok": False, "out": "Auf der Seite wurde kein Patch gefunden."}
    return act_patch_einfuegen({"patch": patch, "meta": meta})


def act_projekt_diagnose():
    token, proj = read_token(), CFG["projekt"]
    if not os.path.isdir(proj):
        return {"ok": False, "out": "Projektordner nicht gefunden: " + proj}
    st = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)
    if not st["ok"] or not head["ok"]:
        return {"ok": False, "out": "Kein Git-Repository unter: " + proj}
    offene = [z for z in st["out"].splitlines() if z.strip()]
    zeilen = [
        "Projekt: %s · HEAD %s · %s"
        % (proj, head["out"].strip(), "Stand sauber" if not offene else "%d offene Änderung(en)" % len(offene))
    ]
    if offene:
        namen = [z[3:].strip() for z in offene[:6]]
        zeilen.append("Offene Dateien: " + ", ".join(namen))
    origin = _origin_main_kurz(proj, token)
    if origin:
        zeilen.append("GitHub-main: %s · lokaler HEAD: %s" % (origin, head["out"].strip()))
        run(["git", "fetch", "origin"], cwd=proj, token=token, timeout=30)
        cnt = run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"], cwd=proj, token=token)["out"].strip()
        parts = cnt.split()
        if len(parts) == 2:
            behind, ahead = parts
            if behind == "0" and ahead == "0":
                zeilen.append("Abgleich: lokal und GitHub identisch (0 0).")
            elif behind == "0":
                zeilen.append("Abgleich: lokal %s Commit(s) vor GitHub (0 %s) – z. B. noch nicht abgelegt." % (ahead, ahead))
            elif ahead == "0":
                zeilen.append("Abgleich: lokal %s Commit(s) hinter GitHub (%s 0) – „Lokal aktualisieren“ drücken." % (behind, behind))
            else:
                zeilen.append("Abgleich: DIVERGENZ (%s %s) – %s GitHub-Commits fehlen lokal, %s lokale fehlen auf GitHub. Nichts pushen!" % (behind, ahead, behind, ahead))
    else:
        zeilen.append("GitHub-main: offline / nicht erreichbar")
    patch_text = ""
    if token:
        try:
            data = _gist_lesen(token)
            patch_text = ((data.get("files") or {}).get("aktuell.patch") or {}).get("content") or ""
        except GistRequestError as e:
            zeilen.append("Postfach: " + e.out)
    gefordert, vorhanden, fehlen = [], [], []
    if "diff --git" in patch_text:
        for m in re.findall(r"\+\+\+ b/(\S+)", patch_text):
            if m not in gefordert:
                gefordert.append(m)
        for pfad in gefordert:
            (vorhanden if os.path.exists(os.path.join(proj, pfad)) else fehlen).append(pfad)
        zeilen.append(
            "Patch fordert %d Datei(en): %d vorhanden, %d fehlen%s"
            % (len(gefordert), len(vorhanden), len(fehlen), (" – fehlt: " + ", ".join(fehlen)) if fehlen else "")
        )
        out = "Projekt-Diagnose fertig – " + (
            "es fehlen Patch-Dateien (noch nicht übernommen)." if fehlen else "alle Patch-Dateien vorhanden."
        )
    else:
        zeilen.append("Kein lesbarer Patch im Postfach." if token else "Kein Token – Postfach nicht gelesen.")
        out = "Projekt-Diagnose fertig – Projektstatus aufgenommen."
    return {"ok": True, "zeilen": zeilen, "out": out, "offen": len(offene), "github_main": origin}


def _sha_varianten(text):
    varianten = set()
    for wert in (
        text.encode("utf-8", "ignore"),
        text.encode("utf-8-sig", "ignore"),
        text.encode("utf-8").replace(b"\r\n", b"\n"),
        text.replace("\r\n", "\n").encode("utf-8", "ignore"),
    ):
        varianten.add(hashlib.sha256(wert).hexdigest()[:16])
    return varianten


def act_patch_einfuegen(payload):
    token = read_token()
    if not token:
        return _token_fehlt()
    patch = (payload.get("patch") or "").strip()
    meta_text = (payload.get("meta") or "").strip()
    if not patch or not re.search(r"(^|\n)diff --git ", patch):
        return {"ok": False, "out": "Kein gültiger Patch-Text (diff --git fehlt)."}
    if len(patch.encode("utf-8", "ignore")) > 200 * 1024:
        return {"ok": False, "out": "Der Patch ist zu groß (über 200 KB)."}
    try:
        meta = json.loads(meta_text)
    except Exception:
        return {"ok": False, "out": "Die json mit der Basis fehlt oder ist nicht lesbar."}
    basis = str(meta.get("basis") or "").strip()
    if not basis:
        return {"ok": False, "out": "In der json fehlt „basis“ – ohne Basis kein Ablegen."}
    patch, entfernt = _filtere_bereits_vorhandene(patch, CFG["projekt"])
    if not re.search(r"^diff --git ", patch, flags=re.M):
        return {
            "ok": True,
            "info": True,
            "out": "Nichts einzutragen – nur bereits vorhandene Dateien: " + ", ".join(entfernt),
        }
    stat = run(["git", "apply", "--stat", "-"], cwd=CFG["projekt"], input_text=patch, token=token)
    if not stat["ok"]:
        return {
            "ok": False,
            "out": "Patch ist unvollständig oder defekt (" + git_klar(stat["out"]) + ")",
            "loesung": "KI den Patch komplett neu liefern lassen – am besten als Datei/ZIP („KI-Anfrage kopieren“), nicht als Chat-Text.",
        }
    dateien = []
    for m in re.findall(r"\+\+\+ b/(\S+)", patch):
        if m not in dateien:
            dateien.append(m)
    titel = str(meta.get("titel") or "").strip() or (dateien[0] if dateien else "eingefügter Patch")
    sha = hashlib.sha256(patch.encode("utf-8", "ignore")).hexdigest()[:16]
    mitgeliefert = str(meta.get("sha256") or "").strip().lower()
    sha_hinweis = ""
    if mitgeliefert and mitgeliefert not in _sha_varianten(patch):
        sha_hinweis = (
            "Mitgelieferte Prüfsumme %s weicht ab; frisch berechnet: %s (BOM/Zeilenenden möglich)."
            % (mitgeliefert, sha)
        )
    neu = {"datei": "aktuell.patch", "sha256": sha, "titel": titel, "basis": basis}
    try:
        _gist_schreiben(
            {
                "aktuell.patch": {"content": patch},
                "aktuell.json": {"content": json.dumps(neu, ensure_ascii=False)},
            },
            token,
        )
        hinweis = (" Entfernt: " + ", ".join(entfernt)) if entfernt else ""
        return {
            "ok": True,
            "sha_info": sha_hinweis,
            "out": "Patch ins Postfach gelegt: %d Datei(en), Prüfsumme %s, Basis %s.%s"
            % (len(dateien), sha, basis, hinweis),
        }
    except GistRequestError as e:
        return {"ok": False, "out": "Ins Postfach legen fehlgeschlagen: " + e.out, "loesung": e.loesung}


def act_postfach_leeren():
    token = read_token()
    if not token:
        return _token_fehlt()
    try:
        data = _gist_lesen(token)
        vorhanden = {k: None for k in ("aktuell.patch", "aktuell.json") if k in (data.get("files") or {})}
        if not vorhanden:
            return {"ok": True, "info": True, "out": "Postfach war schon leer – nichts zu entfernen."}
        _gist_schreiben(vorhanden, token)
        return {
            "ok": True,
            "out": "Postfach geleert: %s entfernt; übrige Gist-Dateien bleiben." % ", ".join(sorted(vorhanden)),
        }
    except GistRequestError as e:
        return {"ok": False, "out": e.out, "loesung": e.loesung}


def _probe(port):
    for host in ("127.0.0.1", "::1"):
        try:
            url = ("http://[%s]:%d/" % (host, port)) if ":" in host else ("http://%s:%d/" % (host, port))
            r = urllib.request.urlopen(url, timeout=0.35)
            html = r.read(4000).decode("utf-8", "ignore")
            m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
            return {"port": port, "title": (m.group(1).strip() if m else "")[:60]}
        except Exception:
            continue
    return None


def find_game():
    ports = list(range(5173, 5201)) + [3000, 4173, 5000, 8000, 8080]
    found = [f for f in (_probe(p) for p in ports) if f]
    best = next((f for f in found if "Adventshaus" in f["title"] or "Luni" in f["title"]), found[0] if found else None)
    return {
        "url": ("http://localhost:%d/" % best["port"]) if best else "",
        "title": (best or {}).get("title", ""),
        "found": found,
    }


def start_game():
    global GAME_PROC
    f = find_game()
    if f["url"]:
        return {"url": f["url"], "gestartet": False, "out": "Spiel läuft bereits: " + f["url"]}
    proj = CFG["projekt"]
    if not os.path.isdir(proj):
        return {"url": "", "out": "Projekt nicht gefunden: " + proj}
    npm = shutil.which("npm")
    if not npm:
        return {"url": "", "out": "npm nicht gefunden – Node.js wird für den Spielstart benötigt."}
    if GAME_PROC is not None and GAME_PROC.poll() is None:
        return {"url": "", "out": "Spielstart läuft bereits – bitte kurz warten."}
    try:
        logf = open(GAME_LOG, "w")
        GAME_PROC = subprocess.Popen(
            [npm, "run", "dev"],
            cwd=proj,
            stdout=logf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except Exception as e:
        return {"url": "", "out": "Spielstart fehlgeschlagen: " + str(e)}
    for _ in range(50):
        time.sleep(0.5)
        f = find_game()
        if f["url"]:
            return {"url": f["url"], "gestartet": True, "out": "Spiel gestartet: " + f["url"]}
        if GAME_PROC.poll() is not None:
            tail = ""
            try:
                with open(GAME_LOG, encoding="utf-8", errors="replace") as fp:
                    tail = fp.read()[-300:].strip()
            except Exception:
                pass
            return {"url": "", "out": "Spielstart endete sofort. " + tail}
    return {"url": "", "out": "Spiel startet nicht (25 s). Log: " + GAME_LOG}


def stop_game():
    global GAME_PROC
    if GAME_PROC is None or GAME_PROC.poll() is not None:
        GAME_PROC = None
        return {"ok": False, "out": "Spiel wurde nicht vom Projektmanager gestartet – nichts beendet."}
    pid = GAME_PROC.pid
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except Exception:
        try:
            GAME_PROC.terminate()
        except Exception:
            pass
    for _ in range(20):
        if GAME_PROC.poll() is not None:
            break
        time.sleep(0.25)
    if GAME_PROC.poll() is None:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            pass
    GAME_PROC = None
    return {"ok": True, "out": "Spiel beendet."}


GET_ACTIONS = {
    "status": act_status,
    "pruefen": act_pruefen,
    "uebergabe": act_uebergabe,
    "projekt-diagnose": act_projekt_diagnose,
}

POST_ACTIONS = {
    "ablegen": act_ablegen,
    "uebernehmen": act_uebernehmen,
    "sichern": act_sichern,
    "postfach-leeren": act_postfach_leeren,
    "basis-korrigieren": act_basis_korrigieren,
    "patch-von-url": act_patch_von_url,
    "patch-einfuegen": act_patch_einfuegen,
    "offene-speichern": act_offene_speichern,
    "token-test": act_token_testen,
    "token-loeschen": act_token_loeschen,
    "einstellungen": act_einstellungen_speichern,
    "spiel": start_game,
    "spiel-stop": stop_game,
    "aktualisieren": act_aktualisieren,
    "zweige": act_zweige,
    "beenden": act_beenden,
    "neustart": act_neustart,
}

STATIC_FILES = set(UEBERGABE_DATEIEN)


class Handler(http.server.BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _pruefe_lokal_sicherheit(self):
        port = int(CFG.get("port", 8790))
        erlaubte_hosts = {"127.0.0.1:%d" % port, "localhost:%d" % port}
        host = (self.headers.get("Host") or "").strip().lower()
        if host not in erlaubte_hosts:
            self._json(403, {"ok": False, "out": "Ungültiger Host-Header blockiert."})
            return False
        origin = (self.headers.get("Origin") or "").strip().lower()
        if origin and origin not in {"http://127.0.0.1:%d" % port, "http://localhost:%d" % port}:
            self._json(403, {"ok": False, "out": "Fremder Origin-Header blockiert (CSRF-Schutz)."})
            return False
        csrf = (self.headers.get("X-Projektmanager-Token") or "").strip()
        if not csrf or not hmac.compare_digest(csrf, SESSION_TOKEN):
            self._json(403, {"ok": False, "out": "Sitzungstoken fehlt oder ungültig – Seite bitte neu laden."})
            return False
        return True

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/"):
            if not self._pruefe_lokal_sicherheit():
                return
            name = path[len("/api/") :].strip("/")
            try:
                if name in GET_ACTIONS:
                    self._json(200, GET_ACTIONS[name]())
                elif name in POST_ACTIONS:
                    self._json(405, {"ok": False, "out": "Diese Aktion erfordert POST."})
                else:
                    self._json(404, {"ok": False, "out": "unbekannte Aktion"})
            except Exception as e:
                self._json(500, {"ok": False, "out": scrub(str(e), read_token())})
            return
        p = path.lstrip("/") or "index.html"
        if p not in STATIC_FILES:
            self._json(404, {"ok": False, "out": "nicht gefunden: " + p})
            return
        fp = os.path.join(HERE, p)
        if not os.path.isfile(fp):
            self._json(404, {"ok": False, "out": "nicht gefunden: " + p})
            return
        ctype = (
            "text/html; charset=utf-8"
            if p.endswith(".html")
            else (
                "text/css; charset=utf-8"
                if p.endswith(".css")
                else ("application/javascript; charset=utf-8" if p.endswith(".js") else "text/plain; charset=utf-8")
            )
        )
        with open(fp, "rb") as fh:
            b = fh.read()
        if p == "index.html":
            html_str = b.decode("utf-8")
            meta_tag = '<meta name="projektmanager-csrf" content="%s">' % SESSION_TOKEN
            html_str = html_str.replace("<head>", "<head>\n" + meta_tag, 1)
            b = html_str.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not path.startswith("/api/"):
            self._json(404, {"ok": False, "out": "nicht gefunden"})
            return
        if not self._pruefe_lokal_sicherheit():
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > 2_100_000:
            self._json(413, {"ok": False, "out": "Anfrage zu groß."})
            return
        body = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            daten = json.loads(body or "{}")
        except Exception:
            daten = {}
        name = path[len("/api/") :].strip("/")
        try:
            if name == "token":
                tok = (daten.get("token") or "").strip()
                if not tok:
                    self._json(200, {"ok": False, "out": "Kein Token übergeben."})
                    return
                os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
                with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                    f.write(tok + "\n")
                os.chmod(TOKEN_PATH, 0o600)
                self._json(200, {"ok": True, "out": "Token gespeichert (Rechte 600)."})
            elif name in ("ablegen", "patch-von-url", "patch-einfuegen", "einstellungen"):
                self._json(200, POST_ACTIONS[name](daten))
            elif name in POST_ACTIONS:
                self._json(200, POST_ACTIONS[name]())
            else:
                self._json(404, {"ok": False, "out": "unbekannte Aktion"})
        except Exception as e:
            self._json(500, {"ok": False, "out": scrub(str(e), read_token())})

    def log_message(self, *a):
        pass


def open_browser(url):
    time.sleep(0.6)
    for app in ("chromium", "google-chrome", "google-chrome-stable", "chromium-browser",
                "microsoft-edge", "brave", "brave-browser", "vivaldi"):
        binapp = shutil.which(app)
        if binapp:
            try:
                subprocess.Popen([binapp, "--app=" + url, "--window-size=860,920", "--window-position=100,80"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return True
            except Exception:
                continue
    for opener in (["xdg-open", url], ["open", url]):
        try:
            subprocess.Popen(opener, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            continue
    try:
        return bool(webbrowser.open(url, new=2))
    except Exception:
        return False


def main():
    port = int(CFG.get("port", 8790))
    url = "http://127.0.0.1:%d/" % port
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    try:
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    except OSError:
        print("Projektmanager läuft bereits. Öffne den Browser: " + url, flush=True)
        open_browser(url)
        return
    print("Projektmanager %s läuft → %s" % (HELPER_VERSION, url), flush=True)
    print("Ordner: " + HERE, flush=True)
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    def _beenden(signum=None, frame=None):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
        os._exit(0)

    try:
        signal.signal(signal.SIGTERM, _beenden)
        signal.signal(signal.SIGINT, _beenden)
        open_browser(url)
        httpd.serve_forever()
    finally:
        try:
            os.remove(PID_FILE)
        except Exception:
            pass


if __name__ == "__main__":
    main()
