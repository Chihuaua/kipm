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
HELPER_VERSION = "23.42.09"
GUI_HINT = "23.42.09"
HELPER_REVISION = "23.42.09"
import io
import ipaddress
import shlex
import zipfile

MAX_PATCH_BYTES = 8 * 1024 * 1024
MAX_HTTP_BYTES = 16 * 1024 * 1024



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


def run(cmd, cwd=None, input_text=None, token="", timeout=180, limit=4000, preserve=False):
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
        raw_out = (r.stdout or "") + (r.stderr or "")
        out = raw_out if preserve and r.returncode == 0 else scrub(raw_out, tok)
        if not preserve:
            out = out.strip()
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
    return _remote_main_full(proj, token)[:7]

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
    if not isinstance(body, dict) or not isinstance(body.get("files"), dict):
        raise GistRequestError("GitHub hat keine lesbare Gist-Dateiliste geliefert.")
    if body.get("truncated"):
        raise GistRequestError("Gist-Dateiliste ist unvollständig.", "Postfach über GitHub prüfen; nichts übernehmen.")
    for name, entry in body["files"].items():
        if name not in ("aktuell.patch", "aktuell.json") or not entry.get("truncated"):
            continue
        limit = MAX_PATCH_BYTES if name == "aktuell.patch" else 65536
        url = entry.get("raw_url") or ""
        text = _raw_gist_datei(url, limit)
        if len(text.encode("utf-8")) != int(entry.get("size", len(text.encode("utf-8")))):
            raise GistRequestError("Die vollständige Gist-Datei hat eine unerwartete Größe.", "Nichts übernehmen.")
        entry["content"] = text
        entry["truncated"] = False
    return body

def _gist_schreiben(files, token):
    body, _ = _gist_request("PATCH", token, payload={"files": files}, timeout=60)
    try:
        confirmation = _gist_lesen(token)
    except GistRequestError as exc:
        raise GistRequestError("Schreiben gesendet, aber nicht bestätigen können: " + exc.out,
                               "Postfach prüfen. Nicht als erfolgreichen Upload behandeln.")
    received = confirmation.get("files") or {}
    for name, spec in files.items():
        if spec is None:
            if name in received:
                raise GistRequestError("Löschen wurde nicht bestätigt: " + name)
        elif name not in received or received[name].get("truncated") or received[name].get("content") != spec.get("content"):
            raise GistRequestError("Postfach-Inhalt weicht nach dem Schreiben ab: " + name,
                                   "Postfach prüfen. Kein erfolgreicher Upload bestätigt.")
    return body

def _patch_zip_aus_archiv(archiv):
    import base64
    if not isinstance(archiv, str) or not archiv.strip():
        raise ValueError("Leeres Patch-ZIP.")
    raw = base64.b64decode(archiv.strip(), validate=True)
    if len(raw) > MAX_HTTP_BYTES:
        raise ValueError("Patch-ZIP überschreitet 16 MiB.")
    found = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            parts = entry.filename.split("/")
            name = parts[-1]
            if len(parts) > 2 or name not in ("aktuell.patch", "aktuell.json") or name in found:
                raise ValueError("Patch-ZIP muss genau aktuell.patch und aktuell.json enthalten.")
            if entry.file_size > (MAX_PATCH_BYTES if name.endswith("patch") else 65536):
                raise ValueError("Patch-ZIP enthält eine zu große Datei.")
            found[name] = archive.read(entry).decode("utf-8")
    if set(found) != {"aktuell.patch", "aktuell.json"}:
        raise ValueError("Patch-ZIP ist unvollständig.")
    return found["aktuell.patch"], found["aktuell.json"]

def _patch_bereits_auf_main(proj, remote, patch, token, basis=""):
    """Prüft Übernahme ohne den Arbeitsbaum zu verändern.

    Mail-Patches werden auf ihrer angegebenen Basis in einem Wegwerf-Worktree
    angewendet. Git-Cherry vergleicht anschließend alle Patch-Kennungen mit main.
    Nur wenn jeder Commit ein Gegenstück hat, gilt der gesamte Patch als übernommen.
    """
    if not remote:
        return False
    mail = _ist_mail_patch(patch)
    start = remote
    if mail:
        start = _commit_full(proj, str(basis or "").strip(), token)
        if not start or start == remote:
            return False
        ancestor = run(["git", "merge-base", "--is-ancestor", start, remote], cwd=proj, token=token)
        if not ancestor["ok"]:
            return False
    temp = tempfile.TemporaryDirectory(prefix="projektmanager-merged-test-")
    added = run(["git", "worktree", "add", "--detach", temp.name, start], cwd=proj, token=token)
    if not added["ok"]:
        temp.cleanup()
        return False
    try:
        if mail:
            applied = run(_git_ident(proj, token) + ["am", "--empty=drop"], cwd=temp.name,
                          input_text=patch, token=token)
            if not applied["ok"]:
                run(["git", "am", "--abort"], cwd=temp.name, token=token)
                return False
            head = _commit_full(temp.name, "HEAD", token)
            if not head or head == start:
                return False
            compared = run(["git", "cherry", remote, head, start], cwd=temp.name, token=token)
            rows = [line.strip() for line in compared["out"].splitlines() if line.strip()]
            return compared["ok"] and bool(rows) and all(line.startswith("- ") for line in rows)
        check = run(["git", "apply", "--reverse", "--check", "-"], cwd=temp.name, input_text=patch, token=token)
        return check["ok"]
    finally:
        run(["git", "worktree", "remove", "--force", temp.name], cwd=proj, token=token)
        temp.cleanup()

def _patch_bereits_hinweis(remote):
    return {"ok": True, "info": True, "bereits_uebernommen": True,
            "out": "Dieser Patch ist bereits in GitHub-main %s enthalten. Keine erneute Anwendung nötig." % remote[:7],
            "loesung": "Falls der Eintrag noch im Postfach liegt: Alten Patch entfernen. Danach Lokal aktualisieren und Stand prüfen."}

