#!/usr/bin/env python3
"""Favicons der Tools einmalig holen und lokal ablegen (docs/img/fav/), damit beim Seitenaufruf kein Browser
mehr einen fremden Dienst anfragt (keine IP-Übermittlung, kein Drittland, kein Gewicht von Riesen-Icons).

Kein Teil des Builds und ohne Abhängigkeiten (nur Python-Standardbibliothek). Aufruf aus dem Repo-Root:
    python3 scripts/fetch_favicons.py           # nur Hosts ohne Datei holen, verwaiste Dateien löschen
    python3 scripts/fetch_favicons.py --retry   # Hosts mit Platzhalter noch einmal versuchen
    python3 scripts/fetch_favicons.py --force   # alles neu holen

Quelle: der Favicon-Dienst von Google (liefert PNG oder JPEG in 64 px, passend für 28 bis 30 px bei doppelter Pixeldichte);
falls der nichts hat, eine PNG-Fassung aus dem ICO von DuckDuckGo. Abgefragt wird nur der Hostname, beim Build,
nie aus dem Browser der Besucher. Aus jedem Bild fliegen alle Metadaten (Text, Exif, XMP, Farbprofile) raus.
Findet keine Quelle etwas, entsteht <host>.svg mit dem Anfangsbuchstaben als Platzhalter.
Die Dateien sind Quellen und werden committet; scripts/build_de_page.py verweist nur auf sie.
"""
import hashlib
import re
import struct
import sys
import urllib.error
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
FAV = ROOT / "docs" / "img" / "fav"
README = ROOT / "README.de.md"
SIZE = 64
# Gleiches Muster wie ITEM_RE in build_de_page.py: "- [Name](url) – Beschreibung"
ITEM_RE = re.compile(r"^- \[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)\s*[-–—]\s*(.*)$")
HOST_OK = re.compile(r"^[a-z0-9.-]+$")
REAL = ("png", "jpg")
KEEP = {b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND"}  # alles andere ist Metadaten (layer_a.py prüft das)
UA = "Mozilla/5.0 (KI-Werkstatt favicon cache; https://github.com/jmp-collab/awesome-ai-tools)"
# Platzhalter-Farben: dunkle Fläche, helle Schrift, in hellem und dunklem Design lesbar
COLORS = ["#2E3A4B", "#3B4A2A", "#4B2E3A", "#2A4A48", "#4A3B2A", "#3A2E4B"]


def host(url):
    return (urlparse(url).hostname or "").lower()


def hosts_from_readme():
    out = set()
    for line in README.read_text(encoding="utf-8").splitlines():
        m = ITEM_RE.match(line)
        if m and re.match(r"https?://", m.group(2), re.I):
            h = host(m.group(2))
            if h and HOST_OK.match(h):
                out.add(h)
    return sorted(out)


def local_file(h):
    """Pfad relativ zu docs/ oder None; echtes Icon schlägt Platzhalter."""
    for ext in ("png", "jpg", "svg"):
        if (FAV / f"{h}.{ext}").exists():
            return f"img/fav/{h}.{ext}"
    return None


def strip_png(data):
    """PNG ohne Zusatz-Chunks; None, wenn es kein gültiges PNG ist. Liefert (bytes, breite, höhe)."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    out, i, w, h = [data[:8]], 8, 0, 0
    while i + 8 <= len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        chunk = data[i:i + 12 + n]
        if len(chunk) < 12 + n:
            return None
        if typ == b"IHDR":
            w, h = struct.unpack(">II", data[i + 8:i + 16])
        if typ in KEEP:
            out.append(chunk)
        i += 12 + n
        if typ == b"IEND":
            break
    if not w or out[-1][4:8] != b"IEND":
        return None
    return b"".join(out), w, h


def strip_jpeg(data):
    """JPEG ohne APP1 bis APP15 und Kommentare (Exif, XMP, Farbprofil); None, wenn es kein JPEG ist.
    Liefert (bytes, breite, höhe)."""
    if data[:2] != b"\xff\xd8":
        return None
    out, i, w, h = [data[:2]], 2, 0, 0
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            return None
        m = data[i + 1]
        n = struct.unpack(">H", data[i + 2:i + 4])[0]
        seg = data[i:i + 2 + n]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
        if m == 0xDA:  # Start of Scan: ab hier Bilddaten bis zum Ende
            out.append(data[i:])
            break
        if not (0xE1 <= m <= 0xEF or m == 0xFE):
            out.append(seg)
        i += 2 + n
    if not w:
        return None
    return b"".join(out), w, h


def png_from_ico(data):
    """Aus einem ICO den eingebetteten PNG-Eintrag nehmen, der 64 px am nächsten kommt (BMP-Einträge zählen nicht)."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return data
    if len(data) < 6 or data[:4] != b"\x00\x00\x01\x00":
        return None
    best = None
    for k in range(struct.unpack("<H", data[4:6])[0]):
        e = data[6 + 16 * k: 22 + 16 * k]
        if len(e) < 16:
            break
        size, off = struct.unpack("<II", e[8:16])
        blob = data[off:off + size]
        if blob[:8] != b"\x89PNG\r\n\x1a\n":
            continue
        w = struct.unpack(">I", blob[16:20])[0]
        score = abs(w - SIZE) + (1000 if w < 32 else 0)
        if best is None or score < best[0]:
            best = (score, blob)
    return best[1] if best else None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(3_000_000)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:  # noqa: BLE001  (Zeitüberschreitung, DNS, TLS: dann eben Platzhalter)
        return 0, b""


def fetch(h):
    """(Endung, Bytes ohne Metadaten) oder None."""
    st, data = get(f"https://www.google.com/s2/favicons?domain={quote(h)}&sz={SIZE}")
    if st == 200:  # 404 heißt: Google hat nichts und schickt nur seine Standard-Weltkugel
        for ext, strip in (("png", strip_png), ("jpg", strip_jpeg)):
            res = strip(data)
            if res and res[1] >= 16:
                return ext, res[0]
    st, data = get(f"https://icons.duckduckgo.com/ip3/{quote(h)}.ico")
    if st == 200:
        png = png_from_ico(data)
        res = strip_png(png) if png else None
        # Nur handliche Größen; Riesen-PNGs (1600 px) ohne Bildbibliothek nicht verkleinerbar, dann Platzhalter
        if res and 16 <= res[1] <= 128 and len(res[0]) <= 40_000:
            return "png", res[0]
    return None


def placeholder_svg(h):
    name = re.sub(r"^(www|app|en|de)\.", "", h)
    letter = next((c for c in name if c.isalnum()), "?").upper()
    color = COLORS[int(hashlib.sha1(h.encode()).hexdigest(), 16) % len(COLORS)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{color}"/>'
            f'<text x="32" y="43" text-anchor="middle" font-family="Space Grotesk, system-ui, sans-serif" font-size="32" '
            f'font-weight="700" fill="#ECEAE3">{letter}</text></svg>\n')


def write_placeholder(h):
    (FAV / f"{h}.svg").write_text(placeholder_svg(h), encoding="utf-8")
    return f"img/fav/{h}.svg"


def main():
    force, retry = "--force" in sys.argv, "--retry" in sys.argv
    FAV.mkdir(parents=True, exist_ok=True)
    hosts = hosts_from_readme()
    todo = [h for h in hosts if force or not any((FAV / f"{h}.{e}").exists() for e in REAL) and (retry or not (FAV / f"{h}.svg").exists())]
    print(f"{len(hosts)} Hosts, {len(todo)} zu holen")
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(fetch, todo))
    got = miss = 0
    for h, res in zip(todo, results):
        for e in REAL + ("svg",):
            (FAV / f"{h}.{e}").unlink(missing_ok=True)
        if res:
            (FAV / f"{h}.{res[0]}").write_bytes(res[1])
            got += 1
        else:
            write_placeholder(h)
            miss += 1
    # Verwaiste Dateien (Tool aus der Liste geflogen) löschen
    keep = set(hosts)
    files = [f for f in FAV.iterdir() if f.suffix in (".png", ".jpg", ".svg")]
    stale = [f for f in files if f.stem not in keep]
    for f in stale:
        f.unlink()
    files = [f for f in files if f not in stale]
    n_real = sum(f.suffix != ".svg" for f in files)
    total = sum(f.stat().st_size for f in files)
    print(f"geholt: {got}, Platzhalter neu: {miss}, gelöscht: {len(stale)}")
    print(f"Bestand: {n_real} Icons (PNG/JPEG), {len(files) - n_real} Platzhalter-SVG, zusammen {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
