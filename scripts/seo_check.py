#!/usr/bin/env python3
"""SEO-Prüfung der gebauten Seite (docs/*.html), nur Standardbibliothek.

Aufruf aus dem Repo-Root, nach dem Build:
    python3 scripts/seo_check.py              # prüft docs/
    python3 scripts/seo_check.py --docs DIR   # anderer Ausgabeordner (z. B. für Tests)

Fehler (Exit-Code 1):
  - Title oder Meta-Description fehlt oder steht auf zwei Seiten gleich
  - nicht genau eine <h1>
  - Canonical fehlt oder zeigt nicht auf die eigene URL
  - interne Links (a href, dazu src/href von Bildern, Skripten, Stylesheets) auf Dateien, die es nicht gibt,
    oder auf Anker, die es auf der Zielseite nicht gibt
  - Sitemap nennt eine fehlende oder noindex-Seite, oder eine indexierbare Seite fehlt in der Sitemap
  - indexierbare Seite ohne eingehenden internen Link von einer anderen Seite (Waise)
  - JSON-LD lässt sich nicht parsen
Warnungen (Exit-Code bleibt 0): Title über 60 / Description über 160 Zeichen, noindex-Seiten ohne eingehende Links
(404, Danke-Seite: erreichbar über Fehler bzw. Formular), JSON-LD ohne @context.

Inhalt von <template> zählt nicht als Seite (keine IDs, keine <h1>), seine Links werden aber mitgeprüft,
weil app.js das Template in die Seite klont.
"""
import json
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
# Eine Quelle für die Adresse: SITE_URL steht im Generator, hier wird sie nur ausgelesen
_m = re.search(r'^SITE_URL = "([^"]+)"', (ROOT / "scripts" / "build_de_page.py").read_text(encoding="utf-8"), re.M)
if not _m:
    sys.exit("seo_check: SITE_URL in scripts/build_de_page.py nicht gefunden")
SITE_URL = _m.group(1)
SITE_PATH = urlparse(SITE_URL).path  # /awesome-ai-tools/
IGNORE = {"og.html"}
TITLE_MAX, DESC_MAX = 60, 160


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.desc, self.canonical, self.noindex = None, None, None, False
        self.h1 = 0
        self.ids = set()
        self.links = []      # (Attribut, Wert, in_template)
        self.ld = []
        self._tpl = 0
        self._in_title = self._in_ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "template":
            self._tpl += 1
        tpl = self._tpl > 0
        if not tpl and "id" in a:
            self.ids.add(a["id"])
        if not tpl and tag == "a" and "name" in a:
            self.ids.add(a["name"])
        if tag == "h1" and not tpl:
            self.h1 += 1
        if tag == "title" and self.title is None:
            self._in_title, self._buf = True, []
        if tag == "meta":
            if a.get("name") == "description":
                self.desc = a.get("content", "")
            if a.get("name") == "robots" and "noindex" in a.get("content", ""):
                self.noindex = True
        if tag == "link" and "canonical" in a.get("rel", "").split():
            self.canonical = a.get("href", "")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, []
        if tag == "a" and "href" in a:
            self.links.append(("a", a["href"], tpl))
        elif tag in ("img", "script", "source") and "src" in a:
            self.links.append(("src", a["src"], tpl))
        elif tag == "link" and "href" in a and set((a.get("rel") or "").lower().split()) & {"stylesheet", "icon", "preload", "alternate", "manifest", "apple-touch-icon"}:
            self.links.append(("src", a["href"], tpl))

    def handle_endtag(self, tag):
        if tag == "template" and self._tpl:
            self._tpl -= 1
        if tag == "title" and self._in_title:
            self.title, self._in_title = "".join(self._buf).strip(), False
        if tag == "script" and self._in_ld:
            self.ld.append("".join(self._buf))
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title or self._in_ld:
            self._buf.append(data)


def own_url(name):
    return SITE_URL if name == "index.html" else SITE_URL + name


def resolve(page, href):
    """Internes Ziel als (Datei relativ zu docs/, Anker) oder None für externe Links und mailto/tel."""
    href = href.strip()
    if not href or href.startswith(("mailto:", "tel:", "data:")):
        return None
    if href.lower().startswith("javascript:"):
        return ("javascript:", "")
    absu = urljoin(own_url(page), href)
    u = urlparse(absu)
    if not (absu.startswith(SITE_URL) or absu == SITE_URL[:-1]) and not (u.scheme in ("", "http", "https") and not u.netloc):
        return None  # fremde Seite
    path = unquote(u.path)
    if not path.startswith(SITE_PATH):
        return (path, unquote(u.fragment))  # außerhalb des Projektpfads: gibt es auf GitHub Pages nicht
    rel = path[len(SITE_PATH):] or "index.html"
    if rel.endswith("/"):
        rel += "index.html"
    return (rel, unquote(u.fragment))