def _patch_meta_fehler(patch, meta):
    if not isinstance(meta, dict):
        return "aktuell.json muss ein JSON-Objekt sein."
    if not isinstance(patch, str) or not re.search(r"^diff --git ", patch, re.M):
        return "Kein vollständiger Git-Patch: Eine Zeile muss mit „diff --git “ beginnen."
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES:
        return "Patch überschreitet 8 MiB. Bitte als vollständigen Repository-Zweig übergeben."
    basis = str(meta.get("basis") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", basis):
        return "In aktuell.json fehlt eine gültige Basis (7–40 Hex-Zeichen)."
    want = str(meta.get("sha256") or "").strip().lower()
    if not re.fullmatch(r"(?:[0-9a-f]{16}|[0-9a-f]{64})", want):
        return "In aktuell.json fehlt die Prüfsumme (16 oder 64 Hex-Zeichen)."
    actual = hashlib.sha256(patch.encode("utf-8")).hexdigest()
    matched = actual.startswith(want) if len(want) == 16 else actual == want
    if not matched:
        return "Prüfsumme stimmt nicht mit den exakten Patch-Bytes überein. Nichts gespeichert oder übernommen; Patch als unveränderte Datei/ZIP neu liefern."
    return None

def _patch_bloecke(patch):
    starts = list(re.finditer(r"^diff --git .*$", patch, re.M))
    blocks = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(patch)
        text = patch[match.start():end]
        try:
            parts = shlex.split(match.group(0))
        except ValueError:
            parts = match.group(0).split()
        new = bool(re.search(r"^new file mode |^--- /dev/null(?:\t|$)", text, re.M))
        deleted = bool(re.search(r"^deleted file mode |^\+\+\+ /dev/null(?:\t|$)", text, re.M))
        path = ""
        if len(parts) >= 4:
            path = parts[3] if deleted else parts[2]
            path = re.sub(r"^[ab]/", "", path)
        blocks.append({"path": path, "new": new, "deleted": deleted, "text": text})
    return blocks

def _patch_parse_check(patch, proj, token):
    stat = run(["git", "apply", "--stat", "-"], cwd=proj, input_text=patch, token=token)
    if not stat["ok"]:
        return {"ok": False, "out": "Patch unvollständig oder defekt: " + git_klar(stat["out"]),
                "loesung": "Vollständige Patch-Datei/ZIP verwenden. Es wurde nichts angewendet."}
    blocks = _patch_bloecke(patch)
    if not blocks:
        return {"ok": False, "out": "Patch enthält keine Dateiänderung."}
    for block in blocks:
        path = block["path"]
        if not path or path.startswith("/") or ".." in path.replace("\\", "/").split("/") or ".git" in path.split("/") or "\\" in path:
            return {"ok": False, "out": "Unsicherer oder nicht lesbarer Dateipfad im Patch: " + path[:120]}
    return None

def _remote_main_full(proj, token=""):
    remote = run(["git", "ls-remote", "origin", "refs/heads/main"], cwd=proj, token=token, timeout=20)
    if not remote["ok"] or not remote["out"].strip():
        return ""
    full = remote["out"].split()[0].lower()
    if not re.fullmatch(r"[0-9a-f]{40}", full):
        return ""
    fetched = run(["git", "fetch", "origin", "+refs/heads/main:refs/remotes/origin/main"],
                  cwd=proj, token=token, timeout=60)
    if not fetched["ok"]:
        return ""
    local = run(["git", "rev-parse", "--verify", "refs/remotes/origin/main"], cwd=proj, token=token)
    return full if local["ok"] and local["out"].strip() == full else ""

def _repo_sicher(proj, token="", main_required=False):
    status = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    if not status["ok"]:
        return {"ok": False, "out": "Projekt nicht lesbar: " + git_klar(status["out"])}
    if status["out"].strip():
        names = [line[3:] for line in status["out"].splitlines()[:6]]
        return {"ok": False, "out": "Arbeitsstand nicht sauber: " + ", ".join(names),
                "loesung": "Eigene Änderungen zuerst ausdrücklich speichern. Nichts wurde überschrieben."}
    branch = run(["git", "symbolic-ref", "--short", "HEAD"], cwd=proj, token=token)
    if not branch["ok"]:
        return {"ok": False, "out": "Kein normaler Branch ausgecheckt. Übergabe gestoppt."}
    if main_required and branch["out"].strip() != "main":
        return {"ok": False, "out": "Übergabe erwartet main; aktuell: " + branch["out"].strip()}
    for marker in ("rebase-apply", "rebase-merge"):
        path = run(["git", "rev-parse", "--git-path", marker], cwd=proj, token=token)["out"].strip()
        if path and os.path.isdir(os.path.join(proj, path)):
            return {"ok": False, "out": "Unvollendeter Git-Vorgang gefunden. Keine automatische Bereinigung.",
                    "loesung": "Vorgang bewusst prüfen und abschließen; der Helfer hat nichts zurückgesetzt."}
    return None

def _commit_full(proj, ref, token=""):
    result = run(["git", "rev-parse", "--verify", ref + "^{commit}"], cwd=proj, token=token)
    return result["out"].strip() if result["ok"] else ""

def _basis_gleich(meta, proj, token):
    remote = _remote_main_full(proj, token)
    if not remote:
        return "", {"ok": False, "out": "GitHub-main nicht bestätigt. Keine schreibende Übergabe ohne erreichbare Basis."}
    basis = str(meta.get("basis") or "").strip()
    resolved = _commit_full(proj, basis, token)
    if resolved != remote:
        return remote, {"ok": False, "basisfehler": True,
                        "out": "Patch-Basis %s passt nicht zu GitHub-main %s." % (basis[:12], remote[:7]),
                        "loesung": "Neuen Patch auf GitHub-main liefern oder „Basis korrigieren“ mit echter Anwendbarkeitsprüfung verwenden."}
    return remote, None

def _ist_mail_patch(patch):
    return bool(re.match(r"^From [0-9a-f]{40} ", patch) or re.match(r"^From:\s", patch))

def _mail_patch_probe(proj, basis, patch, token):
    temp = tempfile.TemporaryDirectory(prefix="projektmanager-am-test-")
    added = run(["git", "worktree", "add", "--detach", temp.name, basis], cwd=proj, token=token)
    if not added["ok"]:
        temp.cleanup()
        return {"ok": False, "out": "Patch-Testarbeitsplatz fehlgeschlagen: " + git_klar(added["out"])}
    try:
        applied = run(["git", "am", "--empty=drop"], cwd=temp.name, input_text=patch, token=token)
        if not applied["ok"]:
            run(["git", "am", "--abort"], cwd=temp.name, token=token)
            return {"ok": False, "out": "Mail-Patch passt nicht auf die Basis: " + git_klar(applied["out"]),
                    "loesung": "KI muss den vollständigen Patch auf den aktuellen Stand neu setzen."}
        return None
    finally:
        run(["git", "worktree", "remove", "--force", temp.name], cwd=proj, token=token)
        temp.cleanup()

def _plain_patch_probe(proj, basis, patch, token):
    temp = tempfile.TemporaryDirectory(prefix="projektmanager-apply-test-")
    added = run(["git", "worktree", "add", "--detach", temp.name, basis], cwd=proj, token=token)
    if not added["ok"]:
        temp.cleanup()
        return {"ok": False, "out": "Patch-Testarbeitsplatz fehlgeschlagen: " + git_klar(added["out"])}
    try:
        check = run(["git", "apply", "--check", "-"], cwd=temp.name, input_text=patch, token=token)
        return None if check["ok"] else {"ok": False, "out": "Patch passt nicht auf GitHub-main: " + git_klar(check["out"])}
    finally:
        run(["git", "worktree", "remove", "--force", temp.name], cwd=proj, token=token)
        temp.cleanup()

def _patch_secret_fehler(patch, token):
    for block in _patch_bloecke(patch):
        if SENSITIVE_FILE_RE.search(block["path"]):
            return "Potenziell geheime Datei im Patch blockiert: " + block["path"]
    if token and token in patch:
        return "Der Patch enthält das lokale Zugriffstoken. Übergabe blockiert."
    if re.search(r"(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]{20,})", patch):
        return "Der Patch enthält ein mögliches GitHub-Token. Übergabe blockiert."
    return None

def _raw_gist_datei(url, limit):
    data, _ = _http_bytes(url, limit, raw_only=True)
    try:
        return data.decode("utf-8")
    except UnicodeError:
        raise GistRequestError("Vollständige Gist-Datei ist kein gültiges UTF-8.", "Patch unverändert neu liefern.")

def _postfach_meta(data):
    files = data.get("files") or {}
    patch = (files.get("aktuell.patch") or {}).get("content") or ""
    try:
        meta = json.loads((files.get("aktuell.json") or {}).get("content") or "{}")
    except Exception:
        meta = {}
    return patch, meta

def _postfach_vergleich(patch, meta, old_patch, old_meta, allow_override=False):
    old_meta = old_meta if isinstance(old_meta, dict) else {}
    if not old_patch and not old_meta:
        return None
    new_sha = hashlib.sha256(patch.encode("utf-8")).hexdigest()[:16]
    old_sha = hashlib.sha256(old_patch.encode("utf-8")).hexdigest()[:16] if old_patch else "–"
    new_basis = str(meta.get("basis") or "").strip().lower()
    old_basis = str(old_meta.get("basis") or "").strip().lower()
    if old_patch == patch and old_basis == new_basis:
        return {"ok": True, "info": True,
                "out": "Identischer Patch liegt bereits im Postfach (Prüfsumme %s, Basis %s). Nichts geändert." % (new_sha, new_basis[:7])}
    if old_patch == patch:
        result = {"ok": False,
                  "out": "Patch-Datei ist inhaltsgleich, aber die Basis weicht ab: Postfach %s, neu %s. Nicht überschrieben." % (old_basis[:7] or "–", new_basis[:7] or "–"),
                  "loesung": "Metadaten/Basis prüfen; keinen identischen Patch mit abweichender Basis stillschweigend ersetzen."}
    else:
        result = {"ok": False,
                  "out": "Postfach enthält einen anderen Patch: alte Prüfsumme %s, Basis %s; neuer Patch Prüfsumme %s, Basis %s. Nicht überschrieben." % (old_sha, old_basis[:7] or "–", new_sha, new_basis[:7] or "–"),
                  "loesung": "Alten Patch entfernen oder ausdrücklich Überschreiben bestätigen."}
    if allow_override:
        result["ueberschreiben"] = True
    return result

def _patch_branch_name(meta, patch):
    checksum = hashlib.sha256(patch.encode("utf-8")).hexdigest()[:16]
    title = str(meta.get("titel") or "Arena-Patch").strip()[:200]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:24] or "patch"
    return "ki/" + slug + "-" + checksum[:8]

