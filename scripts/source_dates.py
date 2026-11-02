#!/usr/bin/env python3
"""Datum der letzten inhaltlichen Änderung einer Quelle, aus der Git-Historie. Nur Standardbibliothek.

Eine Quelle ist ein Ausschnitt einer Datei (ein README-Abschnitt, ein Eintrag in data/*.json, eine Ratgeber-Datei).
Für jeden Commit, der die Datei berührt, wird der Ausschnitt vor und nach dem Commit normalisiert verglichen.
Normalisiert heißt: eigene Domain und UTM-Parameter, das Link-Check-Datum und Leerraum fallen heraus.
Commits, die nur die Domain, Links auf die eigene Seite oder anderes ändern, zählen deshalb nicht.

Ergebnis je Quelle: (erstes Erscheinen, letzte inhaltliche Änderung) als ISO-Datum des Commits (Committer-Datum).
Weicht die Arbeitskopie vom letzten Commit ab, gilt die Änderung als heute (sie wird mit dem nächsten Commit wahr).
Es wird nie ein Datum geschätzt: Gibt es keine Git-Historie oder reicht die Historie der Datei in einem flachen
Klon bis an dessen Grenze, liefert dates() None und der Aufrufer nimmt den zuletzt gespeicherten Stand (data/lastmod.json).
"""
import re
import subprocess
from datetime import date
from pathlib import Path

OWN_URL = re.compile(r"https?://(?:jmp-collab\.github\.io/awesome-ai-tools|ainterview\.space)[^\s)\"'<>\]]*")
UTM = re.compile(r"[?&]utm_[a-z]+=[^&\s)\"'<>\]]*")
LINK_CHECK = re.compile(r"Link-Check \(Stand: \d{2}\.\d{2}\.\d{4}\)")


def normalize(text):
    text = OWN_URL.sub("<SITE>", text)
    text = UTM.sub("", text)
    text = LINK_CHECK.sub("Link-Check", text)
    return re.sub(r"\s+", " ", text).strip()


class History:
    def __init__(self, root):
        self.root = Path(root)
        self._show, self._log = {}, {}
        try:
            self.ok = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--is-inside-work-tree"],
                                     capture_output=True, text=True).stdout.strip() == "true"
        except FileNotFoundError:
            self.ok = False
        self.shallow = set()
        if self.ok:  # flacher Klon: Grenz-Commits haben keine Eltern, Historie dahinter fehlt
            gitdir = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--git-dir"], capture_output=True, text=True).stdout.strip()
            f = (self.root / gitdir / "shallow") if gitdir else None
            if f and f.exists():
                self.shallow = set(f.read_text().split())

    def log(self, path):
        if path not in self._log:
            out = subprocess.run(["git", "-C", str(self.root), "log", "--format=%H%x09%P%x09%cs", "--", path],
                                 capture_output=True, text=True, check=True).stdout
            rows = []
            for line in out.splitlines():
                sha, parents, day = line.split("\t")
                rows.append((sha, parents.split()[0] if parents else None, day))
            self._log[path] = rows
        return self._log[path]

    def show(self, rev, path):
        if rev is None:
            return None
        key = (rev, path)
        if key not in self._show:
            r = subprocess.run(["git", "-C", str(self.root), "show", f"{rev}:{path}"], capture_output=True)
            self._show[key] = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
        return self._show[key]

    def dates(self, path, extract, today=None):
        """(erstes Erscheinen, letzte inhaltliche Änderung) des Ausschnitts extract(dateitext) oder None ohne Git.
        extract bekommt den Dateitext (oder None) und liefert einen Vergleichstext oder None (Ausschnitt fehlt)."""
        if not self.ok:
            return None

        def ex(txt):
            if txt is None:
                return None
            try:
                v = extract(txt)
            except Exception:  # alte Dateiformate: Ausschnitt gilt als nicht vorhanden
                return None
            return None if v is None else normalize(v)
        first = last = None
        rows = self.log(path)
        if any(sha in self.shallow for sha, _, _ in rows):
            return None  # Historie der Datei reicht über die Grenze eines flachen Klons: Datum unbekannt
        for sha, parent, day in rows:
            cur = ex(self.show(sha, path))
            if cur is None:
                continue
            prev = ex(self.show(parent, path))
            if cur != prev:
                last = max(last or day, day)
                if prev is None:
                    first = min(first or day, day)
        work_file = self.root / path
        work = ex(work_file.read_text(encoding="utf-8")) if work_file.exists() else None
        if work is None:
            return None
        if work != ex(self.show("HEAD", path)):
            today = today or date.today().isoformat()
            last = today
            first = first or today
        return first, last