def sitemap_pages():
    xml = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    out = []
    for loc in re.findall(r"<loc>(.*?)</loc>", xml):
        out.append("index.html" if loc == SITE_URL else loc[len(SITE_URL):] if loc.startswith(SITE_URL) else loc)
    return out


def main():
    global DOCS
    if "--docs" in sys.argv:
        DOCS = Path(sys.argv[sys.argv.index("--docs") + 1]).resolve()
    errors, warns = [], []
    pages = {}
    for f in sorted(DOCS.glob("*.html")):
        if f.name in IGNORE:
            continue
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        pages[f.name] = p

    titles, descs = defaultdict(list), defaultdict(list)
    incoming = defaultdict(set)
    for name, p in pages.items():
        if not p.title:
            errors.append(f"{name}: kein <title>")
        else:
            titles[p.title].append(name)
            if len(p.title) > TITLE_MAX and not p.noindex:
                warns.append(f"{name}: Title {len(p.title)} Zeichen (> {TITLE_MAX})")
        if not p.desc:
            errors.append(f"{name}: keine Meta-Description")
        else:
            descs[p.desc].append(name)
            if len(p.desc) > DESC_MAX and not p.noindex:
                warns.append(f"{name}: Description {len(p.desc)} Zeichen (> {DESC_MAX})")
        if p.h1 != 1:
            errors.append(f"{name}: {p.h1} <h1> statt genau einer")
        if not p.canonical:
            errors.append(f"{name}: kein Canonical")
        elif p.canonical != own_url(name):
            errors.append(f"{name}: Canonical {p.canonical} statt {own_url(name)}")
        for i, raw in enumerate(p.ld):
            try:
                ld = json.loads(raw)
            except ValueError as e:
                errors.append(f"{name}: JSON-LD Nr. {i + 1} nicht lesbar ({e})")
                continue
            if isinstance(ld, dict) and "@context" not in ld:
                warns.append(f"{name}: JSON-LD Nr. {i + 1} ohne @context")
        seen = set()
        for kind, href, tpl in p.links:
            r = resolve(name, href)
            if r is None:
                continue
            target, anchor = r
            key = (target, anchor)
            if key in seen:
                continue
            seen.add(key)
            where = f"{name}: {'Template-' if tpl else ''}Link {href!r}"
            if target == "javascript:":
                errors.append(f"{where}: javascript:-Link")
                continue
            if not (DOCS / target).is_file():
                errors.append(f"{where}: Datei {target} gibt es nicht")
                continue
            if kind == "a" and target.endswith(".html") and target != name:
                incoming[target].add(name)
            if kind == "a" and anchor and target.endswith(".html"):
                tp = pages.get(target)
                if tp is not None and anchor not in tp.ids:
                    errors.append(f"{where}: Anker #{anchor} fehlt auf {target}")

    for t, where in titles.items():
        if len(where) > 1:
            errors.append(f"Title doppelt ({', '.join(where)}): {t}")
    for d, where in descs.items():
        if len(where) > 1:
            errors.append(f"Description doppelt ({', '.join(where)}): {d[:80]}")

    smap = sitemap_pages()
    for pg in smap:
        if pg not in pages:
            errors.append(f"sitemap.xml: {pg} gibt es nicht in docs/")
        elif pages[pg].noindex:
            errors.append(f"sitemap.xml: {pg} ist noindex")
    for name, p in pages.items():
        if not p.noindex and name not in smap:
            errors.append(f"{name}: indexierbar, fehlt aber in sitemap.xml")
        if name != "index.html" and not incoming.get(name):
            (warns if p.noindex else errors).append(f"{name}: keine eingehenden internen Links (Waise)")

    for w in warns:
        print("WARNUNG " + w)
    for e in errors:
        print("FEHLER  " + e)
    print(f"SEO-Check: {len(pages)} Seiten, {len(smap)} in der Sitemap, {len(errors)} Fehler, {len(warns)} Warnungen")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