def _gh_offener_pr(proj, branch, token=""):
    view = run(["gh", "pr", "view", branch, "--json", "url,state,headRefName"], cwd=proj, token=token, timeout=30)
    if not view["ok"]:
        return None
    try:
        info = json.loads(view["out"])
    except Exception:
        return None
    if not isinstance(info, dict) or info.get("state") != "OPEN":
        return None
    if info.get("headRefName") and info.get("headRefName") != branch:
        return None
    url = str(info.get("url") or "").strip()
    if not re.fullmatch(r"https://[^/\s]+/[^/\s]+/[^/\s]+/pull/\d+", url):
        return None
    return url

def _erlaubte_adresse(url, raw_only=False):
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    raw_hosts = {"gist.githubusercontent.com", "raw.githubusercontent.com"}
    allowed = raw_hosts if raw_only else raw_hosts | {"github.com", "gist.github.com"}
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Nur HTTPS-Adressen ohne Zugangsdaten oder Sonderport erlaubt.")
    if host not in allowed and not (not raw_only and any(host.endswith(suffix) for suffix in (".e2b.app", ".arena.ai"))):
        raise ValueError("Adresse gehört nicht zu GitHub oder einer Arena-Vorschau.")
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    for item in addresses:
        address = ipaddress.ip_address(item[4][0])
        if getattr(address, "ipv4_mapped", None):
            address = address.ipv4_mapped
        if not address.is_global:
            raise ValueError("Private oder lokale Zieladresse blockiert.")
    return parsed

