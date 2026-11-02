#!/usr/bin/env python3
"""Spiegelt den gebauten Stand eines Commits in das öffentliche Publish-Repo. Nur Standardbibliothek.

Das Quell-Repo bleibt privat. Öffentlich liegen nur der Webroot und die Dateien, auf die die Seite verlinkt:
docs/ (GitHub Pages aus /docs), README.de.md (die Liste), README.md (ohne Hinweise auf Build-Skripte) und LICENSE.
Jeder Lauf hängt genau einen Commit an, Datum = jetzt, Nachricht „Website-Stand TT.MM.JJJJ“. Ist nichts geändert,
passiert nichts.

    python3 scripts/publish.py --ref origin/main --remote https://github.com/jmp-collab/awesome-ai-tools --dir /tmp/publish
    python3 scripts/publish.py --ref origin/main --dir /tmp/publish --no-push      # nur zusammenstellen und prüfen
"""
import argparse
import io
import re
import shutil
import subprocess
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("README.de.md", "README.md", "LICENSE")
AUTHOR = ("Schmitts Katze", "238795302+jmp-collab@users.noreply.github.com")  # Konto, dem beide Repos gehören
DROP_README = re.compile(r"scripts/|build_de_page|check_links|generated from", re.I)


def git(*args, cwd=ROOT, check=True, env=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check, env=env)


def export(ref, dest):
    """docs/ und FILES aus ref nach dest (ohne Arbeitskopie, ohne Git-Metadaten)."""
    data = subprocess.run(["git", "archive", "--format=tar", ref, "docs", *FILES], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        t.extractall(dest, filter="data")
    readme = dest / "README.md"
    lines = readme.read_text(encoding="utf-8").split("\n")
    readme.write_text("\n".join(l for l in lines if not DROP_README.search(l)), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--remote", help="URL des öffentlichen Publish-Repos")
    ap.add_argument("--dir", required=True, help="Arbeitsordner für den Publish-Klon")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    work = Path(a.dir).resolve()
    # Schutz: nie im Quell-Repo oder in einem fremden Ordner löschen
    if work == ROOT or ROOT in work.parents or work in ROOT.parents:
        raise SystemExit(f"--dir {work} liegt im oder über dem Quell-Repo; bitte einen eigenen Publish-Ordner angeben")
    if (work / ".git").exists():
        url = git("remote", "get-url", "origin", cwd=work, check=False).stdout.strip()
        if a.remote and url != a.remote:
            raise SystemExit(f"{work} ist ein Klon von {url or '(kein origin)'}, nicht von {a.remote}")
        if url:
            git("fetch", "--quiet", "origin", cwd=work)
            if git("rev-parse", "--verify", "--quiet", "origin/main", cwd=work, check=False).returncode == 0:
                git("checkout", "--quiet", "-B", "main", "origin/main", cwd=work)
                git("reset", "--quiet", "--hard", "origin/main", cwd=work)
    else:
        if work.exists() and any(work.iterdir()):
            raise SystemExit(f"{work} ist nicht leer und kein Publish-Klon; nichts gelöscht")
        work.mkdir(parents=True, exist_ok=True)
        if a.remote:
            git("clone", "--quiet", a.remote, str(work), cwd=ROOT)  # Fehler (Zugriff, Tippfehler) brechen ab
        else:
            git("init", "--quiet", cwd=work)
    git("symbolic-ref", "HEAD", "refs/heads/main", cwd=work)  # auch bei leerem Repo und init.defaultBranch=master
    if a.ref.startswith("origin/"):  # gemergten Stand holen, nicht den lokalen Zwischenstand
        git("fetch", "--quiet", "origin", a.ref.split("/", 1)[1])
    for p in work.iterdir():
        if p.name != ".git":
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    export(a.ref, work)
    git("add", "-A", cwd=work)
    if not git("status", "--porcelain", cwd=work).stdout.strip():
        print("Publish-Repo ist schon auf diesem Stand.")
        return
    name, mail = AUTHOR
    msg = f"Website-Stand {date.today().strftime('%d.%m.%Y')}"
    git("-c", f"user.name={name}", "-c", f"user.email={mail}", "commit", "--quiet", "-m", msg, cwd=work)
    print(git("log", "--oneline", "-1", cwd=work).stdout.strip(), "|", git("ls-files", cwd=work).stdout.count("\n"), "Dateien")
    if a.remote and not a.no_push:
        git("push", "--quiet", "-u", "origin", "main", cwd=work)
        print("gepusht:", a.remote)


if __name__ == "__main__":
    main()