def _http_bytes(url, limit, raw_only=False):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(NoRedirect())
    current = url
    for _ in range(4):
        _erlaubte_adresse(current, raw_only)
        request = urllib.request.Request(current, headers={"User-Agent": "Projektmanager-Patch-Import"})
        try:
            with opener.open(request, timeout=30) as response:
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("Datei überschreitet die sichere Größengrenze.")
                return data, current
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location") if exc.code in (301, 302, 303, 307, 308) else None
            exc.close()
            if not location:
                raise
            current = urllib.parse.urljoin(current, location)
    raise ValueError("Zu viele Weiterleitungen.")

def _freier_spiel_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]

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
        "revision": HELPER_REVISION,
        "guiPfad": os.path.join(HERE, "index.html"),
        "guiVorhanden": os.path.isfile(os.path.join(HERE, "index.html")),
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
        return {"ok": True, "out": "Kein Token – Postfach nicht gelesen."}
    try:
        patch, meta = _postfach_meta(_gist_lesen(token))
        if not patch and not meta:
            return {"ok": True, "out": "Kein Patch im Postfach."}
        error = _patch_meta_fehler(patch, meta)
        if error:
            return {"ok": False, "out": error}
        remote, basis_error = _basis_gleich(meta, proj, token)
        if basis_error:
            if _patch_bereits_auf_main(proj, remote, patch, token, str(meta.get("basis") or "")):
                return _patch_bereits_hinweis(remote)
            return basis_error
        return {"ok": True, "out": "Prüfsumme und Basis %s stimmen mit GitHub-main überein." % str(meta["basis"])[:7]}
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}

def act_pruefen():
    proj, token = CFG["projekt"], read_token()
    status = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)
    remote = _remote_main_full(proj, token)
    steps = [["git status", status], ["HEAD", head],
             ["GitHub main", {"ok": bool(remote), "out": remote[:7] if remote else "nicht erreichbar"}]]
    if os.path.isdir(CFG["sicherung"]):
        steps.append(["Sicherung", run(["git", "-C", CFG["sicherung"], "rev-parse", "--short", "refs/heads/main"], token=token)])
    else:
        steps.append(["Sicherung", {"ok": False, "out": "Sicherungspfad nicht gefunden."}])
    if os.path.isfile(os.path.join(proj, "tools", "check.sh")):
        steps.append(["check.sh", run(["bash", "-c", 'ADVENTS_PROJ="$PWD" bash tools/check.sh'], cwd=proj, token=token)])
    steps.append(["Postfach", postfach_basis_check(token, proj)])
    return {"ok": all(step[1]["ok"] for step in steps), "github_main": remote[:7],
            "steps": [{"name": name, **value} for name, value in steps]}

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
    token = read_token()
    if not token:
        return _token_fehlt()
    proj = CFG["projekt"]
    safety = _repo_sicher(proj, token)
    if safety:
        return safety
    remote = _remote_main_full(proj, token)
    if not remote:
        return {"ok": False, "out": "GitHub-main nicht bestätigt – nichts abgelegt."}
    counts = run(["git", "rev-list", "--left-right", "--count", remote + "...HEAD"], cwd=proj, token=token)
    parts = counts["out"].split() if counts["ok"] else []
    if len(parts) != 2:
        return {"ok": False, "out": "Lokal/GitHub-Vergleich nicht lesbar."}
    behind, ahead = map(int, parts)
    if behind:
        return {"ok": False, "out": "Divergenz: lokal %s voraus, GitHub %s voraus. Nichts abgelegt." % (ahead, behind)}
    if not ahead:
        return {"ok": True, "info": True, "out": "Nichts abgelegt – keine lokalen Commits vor GitHub-main."}
    generated = run(["git", "format-patch", remote + "..HEAD", "--stdout"], cwd=proj, token=token,
                    limit=None, preserve=True)
    if not generated["ok"] or not generated["out"]:
        return {"ok": False, "out": "Kein Patch erzeugt: " + git_klar(generated["out"])}
    patch = generated["out"]
    secret = _patch_secret_fehler(patch, token)
    if secret:
        return {"ok": False, "out": secret, "loesung": "Geheimnis entfernen und den Stand bewusst neu speichern; nichts ins Postfach geschrieben."}
    title = run(["git", "log", "-1", "--pretty=%s"], cwd=proj, token=token)["out"].strip()
    meta = {"datei": "aktuell.patch", "sha256": hashlib.sha256(patch.encode()).hexdigest()[:16],
            "titel": title, "basis": remote, "commits": ahead}
    error = _patch_meta_fehler(patch, meta) or _patch_parse_check(patch, proj, token)
    if error:
        return error if isinstance(error, dict) else {"ok": False, "out": error}
    if not payload.get("force"):
        try:
            old_patch, old_meta = _postfach_meta(_gist_lesen(token))
            duplicate = _postfach_vergleich(patch, meta, old_patch, old_meta, allow_override=True)
            if duplicate:
                return duplicate
        except GistRequestError as exc:
            return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    try:
        _gist_schreiben({"aktuell.patch": {"content": patch}, "aktuell.json": {"content": json.dumps(meta, ensure_ascii=False)}}, token)
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    return {"ok": True, "out": "Patch abgelegt und zurückgelesen (%d Commit(s)), Prüfsumme %s, Basis %s." % (ahead, meta["sha256"], remote[:7])}

def act_uebernehmen():
    token = read_token()
    if not token:
        return _token_fehlt()
    proj = CFG["projekt"]
    safety = _repo_sicher(proj, token, main_required=True)
    if safety:
        return safety
    try:
        patch, meta = _postfach_meta(_gist_lesen(token))
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    error = _patch_meta_fehler(patch, meta)
    if error:
        return {"ok": False, "out": error}
    secret = _patch_secret_fehler(patch, token)
    if secret:
        return {"ok": False, "out": secret}
    error = _patch_parse_check(patch, proj, token)
    if error:
        return error
    remote, basis_error = _basis_gleich(meta, proj, token)
    if basis_error:
        if _patch_bereits_auf_main(proj, remote, patch, token, str(meta.get("basis") or "")):
            return _patch_bereits_hinweis(remote)
        return basis_error
    mail = _ist_mail_patch(patch)
    if mail:
        error = _mail_patch_probe(proj, remote, patch, token)
    else:
        error = _plain_patch_probe(proj, remote, patch, token)
    if error:
        return error
    branch = _patch_branch_name(meta, patch)
    title = str(meta.get("titel") or "Arena-Patch").strip()[:200]
    local_exists = run(["git", "show-ref", "--verify", "--quiet", "refs/heads/" + branch], cwd=proj, token=token)["ok"]
    remote_exists = bool(run(["git", "ls-remote", "origin", "refs/heads/" + branch], cwd=proj, token=token)["out"].strip())
    if local_exists or remote_exists:
        pr_url = _gh_offener_pr(proj, branch, token)
        if pr_url:
            return {"ok": True, "info": True, "pr_url": pr_url,
                    "out": "Vorhandener offener Pull Request erkannt: " + pr_url + ". Keine erneute Anwendung, kein Push.",
                    "loesung": "Knopf „PR öffnen“ verwenden."}
        if local_exists:
            return {"ok": False, "out": "Lokaler Zweig existiert bereits: " + branch + ". Nichts überschrieben."}
        return {"ok": False, "out": "GitHub-Zweig existiert bereits: " + branch + ". Nichts überschrieben."}
    original_branch = run(["git", "symbolic-ref", "--short", "HEAD"], cwd=proj, token=token)["out"].strip()
    created = run(["git", "checkout", "-b", branch, remote], cwd=proj, token=token)
    if not created["ok"]:
        return {"ok": False, "out": "Zweig nicht angelegt: " + git_klar(created["out"])}

    def finish(result, keep_branch):
        back = run(["git", "checkout", original_branch], cwd=proj, token=token)
        if not back["ok"]:
            result["ok"] = False
            result["out"] += " Rückwechsel auf %s NICHT bestätigt: %s" % (original_branch, git_klar(back["out"]))
            return result
        if not keep_branch:
            run(["git", "branch", "-D", branch], cwd=proj, token=token)
        return result

    if mail:
        applied = run(["git", "am", "--empty=drop"], cwd=proj, input_text=patch, token=token)
        if not applied["ok"]:
            run(["git", "am", "--abort"], cwd=proj, token=token)
            return finish({"ok": False, "out": "git am fehlgeschlagen: " + git_klar(applied["out"])}, False)
        if _commit_full(proj, "HEAD", token) == remote:
            return finish({"ok": True, "info": True, "out": "Mail-Patch enthielt keine neue Änderung; main unverändert."}, False)
    else:
        applied = run(["git", "apply", "--index", "-"], cwd=proj, input_text=patch, token=token)
        if not applied["ok"]:
            return finish({"ok": False, "out": "git apply fehlgeschlagen: " + git_klar(applied["out"])}, False)
        committed = run(_commit_ident(proj, token) + ["-m", title], cwd=proj, token=token)
        if not committed["ok"]:
            return {"ok": False, "branch": branch,
                    "out": "Plain-Diff angewendet, aber Commit fehlgeschlagen. Änderungen verbleiben isoliert auf Zweig " + branch + "; nicht automatisch nach main mitgenommen.",
                    "detail": git_klar(committed["out"]),
                    "loesung": "Arbeitszweig bewusst prüfen. Kein Push und kein PR erfolgt."}
    if not os.path.isfile(os.path.join(proj, "node_modules/.bin/tsc")):
        return finish({"ok": False, "out": "tsc fehlt im Projekt. Abhängigkeiten zuerst installieren; kein Push."}, False)
    tsc = run(["./node_modules/.bin/tsc", "--noEmit"], cwd=proj, token=token)
    build = run(["npm", "run", "build"], cwd=proj, token=token)
    if not tsc["ok"] or not build["ok"]:
        return finish({"ok": False, "out": "Typen %s / Build %s – kein Push, kein PR." % ("OK" if tsc["ok"] else "Fehler", "OK" if build["ok"] else "Fehler"),
                       "detail": tsc["out"][-500:] + "\n" + build["out"][-500:]}, False)
    branch_head = _commit_full(proj, "HEAD", token)
    push = run(["git", "push", "-u", "origin", branch], cwd=proj, token=token, timeout=60)
    pushed = run(["git", "ls-remote", "origin", "refs/heads/" + branch], cwd=proj, token=token)["out"].strip()
    remote_head = pushed.split()[0] if pushed else ""
    if remote_head != branch_head:
        return finish({"ok": False, "out": "Push nicht bestätigt: " + git_klar(push["out"])}, False)
    pr = run(["gh", "pr", "create", "--base", "main", "--head", branch, "--fill"], cwd=proj, token=token, timeout=45)
    match = re.search(r"https://\S+?/pull/\d+", pr["out"]) if pr["ok"] else None
    pr_url = match.group(0) if match else ""
    if not pr_url:
        pr_url = _gh_offener_pr(proj, branch, token) or ""
    if not pr_url:
        return finish({"ok": False, "branch": branch,
                       "out": "Zweig gepusht, aber kein Pull Request bestätigt. Das ist kein PR-Erfolg.",
                       "detail": pr["out"], "loesung": "Lokale gh-Anmeldung prüfen; Zweig bleibt für eine bewusste PR-Öffnung erhalten."}, True)
    return finish({"ok": True, "branch": branch, "pr_url": pr_url,
                   "out": "Zweig %s · Typen/Build OK · Pull Request bestätigt · zurück auf %s." % (branch, original_branch)}, True)

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
    token, proj = read_token(), CFG["projekt"]
    safety = _repo_sicher(proj, token, main_required=True)
    if safety:
        return safety
    remote = _remote_main_full(proj, token)
    if not remote:
        return {"ok": False, "out": "GitHub-main nicht bestätigt; nichts aktualisiert."}
    counts = run(["git", "rev-list", "--left-right", "--count", remote + "...HEAD"], cwd=proj, token=token)
    parts = counts["out"].split() if counts["ok"] else []
    if len(parts) != 2:
        return {"ok": False, "out": "Abgleich nicht lesbar; nichts aktualisiert."}
    behind, ahead = map(int, parts)
    if behind and ahead:
        return {"ok": False, "out": "Divergenz: GitHub %s voraus, lokal %s voraus. Kein Reset, kein Merge." % (behind, ahead)}
    if not behind:
        return {"ok": True, "info": True, "out": "GitHub-main enthält nichts Neues; lokale Commits bleiben unverändert."}
    before = _commit_full(proj, "HEAD", token)
    pull = run(["git", "pull", "--ff-only", "origin", "main"], cwd=proj, token=token, timeout=60)
    if not pull["ok"]:
        return {"ok": False, "out": "Aktualisierung fehlgeschlagen: " + git_klar(pull["out"])}
    return {"ok": True, "out": "Lokal aktualisiert: %s → %s." % (before[:7], _commit_full(proj, "HEAD", token)[:7])}

def act_sichern():
    token, sicher, proj = read_token(), CFG["sicherung"], CFG["projekt"]
    if not os.path.isdir(sicher) or not run(["git", "-C", sicher, "rev-parse", "--git-dir"], token=token)["ok"]:
        return {"ok": False, "out": "Sicherung ist kein vorhandenes Git-Repository: " + sicher}
    remote = _remote_main_full(proj, token)
    if not remote:
        return {"ok": False, "out": "GitHub-main nicht bestätigt; Sicherung und Übergabedatei nicht geschrieben."}
    bare = run(["git", "-C", sicher, "rev-parse", "--is-bare-repository"], token=token)["out"].strip() == "true"
    # Quelle ist die bestätigte GitHub-Referenz des Projekts, nicht ein eventuell lokales Spiegel-origin.
    source_ref = "refs/remotes/origin/main"
    if bare:
        updated = run(["git", "-C", sicher, "fetch", proj, "+" + source_ref + ":refs/heads/main"], token=token, timeout=30)
        main_ref = "refs/heads/main"
    else:
        updated = run(["git", "-C", sicher, "fetch", proj, source_ref], token=token, timeout=30)
        if updated["ok"] and run(["git", "-C", sicher, "status", "--porcelain"], token=token)["out"].strip():
            return {"ok": False, "out": "Sicherung hat offene Änderungen – nichts zurückgesetzt."}
        if updated["ok"]:
            updated = run(["git", "-C", sicher, "reset", "--hard", "FETCH_HEAD"], token=token)
        main_ref = "HEAD"
    if not updated["ok"]:
        return {"ok": False, "out": "Sicherung nicht aktualisiert: " + git_klar(updated["out"])}
    backup_full = run(["git", "-C", sicher, "rev-parse", "--verify", main_ref], token=token)["out"].strip()
    if backup_full != remote:
        return {"ok": False, "out": "Sicherung folgt nicht GitHub-main; Übergabedatei nicht geschrieben."}
    main = remote[:7]
    path = os.path.join(proj, "docs", "UEBERGABE.md")
    existing = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as handle:
            existing = handle.read()
    hand_match = re.search(r"<!--\s*HAND:.*", existing, re.S)
    hand = hand_match.group(0) if hand_match else "<!-- HAND: ab hier schreibt nur der Besitzer -->\n\n## Als Nächstes\n"
    previous_auto = existing[:hand_match.start()] if hand_match else ""
    marker = re.search(r"main ([0-9a-f]+) · Kennung ([^\n]+)", previous_auto)
    if marker and marker.group(1) == main and marker.group(2).strip() == str(CFG.get("kennung", "")):
        auto = previous_auto
    else:
        auto = "## Stand (automatisch, %s)\nmain %s · Kennung %s · Prüfung: siehe Projektmanager\n\n" % (time.strftime("%d.%m.%Y %H:%M"), main, CFG.get("kennung", ""))
    desired = auto + hand
    changed = desired != existing
    if changed:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(desired)
        except Exception as exc:
            return {"ok": False, "out": "Übergabedatei nicht schreibbar: " + str(exc)}
    return {"ok": True, "out": "Sicherung auf GitHub-main %s aktualisiert. Übergabedatei %s" % (main, "geändert – nicht automatisch committet; bewusst speichern." if changed else "unverändert – kein neuer Commit erzeugt.")}

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
    proj = CFG["projekt"]
    try:
        patch, meta = _postfach_meta(_gist_lesen(token))
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out}
    remote = _remote_main_full(proj, token)
    if not remote:
        return {"ok": False, "out": "GitHub-main nicht bestätigt; Basis nicht geändert."}
    candidate = dict(meta) if isinstance(meta, dict) else {}
    old = str(candidate.get("basis") or "–")
    candidate["basis"] = remote
    error = _patch_meta_fehler(patch, candidate) or _patch_parse_check(patch, proj, token)
    if error:
        return error if isinstance(error, dict) else {"ok": False, "out": error}
    if _patch_bereits_auf_main(proj, remote, patch, token, str(meta.get("basis") or "")):
        return _patch_bereits_hinweis(remote)
    if _ist_mail_patch(patch):
        error = _mail_patch_probe(proj, remote, patch, token)
    else:
        error = _plain_patch_probe(proj, remote, patch, token)
    if error:
        return error
    try:
        _gist_schreiben({"aktuell.json": {"content": json.dumps(candidate, ensure_ascii=False)}}, token)
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    return {"ok": True, "out": "Basis %s → %s gesetzt, nachdem der unveränderte Patch Anwendbarkeitsprüfung bestanden hat." % (old[:7], remote[:7])}

def _data_uri_inhalt(html_text):
    import base64
    patch, meta = "", ""
    for match in re.finditer(r"data:[A-Za-z0-9/.+-]+;(?:charset=[^;]+;)?base64,([A-Za-z0-9+/=]+)", html_text):
        try:
            raw = base64.b64decode(match.group(1), validate=True)
            if len(raw) > MAX_PATCH_BYTES:
                continue
            text = raw.decode("utf-8")
        except Exception:
            continue
        if re.search(r"^diff --git ", text, re.M) and not patch:
            patch = text
        elif '"basis"' in text and not meta:
            meta = text
    return patch, meta

def act_patch_von_url(payload):
    url = str(payload.get("url") or "").strip()
    if not url:
        return {"ok": False, "out": "Keine Adresse angegeben."}
    if not url.startswith("https://"):
        return {"ok": False, "out": "Bitte eine vollständige HTTPS-Adresse verwenden."}
    try:
        data, final_url = _http_bytes(url, MAX_HTTP_BYTES)
        patch, meta_text = "", ""
        if data.startswith(b"PK\x03\x04"):
            found = {}
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for entry in archive.infolist():
                    if entry.is_dir():
                        continue
                    parts = entry.filename.split("/")
                    name = parts[-1]
                    if len(parts) > 2 or name not in ("aktuell.patch", "aktuell.json") or name in found:
                        raise ValueError("Patch-ZIP muss genau aktuell.patch und aktuell.json enthalten.")
                    if entry.file_size > (MAX_PATCH_BYTES if name.endswith("patch") else 65536):
                        raise ValueError("Patch-ZIP enthält eine zu große Datei.")
                    found[name] = archive.read(entry).decode("utf-8")
            if set(found) != {"aktuell.patch", "aktuell.json"}:
                raise ValueError("Patch-ZIP ist unvollständig.")
            patch, meta_text = found["aktuell.patch"], found["aktuell.json"]
        else:
            parsed = urllib.parse.urlparse(final_url)
            host = (parsed.hostname or "").lower()
            if host == "gist.github.com" and GIST_ID in parsed.path:
                patch, meta = _postfach_meta(_gist_lesen(read_token()))
                meta_text = json.dumps(meta, ensure_ascii=False)
            else:
                text = data.decode("utf-8")
                if re.search(r"^diff --git ", text, re.M):
                    patch = text
                    base_url = final_url.rsplit("/", 1)[0]
                    if host == "github.com" and "/blob/" in parsed.path:
                        parts = parsed.path.strip("/").split("/")
                        if len(parts) >= 5:
                            base_url = "https://raw.githubusercontent.com/" + "/".join(parts[:2] + parts[3:-1])
                    if urllib.parse.urlparse(base_url).hostname not in ("gist.githubusercontent.com", "raw.githubusercontent.com"):
                        raise ValueError("Für GitHub bitte einen Raw-Link oder den direkten Patch-ZIP-Link verwenden.")
                    raw, _ = _http_bytes(base_url + "/aktuell.json", 65536, raw_only=True)
                    meta_text = raw.decode("utf-8")
                else:
                    patch, meta_text = _data_uri_inhalt(text)
        if not patch or not meta_text:
            return {"ok": False, "out": "Kein vollständiges Patch-Paket gefunden.",
                    "loesung": "Direkten ZIP-Link mit aktuell.patch/aktuell.json oder Raw-Patch plus Metadatei verwenden."}
        return act_patch_einfuegen({"patch": patch, "meta": meta_text})
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    except Exception as exc:
        return {"ok": False, "out": "Patch-Import gestoppt: " + scrub(str(exc), read_token())[:200],
                "loesung": "Direkten HTTPS-Link auf das vollständige Patch-ZIP verwenden."}

def act_projekt_diagnose():
    token, proj = read_token(), CFG["projekt"]
    status = run(["git", "status", "--porcelain", "-uall"], cwd=proj, token=token)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, token=token)
    if not status["ok"] or not head["ok"]:
        return {"ok": False, "out": "Projektordner ist kein lesbares Git-Repository: " + proj}
    offene = [line for line in status["out"].splitlines() if line.strip()]
    zeilen = ["Projekt: %s · HEAD %s · %s" % (proj, head["out"].strip(), "Stand sauber" if not offene else "%d offene Änderung(en)" % len(offene))]
    remote = _remote_main_full(proj, token)
    if remote:
        zeilen.append("GitHub-main: %s · lokaler HEAD: %s" % (remote[:7], head["out"].strip()))
        counts = run(["git", "rev-list", "--left-right", "--count", remote + "...HEAD"], cwd=proj, token=token)
        parts = counts["out"].split() if counts["ok"] else []
        if len(parts) == 2:
            behind, ahead = parts
            zeilen.append("Abgleich: GitHub %s voraus · lokal %s voraus (%s %s)." % (behind, ahead, behind, ahead))
    else:
        zeilen.append("GitHub-main: nicht erreichbar; kein verlässlicher Abgleich.")
    patch_ok = True
    pr_url = ""
    if token:
        try:
            patch, meta = _postfach_meta(_gist_lesen(token))
            if not patch and not meta:
                zeilen.append("Postfach leer.")
            else:
                error = _patch_meta_fehler(patch, meta)
                if error:
                    zeilen.append("Postfach-Warnung: " + error)
                    patch_ok = False
                else:
                    blocks = _patch_bloecke(patch)
                    new = [b["path"] for b in blocks if b["new"] and not os.path.exists(os.path.join(proj, b["path"]))]
                    existing = [b["path"] for b in blocks if not b["new"] and os.path.exists(os.path.join(proj, b["path"]))]
                    missing = [b["path"] for b in blocks if not b["new"] and not b["deleted"] and not os.path.exists(os.path.join(proj, b["path"]))]
                    zeilen.append("Patch betrifft %d Dateiabschnitt(e): %d bereits vorhanden, %d neu vorgesehen%s." %
                                  (len(blocks), len(existing), len(new), ("; neu: " + ", ".join(new)) if new else ""))
                    if missing:
                        zeilen.append("Basisdateien fehlen lokal: " + ", ".join(missing))
                    detected_pr = _gh_offener_pr(proj, _patch_branch_name(meta, patch), token)
                    if detected_pr:
                        pr_url = detected_pr
                        zeilen.append("Offener Pull Request erkannt: " + pr_url)
                    remote_main, basis_error = _basis_gleich(meta, proj, token)
                    if basis_error:
                        if _patch_bereits_auf_main(proj, remote_main, patch, token, str(meta.get("basis") or "")):
                            hint = _patch_bereits_hinweis(remote_main)
                            zeilen.append(hint["out"] + " " + hint["loesung"])
                        else:
                            zeilen.append(basis_error["out"])
                            patch_ok = False
                    zeilen.append("Dateiexistenz allein beweist keine Patch-Übernahme; Dafür sind Prüfsumme, Basis und Git-Anwendung zuständig.")
        except GistRequestError as exc:
            zeilen.append("Postfach: " + exc.out)
            patch_ok = False
    else:
        zeilen.append("Kein Token – Postfach nicht gelesen.")
    result = {"ok": patch_ok, "zeilen": zeilen, "offen": len(offene), "github_main": remote[:7],
              "out": "Projekt-Diagnose fertig – Patch-Inhalt erfasst; Übernahme nicht durch Dateiexistenz bewiesen." if patch_ok else "Projekt-Diagnose fertig – Postfachprüfung erfordert Aufmerksamkeit."}
    if pr_url:
        result["pr_url"] = pr_url
    return result

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
    if payload.get("archiv"):
        try:
            patch, meta_text = _patch_zip_aus_archiv(payload["archiv"])
        except Exception as exc:
            return {"ok": False, "out": "Patch-ZIP nicht lesbar: " + str(exc)[:160],
                    "loesung": "ZIP mit genau aktuell.patch und aktuell.json wählen; keine Textumwandlung."}
    else:
        patch = payload.get("patch") or ""
        meta_text = str(payload.get("meta") or "").strip()
    if len(meta_text.encode("utf-8")) > 65536:
        return {"ok": False, "out": "aktuell.json ist zu groß (maximal 64 KiB)."}
    try:
        meta = json.loads(meta_text)
    except Exception:
        return {"ok": False, "out": "aktuell.json fehlt oder ist nicht lesbar."}
    error = _patch_meta_fehler(patch, meta)
    if error:
        return {"ok": False, "out": error, "loesung": "Originaldatei unverändert liefern; Prüfsumme wird niemals stillschweigend ersetzt."}
    proj = CFG["projekt"]
    secret = _patch_secret_fehler(patch, token)
    if secret:
        return {"ok": False, "out": secret}
    error = _patch_parse_check(patch, proj, token)
    if error:
        return error
    remote, basis_error = _basis_gleich(meta, proj, token)
    if basis_error:
        if _patch_bereits_auf_main(proj, remote, patch, token, str(meta.get("basis") or "")):
            return _patch_bereits_hinweis(remote)
        return basis_error
    try:
        old_patch, old_meta = _postfach_meta(_gist_lesen(token))
        duplicate = _postfach_vergleich(patch, meta, old_patch, old_meta, allow_override=False)
        if duplicate:
            return duplicate
        _gist_schreiben({"aktuell.patch": {"content": patch}, "aktuell.json": {"content": json.dumps(meta, ensure_ascii=False)}}, token)
    except GistRequestError as exc:
        return {"ok": False, "out": exc.out, "loesung": exc.loesung}
    paths = list(dict.fromkeys(block["path"] for block in _patch_bloecke(patch)))
    return {"ok": True, "out": "Patch unverändert abgelegt und zurückgelesen: %d Datei(en), Prüfsumme %s, Basis %s." % (len(paths), str(meta["sha256"])[:16], str(meta["basis"])[:7])}

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
    proj = CFG["projekt"]
    if not os.path.isdir(proj):
        return {"url": "", "out": "Projekt nicht gefunden: " + proj}
    npm = shutil.which("npm")
    if not npm:
        return {"url": "", "out": "npm nicht gefunden – Node.js wird für den Spielstart benötigt."}
    if GAME_PROC is not None and GAME_PROC.poll() is None:
        stopped = stop_game()
        if not stopped.get("ok"):
            return {"url": "", "out": "Alter Spielserver konnte nicht beendet werden: " + stopped.get("out", "")}
    port = _freier_spiel_port()
    try:
        logf = open(GAME_LOG, "w")
        GAME_PROC = subprocess.Popen(
            [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", str(port), "--strictPort"],
            cwd=proj,
            stdout=logf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except Exception as e:
        return {"url": "", "out": "Spielstart fehlgeschlagen: " + str(e)}
    for _ in range(60):
        time.sleep(0.5)
        if GAME_PROC.poll() is not None:
            tail = ""
            try:
                with open(GAME_LOG, encoding="utf-8", errors="replace") as fp:
                    tail = fp.read()[-300:].strip()
            except Exception:
                pass
            return {"url": "", "out": "Spielstart endete sofort. " + tail}
        probe = _probe(port)
        title = (probe or {}).get("title", "")
        if probe and ("Adventshaus" in title or "Luni" in title):
            url = "http://127.0.0.1:%d/?pm_fresh=%d" % (port, int(time.time()))
            return {"url": url, "gestartet": True, "out": "Spiel frisch aus dem aktuellen Projektordner gestartet: " + url}
    return {"url": "", "out": "Spiel startet nicht (30 s). Log: " + GAME_LOG}

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
            self._json(404, {
                "ok": False,
                "out": "GUI-Datei nicht gefunden: " + fp,
                "ordner": HERE,
                "erwartet": fp,
                "prozess_pid": os.getpid(),
                "loesung": "Diesen Helfer beenden und genau den Ordner neu starten, der die index.html enthaelt: bash " + os.path.join(HERE, "neustart.sh"),
            })
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
        if length > MAX_HTTP_BYTES + 65_536:
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
    import errno
    import shlex

    gui_path = os.path.join(HERE, "index.html")
    if not os.path.isfile(gui_path):
        print("Projektmanager wurde NICHT gestartet: index.html fehlt am Helfer-Ort.", flush=True)
        print("Erwartete Datei: " + gui_path, flush=True)
        print("Helfer-Ordner: " + HERE, flush=True)
        print("Das Projekt-Pfadfeld in Einstellungen ist nicht der Helfer-Ordner. Das Paket vollstaendig in einen Ordner entpacken; keinen laufenden Ordner verschieben.", flush=True)
        return 1

    port = int(CFG.get("port", 8790))
    url = "http://127.0.0.1:%d/" % port
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    try:
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            print("Port %d ist bereits belegt. Dieser Helfer wurde NICHT gestartet." % port, flush=True)
            print("Ein anderer Prozess oder ein alter Helfer kann diese Adresse bedienen. Das ist keine Erfolgsmeldung.", flush=True)
        else:
            print("Helfer konnte Port %d nicht öffnen: %s" % (port, exc), flush=True)
            print("Dieser Helfer wurde NICHT gestartet; es wurde kein Browser geöffnet.", flush=True)
        print("Vorgesehener Helfer-Ordner: " + HERE, flush=True)
        print("GUI-Datei vorhanden: " + gui_path, flush=True)
        print("Gezielter Neustart aller erkannten Projektmanager-Helfer: bash " + shlex.quote(os.path.join(HERE, "neustart.sh")), flush=True)
        return 1
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
    raise SystemExit(main())
