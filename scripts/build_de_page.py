#!/usr/bin/env python3
"""Baut die KI-Werkstatt-Seite (docs/) aus README.de.md.

Keine Abhängigkeiten, nur Python 3.8+. Aufruf aus dem Repo-Root:
    python3 scripts/build_de_page.py

Quellen:  README.de.md (Tool-Liste), brand/ki-werkstatt.json (Marke),
          data/stacks.json (Werkzeugkisten + Stack-Finder), data/rechner.json (Zeitspar-Rechner),
          data/glossar.json (KI-Glossar), data/kategorien.json (eigene Texte je Kategorie-Seite),
          scripts/template/icons.svg
Ausgabe:  docs/index.html, docs/ki-tools-*.html (eine Seite je Kategorie), docs/ki-glossar.html,
          docs/404.html, docs/danke.html, docs/impressum.html, docs/datenschutz.html, docs/img/*.svg,
          docs/ratgeber.html, docs/ki-einsatz.html (Übersichten), docs/seiten.json (Seitenindex fürs Such-Panel),
          docs/tools.json, docs/tools.csv, docs/sitemap.xml, docs/robots.txt
README.de.md bleibt die einzige Quelle für die Liste; docs/ nie von Hand bearbeiten.
Am Ende prüft scripts/check_unique.py, dass kein Satz auf zwei Seiten steht.
"""
import base64
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.de.md"
DOCS = ROOT / "docs"
IMG = DOCS / "img"
BRAND = json.loads((ROOT / "brand" / "ki-werkstatt.json").read_text(encoding="utf-8"))
STACKS = json.loads((ROOT / "data" / "stacks.json").read_text(encoding="utf-8"))
RECHNER = json.loads((ROOT / "data" / "rechner.json").read_text(encoding="utf-8"))
GLOSSAR = json.loads((ROOT / "data" / "glossar.json").read_text(encoding="utf-8"))
KAT = json.loads((ROOT / "data" / "kategorien.json").read_text(encoding="utf-8"))
TRENDS = json.loads((ROOT / "data" / "trends.json").read_text(encoding="utf-8"))
NEU = json.loads((ROOT / "data" / "neu.json").read_text(encoding="utf-8"))
EINSATZ = json.loads((ROOT / "data" / "einsatz.json").read_text(encoding="utf-8"))
RATGEBER = json.loads((ROOT / "data" / "ratgeber.json").read_text(encoding="utf-8"))
RG_DIR = ROOT / "content" / "ratgeber"
ZAHLWORT = {2: "Zwei", 3: "Drei", 4: "Vier", 5: "Fünf", 6: "Sechs", 7: "Sieben", 8: "Acht", 9: "Neun", 10: "Zehn", 11: "Elf", 12: "Zwölf"}
ICONS = (ROOT / "scripts" / "template" / "icons.svg").read_text(encoding="utf-8")

SITE_URL = "https://jmp-collab.github.io/awesome-ai-tools/"
REPO_URL = "https://github.com/jmp-collab/awesome-ai-tools"
TITLE = "KI-Werkstatt: KI-Tools auf Deutsch, sortiert und erklärt"
DESCRIPTION = (  # höchstens 155 Zeichen, das Wichtigste zuerst
    "Über 400 KI-Tools auf Deutsch, jedes in einem Satz erklärt: Chatbots, Texte, Bilder, Video, "
    "Automatisierung, SEO. EU-Anbieter markiert, mit Stack-Finder."
)
SUBSTACK = "https://promptgott.substack.com/"
UTM = "utm_source=github-pages&utm_medium=referral&utm_campaign=awesome-ki-tools-de"


def utm(placement):
    """UTM-Parameter mit Platzierung (utm_content), damit Substack Footer, Band, Danke-Seite usw. unterscheiden kann."""
    return f"{UTM}&utm_content={placement}"


def pg_sub(placement):
    return f"{SUBSTACK}subscribe?{utm(placement)}"
LEAD_TO = BRAND["lead_offer"]["recipient"]
# Sichtbare Adresse zeichenweise als HTML-Entities: Browser zeigen sie normal, einfache Scraper finden sie nicht.
# Der FormSubmit-Endpunkt im form action trägt sie noch im Klartext, bis Jean den Alias aus FormSubmit liefert.
LEAD_TO_ENT = "".join(f"&#{ord(c)};" for c in LEAD_TO)


def mail_link(subject=""):
    q = f"?subject={html.escape(subject)}" if subject else ""
    return f'<a href="mailto:{LEAD_TO_ENT}{q}">{LEAD_TO_ENT}</a>'
TODAY = date.today().strftime("%d.%m.%Y")  # Build-Datum (Sitemap, Export)
_LC = json.loads((ROOT / "data" / "linkcheck.json").read_text(encoding="utf-8"))
LINK_CHECK = date.fromisoformat(_LC["date"]).strftime("%d.%m.%Y")  # setzt nur scripts/check_links.py
LINK_CHECK_N = _LC["checked"]
if _LC.get("dead"):
    raise SystemExit(f"Abbruch: data/linkcheck.json meldet {len(_LC['dead'])} tote Links. Erst README.de.md bereinigen und scripts/check_links.py erneut laufen lassen.")
sys.path.insert(0, str(ROOT / "scripts"))
from check_links import all_urls, url_hash  # noqa: E402  (gleiche Linkliste wie der Checker)
from fetch_favicons import local_file as local_fav, write_placeholder as write_fav_placeholder  # noqa: E402
if _LC.get("urls_sha256") != url_hash(all_urls(SRC.read_text(encoding="utf-8"))):
    raise SystemExit("Abbruch: Die Links in README.de.md, data/rechner.json oder data/trends.json haben sich seit dem letzten Link-Check geändert. Erst scripts/check_links.py laufen lassen.")
N_STACKS = len(STACKS["stacks"])
STACK_SIZES = sorted({len(s["tools"]) for s in STACKS["stacks"]})
STACK_SIZE_TXT = str(STACK_SIZES[0]) if len(STACK_SIZES) == 1 else f"{STACK_SIZES[0]} bis {STACK_SIZES[-1]}"

# Icon je Kategorie (Slug der H2-Überschrift)
CAT_ICON = {
    "empfehlungen-der-redaktion": "star", "promptgott-deep-dives": "flame", "text-und-sprache": "text",
    "automatisierung-und-ki-agenten": "bot", "entwickler-tools-und-llmops": "cpu", "programmieren-mit-ki": "code",
    "bilder": "image", "video": "video", "audio": "music", "marketing-und-seo": "megaphone",
    "ki-telefonagenten": "phone", "weitere-ki-tools": "box", "lernen-prompting-und-ki-grundlagen": "book",
    "verwandte-listen": "link", "mitmachen": "plus",
}
SUB_ICON = {  # H3-Icons, wo sie etwas aussagen
    "sprachmodelle-und-apis": "cpu", "chatbots-und-assistenten": "chat", "ki-suchmaschinen": "search",
    "lokal-und-privat-mit-dokumenten-chatten": "lock", "schreibassistenten": "pen",
    "übersetzung-und-lokalisierung": "globe", "browser-erweiterungen-und-add-ons": "puzzle",
    "produktivität": "zap", "meeting-assistenten": "calendar", "wissenschaft-und-recherche": "flask",
    "kundenservice": "headset",
}
# H1 der Kategorie-Seiten (sonst "KI-Tools: <Titel>")
CAT_H1 = {
    "text-und-sprache": "KI-Tools für Text und Sprache", "automatisierung-und-ki-agenten": "KI-Tools für Automatisierung und Agenten",
    "entwickler-tools-und-llmops": "KI-Entwickler-Tools und LLMOps", "programmieren-mit-ki": "Programmieren mit KI",
    "bilder": "KI-Tools für Bilder", "video": "KI-Tools für Video", "audio": "KI-Tools für Audio",
    "marketing-und-seo": "KI-Tools für Marketing und SEO", "ki-telefonagenten": "KI-Telefonagenten", "weitere-ki-tools": "Weitere KI-Tools",
}
# Suchbegriffe als H2 der Fächer auf den Kategorie-Seiten (sonst der Fach-Titel aus README.de.md)
SUB_H2 = {
    "sprachmodelle-und-apis": "Sprachmodelle und KI-APIs", "chatbots-und-assistenten": "KI-Chatbots und ChatGPT-Alternativen",
    "ki-suchmaschinen": "KI-Suchmaschinen", "lokal-und-privat-mit-dokumenten-chatten": "Lokale KI: privat mit Dokumenten chatten",
    "schreibassistenten": "KI-Textgeneratoren und Schreibassistenten", "übersetzung-und-lokalisierung": "KI-Übersetzer und Lokalisierung",
    "browser-erweiterungen-und-add-ons": "KI-Browser-Erweiterungen", "produktivität": "KI-Tools für Produktivität",
    "meeting-assistenten": "KI-Meeting-Assistenten", "wissenschaft-und-recherche": "KI für Wissenschaft und Recherche",
    "kundenservice": "KI-Chatbots für den Kundenservice", "bildmodelle": "KI-Bildgeneratoren und Bildmodelle",
    "bild-dienste": "KI-Bildbearbeitung und Freisteller", "grafikdesign": "KI für Grafikdesign und Präsentationen",
    "bildarchive-und-prompt-sammlungen": "Bildarchive und Prompt-Sammlungen", "modell-bibliotheken-und-stable-diffusion-ressourcen": "Stable-Diffusion-Modelle und Ressourcen",
    "stimmen-und-voice-cloning": "KI-Stimmen und Voice Cloning", "sprache-zu-text-und-text-zu-sprache": "Transkription und Text-to-Speech",
    "musik": "KI-Musikgeneratoren", "seo-und-content-optimierung": "KI-Tools für SEO und Content",
    "werbung-social-und-personalisierung": "KI für Werbung, Social Media und Personalisierung",
}
GLOSSAR_PAGE = "ki-glossar.html"
TRENDS_PAGE = "ki-trends.html"
RATGEBER_PAGE = "ratgeber.html"   # Übersicht aller Ratgeber
EINSATZ_PAGE = "ki-einsatz.html"  # Übersicht aller Einsatzgebiete
LERNEN_IDS = ("lernen-prompting-und-ki-grundlagen", "verwandte-listen")  # stehen als Band "Weiterlernen" im Glossar
# Rollen, für die style.css einen Filter auf ratgeber.html kennt (.rg-hub:has(#rolle-<id>:checked))
HUB_ROLLEN_CSS = {"shop", "marketing", "entwicklung", "service", "kreativ", "buero"}
NAV = {"secs": [], "home": {}, "sec": {}}  # Kategorie-Seiten, Tool -> Anker in seiner Schublade, Tool -> Schublade
# NEU-Badge: gilt ab "seit" für genau NEU["tage"] Tage (seit <= heute < seit + tage); vorher und danach kein Badge
NEU_AKTIV = [t for t in NEU["tools"] if date.fromisoformat(t["seit"]) <= date.today() < date.fromisoformat(t["seit"]) + timedelta(days=NEU["tage"])]
NEU_NAMES = {t["name"] for t in NEU_AKTIV}
NEU_BADGE = '<span class="badge neu" title="Neu in der Liste">NEU</span>'


def cat_page(sec_id):
    return f"ki-tools-{sec_id}.html"


def cat_h1(sec):
    return CAT_H1.get(sec["id"], "KI-Tools: " + sec["title"])


def tool_id(name):
    return "tool-" + slug(name)


# Link-Ziel mit bis zu einer Ebene balancierter Klammern, z. B. Wikipedia-Titel
DEST = r"((?:[^()\s]|\([^()\s]*\))+)"
ITEM_RE = re.compile(r"^- \[([^\]]+)\]\(" + DEST + r"\)\s*[-–—]\s*(.*)$")


def slug(text):
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def retag(href, placement=None):
    if href.startswith(SUBSTACK):
        href = re.sub(r"utm_source=[^&]+&utm_medium=[^&]+&utm_campaign=[^&#]+", UTM, href)
        if placement and "utm_content=" not in href and UTM in href:
            href = href.replace(UTM, utm(placement), 1)
    return href


SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def check_url(url, where, external=True):
    """Gespeichertes XSS verhindern: Tool- und Quellen-Links (auch aus PR-Beiträgen) müssen http(s) sein.
    external=False erlaubt zusätzlich relative Pfade, Anker und mailto: (Fließtext der Ratgeber)."""
    if re.match(r"https?://", url, re.I):
        return url
    if not external and (url.startswith("mailto:") or not SCHEME.match(url)):
        return url
    raise SystemExit(f"Abbruch: unsicherer Link {url[:80]!r} in {where}. Erlaubt sind nur http(s)-Adressen.")


def plain(text):
    text = re.sub(r"\[([^\]]+)\]\(" + DEST + r"\)", r"\1", text)
    return re.sub(r"\s+", " ", text.replace("`", "").replace("*", "")).strip()


def inline(text, site=False):
    out = html.escape(text, quote=False)
    # Code-Spans erst am Ende einsetzen, damit `[Name](https://url)` wörtlich bleibt
    codes = []
    out = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", out)

    def link(m):
        label, href = m.group(1), html.unescape(m.group(2))
        check_url(href, f"Link „{plain(label)}“", external=False)
        if href.startswith("#"):
            pass
        elif not href.startswith("http") and not site:
            href = REPO_URL + "/blob/main/" + href
        href = retag(href)
        attrs = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return f'<a href="{html.escape(href)}"{attrs}>{label}</a>'

    out = re.sub(r"\[([^\]]+)\]\(" + DEST + r"\)", link, out)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", out)


def icon(name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


NUM_CELL = re.compile(r"(?:ca\.|rund|~)?\s*\d[\d.,]*\s*(?:%|Dollar|Euro|€|\$)?(?:\s.*)?")


def md_table(head, body, site=False):
    """Markdown-Tabelle als HTML. Spalten, die überwiegend mit einer Zahl beginnen, bekommen class="num"
    (rechtsbündig, Ziffern gleich breit); "k. A." und Striche zählen nicht mit."""
    num = set()
    for j in range(len(head)):
        vals = [r[j] for r in body if j < len(r) and r[j] not in ("", "k. A.", "–", "-")]
        if vals and sum(bool(NUM_CELL.fullmatch(v)) and len(v) <= 14 for v in vals) >= 0.7 * len(vals):
            num.add(j)
    cls = lambda j: ' class="num"' if j in num else ""
    # Scrollbarer Bereich: per Tastatur erreichbar und benannt (axe: scrollable-region-focusable)
    label = "Tabelle: " + ", ".join(plain(c) for c in head[:3]) + (" …" if len(head) > 3 else "")
    t = [f'<div class="table" tabindex="0" role="region" aria-label="{html.escape(label)}"><table><thead><tr>'] + [f"<th{cls(j)}>{inline(c, site)}</th>" for j, c in enumerate(head)]
    t.append("</tr></thead><tbody>")
    t += ["<tr>" + "".join(f"<td{cls(j)}>{inline(c, site)}</td>" for j, c in enumerate(r)) + "</tr>" for r in body]
    return "".join(t) + "</tbody></table></div>"


def host(url):
    return urlparse(url).hostname or ""


FAV_MISSING = set()


def fav_src(url):
    """Lokales Favicon (docs/img/fav/, geholt von scripts/fetch_favicons.py). Fehlt es, schreibt der Build den
    Buchstaben-Platzhalter selbst und warnt; kein Besucher-Browser fragt je einen fremden Icon-Dienst an."""
    h = host(url).lower()
    src = local_fav(h)
    if not src:
        FAV_MISSING.add(h)
        src = write_fav_placeholder(h)
    return src


def favicon(url):
    # Kein onerror-Attribut (CSP ohne Inline-Handler): der Listener im Head blendet ein kaputtes Bild aus
    return f'<img loading="lazy" alt="" width="30" height="30" src="{html.escape(fav_src(url))}">'


# --------------------------------------------------------------------------- Parser
def parse(md):
    """README -> Liste von Sektionen: {title, id, blocks:[...], subs:[{title,id,blocks}]}"""
    lines = md.splitlines()
    sections, cur, sub = [], None, None
    head_md = []
    i = 0

    def target():
        return sub if sub else cur

    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            cur = {"title": title, "id": slug(title), "blocks": [], "subs": []}
            sub = None
            if title != "Inhalt":
                sections.append(cur)
            i += 1
            continue
        if cur is None:
            head_md.append(line)
            i += 1
            continue
        if cur["title"] == "Inhalt":
            i += 1
            continue
        if line.startswith("### "):
            title = line[4:].strip()
            sub = {"title": title, "id": slug(title), "blocks": []}
            cur["subs"].append(sub)
            i += 1
            continue
        blocks = target()["blocks"]
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
            continue
        if line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ").rstrip())
                i += 1
            blocks.append(("quote", " ".join(q for q in quote if q)))
            continue
        if ITEM_RE.match(line):
            items = []
            while i < len(lines) and ITEM_RE.match(lines[i]):
                name, url, desc = ITEM_RE.match(lines[i]).groups()
                check_url(url, f"README.de.md, Tool „{name}“")
                items.append({"name": name, "url": retag(url), "desc": desc})
                i += 1
            blocks.append(("items", items))
            continue
        if re.match(r"^\d+\. ", line) or line.startswith("- "):
            buf, ordered = [], line[0].isdigit()
            while i < len(lines) and (re.match(r"^\d+\. ", lines[i]) or lines[i].startswith("- ")) and not ITEM_RE.match(lines[i]):
                buf.append(re.sub(r"^(\d+\.|-) ", "", lines[i]))
                i += 1
            blocks.append(("list", (ordered, buf)))
            continue
        if line.strip() and line.strip() != "---":
            para = [line.strip()]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||>|- |\d+\. |---)", lines[i + 1]):
                i += 1
                para.append(lines[i].strip())
            blocks.append(("p", " ".join(para)))
        i += 1
    return sections, head_md


def all_items(sections):
    for s in sections:
        for kind, val in s["blocks"]:
            if kind == "items":
                for it in val:
                    yield s, None, it
        for sub in s["subs"]:
            for kind, val in sub["blocks"]:
                if kind == "items":
                    for it in val:
                        yield s, sub, it


def item_meta(it):
    desc = it["desc"]
    eu = "🇪🇺" in desc
    oss = "OSS`" in desc or "`OSS" in desc
    clean = plain(re.sub(r"🇪🇺|\[`OSS`\]\([^)]*\)|`OSS`", " ", desc))
    return eu, oss, clean


# --------------------------------------------------------------------------- Grafiken
def icon_body(name):
    m = re.search(r'<symbol id="i-' + name + r'"[^>]*>(.*?)</symbol>', ICONS, re.S)
    return m.group(1) if m else ""


def cat_art(idx, name, icon_name, dark_first):
    """Abstrakte Kategorie-Grafik: Verlauf, Raster, große Werkzeug-Silhouette, Schubladen-Nummer."""
    a, b = ("#0E1116", "#1C2430") if dark_first else ("#D7FF3C", "#9ED400")
    ink = "#D7FF3C" if dark_first else "#0E1116"
    g = icon_body(icon_name)
    # Versalien in Space Grotesk sind etwa 0,7 em breit; links bleiben rund 480 px bis zum Kreis
    fs = min(44, int(480 / (0.64 * max(1, len(name)))))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" role="img" aria-label="{html.escape(name)}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
<pattern id="p" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{ink}" stroke-opacity=".14"/></pattern></defs>
<rect width="800" height="300" fill="url(#g)"/><rect width="800" height="300" fill="url(#p)"/>
<circle cx="640" cy="150" r="120" fill="none" stroke="{ink}" stroke-opacity=".25" stroke-width="2"/>
<circle cx="640" cy="150" r="80" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="6 8"/>
<g transform="translate(560 70) scale(6.7)" fill="none" stroke="{ink}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">{g}</g>
<g transform="translate(40 40) scale(2.2)" fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">{g}</g>
<text x="40" y="250" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="18" font-weight="500" fill="{ink}" fill-opacity=".85" letter-spacing="3">SCHUBLADE {idx:02d}</text>
<text x="40" y="200" font-family="Space Grotesk, system-ui, sans-serif" font-size="{fs}" font-weight="700" fill="{ink}">{html.escape(name.upper())}</text>
<path d="M40 268h220" stroke="{ink}" stroke-width="3"/>
</svg>"""


def hero_floats():
    shapes = [("wrench", "f1", 0.35), ("spark", "f2", 0.6), ("cpu", "f3", 0.25), ("ruler", "f4", 0.5), ("code", "f5", 0.15)]
    out = []
    for name, cls, depth in shapes:
        out.append(f'<div class="float {cls}" data-depth="{depth}"><svg viewBox="0 0 24 24">{icon_body(name)}</svg></div>')
    return "".join(out)


# --------------------------------------------------------------------------- Renderer
def render_blocks(blocks, sec_id, sub_id, tools_map, ids=None):
    """ids: Menge schon vergebener Tool-Anker auf der Seite; None = keine Anker (Startseite)."""
    out = []
    for kind, val in blocks:
        if kind == "items":
            out.append(f'<ul class="tools" style="--n:{len(val)}">')
            for it in val:
                eu, oss, clean = item_meta(it)
                badges = (f'<span class="badge eu" title="Anbieter mit Sitz in der EU">EU</span>' if eu else "") + (
                    '<span class="badge oss" title="Open Source">OSS</span>' if oss else "") + (NEU_BADGE if it["name"] in NEU_NAMES else "")
                search = plain(" ".join([it["name"], clean, sec_id.replace("-", " "), (sub_id or "").replace("-", " ")])).lower()
                desc_html = inline(re.sub(r"\s*🇪🇺\s*", " ", re.sub(r"\[`OSS`\]\([^)]*\)|`OSS`", "", it["desc"])).strip())
                aid = ""
                if ids is not None and tool_id(it["name"]) not in ids:
                    ids.add(tool_id(it["name"]))
                    aid = f' id="{html.escape(tool_id(it["name"]))}"'
                out.append(
                    f'<li{aid} data-eu="{int(eu)}" data-oss="{int(oss)}" data-search="{html.escape(search)}">{favicon(it["url"])}'
                    f'<div><a class="name" href="{html.escape(it["url"])}" target="_blank" rel="noopener">{html.escape(it["name"])}</a>'
                    f'<span class="badges">{badges}</span><span class="desc">{desc_html}</span></div></li>')
                tools_map.setdefault(it["name"], {"u": it["url"], "d": clean, "eu": eu})
            out.append("</ul>")
        elif kind == "quote":
            cls = "tip" if "💡" in val else "lead"
            out.append(f'<aside class="{cls}">{inline(val)}</aside>')
        elif kind == "table":
            head, *rest = val
            out.append(md_table(head, rest))
        elif kind == "list":
            ordered, buf = val
            tag = "ol" if ordered else "ul"
            out.append(f'<{tag} class="plain">' + "".join(f"<li>{inline(x)}</li>" for x in buf) + f"</{tag}>")
        elif kind == "p":
            out.append(f"<p>{inline(val)}</p>")
    return "\n".join(out)


def render_section(sec, idx, tools_map, page_link=False, cat_page_mode=False, level=2):
    """cat_page_mode: Kategorie-Seite. Die Fächer werden dort H2 mit Suchbegriff (SUB_H2) und bekommen Tool-Anker;
    der Kategorie-Name im Kopf ist dann nur Beschriftung, weil die H1 ihn schon nennt.
    level: Überschriftenebene des Kategorie-Kopfs (2 auf der Startseite, 3 im Glossar-Band)."""
    ico = CAT_ICON.get(sec["id"], "box")
    n = len(sec_items(sec))  # eindeutige Tools, wie Kategorie-Seite und Kacheln
    ids = set() if cat_page_mode else None
    art = f'<div class="cat-art reveal"><img src="img/cat-{sec["id"]}.svg" alt="" loading="lazy" width="800" height="300"></div>' if n else ""
    body = [render_blocks(sec["blocks"], sec["id"], None, tools_map, ids)]
    sub_tag = "h2" if cat_page_mode else f"h{level + 1}"
    for sub in sec["subs"]:
        sico = SUB_ICON.get(sub["id"])
        title = html.escape(SUB_H2[sub["id"]]) if cat_page_mode and sub["id"] in SUB_H2 else inline(sub["title"])
        body.append(f'<{sub_tag} class="sub" id="{sub["id"]}">{icon(sico) if sico else ""}{title}</{sub_tag}>')
        body.append(render_blocks(sub["blocks"], sec["id"], sub["id"], tools_map, ids))
    count = f'<span class="count">{n} Tools</span>' if n else ""
    if page_link:
        count += f'<a class="more" href="{cat_page(sec["id"])}" title="Eigene Seite: {html.escape(sec["title"])}">Seite{icon("arrow")}</a>'
    head_tag = "p" if cat_page_mode and sec["subs"] else ("h2" if cat_page_mode else f"h{level}")
    return (f'<section class="cat" id="{sec["id"]}"><div class="cat-head">{icon(ico)}<{head_tag} class="cat-title">{inline(sec["title"])}</{head_tag}>{count}</div>'
            f'{art}{"".join(body)}</section>')


def render_featured(sec, tools_map):
    cards = []
    for kind, val in sec["blocks"]:
        if kind != "items":
            continue
        for it in val:
            eu, oss, clean = item_meta(it)
            tools_map.setdefault(it["name"], {"u": it["url"], "d": clean, "eu": eu})
            eu_badge = '<span class="badge eu">EU</span>' if eu else ""
            cards.append(
                f'<li data-eu="{int(eu)}" data-oss="{int(oss)}" data-search="{html.escape((it["name"] + " " + clean + " favoriten").lower())}">'
                f'{favicon(it["url"])}<div><a class="name" href="{html.escape(it["url"])}" target="_blank" rel="noopener">{html.escape(it["name"])}</a>'
                f'<span class="badges">{eu_badge}</span><span class="desc">{html.escape(clean)}</span></div></li>')
    return "".join(cards)


def render_pg(sec):
    cards = []
    for kind, val in sec["blocks"]:
        if kind != "table":
            continue
        for row in val[1:]:
            m = re.match(r"\[([^\]]+)\]\(" + DEST + r"\)", row[0])
            if not m:
                continue
            title, url = m.group(1), retag(check_url(m.group(2), "PROMPTGOTT-Tabelle"), "pg-band")
            cards.append(f'<a class="pg-card reveal" href="{html.escape(url)}" target="_blank" rel="noopener"><b>{html.escape(title)}</b>'
                         f'<span>{html.escape(plain(row[1]))}</span><small>Passt zu: {html.escape(plain(row[2]))}</small></a>')
    intro = next((v for k, v in sec["blocks"] if k == "p"), "")
    return intro, "".join(cards)


def render_stacks(tools_map, stacks=None):
    out = []
    for st in (STACKS["stacks"] if stacks is None else stacks):
        lis = []
        for name, why in st["tools"]:
            t = tools_map.get(name)
            if not t:
                raise SystemExit(f"Stack {st['id']}: Tool '{name}' nicht in README.de.md gefunden")
            lis.append(f'<li>{favicon(t["u"])}<div><a href="{html.escape(t["u"])}" target="_blank" rel="noopener">{html.escape(name)}</a> '
                       f'<span>{html.escape(why)}</span></div></li>')
        pg = ""
        if st.get("promptgott"):
            pg = f'<p class="pgline">💡 PROMPTGOTT dazu: <a href="{html.escape(retag(check_url(st["promptgott"][1], "data/stacks.json") + "?" + utm("kiste-" + st["id"])))}" target="_blank" rel="noopener">{html.escape(st["promptgott"][0])}</a></p>'
        if st.get("note"):
            pg = f'<p class="pgline">{html.escape(st["note"])}</p>'
        out.append(f'<article class="stack reveal" id="kiste-{st["id"]}"><div class="head">{icon(st["icon"])}<div><h3>{html.escape(st["title"])}</h3>'
                   f'<p class="for">{html.escape(st["for"])}</p></div></div><ol>{"".join(lis)}</ol>{pg}</article>')
    return "".join(out)


ROLLEN_FORM = ["Selbstständig / Freelancer", "Marketing / SEO", "Shop-Betreiber", "Entwickler / Maker", "Kundenservice / Vertrieb",
               "Content / Social Media", "Büro / Geschäftsführung", "Agentur", "Anderes"]


# Honeypot: für Bots ein normales Feld, für Screenreader und Tastatur unsichtbar (aria-hidden, tabindex=-1, eigenes Label)
HONEY = '<div class="honey" aria-hidden="true"><label>Bitte leer lassen <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>'
# Seite und vorherige Seite füllt app.js beim Absenden (kein Speicher im Browser, kein Tracking)
CONTEXT_FIELDS = '<input type="hidden" name="seite" value=""><input type="hidden" name="vorher" value="">'
REQ = '<span class="req" aria-hidden="true"> *</span>'
# Einwilligungstext für jedes Formular (Stack-Check und, wortgleich in app.js, Stack-Finder). Rechtsgrundlagen
# und Empfänger erklärt datenschutz.html; Formulardienst und Postfach legt Jean noch fest (dann hier anpassen).
CONSENT = ('Ich habe die <a href="datenschutz.html">Datenschutzhinweise</a> gelesen. Meine Angaben gehen über den Formulardienst '
           'FormSubmit per E-Mail an Jean Maurice Port und werden nur für die Antwort auf diese Anfrage genutzt. Dabei können sie '
           'in Länder ohne gleichwertigen Datenschutz wie die USA gelangen. Damit bin ich einverstanden; widerrufen kann ich das jederzeit per E-Mail.')


def lead_form(source, subject, compact=False, rolle=""):
    nxt = SITE_URL + "danke.html?typ=check"
    if rolle and rolle not in ROLLEN_FORM:
        raise SystemExit(f"lead_form: unbekannte Rolle {rolle!r}")
    # Leere Erstoption: ohne Auswahl kommt keine Rolle an, statt still "Selbstständig" zu melden
    opts = f'<option value=""{"" if rolle else " selected"}>Bitte wählen (optional)</option>' + "".join(
        f"<option{' selected' if r == rolle else ''}>{r}</option>" for r in ROLLEN_FORM)
    return f"""<form class="form" action="https://formsubmit.co/{LEAD_TO}" method="POST">
<input type="hidden" name="_subject" value="{html.escape(subject)}"><input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="false"><input type="hidden" name="_next" value="{nxt}">
<input type="hidden" name="quelle" value="{html.escape(source)}">{CONTEXT_FIELDS}
{HONEY}
<input type="hidden" name="merkliste" id="l-merk" value=""><input type="hidden" name="rechner" id="l-rechner" value=""><input type="hidden" name="radar" id="l-radar" value="">
<p class="req-note">Felder mit * sind Pflicht.</p>
<div class="row"><div><label for="l-name">Name (optional, Vorname reicht)</label><input id="l-name" name="name" autocomplete="given-name"></div>
<div><label for="l-mail">E-Mail{REQ}</label><input id="l-mail" type="email" name="email" required autocomplete="email"></div></div>
<div class="row"><div><label for="l-web">Website oder Shop (optional)</label><input id="l-web" name="website" placeholder="https://" autocomplete="url"></div>
<div><label for="l-rolle">Du bist</label><select id="l-rolle" name="rolle">{opts}</select></div></div>
<label for="l-proj">Was baust du gerade, und wo hakt es?{REQ}</label><textarea id="l-proj" name="projekt" rows="4" required placeholder="Beispiel: Shop mit 2.000 Artikeln, Produkttexte in DE/EN/NL, ein Mensch für alles."></textarea>
<div class="attach hidden" id="l-attach-merk">{icon("bookmark")}<span></span><button type="button" data-clear="l-merk">Entfernen</button></div>
<div class="attach hidden" id="l-attach-rechner">{icon("clock")}<span></span><button type="button" data-clear="l-rechner">Entfernen</button></div>
<div class="attach hidden" id="l-attach-radar">{icon("chart")}<span></span><button type="button" data-clear="l-radar">Entfernen</button></div>
<label class="consent"><input type="checkbox" name="einwilligung" value="ja" required><span>{CONSENT}{REQ}</span></label>
<button class="btn" type="submit">{icon("mail")}Stack-Check anfragen</button>
<p class="hint">Die Antwort kommt per E-Mail, meist innerhalb weniger Tage. Oder direkt an {mail_link("Stack-Check")}.</p>
</form>"""


def absolutize(doc, base):
    """Relative href/src auf den Seitenpfad umschreiben. Ersatz für <base>, das Fragment-Verweise wie
    <use href="#i-wrench"> auf die Startseite umbiegen würde."""
    def fix(m):
        url = m.group(2)
        if re.match(r"(https?:|mailto:|#|/|data:)", url):
            return m.group(0)
        return f'{m.group(1)}="{base}{url[2:] if url.startswith("./") else url}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, doc)


TOPBAR_END = "<!--/topbar-->"


def main_landmark(body):
    """Alles zwischen Kopfleiste (samt Such-Panel) und Fußzeile wird <main>, Ziel des Skip-Links."""
    head, sep, rest = body.partition(TOPBAR_END)
    if not sep or "<footer" not in rest:
        raise SystemExit("page_shell: Seite braucht topbar() und footer()")
    i = rest.index("<footer")
    return f'{head}<main id="werkbank" tabindex="-1">{rest[:i]}</main>\n{rest[i:]}'


# Inline-Snippet im Head: JS-Klasse und gespeichertes Farbschema vor dem ersten Rendern (kein Theme-Flackern),
# dazu ein einziger Listener, der Bilder ohne Antwort (fehlende Favicons) ausblendet, statt onerror an jedem <img>.
# Es ist das einzige Inline-Skript; die CSP erlaubt es per Hash, den der Build aus genau diesem Text bildet.
HEAD_JS = ('document.documentElement.classList.add("js");try{var t=localStorage.getItem("kw-theme");'
           'if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}'
           'document.addEventListener("error",function(e){var i=e.target;if(i&&i.tagName==="IMG")i.style.visibility="hidden"},true);')
HEAD_JS_HASH = base64.b64encode(hashlib.sha256(HEAD_JS.encode("utf-8")).digest()).decode("ascii")
# Meta-CSP: keine Inline-Handler, Daten nur als <script type="application/json">. frame-ancestors wirkt per Meta nicht.
# Bilder nur von der eigenen Seite: die Favicons liegen lokal unter docs/img/fav/.
CSP = ("default-src 'self'; "
       f"script-src 'self' 'sha256-{HEAD_JS_HASH}'; "
       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
       "connect-src 'self' https://formsubmit.co; form-action 'self' https://formsubmit.co; "
       "base-uri 'none'; object-src 'none'; upgrade-insecure-requests")
# Bewusst kein Font-Preload: Chrome hält den ersten Paint für vorgeladene Schriften an, bis sie da sind.
# Gemessen (Slow 4G, 4x CPU, 29.10.2026): beide Schriften vorladen kostete 180 bis 360 ms LCP, nur Space Grotesk
# rund 150 ms auf Ratgebern, ohne messbaren CLS-Gewinn (Swap 0,015). Die @font-face-Regeln stehen jetzt am Anfang
# von style.css, damit die Schriften ohne extra CSS-Request angefordert werden. Bei Bedarf hier Dateinamen eintragen.
PRELOAD_FONTS = ()
ASSETS = DOCS / "assets"


def asset_v(name):
    """?v=<Inhalts-Hash>: neue HTML trifft nach einem Deploy nie auf altes CSS/JS aus dem Cache."""
    return f"assets/{name}?v=" + hashlib.sha1((ASSETS / name).read_bytes()).hexdigest()[:8]


SYMBOLS = {sid: full for full, sid in re.findall(r'(<symbol id="i-([\w-]+)"[^>]*>.*?</symbol>)', ICONS, re.S)}
APP_ICONS = set(re.findall(r'(?:svg|icon)\("([\w-]+)"\)', (ASSETS / "app.js").read_text(encoding="utf-8")))
FINDER_ICONS = {o[2] for q in STACKS["finder"]["questions"] for o in q["options"]}


def icon_sprite(doc):
    """Nur die Symbole, die die Seite (oder app.js auf ihr) wirklich benutzt."""
    used = set(re.findall(r'#i-([\w-]+)', doc)) | APP_ICONS | (FINDER_ICONS if 'id="kw-finder"' in doc else set())
    missing = sorted(used - set(SYMBOLS))
    if missing:
        raise SystemExit(f"Icons fehlen in scripts/template/icons.svg: {missing}")
    return ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">'
            + "".join(SYMBOLS[i] for i in sorted(used)) + "</svg>")


WARN = []  # Build-Warnungen (Title/Description zu lang), am Ende gesammelt ausgegeben
SUFFIX = " – KI-Werkstatt"


def seo_title(t):
    """Markenzusatz nur, wenn der Title damit höchstens 60 Zeichen hat; sonst schneidet Google ihn ohnehin ab."""
    return t + SUFFIX if len(t + SUFFIX) <= 60 else t


def page_shell(title, body, desc=DESCRIPTION, canonical=SITE_URL, extra_head="", og_type="website", published=None, modified=None):
    noindex = 'name="robots" content="noindex"' in extra_head
    if not noindex:
        if len(title) > 60:
            WARN.append(f"Title {len(title)} Zeichen (> 60): {canonical.replace(SITE_URL, '') or 'index.html'}")
        if len(desc) > 160:
            WARN.append(f"Description {len(desc)} Zeichen (> 160): {canonical.replace(SITE_URL, '') or 'index.html'}")
    # JSON-LD ans Ende des Body: Google liest es überall, der sichtbare Inhalt kommt so früher
    ld = "".join(re.findall(r'<script type="application/ld\+json">.*?</script>', extra_head, re.S))
    extra_head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", extra_head, flags=re.S).strip()
    og_extra = ""
    if og_type == "article":
        og_extra = (f'<meta property="article:published_time" content="{published}">'
                    f'<meta property="article:modified_time" content="{modified or published}">')
    main = main_landmark(body)
    preload = "".join(f'<link rel="preload" href="assets/fonts/{f}" as="font" type="font/woff2" crossorigin>' for f in PRELOAD_FONTS)
    doc_head = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<script>{HEAD_JS}</script>
{preload}<link rel="stylesheet" href="{asset_v("style.css")}">
<meta property="og:type" content="{og_type}"><meta property="og:locale" content="de_DE"><meta property="og:site_name" content="KI-Werkstatt">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE_URL}og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="KI-Werkstatt: KI-Tools auf Deutsch, sortiert, Links geprüft">{og_extra}
<meta name="twitter:card" content="summary_large_image">{'' if noindex else chr(10) + '<meta name="robots" content="max-image-preview:large">'}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/atom+xml" title="KI-Werkstatt: Trends und Neuzugänge" href="{SITE_URL}feed.xml">
{extra_head}
</head>
<body>
<a class="skip" href="#werkbank" data-chrome>Zum Inhalt springen</a>
"""
    tail = f"""
{main}
{ld}
<script src="{asset_v("app.js")}" defer></script>
</body>
</html>
"""
    return doc_head + icon_sprite(main) + tail


# Seiten mit eigenem Stack-Check-Formular; alle anderen verlinken das Formular der Startseite
SC_HERE = {"index", "kategorien", "glossar", "trends", "einsatz", "ratgeber"}


def topbar(here=""):
    """Kopfleiste für alle Seiten: Logo, Suche (Panel über alle Tools, Ratgeber und Begriffe), Hauptnavigation,
    unter 1100 px als Menü hinter einem Knopf. here: index, kategorien, einsatz, ratgeber, trends, glossar,
    einsatz-hub, ratgeber-hub oder sub (Danke, 404, Rechtliches)."""
    home = "" if here == "index" else "./"
    sc = "#stack-check" if here in SC_HERE else "./#stack-check"
    nav_items = [("kategorien", f"{home}#kategorien", "Tools"), ("einsatz", EINSATZ_PAGE, "Einsatz"), ("ratgeber", RATGEBER_PAGE, "Ratgeber"),
                 ("trends", TRENDS_PAGE, "Trends"), ("glossar", GLOSSAR_PAGE, "Glossar")]
    key = here.replace("-hub", "")
    # Übersicht, Trends, Glossar: diese Seite; Unterseiten eines Bereichs: im Bereich
    cur = ' aria-current="page"' if here.endswith("-hub") or here in ("trends", "glossar") else ' aria-current="true"'
    nav = '<nav class="mainnav" id="nav" aria-label="Hauptnavigation">' + "".join(
        f'<a href="{href}"{cur if k == key else ""}>{label}</a>' for k, href, label in nav_items) + "</nav>"
    return f"""<header class="topbar"><div class="wrap in">
<a class="logo" href="./" aria-label="KI-Werkstatt, zur Startseite"><span class="mark">{icon("wrench")}</span><span>KI-WERKSTATT</span></a>
<form id="searchform" role="search"><label class="sr" for="q">Tools, Ratgeber und Begriffe durchsuchen</label><input type="search" id="q" placeholder="Suchen: Podcast, DSGVO, Shop …" autocomplete="off" role="combobox" aria-haspopup="dialog" aria-controls="searchpanel" aria-expanded="false"></form>
{nav}
<div class="tools"><button class="iconbtn" id="theme" type="button" title="Hell/Dunkel umschalten" aria-label="Dunkles Design" aria-pressed="false">{icon("sun")}</button>
<a class="iconbtn sc-m" href="{sc}" title="Stack-Check" aria-label="Stack-Check: kostenlose Tool-Empfehlung">{icon("mail")}</a>
<button class="iconbtn menubtn" id="menubtn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menü">{icon("menu")}</button>
<a class="btn btn-lime btn-sm hide-m" href="{sc}">{icon("mail")}Stack-Check anfragen</a></div>
</div><div id="progress"></div></header>
<div class="searchpanel" id="searchpanel" role="dialog" aria-label="Suchergebnisse" hidden><div class="wrap">
<div class="sp-head"><b id="sp-count" aria-live="polite"></b><label><input type="checkbox" id="sp-eu"> nur EU-Anbieter</label><label><input type="checkbox" id="sp-oss"> nur Open Source</label><label><input type="checkbox" id="sp-neu"> nur neu</label><button class="close" type="button" title="Suche schließen" aria-label="Suche schließen">{icon("x")}</button></div>
<div class="sp-pages" hidden><p class="sp-lbl">Ratgeber, Einsatzgebiete und Begriffe</p><ul></ul></div>
<p class="sp-lbl sp-tools-lbl" hidden>Tools</p>
<ol class="sp-list"></ol>
<div class="sp-empty hidden">{kurbel("kb-sm", wink=True)}<p><b>Die Schublade klemmt.</b> Zu diesem Wort hat Kurbel nichts gefunden. Probier ein anderes oder frag direkt beim <a href="{sc}">Stack-Check</a>.</p></div>
</div></div>{TOPBAR_END}"""


def footer(bar=True):
    """Fußzeile als Sitemap: alle Schubladen, Einsatzgebiete und Ratgeber. bar=False für Nebenseiten
    (Danke, 404, Rechtliches): ohne Sticky-Leiste und Merkliste."""
    def col(title, links, cls=""):
        return f'<div class="fcol{cls}"><h2 class="fh">{title}</h2><ul>' + "".join(f"<li>{x}</li>" for x in links) + "</ul></div>"
    ext_attr = ' target="_blank" rel="noopener"'
    a = lambda href, label, ext=False: f'<a href="{href}"{ext_attr if ext else ""}>{html.escape(label)}</a>'
    cols = [
        f'<div class="fcol fbrand"><h2 class="fh">KI-Werkstatt</h2><p>{html.escape(BRAND["claim"])} {html.escape(BRAND["tagline"])}</p></div>',
        col("KI-Tools", [a(cat_page(s["id"]), cat_h1(s)) for s in NAV["secs"]]),
        col("Einsatz", [a(EINSATZ_PAGE, "Alle Einsatzgebiete")] + [a(e["page"], e["h1"]) for e in EINSATZ["seiten"]]),
        col("Ratgeber", [a(RATGEBER_PAGE, "Alle Ratgeber")] + [a(r["page"], r["label"]) for r in RATGEBER["artikel"]]),
        col("Werkstatt", [a(TRENDS_PAGE, "KI-Trends"), a(GLOSSAR_PAGE, "KI-Glossar"), a(GLOSSAR_PAGE + "#weiterlernen", "Weiterlernen und Listen"),
                          a("./#finder-band", "Stack-Finder"), a("./#werkzeugkisten", "Werkzeugkisten"), a("./#rechner", "Zeitspar-Rechner"),
                          a("./#stack-check", "Stack-Check")]),
        col("Projekt", [a(REPO_URL, "GitHub-Repository"), a(REPO_URL + "/blob/main/README.de.md#mitmachen", "Mitmachen: Tool vorschlagen"),
                        a(REPO_URL + "/blob/main/README.de.md", "Liste als Markdown"), f'{a("tools.csv", "Liste als CSV")} · {a("tools.json", "JSON")}',
                        a("feed.xml", "Trends als Feed (Atom)"), a(REPO_URL + "/blob/main/README.md", "About (English)")]),
        col("Praxis", [a(f"{SUBSTACK}?{utm('footer')}", "PROMPTGOTT auf Substack", True), a(pg_sub("footer"), "Newsletter abonnieren", True)]),
        col("Rechtliches", [a("impressum.html", "Impressum"), a("datenschutz.html", "Datenschutz"), a(REPO_URL + "/blob/main/LICENSE", "MIT-Lizenz")]),
    ]
    out = f"""<footer><div class="wrap">
<nav class="cols" aria-label="Alle Seiten">{"".join(cols)}</nav>
<p class="screws" id="screws" hidden></p>
<p>Letzter Link-Check: {LINK_CHECK} ({LINK_CHECK_N} Links). Keine Affiliate-Links, keine bezahlten Platzierungen. Tool-Namen und -Logos bezeichnen nur das jeweilige Produkt, Marken und Logos gehören ihren Inhabern; die Favicons liegen als Kopie auf dieser Seite. Mit keinem Anbieter besteht eine Verbindung. <a href="impressum.html#werkstatt">So entsteht die KI-Werkstatt</a></p>
</div>
<button id="totop" type="button" title="Nach oben" aria-label="Nach oben">{icon("up")}</button></footer>"""
    if not bar:
        return out
    # Sticky-Leiste ohne Formular: CSV direkt laden oder PROMPTGOTT abonnieren. app.js zeigt sie ab 60 % Scrolltiefe,
    # nie neben einem Lead-Formular oder dem Footer. Eigene Landmarks, damit nichts außerhalb von Regionen steht.
    return out + f"""
<aside class="stickybar" id="stickybar" aria-label="Liste und Newsletter"><div class="wrap in">
<p class="sb-txt">Alle Tools zum Mitnehmen</p>
<a class="btn btn-lime btn-sm" href="tools.csv" download>{icon("download")}<span><span class="sb-long">Liste als </span>CSV laden</span></a>
<a class="btn btn-pg btn-sm" href="{html.escape(pg_sub("sticky"))}" target="_blank" rel="noopener">{icon("flame")}PROMPTGOTT abonnieren</a>
<button class="close" type="button" title="Ausblenden" aria-label="Leiste ausblenden">{icon("x")}</button>
</div></aside>
<aside class="merk-dock" aria-label="Merkliste">
<button id="merk-pill" class="merk-pill hidden" type="button" aria-controls="merk" aria-expanded="false">{icon("bookmark")}Merkliste <b id="merk-n">0</b></button>
<div id="merk" class="merk" role="dialog" aria-labelledby="merk-h" hidden>
<div class="merk-head"><h2 id="merk-h">{icon("bookmark")}Deine Merkliste</h2><button class="close" type="button" title="Schließen" aria-label="Merkliste schließen">{icon("x")}</button></div>
<p class="merk-empty">Noch leer. Klick bei einem Tool auf das Lesezeichen.</p>
<ol class="merk-list"></ol>
<div class="merk-actions"><button type="button" class="btn btn-lime btn-sm" id="merk-send">{icon("mail")}Mit Merkliste zum Stack-Check</button><button type="button" class="btn btn-sm" id="merk-copy">{icon("copy")}Kopieren</button><button type="button" class="btn btn-sm" id="merk-clear">{icon("trash")}Leeren</button></div>
<p class="merk-note">Die Merkliste liegt nur in deinem Browser. An Jean geht sie erst, wenn du das Stack-Check-Formular abschickst.</p>
</div></aside>"""


# --------------------------------------------------------------------------- Kurbel, der Werkstatt-Roboter
def kurbel(cls="", wink=False, label="Kurbel, der Werkstatt-Roboter"):
    eye_r = ('<path d="M68 42h10"/>' if wink else '<circle cx="73" cy="42" r="4.5" fill="currentColor" stroke="none"/>')
    return f"""<svg class="kurbel {cls}" viewBox="0 0 130 124" role="img" aria-label="{html.escape(label)}">
<g class="kb-ant"><path d="M60 22V11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="60" cy="8" r="4.5" class="kb-spark"/><circle cx="60" cy="8" r="3" class="kb-spark-hi"/>
<path d="M50 5l-4-3M70 5l4-3M60-3v0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></g>
<g class="kb-bob" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
<rect x="30" y="22" width="60" height="44" rx="14" class="kb-head"/>
<circle cx="47" cy="42" r="4.5" fill="currentColor" stroke="none"/>{eye_r}
<path d="M48 54q12 8 24 0"/>
<circle cx="38" cy="53" r="3" class="kb-cheek" stroke="none"/><circle cx="82" cy="53" r="3" class="kb-cheek" stroke="none"/>
<path d="M54 66v6M66 66v6"/>
<rect x="36" y="72" width="48" height="32" rx="10" class="kb-body"/>
<circle cx="60" cy="88" r="5"/><path d="M57 88h6"/>
<path d="M36 80q-12 4-14 16"/><path d="M84 80q10-2 15-12"/>
<g transform="translate(97 52) rotate(35)"><path d="M0 14V4"/><path d="M-5 4a5 5 0 1 1 10 0l-2 2h-6Z"/></g>
<path d="M48 104v10M72 104v10"/>
</g>
<g transform="translate(96 114) rotate(-18)" class="kb-screw"><rect x="0" y="0" width="12" height="4.5" rx="1.5"/><rect x="11" y="-1.5" width="3.5" height="7.5" rx="1"/></g>
</svg>"""


# --------------------------------------------------------------------------- Hans Moritz, der Werkstattmeister
def hans(cls="", wink=False, label="Hans Moritz, der Werkstattmeister", thumb=False):
    def eye(x, closed=False):
        if closed:
            return f'<path d="M{x-4.5} 61.5q4.5 3 9 0" fill="none" class="hm-ln" stroke-linecap="round"/>'
        return (f'<g class="hm-eye" style="transform-origin:{x}px 61px"><ellipse cx="{x}" cy="61" rx="4.8" ry="2.9" fill="#fff"/><g class="hm-pupil"><circle cx="{x+.4}" cy="61.3" r="2.6" class="hm-iris"/>'
                f'<circle cx="{x+.4}" cy="61.3" r="1.15" fill="#1b1f26"/><circle cx="{x+1.2}" cy="60.4" r=".6" fill="#fff"/></g></g>'
                f'<path d="M{x-5.2} 59.6q5.2-2.6 10.4 0" fill="none" class="hm-ln" stroke-width="1.4" stroke-linecap="round"/>'
                f'<path d="M{x-5} 64.4q5 2 10 0" fill="none" stroke="#d99b7c" stroke-width="1" stroke-linecap="round"/>')
    def bud(x, d):
        return (f'<ellipse cx="{x}" cy="64.5" rx="3.6" ry="3.2" class="hm-bud"/>'
                f'<rect x="{x-1.5}" y="65.5" width="3" height="9.5" rx="1.5" class="hm-bud"/>')
    # Ohne Label (z. B. im Button mit eigenem Namen oder in der Druckzeile) ist Hans Dekoration
    a11y = f'role="img" aria-label="{html.escape(label)}"' if label else 'aria-hidden="true"'
    return f"""<svg class="hans {cls}" viewBox="0 0 140 160" {a11y}>
<g class="hm-bob">
<path class="hm-jacket" d="M8 160q2-30 30-40l18-6h28l18 6q28 10 30 40Z"/>
<path d="M44 116q-22 6-28 30M96 116q22 6 28 30" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>
<path class="hm-skin" d="M57 92h26v20H57Z"/>
<path class="hm-collar" d="M52 103q18 7 36 0l3 15q-21 9-42 0Z"/>
<path d="M70 108v52" stroke="#c9ced8" stroke-width="1.6"/><rect x="68" y="109" width="4" height="7" rx="1.5" fill="#c9ced8"/>
<g transform="translate(52 130) rotate(-8)"><rect x="-7" y="-7" width="14" height="14" rx="3.5" fill="#D7FF3C"/><path d="M-3.5 3.5 3.5-3.5M-.5-3.5h4v4" fill="none" stroke="#0E1116" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>
<path d="M106 117 38 160" stroke="#14171c" stroke-width="8"/>
<path d="M44 160q-2-12 10-18l6 7q-8 4-8 11" fill="#efe6cf" stroke="#14171c" stroke-width="1.4"/>
<g class="hm-head">
<ellipse class="hm-skin hm-ln" cx="37.5" cy="66" rx="5.5" ry="8.5"/><ellipse class="hm-skin hm-ln" cx="102.5" cy="66" rx="5.5" ry="8.5"/>
<path class="hm-skin hm-ln" d="M41 62q-1-36 29-37q30 1 29 37q0 14-4 22H45q-4-8-4-22Z"/>
{bud(37.5, -1)}{bud(102.5, 1)}
<path class="hm-buzz" d="M42 52q2-25 28-26q26 1 28 26q-9-16-28-17q-19 1-28 16Z"/>
<path d="M57 40q13-3 26 0M60 45q10-2 20 0" fill="none" stroke="#d99b7c" stroke-width="1" stroke-linecap="round"/>
<path class="hm-beard" d="M41 60q-1 27 12 39q8 7 17 7t17-7q13-12 12-39q-3 12-10 17q-7-4-19-4t-19 4q-7-5-10-17Z"/>
<path class="hm-beard-d" d="M54 81q8-7 16-5q8-2 16 5q-8 3-16 1q-8 2-16-1Z"/>
<path d="M60 86.5q10 5.5 20-1" fill="none" stroke="#7a2f12" stroke-width="1.9" stroke-linecap="round"/>
<path d="M49.5 54q7.5-3.8 14-.6M76.5 53.4q6.5-3.2 14 .6" fill="none" stroke="#c8642a" stroke-width="2.5" stroke-linecap="round"/>
{eye(58)}{eye(82, wink)}
<path d="M51 62.5l-3 1.6M89 62.5l3 1.6" stroke="#d99b7c" stroke-width="1" stroke-linecap="round"/>
<path d="M70 61q-1.5 8-4.5 11q4.5 2.2 9 0" fill="none" stroke="#b9775a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<g fill="#d0865a" opacity=".75"><circle cx="52" cy="69" r=".8"/><circle cx="55.5" cy="71" r=".7"/><circle cx="50" cy="72" r=".6"/><circle cx="86" cy="69" r=".8"/><circle cx="89.5" cy="71.5" r=".7"/><circle cx="84" cy="72" r=".6"/><circle cx="66.5" cy="66" r=".55"/><circle cx="73.5" cy="66.5" r=".55"/></g>
<g class="hm-lamp" aria-hidden="true"><circle cx="70" cy="37" r="15" class="hm-glow"/><path d="M42.5 45q27.5-11 55 0" fill="none" stroke="#2b2f36" stroke-width="3.2" stroke-linecap="round"/><rect x="63" y="33" width="14" height="9" rx="3" fill="#2b2f36"/><circle cx="70" cy="37.5" r="2.9" fill="#FFF6A8"/></g>
<g class="hm-hat" aria-hidden="true"><path d="M43 41q2-20 27-21q14 0 23 8q9 7 16-3l3 4q-7 12-17 6q2 4 2 8Z" fill="#C8302C" stroke="#7a1512" stroke-width="1.4" stroke-linejoin="round"/><path d="M41 43q29-9 58 0q1 4-1 7q-28-8-56 0q-2-3-1-7Z" fill="#fff" stroke="#d9d4c8" stroke-width="1"/><circle cx="112" cy="26" r="5" fill="#fff" stroke="#d9d4c8" stroke-width="1"/></g>
</g>
{'<g class="hm-thumb"><path d="M104 160q2-22 8-34l9 3q-3 14-3 31Z" class="hm-jacket"/><path d="M110 128q-1-9 3-13h10q3 3 2 8l-1 5q-5 3-14 0Z" class="hm-skin hm-ln"/><path d="M114 115q-1-10 4-12q4 1 2 12" class="hm-skin hm-ln"/><path d="M113 120h10M113 124h10" stroke="#d99b7c" stroke-width="1" stroke-linecap="round"/></g>' if thumb else ''}
</g>
</svg>"""


def pumpkin():
    """Kürbis für die Halloween-Woche, sitzt neben Hans im Hero (per CSS nur dann sichtbar)."""
    return ('<svg class="hm-pumpkin" viewBox="0 0 60 52" aria-hidden="true">'
            '<path d="M30 12q-2-8 4-11" fill="none" stroke="#4d6b1f" stroke-width="3" stroke-linecap="round"/>'
            '<ellipse cx="30" cy="31" rx="27" ry="19" fill="#E8761F" stroke="#0E1116" stroke-width="2"/>'
            '<path d="M30 12q-9 19 0 38M30 12q9 19 0 38M14 15q-6 16 2 33M46 15q6 16-2 33" fill="none" stroke="#B9530E" stroke-width="1.6"/>'
            '<path d="M19 27l5-4 3 5ZM41 27l-5-4-3 5ZM19 36q11 8 22 0l-4 1-3 3-4-3-4 3-3-3Z" fill="#FFD23F" stroke="#0E1116" stroke-width="1.2" stroke-linejoin="round"/>'
            '</svg>')


def screw_svg():
    return ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="#B9BEC6" stroke="#0E1116" stroke-width="1.6"/>'
            '<path d="M7.5 12h9M12 7.5v9" stroke="#0E1116" stroke-width="2" stroke-linecap="round"/></svg>')


def eu_names(sec, limit=5):
    names = [it["name"] for it in sec_items(sec) if item_meta(it)[0]]
    if not names:
        return ""
    names = names[:limit]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " und " + names[-1]


def kat_text(sec, key):
    """Text aus data/kategorien.json mit Platzhaltern {n}, {subs}, {eu}."""
    raw = KAT[sec["id"]][key]
    eu = eu_names(sec)

    def fill(t):
        if "{eu}" in t and not eu:
            raise SystemExit(f"kategorien.json/{sec['id']}/{key}: {{eu}} benutzt, aber keine EU-Anbieter in dieser Schublade")
        return t.replace("{n}", str(len(sec_items(sec)))).replace("{subs}", str(max(1, len(sec["subs"])))).replace("{eu}", eu)
    if isinstance(raw, list):
        return [[fill(x) for x in r] if isinstance(r, list) else fill(r) for r in raw]
    return fill(raw)


def top_tools(sec, k=3):
    """Bekannte Tools zuerst: was in Favoriten oder Werkzeugkisten steht, dann der Rest."""
    known = {n for st in STACKS["stacks"] for n, _ in st["tools"]}
    its = sec_items(sec)
    return (sorted(its, key=lambda it: 0 if it["name"] in known else 1))[:k]


def faq_html(items):
    return "".join(f'<details class="faq-item reveal"><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in items)


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


PG_BOX = {  # ein Satz je Platzierung; Takt und Versprechen des Newsletters legt Jean fest, deshalb hier keins
    "danke": "Bis Jean antwortet: PROMPTGOTT zeigt in Deep Dives, wie aus einzelnen Tools ein System wird, das im Alltag hält.",
    "geschafft": "Noch Luft für mehr? PROMPTGOTT geht bei solchen Themen eine Ebene tiefer, mit Praxis statt Produktliste.",
    "trends": "Wer tiefer als eine Trendkarte einsteigen will: PROMPTGOTT zeigt in Deep Dives, wie aus Neuerungen Arbeitsabläufe werden.",
    "glossar": "Vokabeln sind der Anfang. Wie daraus Abläufe werden, die jeden Tag laufen, zeigt PROMPTGOTT in Deep Dives.",
}


def pg_box(placement):
    """Abo-Box für PROMPTGOTT: nur ein Link (kein Substack-Embed, also keine Dritt-Requests), utm_content je Platzierung."""
    return (f'<div class="pg-box" data-chrome><p>{icon("flame")}<span>{html.escape(PG_BOX[placement])}</span></p>'
            f'<a class="btn btn-pg" href="{html.escape(pg_sub(placement))}" target="_blank" rel="noopener">{icon("flame")}PROMPTGOTT abonnieren</a></div>')


def legal_note(stand=None):
    """Einheitlicher Hinweis auf Ratgeber-, Einsatz- und Glossarseiten (Legal B10); auf jeder Seite gleich, daher data-chrome."""
    st = f"Stand {de_date(stand)}. " if stand else ""
    return (f'<p class="legal-note" data-chrome>{icon("shield")}<span>{st}Diese Seite ist keine Rechtsberatung, sondern eine Arbeitshilfe. '
            "Für deinen konkreten Fall frag eine Anwältin, einen Anwalt oder die Person, die bei dir den Datenschutz verantwortet.</span></p>")


def quellen_note():
    """Abrufdatum der Quellen: scripts/check_links.py fragt auch alle Quellen aus data/ ab."""
    return f'<p class="quellen-note">Alle Quellen-Links zuletzt abgerufen am {LINK_CHECK} (Link-Check).</p>'


SPRECHER = {"hans", "kurbel"}


def speaker(item):
    """Sprechblasen-Figur aus dem Datenfeld "sprecher": Roboter-Zeilen und die übrige Schraube gehören Kurbel (Brand-Voice)."""
    who = item.get("sprecher", "hans")
    if who not in SPRECHER:
        raise SystemExit(f"{item.get('id')}: sprecher {who!r} unbekannt (erlaubt: {sorted(SPRECHER)})")
    return kurbel("kb-md", wink=True) if who == "kurbel" else hans("hm-md")


def build_index(sections, head_md):
    by_id = {s["id"]: s for s in sections}
    featured = by_id.pop("empfehlungen-der-redaktion", None)
    pg_sec = by_id.pop("promptgott-deep-dives", None)
    tail_ids = ["lernen-prompting-und-ki-grundlagen", "verwandte-listen", "mitmachen"]
    list_secs = [s for s in sections if s["id"] in by_id and s["id"] not in tail_ids]
    tail_secs = [by_id[i] for i in tail_ids if i in by_id]
    missing = [s["id"] for s in list_secs if s["id"] not in KAT]
    if missing:
        raise SystemExit(f"data/kategorien.json: Texte fehlen für {missing}")

    # Werkzeug-Verzeichnis für Finder und Kisten: sachliche Beschreibung aus der Kategorie, nicht der Favoriten-Gag
    tools_map = {}
    for s_, sub, it in all_items(list_secs + tail_secs):
        eu, oss, clean = item_meta(it)
        tools_map.setdefault(it["name"], {"u": it["url"], "d": clean, "eu": eu})
    # Nachschlagen statt Anhängsel: Lernen und Verwandte Listen stehen im Glossar, Mitmachen verlinkt die Fußzeile
    NAV["secs"] = list_secs
    NAV["lernen"] = [s for s in tail_secs if s["id"] in LERNEN_IDS]
    for s_, sub, it in all_items(list_secs):
        NAV["home"].setdefault(it["name"], cat_page(s_["id"]) + "#" + tool_id(it["name"]))
        NAV["sec"].setdefault(it["name"], s_["id"])
    featured_html = render_featured(featured, tools_map) if featured else ""
    pg_intro, pg_cards = render_pg(pg_sec) if pg_sec else ("", "")
    stacks_html = render_stacks(tools_map)

    uniq = {}
    for s_, sub, it in all_items(sections):
        uniq.setdefault(it["url"], it)
    n_tools = len(uniq)
    n_eu = sum(1 for it in uniq.values() if item_meta(it)[0])
    n_oss = sum(1 for it in uniq.values() if item_meta(it)[1])
    n_cats = len(list_secs)
    n_subs = sum(len(s["subs"]) for s in list_secs)

    IMG.mkdir(parents=True, exist_ok=True)
    # Nur Grafiken, die eine Seite zeigt: Schubladen und die Weiterlernen-Bänder im Glossar (mit Tools); Reste löschen
    art_ids = set()
    for i, s in enumerate(list_secs + tail_secs):
        if s in list_secs or (s["id"] in LERNEN_IDS and sec_items(s)):
            art_ids.add(s["id"])
            (IMG / f"cat-{s['id']}.svg").write_text(cat_art(i + 1, s["title"], CAT_ICON.get(s["id"], "box"), i % 2 == 0), encoding="utf-8")
    for f in IMG.glob("cat-*.svg"):
        if f.stem[4:] not in art_ids:
            f.unlink()
    drawers = []
    for i, s in enumerate(list_secs):
        its = sec_items(s)
        n_e = sum(1 for it in its if item_meta(it)[0])
        tops = "".join(f'<li>{favicon(it["url"])}<span>{html.escape(it["name"])}</span></li>' for it in top_tools(s))
        eu_txt = f" · {n_e} EU" if n_e else ""
        drawers.append(f"""<a class="drawer reveal" href="{cat_page(s['id'])}">
<span class="drawer-art"><img src="img/cat-{s['id']}.svg" alt="" loading="lazy" width="800" height="300"></span>
<span class="drawer-body"><b class="drawer-title">{icon(CAT_ICON.get(s["id"], "box"))}{html.escape(cat_h1(s))}</b><span class="drawer-no">Schublade {i + 1:02d}</span>
<span class="drawer-teaser">{html.escape(kat_text(s, "teaser"))}</span>
<ul class="drawer-tools">{tops}</ul>
<span class="drawer-meta">{len(its)} Tools · {max(1, len(s["subs"]))} {"Fächer" if len(s["subs"]) > 1 else "Fach"}{eu_txt}</span><span class="drawer-cta">Schublade aufziehen{icon("arrow")}</span></span></a>""")

    finder = dict(STACKS["finder"], to=LEAD_TO, next=SITE_URL + "danke.html?typ=finder")
    # Inline nur, was der Finder zeigen kann; die ganze Liste lädt app.js erst bei Bedarf aus tools.json
    f_names = {n for v in finder["base"].values() for n in v} | set(finder["eu_swap"].values()) | set(finder["firma_add"])
    missing = sorted(n for n in f_names if n not in tools_map)
    if missing:
        raise SystemExit(f"data/stacks.json/finder: Tools fehlen in README.de.md: {missing}")
    finder_js = json.dumps({"finder": finder, "tools": {n: dict(tools_map[n], i=fav_src(tools_map[n]["u"])) for n in sorted(f_names)}},
                           ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    faq = [
        ("Was bedeutet das EU-Zeichen bei einem Tool?", "Der Anbieter hat seinen Firmensitz in der EU. Das ist ein Hinweis, keine Datenschutz-Prüfung. Für die DSGVO zählen Auftragsverarbeitungsvertrag, Serverstandort und Einstellungen."),
        ("Wie prüft ihr die Tools?", f"Jeder Link wird per HTTP abgefragt, zuletzt am {LINK_CHECK}. Tote Links, Serverfehler und verschwundene Domains fliegen raus. Bot-Schutz gilt als erreichbar, denn dahinter steckt fast immer eine echte Seite."),
        ("Was kostet der Stack-Check?", "Nichts. Du schreibst, was du baust, und bekommst einen Vorschlag per E-Mail. Keine Beratungsstunde, kein Vertrag, kein Newsletter-Abo durch die Hintertür."),
        ("Wer ist Hans Moritz?", "Der Werkstattmeister der KI-Werkstatt: Glatze, roter Vollbart, Trainingsjacke, Earbuds im Ohr. Hans Moritz prüft und sortiert jedes Werkzeug, bevor es in eine Schublade darf, und sagt dir in einem Satz, wofür es taugt. Ausprobiert hat er nicht jedes, und das gibt er offen zu."),
        ("Wer ist Kurbel?", "Der Werkstatt-Roboter von Hans Moritz. Hilfsbereit, gründlich und leicht schusselig, denn nach jeder Reparatur bleibt eine Schraube übrig. Du triffst Kurbel überall dort, wo es sonst leer wäre."),
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE_URL, "url": SITE_URL, "name": TITLE, "description": DESCRIPTION, "inLanguage": "de-DE",
         "publisher": {"@type": "Organization", "name": "KI-Werkstatt", "url": SITE_URL},
         "citation": {"@type": "CreativeWork", "name": "PROMPTGOTT", "url": SUBSTACK}},
        {"@type": "ItemList", "name": "Die Schubladen der KI-Werkstatt", "numberOfItems": n_cats,
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["title"], "url": SITE_URL + cat_page(s["id"])}
                             for i, s in enumerate(list_secs)]},
        faq_ld(faq),
    ]}

    body = f"""{topbar("index")}
<section class="hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
<p class="kicker">{icon("wrench")} <b>KI-Werkstatt</b> · Link-Check {LINK_CHECK}: {LINK_CHECK_N} Links geprüft</p>
<h1><em>{n_tools} KI-Tools</em> auf Deutsch, sortiert und erklärt</h1>
<p class="slogan">Ohne Zauberstab. Nur gutes Werkzeug.</p>
<p class="sub">Hier gibt es kein Wundermittel, nur gutes Werkzeug: jedes Tool in einem Satz erklärt, tote Links aussortiert, EU-Anbieter markiert. Dazu Werkzeugkisten für typische Jobs und ein Stack-Finder, der schneller zum Punkt kommt als jedes Beratungsgespräch.</p>
<div class="ctas"><a class="btn btn-lime" href="#finder-band">{icon("compass")}Stack-Finder starten</a><a class="btn" href="#kategorien">{icon("layers")}Schubladen öffnen</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
<div class="hero-hm"><div class="hm-fig">{pumpkin()}<button class="hm-btn" type="button" id="hm-hero" aria-label="Hans Moritz antippen: eine Werkstatt-Weisheit hören">{hans("hm-xl", label="")}</button></div><p class="bubble" id="hm-say" aria-live="polite">Moin, ich bin Hans Moritz. Erst prüfen, dann einsortieren.</p></div>
<div class="stats">
<div class="stat reveal"><b data-count="{n_tools}">{n_tools}</b><span>Tools, Links geprüft</span></div>
<div class="stat reveal"><b data-count="{n_cats}">{n_cats}</b><span>Schubladen, {n_subs} Fächer</span></div>
<div class="stat reveal"><b data-count="{n_eu}">{n_eu}</b><span>Anbieter mit EU-Sitz</span></div>
<div class="stat reveal"><b data-count="{n_oss}">{n_oss}</b><span>Open-Source-Tools</span></div>
<div class="stat reveal"><b data-count="{N_STACKS}">{N_STACKS}</b><span>Werkzeugkisten</span></div>
</div>
<div class="wotd" id="wotd"></div></div></section>

<section class="band" id="finder-band"><div class="wrap">
<p class="eyebrow">Stack-Finder</p><h2>Drei Fragen. Dann weißt du, womit du anfängst.</h2>
<p class="intro">Welches Werkzeug? Kommt drauf an, was du baust. Der Finder fragt kurz nach und legt dir sechs bis acht Tools auf die Werkbank. Wenn du magst, schaut Jean danach noch einmal drüber.</p>
<div class="finder reveal" id="finder"><p class="finder-q"></p><div class="opts"></div><div class="finder-result hidden"></div>
<div class="finder-bar"><button type="button" class="btn btn-sm back hidden">{icon("arrow")}Zurück</button><div class="dots"></div><span class="steplbl"></span></div></div>
</div></section>

<section class="band" id="favoriten"><div class="wrap">
<p class="eyebrow">Werkbank-Favoriten</p><h2>Zehn Werkzeuge für den Anfang. Mehr braucht kaum jemand.</h2>
<p class="intro">Wer nur zehn Minuten hat, fängt hier an. Bewusst mit Alternativen aus der EU, weil nicht jeder Schraubenschlüssel aus Kalifornien kommen muss.</p>
<ul class="tools">{featured_html}</ul>
<p class="bridge" data-chrome>{icon("mail")}<span>Dein Fall ist spezieller? <a href="#stack-check">Beim Stack-Check sucht Jean dir 4 bis 6 passende Tools heraus.</a></span></p>
</div></section>

{einsatz_band()}

{neu_band(list_secs)}

{ratgeber_band()}

<section class="band" id="so-arbeiten-wir"><div class="wrap">
<p class="eyebrow">So arbeitet die Werkstatt</p><h2>Sammeln. Prüfen. Sortieren.</h2>
<p class="intro">Kein Tool kommt in die Liste ohne funktionierenden Link und ohne eigene Beschreibung. Tote Links sind keine Tools, sondern Staubfänger.</p>
<div class="steps">
<div class="step reveal"><span class="n">1</span>{icon("search")}<h3>Sammeln</h3><p>Gesammelt wird, was in Projekten, Fachartikeln und Herstellerankündigungen auftaucht, mit besonderem Blick auf den DACH-Raum. Jeder Eintrag bekommt einen deutschen Satz, der sagt, wofür das Tool taugt. Ohne Werbeprosa.</p></div>
<div class="step reveal"><span class="n">2</span>{icon("check")}<h3>Prüfen</h3><p>Jeder Link wird per HTTP abgeklopft. 404, Serverfehler oder Domain weg: ab in die Tonne. Affiliate- und Referral-Parameter bei Tool-Links fliegen auch raus. Nur Links zu PROMPTGOTT tragen UTM-Parameter, damit erkennbar ist, dass der Besuch von hier kam.</p></div>
<div class="step reveal"><span class="n">3</span>{icon("layers")}<h3>Sortieren</h3><p>{n_cats} Schubladen nach Aufgabe, nicht nach Hype. EU-Sitz und Open Source als Badge. Dazu Werkzeugkisten für typische Jobs, damit du nicht alle {n_tools} Tools einzeln anfassen musst.</p></div>
</div>
<aside class="method-box reveal" id="methode"><h3>{icon("ruler")}Was „geprüft“ hier heißt</h3><ul>
<li>{icon("check")}<span><b>Link-Check:</b> Jeder Link wird automatisch abgefragt, zuletzt am {LINK_CHECK}. Ob ein Tool gut ist, sagt das noch nicht.</span></li>
<li>{icon("check")}<span><b>Beschreibung:</b> Jede ist von Hand auf Deutsch geschrieben und an der Herstellerseite abgeglichen.</span></li>
<li>{icon("x")}<span><b>Kein Praxistest:</b> Nicht jedes Tool wurde ausprobiert. EU-Sitz und Open Source stehen so da, wie die Anbieter sie angeben.</span></li>
<li>{icon("user")}<span><b>Entstehung:</b> Recherche und Entwürfe laufen mit KI-Unterstützung, jede Seite prüft und verantwortet ein Mensch. Mehr im <a href="impressum.html#werkstatt">Impressum</a>.</span></li>
</ul></aside></div></section>

<section class="band" id="werkzeugkisten"><div class="wrap">
<p class="eyebrow">Werkzeugkisten</p><h2>Fertig gepackte Kisten für typische Jobs</h2>
<p class="intro">{N_STACKS} Kisten mit je {STACK_SIZE_TXT} Tools, die zusammenpassen, und einem Satz, warum jedes drin liegt. Nimm die Kiste als Startpunkt, nicht als Bauanleitung.</p>
<div class="stacks">{stacks_html}</div>
<p class="bridge" data-chrome>{icon("mail")}<span>Keine Kiste passt? <a href="#stack-check">Dann packt Jean dir beim Stack-Check eine eigene.</a></span></p>
</div></section>

{rechner_band()}

<section class="band" id="kategorien"><div class="wrap">
<p class="eyebrow">Die Schubladen</p><h2>{n_cats} Schubladen, {n_tools} Tools, eine Werkstatt</h2>
<p class="intro">Jede Schublade hat eine eigene Seite mit allen Tools, einem Werkstatt-Tipp und Antworten auf die Fragen, die uns am häufigsten gestellt werden. Such dir eine aus oder tipp oben ins Suchfeld, was du vorhast.</p>
<p class="sp-filters"><button type="button" class="btn btn-sm" data-sp="eu">{icon("globe")}Alle {n_eu} EU-Anbieter zeigen</button><button type="button" class="btn btn-sm" data-sp="oss">{icon("code")}Alle {n_oss} Open-Source-Tools zeigen</button>{f'<button type="button" class="btn btn-sm" data-sp="neu">{icon("plus")}Alle {len(NEU_AKTIV)} Neuzugänge zeigen</button>' if NEU_AKTIV else ""}</p>
<div class="drawers">{"".join(drawers)}
<a class="drawer drawer-gl reveal" href="{GLOSSAR_PAGE}"><span class="drawer-art gl-art">{icon("abc")}</span><span class="drawer-body"><span class="drawer-no">Nachschlagen</span><b class="drawer-title">{icon("book")}KI-Glossar</b>
<span class="drawer-teaser">Token, RAG, Halluzination: {len(GLOSSAR["begriffe"])} Begriffe, jeder mit ernster Erklärung und einer Werkstatt-Übersetzung zum Merken.</span>
<span class="drawer-cta">Glossar aufschlagen{icon("arrow")}</span></span></a></div>
</div></section>

<section class="band pg" id="promptgott"><div class="wrap">
<p class="eyebrow">PROMPTGOTT Deep Dives</p><h2>Werkzeug ist das eine. Systeme bauen das andere.</h2>
<p class="intro">{inline(pg_intro)}</p>
<div class="pg-grid">{pg_cards}</div>
<p style="margin-top:24px"><a class="btn btn-pg" href="{html.escape(pg_sub("pg-band"))}" target="_blank" rel="noopener">{icon("flame")}PROMPTGOTT abonnieren</a></p>
</div></section>

<section class="band faq" id="faq"><div class="wrap">
<p class="eyebrow">Fragen an der Werkbank</p><h2>Was Leute uns am Tresen fragen</h2>
<div class="faq-list">{faq_html(faq)}</div>
</div></section>

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>Sag, was du baust. Jean legt dir das Werkzeug hin.</h2>
<p class="intro">{html.escape(BRAND["lead_offer"]["promise"])}</p>
<ul>
<li>{icon("check")}<span><b>Was du bekommst:</b> 4 bis 6 Tools, die zu deinem Fall passen, mit je einem Satz, warum.</span></li>
<li>{icon("check")}<span><b>Was es kostet:</b> zwei Minuten fürs Formular. Kein Vertrag, kein Pitch.</span></li>
<li>{icon("check")}<span><b>Was wir nicht versprechen:</b> Preise oder DSGVO-Freigaben. Die prüfst du beim Anbieter.</span></li>
<li>{icon("shield")}<span><b>Deine Daten:</b> gehen über den Formulardienst FormSubmit (speichert Einsendungen 30 Tage) per E-Mail an Jean. Kein CRM, keine Liste. <a href="datenschutz.html">Details</a>.</span></li>
</ul>
<div class="kb-say hm-say">{hans("hm-md")}{kurbel("kb-sm", wink=True)}<p class="bubble">Ich sortier vor, Jean sucht aus. Kurbel hält so lange die Schraube fest.</p></div></div>
<div>{lead_form("Hauptformular", "Stack-Check – KI-Werkstatt")}</div></div>
</div></section>

{footer()}
<script type="application/json" id="kw-finder">{finder_js}</script>
"""
    ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    extra = f'<script type="application/ld+json">{ld_js}</script>'
    (DOCS / "index.html").write_text(page_shell(TITLE, body, extra_head=extra), encoding="utf-8")
    return uniq, n_tools, n_cats, list_secs, tools_map


def build_subpages(list_secs=()):
    # Danke-Seite je Formular: ?typ=check (Stack-Check) oder ?typ=finder (Stack-Finder); app.js blendet die passende Fassung ein
    danke = f"""{topbar("sub")}
<div class="page page-kb page-danke"><div class="kb-say kb-hero duo">{hans("hm-lg", label="Hans Moritz zeigt den Daumen hoch", thumb=True)}{kurbel("kb-md", wink=True)}<p class="bubble">Angekommen! Kurbel sortiert so lange die Schrauben, ich setz schon mal Kaffee auf.</p></div>
<p class="eyebrow">Angekommen</p>
<div data-typ="check"><h1>Danke. Deine Anfrage liegt auf der Werkbank.</h1>
<ol class="steps-mini"><li><b class="n">1</b><span>Jean liest deine Nachricht selbst, kein Bot und kein Callcenter.</span></li><li><b class="n">2</b><span>Danach legt Jean dir die Werkzeuge hin, die zu deinem Fall passen, mit je einem Satz, warum.</span></li><li><b class="n">3</b><span>Die Antwort kommt per E-Mail, ohne Verkaufsgespräch und ohne Kleingedrucktes.</span></li></ol></div>
<div data-typ="finder" hidden><h1>Danke. Jean schaut jetzt über dein Setup.</h1>
<ol class="steps-mini"><li><b class="n">1</b><span>Jean liest deine drei Antworten und die Tools, die der Finder dir vorgeschlagen hat.</span></li><li><b class="n">2</b><span>Was nicht zu deinem Fall passt, fliegt raus, und an seine Stelle kommt etwas Passenderes mit Begründung.</span></li><li><b class="n">3</b><span>Das überarbeitete Setup bekommst du per E-Mail, ohne Pitch und ohne Abo.</span></li></ol></div>
<p>Meist dauert das nur wenige Tage. Hörst du nichts, wirf einen Blick in den Spam-Ordner, manchmal versteckt sich die Post dort. Oder schreib direkt an {mail_link()}.</p>
{pg_box("danke")}
<p class="danke-more"><a class="btn" href="./#werkzeugkisten">{icon("layers")}Werkzeugkisten ansehen</a> <a class="btn" href="tools.csv" download>{icon("download")}Die Liste als CSV laden</a></p>
<p><a href="./">Zurück in die Werkstatt</a></p></div>
{footer(bar=False)}"""
    (DOCS / "danke.html").write_text(page_shell("Danke – KI-Werkstatt", danke, "Anfrage angekommen.", SITE_URL + "danke.html", '<meta name="robots" content="noindex">'), encoding="utf-8")

    # 404: GitHub Pages liefert docs/404.html für jede unbekannte Adresse aus, deshalb absolute Pfade
    base = urlparse(SITE_URL).path or "/"
    chips = "".join(f'<a class="chip" href="{cat_page(s["id"])}">{icon(CAT_ICON.get(s["id"], "box"))}{html.escape(cat_h1(s))}</a>' for s in list_secs)
    nf = f"""{topbar("sub")}
<div class="page page-kb"><div class="kb-say kb-hero">{kurbel("kb-lg")}<p class="bubble">Eine Schraube hab ich gefunden. Die Seite nicht.</p></div>
<p class="eyebrow">Fehler 404</p><h1>Diese Schublade gibt es nicht.</h1>
<p>Kurbel hat überall nachgesehen, sogar unter der Werkbank und hinter dem Kaffeeautomaten. Vielleicht hat sich die Adresse verschraubt, vielleicht ist die Seite umgezogen.</p>
<p>Von hier aus kommst du sicher weiter:</p>
<div class="chips nf-chips" data-chrome><a class="chip cat" href="./">{icon("wrench")}Startseite</a><a class="chip cat" href="{RATGEBER_PAGE}">{icon("book")}Alle Ratgeber</a><a class="chip cat" href="{EINSATZ_PAGE}">{icon("layers")}Alle Einsatzgebiete</a><a class="chip cat" href="{TRENDS_PAGE}">{icon("chart")}KI-Trends</a><a class="chip" href="{GLOSSAR_PAGE}">{icon("abc")}KI-Glossar</a>{chips}</div>
<p style="margin-top:22px"><a class="btn btn-lime" href="./#stack-check">{icon("mail")}Stack-Check anfragen</a> <button type="button" class="btn" id="surprise-btn" hidden>{icon("dice")}Überrasch mich mit einem Tool</button></p>
<div class="surprise wotd" id="surprise" hidden></div></div>
{footer(bar=False)}"""
    (DOCS / "404.html").write_text(absolutize(page_shell("Schublade nicht gefunden – KI-Werkstatt", nf, "Diese Seite gibt es nicht.", SITE_URL + "404.html",
                                                         '<meta name="robots" content="noindex">'), base), encoding="utf-8")

    needs = ('<p class="needs"><b>[NEEDS_REVIEW]</b> Platzhalter: Name und Anschrift fehlen noch. Wer eine Seite mit Kontaktformular '
             'und geschäftlichem Zweck betreibt, braucht in Deutschland ein vollständiges Impressum nach § 5 DDG.</p>')
    needs_ds = ('<p class="needs"><b>[NEEDS_REVIEW]</b> Entwurf, vor dem Bewerben der Seite rechtlich prüfen lassen. Die Informationspflichten '
                'nach Art. 13 DSGVO gelten ab dem ersten Formular, das Daten einsammelt.</p>')
    impressum = f"""{topbar("sub")}
<div class="page legal"><p class="eyebrow">Rechtliches</p><h1>Impressum</h1>{needs}
<p><b>Angaben gemäß § 5 DDG</b><br>[NAME, VORNAME]<br>[STRASSE, HAUSNUMMER]<br>[PLZ, ORT]<br>Deutschland</p>
<p id="kontakt"><b>Kontakt</b><br>E-Mail: {mail_link()}<br>[TELEFON, optional]</p>
<p><b>Verantwortlich für den Inhalt</b> nach § 18 Abs. 2 MStV: [NAME, ANSCHRIFT wie oben]</p>
<p><b>Umsatzsteuer</b>: [USt-IdNr., falls vorhanden, sonst Zeile löschen]</p>
<h2 id="werkstatt">So entsteht die KI-Werkstatt</h2>
<p>Recherche und Textentwürfe entstehen mit KI-Unterstützung. Vor der Veröffentlichung wird jede Seite von einem Menschen geprüft und redaktionell verantwortet.</p>
<p>„Geprüft“ heißt bei der Tool-Liste: Ein Skript fragt jeden Link regelmäßig ab, zuletzt am {LINK_CHECK}, und jede Beschreibung ist von Hand geschrieben. Ausprobiert wurde nicht jedes Tool. Angaben zu EU-Sitz und Open Source stammen von den Anbietern.</p>
<h2>Unabhängigkeit und Werbung</h2>
<p>Die Liste enthält keine Affiliate-Links und keine bezahlten Platzierungen; für eine Nennung fließt kein Geld. Die KI-Werkstatt steht mit keinem der genannten Anbieter in Verbindung. Links zu PROMPTGOTT (Substack) tragen UTM-Parameter, damit dort erkennbar ist, dass der Besuch von hier kam. <b>[NEEDS_REVIEW: Verhältnis zu PROMPTGOTT bestätigen, etwa „PROMPTGOTT ist Jeans eigener Newsletter; Links dorthin sind Eigenwerbung.“]</b> Kommt später ein bezahlter oder Affiliate-Link dazu, wird er einzeln und sichtbar als Anzeige oder Affiliate-Link gekennzeichnet.</p>
<h2>Haftung für Links</h2>
<p>Die Liste verlinkt externe Websites, auf deren Inhalte wir keinen Einfluss haben; verantwortlich ist der jeweilige Anbieter. Regelmäßig geprüft wird nur, ob ein Link erreichbar ist, nicht was dahinter steht. Bei der Verlinkung waren keine Rechtsverstöße erkennbar. Wird uns eine Rechtsverletzung bekannt, entfernen wir den Link umgehend. Hinweise bitte an {mail_link("Hinweis auf einen Link")}.</p>
<h2>Marken, Logos und Schriften</h2>
<p>Tool-Namen und -Logos dienen nur dazu, das jeweilige Produkt zu bezeichnen. Marken und Logos gehören ihren Inhabern. Die Logos sind die Favicons der Anbieter: einmalig abgerufen, klein skaliert und als Kopie auf dieser Seite abgelegt. Fehlt eines, steht an seiner Stelle der Anfangsbuchstabe. Wer als Inhaber sein Logo hier nicht sehen möchte, schreibt eine E-Mail, dann wird es entfernt.</p>
<p>Die Schriften IBM Plex (IBM Corp.) und Space Grotesk (Florian Karsten) stehen unter der SIL Open Font License 1.1; die Lizenztexte liegen unter <a href="assets/fonts/LICENSE-IBM-Plex.txt">assets/fonts/LICENSE-IBM-Plex.txt</a> und <a href="assets/fonts/LICENSE-Space-Grotesk.txt">assets/fonts/LICENSE-Space-Grotesk.txt</a>. Die Vorlage der Liste steht unter der <a href="{REPO_URL}/blob/main/LICENSE" target="_blank" rel="noopener">MIT-Lizenz</a>.</p>
<p><a href="{SITE_URL}">Zurück zur Werkstatt</a></p></div>
{footer(bar=False)}"""
    (DOCS / "impressum.html").write_text(page_shell("Impressum – KI-Werkstatt", impressum, "Impressum der KI-Werkstatt.", SITE_URL + "impressum.html", '<meta name="robots" content="noindex">'), encoding="utf-8")

    # Browser-Speicher: vollständige Liste der Schlüssel aus docs/assets/app.js (store.set/get); bei neuen Schlüsseln hier ergänzen
    speicher = [
        ("kw-theme", "helles oder dunkles Farbschema, sobald du umschaltest"),
        ("kw-bar", "dass du die Leiste am unteren Rand geschlossen hast"),
        ("kw-merk", "deine Merkliste: Name und Link der Tools, die du mit dem Lesezeichen markierst"),
        ("kw-merk-attach", "ob die Merkliste an das Stack-Check-Formular angehängt werden soll"),
        ("kw-screws", "welche Schrauben du bei Kurbels Schraubensuche schon gefunden hast"),
        ("kw-read:<Seite>", "bis zu welchem Kapitel du einen Ratgeber gelesen hast, nur wenn du „Lesefortschritt merken“ einschaltest"),
        ("kw-hilf:<Seite>", "deine Antwort auf „War das hilfreich?“ unter einem Ratgeber"),
    ]
    app_keys = set(re.findall(r'"(kw-[a-z-]+)', (ASSETS / "app.js").read_text(encoding="utf-8"))) - {"kw-finder", "kw-radar", "kw-toast"}
    listed = {k.split(":")[0].rstrip(":") for k, _ in speicher}
    if {k.rstrip(":") for k in app_keys} != listed:
        raise SystemExit(f"datenschutz.html: Speicher-Liste passt nicht zu app.js (app.js: {sorted(app_keys)}, Liste: {sorted(listed)})")
    speicher_html = "".join(f"<li><code>{html.escape(k)}</code>: {html.escape(t)}.</li>" for k, t in speicher)
    gh_privacy = "https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement"
    ds = f"""{topbar("sub")}
<div class="page legal"><p class="eyebrow">Rechtliches</p><h1>Datenschutz</h1>{needs_ds}
<p><b>Verantwortlicher:</b> [NAME, ANSCHRIFT wie im Impressum], E-Mail: {mail_link("Datenschutz")}</p>
<p class="ds-kurz">Kurz gesagt: keine Cookies, kein Tracking, keine Analyse-Tools, keine fremden Skripte, Schriften oder Bilder. Persönliche Angaben verlassen deinen Browser nur, wenn du ein Formular abschickst.</p>
<h2>Hosting (GitHub Pages)</h2>
<p>Die Seite wird über GitHub Pages ausgeliefert (GitHub, Inc., USA). Beim Aufruf verarbeitet GitHub technisch notwendige Daten wie IP-Adresse, Zeitpunkt und aufgerufene Adresse, um die Seite auszuliefern und vor Angriffen zu schützen. Wie lange GitHub diese Protokolle aufbewahrt, legt GitHub fest (<a href="{gh_privacy}" target="_blank" rel="noopener">GitHub-Datenschutzerklärung</a>). Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO, das berechtigte Interesse an einer sicheren Auslieferung der Seite.</p>
<p>GitHub gibt in dieser Datenschutzerklärung an, nach dem EU-US Data Privacy Framework zertifiziert zu sein. Die Übermittlung in die USA stützt sich damit auf den Angemessenheitsbeschluss der EU-Kommission (Art. 45 DSGVO).</p>
<h2>Stack-Check und Stack-Finder (Formulare)</h2>
<p>Ob du ein Formular ausfüllst, entscheidest du; ohne E-Mail-Adresse kann Jean allerdings nicht antworten. Schickst du es ab, gehen deine Angaben über den Formulardienst FormSubmit (formsubmit.co) per E-Mail an Jean: deine E-Mail-Adresse und dein Text, dazu Name, Website und Rolle, falls du sie ausfüllst. Hängst du Merkliste, Rechner-Ergebnis oder Trend-Radar an, gehen auch diese mit, beim Stack-Finder außerdem deine drei Antworten und der Vorschlag.</p>
<p>Automatisch steht in jeder Anfrage, über welches Formular und von welcher Seite der KI-Werkstatt sie kam und welche Seite du davor aufgerufen hattest; kamst du von einer fremden Website, steht dort nur deren Domain. Diese Angabe liest das Formular erst beim Absenden aus deinem Browser (Referrer) und speichert sie nirgends.</p>
<p>Zweck ist die Antwort auf deine Anfrage, Rechtsgrundlage Art. 6 Abs. 1 lit. b DSGVO. Die Angaben landen in keinem CRM und keinem Newsletter. Gelöscht wird eine Anfrage, sobald sie erledigt ist und keine gesetzliche Aufbewahrungspflicht entgegensteht. <b>[NEEDS_REVIEW: feste Höchstfrist festlegen, zum Beispiel 12 Monate]</b></p>
<p>FormSubmit leitet die Daten per E-Mail weiter und speichert Einsendungen nach eigenen Angaben 30 Tage in einem Archiv (<a href="https://formsubmit.co/documentation" target="_blank" rel="noopener">Dokumentation</a>, <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener">Datenschutzhinweise von FormSubmit</a>). Diese Datenschutzhinweise nennen keinen Firmensitz. Dass die Daten dabei in ein Land ohne gleichwertiges Datenschutzniveau wie die USA gelangen, ist deshalb nicht auszuschließen. Dafür holt das Formular mit dem Häkchen deine ausdrückliche Einwilligung ein (Art. 49 Abs. 1 lit. a DSGVO); du kannst sie jederzeit per E-Mail widerrufen. Das Empfangspostfach ist ein Gmail-Konto (Google). <b>[NEEDS_REVIEW: Formulardienst und Postfach festlegen, Auftragsverarbeitungsvertrag klären, dann Empfänger, Sitz und Übermittlungsgrundlage hier eintragen]</b></p>
<p>Antwortet FormSubmit nicht oder lehnt die Anfrage ab, bietet das Formular an, sie über dein eigenes E-Mail-Programm zu senden. Deine Angaben können zu diesem Zeitpunkt schon bei FormSubmit angekommen sein; auf dem E-Mail-Weg gehen sie außerdem über deinen E-Mail-Anbieter.</p>
<h2>Tool-Logos</h2>
<p>Die kleinen Logos neben den Tools sind Favicons der Anbieter. Sie wurden einmalig beim Erstellen der Seite abgerufen und liegen als Kopie auf diesem Server. Dein Browser fragt deshalb beim Besuch weder die Anbieter noch einen Icon-Dienst an.</p>
<h2>Speicher in deinem Browser</h2>
<p>Schriften und Skripte liegen auf dieser Seite selbst; Google Fonts oder andere fremde Server werden nicht angefragt. Im Browser-Speicher (localStorage) deines Geräts legt die Seite nur ab, was du selbst auslöst, und zwar unter diesen Schlüsseln:</p>
<ul class="plain">{speicher_html}</ul>
<p>Diese Einträge verlassen dein Gerät nicht. Rechtsgrundlage ist § 25 Abs. 2 Nr. 2 TDDDG, weil du die jeweilige Funktion selbst anforderst. Löschen kannst du sie jederzeit über die Website-Daten deines Browsers, Merkliste und Lesestand auch direkt auf der Seite. Zeitspar-Rechner und Trend-Radar rechnen nur in deinem Browser und speichern nichts. Merkliste, Rechner-Ergebnis und Radar bekommt Jean nur, wenn du sie an das Stack-Check-Formular hängst und es abschickst.</p>
<h2>Externe Links</h2>
<p>Links zu Tools, zu PROMPTGOTT (Substack) und zu GitHub führen auf fremde Seiten mit eigenen Datenschutzregeln. Links zu PROMPTGOTT enthalten UTM-Parameter, damit erkennbar ist, dass der Besuch von dieser Seite kam; persönliche Daten werden dabei nicht übertragen.</p>
<h2>Deine Rechte</h2>
<p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung und Datenübertragbarkeit (Art. 15 bis 20 DSGVO) und kannst dich bei einer Datenschutz-Aufsichtsbehörde beschweren (Art. 77 DSGVO). Eine Einwilligung kannst du jederzeit mit Wirkung für die Zukunft widerrufen (Art. 7 Abs. 3 DSGVO). Schreib dafür an {mail_link("Datenschutz")}.</p>
<p class="ds-widerspruch"><b>Widerspruchsrecht nach Art. 21 DSGVO:</b> Verarbeitungen auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO, hier die Auslieferung der Seite über GitHub, kannst du jederzeit aus Gründen widersprechen, die sich aus deiner besonderen Situation ergeben.</p>
<p><a href="{SITE_URL}">Zurück zur Werkstatt</a></p></div>
{footer(bar=False)}"""
    (DOCS / "datenschutz.html").write_text(page_shell("Datenschutz – KI-Werkstatt", ds, "Datenschutzerklärung der KI-Werkstatt.", SITE_URL + "datenschutz.html", '<meta name="robots" content="noindex">'), encoding="utf-8")


# --------------------------------------------------------------------------- Zeitspar-Rechner
def fmt_pct(v):
    return f"{v} %"


def rechner_band():
    rows = []
    for a in RECHNER["aufgaben"]:
        src = (f' <a href="{html.escape(check_url(a["url"], "data/rechner.json"))}" target="_blank" rel="noopener">Quelle: {html.escape(a["quelle"])}</a>' if a["url"] else "")
        # Weitere Quellen, z. B. ein Gegenbefund: "weitere_quellen": [["Beschriftung", "https://…"], …]
        src += "".join(f' · <a href="{html.escape(check_url(u, "data/rechner.json/" + a["id"]))}" target="_blank" rel="noopener">{html.escape(lbl)}</a>'
                       for lbl, u in a.get("weitere_quellen", []))
        cat = (f' <a href="{cat_page(a["kategorie"])}">Passende Tools</a>' if a.get("kategorie") else "")
        rows.append(f"""<div class="calc-row reveal" data-id="{a['id']}" data-label="{html.escape(a['label'])}">
<div class="calc-head"><span class="calc-ico">{icon(a["icon"])}</span><b>{html.escape(a["label"])}</b></div>
<div class="calc-in"><div><label for="c-h-{a['id']}">Stunden pro Woche<span class="sr"> für {html.escape(a["label"])}</span></label><input type="number" id="c-h-{a['id']}" class="c-h" min="0" max="60" step="0.5" value="{a['stunden']}" inputmode="decimal"></div>
<div><label for="c-p-{a['id']}">Ersparnis<span class="sr"> bei {html.escape(a["label"])}</span>: <output id="c-po-{a['id']}" for="c-p-{a['id']}">{fmt_pct(a['prozent'])}</output></label><input type="range" id="c-p-{a['id']}" class="c-p" min="0" max="60" step="1" value="{a['prozent']}"></div></div>
<div class="calc-bar" aria-hidden="true"><div class="track"><i></i></div><span></span></div>
<p class="calc-src">{html.escape(a["befund"])}{src}{cat}</p></div>""")
    return f"""<section class="band" id="rechner"><div class="wrap">
<p class="eyebrow">Zeitspar-Rechner</p><h2>Wie viel Feierabend steckt in deiner Woche?</h2>
<p class="intro">Trag ein, wie viele Stunden du pro Woche mit diesen Aufgaben verbringst. Jeder Regler startet bei ungefähr der Hälfte des Werts aus einer Studie, die Quelle steht jeweils darunter. Gerechnet wird nur in deinem Browser, wir gucken nicht mit.</p>
<p class="nojs">Der Rechner braucht JavaScript. Ohne JavaScript siehst du hier die Studienwerte.</p>
<div class="calc" id="calc" data-wochen="{RECHNER['wochen']}">
<div class="calc-rows">{"".join(rows)}</div>
<aside class="calc-out"><div class="in">
<p class="eyebrow">Dein Ergebnis</p>
<div class="calc-ring"><svg viewBox="0 0 120 120" aria-hidden="true"><circle class="bg" cx="60" cy="60" r="50"/><circle class="fg" cx="60" cy="60" r="50" pathLength="100" stroke-dasharray="0 100"/></svg><div><b id="c-share">0 %</b><small>deiner Stunden</small></div></div>
<p class="sr" id="c-live" aria-live="polite" aria-atomic="true"></p>
<dl><div><dt>pro Woche</dt><dd id="c-week">0 h</dd></div><div><dt>pro Jahr</dt><dd id="c-year">0 h</dd></div><div><dt>Gegenwert</dt><dd id="c-eur">0 €</dd></div></dl>
<label for="c-rate">Dein Stundensatz in Euro</label><input type="number" id="c-rate" min="0" max="1000" step="5" value="{RECHNER['stundensatz']}" inputmode="decimal">
<p class="calc-note">{html.escape(RECHNER["wochen_hinweis"])}</p>
<button type="button" class="btn btn-lime" id="c-send">{icon("mail")}Mit diesen Zahlen zum Stack-Check</button>
</div></aside></div>
<p class="calc-method">{icon("ruler")} {html.escape(RECHNER["methode"])}</p>
</div></section>"""


# --------------------------------------------------------------------------- Kategorie-Seiten
def sec_items(sec):
    seen = {}
    for _, _, it in all_items([sec]):
        seen.setdefault(it["url"], it)
    return list(seen.values())


def breadcrumb_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": url} for i, (name, url) in enumerate(trail)]}


def crumbs(*trail):
    """Brotkrümel aus einer Liste (Name, Seite); "" ist die Startseite, der letzte Eintrag die aktuelle Seite.
    Liefert sichtbares HTML und BreadcrumbList aus derselben Liste, damit beides nie auseinanderläuft.
    Jede Zwischenebene ist eine eigene URL, nie ein Anker der Startseite."""
    trail = (("KI-Werkstatt", ""),) + trail
    for name, page in trail[:-1]:
        if "#" in page:
            raise SystemExit(f"crumbs: Zwischenebene {name!r} zeigt auf einen Anker ({page}), braucht eine eigene Seite")
    parts = [f'<a href="{page or "./"}">{html.escape(name)}</a>' for name, page in trail[:-1]]
    parts.append(f'<span aria-current="page">{html.escape(trail[-1][0])}</span>')
    nav = f'<nav class="crumbs" aria-label="Brotkrümel">{icon("arrow").join(parts)}</nav>'
    return nav, breadcrumb_ld([(name, SITE_URL + page) for name, page in trail])


def tool_chip(name, tools_map):
    """Tool-Chip: führt in die Schublade zum Tool (Einordnung, Badges, Merkliste), das kleine Pfeil-Symbol direkt zum Anbieter."""
    t = tools_map[name]
    neu = NEU_BADGE if name in NEU_NAMES else ""
    home = NAV["home"].get(name)
    if not home:
        return f'<a class="chip tool" href="{html.escape(t["u"])}" target="_blank" rel="noopener">{favicon(t["u"])}{html.escape(name)}{neu}</a>'
    return (f'<span class="chip tool"><a href="{html.escape(home)}">{favicon(t["u"])}{html.escape(name)}{neu}</a>'
            f'<a class="chip-ext" href="{html.escape(t["u"])}" target="_blank" rel="noopener" title="Zum Anbieter" '
            f'aria-label="{html.escape(name)} beim Anbieter öffnen (neues Fenster)">{icon("arrow")}</a></span>')


def cat_chip(sec_id):
    sec = next(s for s in NAV["secs"] if s["id"] == sec_id)
    return f'<a class="chip cat" href="{cat_page(sec_id)}">{icon(CAT_ICON.get(sec_id, "layers"))}{html.escape(cat_h1(sec))}</a>'


def secs_for_tools(names, limit=3):
    """Schubladen, in denen die meisten dieser Tools liegen (Reihenfolge: Trefferzahl, dann Schubladen-Folge)."""
    order = [s["id"] for s in NAV["secs"]]
    hits = {}
    for n in names:
        sid = NAV["sec"].get(n)
        if sid:
            hits[sid] = hits.get(sid, 0) + 1
    return sorted(hits, key=lambda sid: (-hits[sid], order.index(sid)))[:limit]


def build_category_pages(list_secs, tools_map):
    pages = []
    terms_by_cat = {}
    for g in GLOSSAR["begriffe"]:
        if g.get("cat"):
            terms_by_cat.setdefault(g["cat"], []).append(g)
    for idx, sec in enumerate(list_secs):
        its = sec_items(sec)
        n = len(its)
        n_eu = sum(1 for it in its if item_meta(it)[0])
        n_oss = sum(1 for it in its if item_meta(it)[1])
        urls = {it["url"] for it in its}
        h1 = cat_h1(sec)
        page = cat_page(sec["id"])
        desc = kat_text(sec, "meta")
        faq = [tuple(x) for x in kat_text(sec, "faq")]
        # Werkzeugkisten nur als Verweis: die ausführliche Kiste steht einmal, auf der Startseite
        ranked = []
        for st in STACKS["stacks"]:
            hits = [name for name, _ in st["tools"] if tools_map.get(name, {}).get("u") in urls]
            if len(hits) >= 2:
                ranked.append((len(hits), st, hits))
        ranked.sort(key=lambda x: -x[0])
        refs = []
        for cnt, st, hits in ranked[:3]:
            names = ", ".join(hits[:-1]) + " und " + hits[-1]
            refs.append(f'<a class="kiste-ref reveal" href="./#kiste-{st["id"]}">{icon(st["icon"])}<span><b>{html.escape(st["title"])}</b>'
                        f'<small>{cnt} von {len(st["tools"])} Tools liegen in dieser Schublade: {html.escape(names)}.</small></span>{icon("arrow")}</a>')
        stacks_html = (f"""<section class="band" id="werkzeugkisten"><div class="wrap">
<p class="eyebrow">Passende Werkzeugkisten</p><h2>Kisten mit Werkzeug aus „{html.escape(sec["title"])}“</h2>
<div class="kisten-refs">{"".join(refs)}</div></div></section>""") if refs else ""
        terms = terms_by_cat.get(sec["id"], [])
        terms_html = "".join(f'<a class="chip" href="{GLOSSAR_PAGE}#{slug(g["t"])}">{icon(g["icon"])}{html.escape(g["t"])}</a>' for g in terms)
        side = []
        if any(a.get("kategorie") == sec["id"] for a in RECHNER["aufgaben"]):
            side.append(f'<div class="side-card reveal">{icon("clock")}<b>Wie viel Zeit spart das?</b><a class="btn btn-sm" href="./#rechner">{icon("calc")}Zum Zeitspar-Rechner</a></div>')
        if terms:
            side.append(f'<div class="side-card reveal">{icon("abc")}<b>Begriffe zu dieser Schublade</b><div class="chips">{terms_html}</div></div>')
        # Rückverweise aus vorhandenen Daten: Ratgeber, deren Tools hier liegen; Einsatzgebiete, die diese Schublade nennen
        rg_hits = sorted(((sum(NAV["sec"].get(n) == sec["id"] for n in a["tools"]), i, a) for i, a in enumerate(RATGEBER["artikel"])), key=lambda x: (-x[0], x[1]))
        rg_rel = [a for cnt, _, a in rg_hits if cnt][:3]
        if rg_rel:
            side.append(f'<div class="side-card reveal">{icon("book")}<b>Ratgeber dazu</b><div class="chips" data-chrome>'
                        + "".join(f'<a class="chip cat" href="{a["page"]}">{icon(a["icon"])}{html.escape(a["label"])}</a>' for a in rg_rel) + "</div></div>")
        ei_rel = [e for e in EINSATZ["seiten"] if sec["id"] in e["kategorien"]]
        if ei_rel:
            side.append(f'<div class="side-card reveal">{icon("layers")}<b>Dazu im Einsatz</b><div class="chips" data-chrome>'
                        + "".join(f'<a class="chip cat" href="{e["page"]}">{icon(e["icon"])}{html.escape(e["h1"])}</a>' for e in ei_rel) + "</div></div>")
        rail_links = "".join(f'<a href="#{sub["id"]}">{icon(SUB_ICON.get(sub["id"], "layers"))}{html.escape(sub["title"])}</a>' for sub in sec["subs"]) \
            or f'<a href="#{sec["id"]}">{icon(CAT_ICON.get(sec["id"], "box"))}Alle Tools</a>'
        if side:
            rail_links += f'<a href="#mehr">{icon("book")}Mehr zum Thema</a>'
        rail_links += f'<a href="#faq">{icon("chat")}Fragen</a>'
        if refs:
            rail_links += f'<a href="#werkzeugkisten">{icon("layers")}Werkzeugkisten</a>'
        rail_links += f'<a href="#stack-check">{icon("mail")}Stack-Check</a>'
        others = []
        for j, o in enumerate(list_secs):
            if o is sec:
                continue
            others.append(f'<a class="cat-tile reveal" href="{cat_page(o["id"])}"><img src="img/cat-{o["id"]}.svg" alt="" loading="lazy">'
                          f'<span class="t">{html.escape(cat_h1(o))}<small>Schublade {j + 1:02d} · {len(sec_items(o))} Tools</small></span></a>')
        section_html = render_section(sec, idx + 1, {}, cat_page_mode=True)
        crumb_html, crumb_ld = crumbs((sec["title"], page))
        intro_html = "".join(f"<p>{html.escape(x)}</p>" for x in kat_text(sec, "intro"))
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "CollectionPage", "@id": SITE_URL + page, "url": SITE_URL + page, "name": h1, "description": desc, "inLanguage": "de-DE",
             "isPartOf": {"@type": "WebSite", "name": "KI-Werkstatt", "url": SITE_URL}},
            crumb_ld,
            {"@type": "ItemList", "name": h1, "numberOfItems": n,
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": it["name"], "url": it["url"], "description": item_meta(it)[2]}
                                 for i, it in enumerate(its)]},
            faq_ld(faq),
        ]}
        ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
        first = sec["subs"][0]["id"] if sec["subs"] else sec["id"]
        body = f"""{topbar("kategorien")}
<section class="hero cat-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumb_html}
<div class="cat-hero-grid"><div>
<p class="kicker">{icon(CAT_ICON.get(sec["id"], "box"))} <b>Schublade {idx + 1:02d}</b> · Link-Check {LINK_CHECK}</p>
<h1><em>{html.escape(h1)}</em></h1>
<p class="sub">{html.escape(kat_text(sec, "hero"))}</p>
<div class="ctas"><a class="btn btn-lime" href="#{first}">{icon("layers")}Zu den {n} Tools</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
</div><div class="cat-hero-art reveal"><img src="img/cat-{sec["id"]}.svg" alt="" width="800" height="300"></div></div>
<div class="stats">
<div class="stat reveal"><b data-count="{n}">{n}</b><span>Tools in dieser Schublade</span></div>
<div class="stat reveal"><b data-count="{max(1, len(sec["subs"]))}">{max(1, len(sec["subs"]))}</b><span>{"Fächer" if len(sec["subs"]) > 1 else "Fach"}</span></div>
<div class="stat reveal"><b data-count="{n_eu}">{n_eu}</b><span>mit EU-Sitz</span></div>
<div class="stat reveal"><b data-count="{n_oss}">{n_oss}</b><span>Open Source</span></div>
</div></div></section>

<section class="band cat-intro"><div class="wrap intro-grid">
<div class="intro-text reveal">{intro_html}</div>
<aside class="tipp reveal">{kurbel("kb-sm", wink=True)}<p class="eyebrow">Werkstatt-Tipp</p><p>{html.escape(kat_text(sec, "tipp"))}</p></aside>
</div></section>

<div class="wrap layout" id="liste">
<nav class="rail" aria-label="Auf dieser Seite" data-chrome><div class="in"><p class="rail-h">Auf dieser Seite</p>{rail_links}
<div class="lead-mini"><p>Kostet nichts außer zwei Minuten.</p><a class="btn btn-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div></div></nav>
<div class="content"><div class="filters" role="search" aria-label="In dieser Schublade filtern"><label class="lq"><span class="sr">In dieser Schublade filtern</span><input type="search" id="lq" placeholder="In dieser Schublade filtern …" autocomplete="off"></label>
<label><input type="checkbox" class="f-eu"> nur EU-Anbieter</label><label><input type="checkbox" class="f-oss"> nur Open Source</label><span id="lcount" aria-live="polite"></span>
<p class="lq-empty" hidden>{icon("search")}<span>In dieser Schublade passt nichts.</span><button type="button" class="btn btn-sm btn-lime" id="lq-all">{icon("search")}In allen Tools suchen</button></p></div>
{section_html}
<div class="side-cards" id="mehr">{"".join(side)}</div>
</div>
</div>

<section class="band faq" id="faq"><div class="wrap">
<p class="eyebrow">Fragen aus der Werkstatt · {html.escape(sec["title"])}</p><h2>Kurz gefragt, kurz beantwortet</h2>
<div class="faq-list">{faq_html(faq)}</div>
</div></section>

{stacks_html}

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>{html.escape(kat_text(sec, "lead_hook"))}</h2>
<p class="intro">{html.escape(kat_text(sec, "lead_text"))}</p>
<p class="lead-merk" data-chrome>{icon("bookmark")}<span>Markier Tools mit dem Lesezeichen, die Merkliste reist mit deiner Anfrage mit.</span></p>
</div>
<div>{lead_form("Kategorie: " + sec["title"], "Stack-Check (" + sec["title"] + ") – KI-Werkstatt")}</div></div>
</div></section>

<section class="band" id="weitere"><div class="wrap">
<p class="eyebrow">Weitere Schubladen</p><h2>Woanders weiterstöbern</h2>
<div class="catgrid">{"".join(others)}</div>
</div></section>
{footer()}
"""
        title = seo_title(kat_text(sec, "seo_title"))
        (DOCS / page).write_text(page_shell(title, body, desc, SITE_URL + page, f'<script type="application/ld+json">{ld_js}</script>'), encoding="utf-8")
        pages.append(page)
    return pages


# --------------------------------------------------------------------------- KI-Glossar
def build_glossar(tools_map, list_secs, sections):
    terms = sorted(GLOSSAR["begriffe"], key=lambda g: g["t"].lower())
    names = {g["t"] for g in terms}
    page_ids = {s["id"] for s in list_secs}
    slugs = [slug(g["t"]) for g in terms]
    if len(set(slugs)) != len(slugs):
        raise SystemExit("Glossar: doppelte Anker")
    letters = []
    cards = []
    cur = None
    lern_ids = {x["id"] for x in NAV["lernen"]}
    # Rückwärtsindex: wo ein Begriff ausführlich vorkommt (Ratgeber und Einsatzgebiete nennen ihre Begriffe in den Daten)
    erklaert = {}
    for a in RATGEBER["artikel"]:
        for t in a["glossar"]:
            erklaert.setdefault(t, []).append((a["page"], a["label"], "book"))
    for e in EINSATZ["seiten"]:
        for t in e["glossar"]:
            erklaert.setdefault(t, []).append((e["page"], e["h1"], e["icon"]))
    for g in terms:
        for ref in g["see"]:
            if ref not in names:
                raise SystemExit(f"Glossar '{g['t']}': Verweis '{ref}' fehlt")
        for t in g["tools"]:
            if t not in tools_map:
                raise SystemExit(f"Glossar '{g['t']}': Tool '{t}' nicht in README.de.md gefunden")
        L = g["t"][0].upper()
        if L != cur:
            cur = L
            letters.append(L)
            cards.append(f'<p class="az-letter" id="buchstabe-{L.lower()}" aria-hidden="true">{L}</p>')
        see = " ".join(f'<a href="#{slug(r)}">{html.escape(r)}</a>' for r in g["see"])
        tools = "".join(tool_chip(t, tools_map) for t in g["tools"])
        cat = ""
        if g.get("cat"):
            sec = next((s for s in sections if s["id"] == g["cat"]), None)
            if sec is None:
                raise SystemExit(f"Glossar '{g['t']}': Kategorie '{g['cat']}' fehlt")
            if g["cat"] in page_ids:
                cat = cat_chip(g["cat"])
            else:
                href = f'#{g["cat"]}' if g["cat"] in lern_ids else f'./#{g["cat"]}'
                cat = f'<a class="chip cat" href="{href}">{icon("layers")}{html.escape(sec["title"])}</a>'
        extra = ""
        if tools or cat:
            extra = f'<div class="chips" data-chrome>{tools}{cat}</div>'
        if g["t"] in erklaert:
            extra += ('<p class="see erklaert" data-chrome><b>Ausführlich in:</b> '
                      + " ".join(f'<a href="{u}">{html.escape(lbl)}</a>' for u, lbl, _ in erklaert[g["t"]][:4]) + "</p>")
        search = " ".join([g["t"], g["d"]] + g.get("auch", [])).lower()
        cards.append(f"""<article class="term reveal" id="{slug(g['t'])}" data-search="{html.escape(search)}">
<div class="term-head"><span class="term-ico">{icon(g["icon"])}</span><h2><dfn>{html.escape(g["t"])}</dfn></h2><a class="anchor" href="#{slug(g['t'])}" title="Link auf diesen Begriff" aria-label="Link auf den Begriff {html.escape(g['t'])}">#</a></div>
<p>{html.escape(g["d"])}</p>
<p class="spruch">{icon("wrench")}<span><b>Werkstatt-Übersetzung:</b> {html.escape(g["spruch"])}</span></p>
<p class="see"><b>Siehe auch:</b> {see}</p>{extra}</article>""")
    az = "".join(f'<a href="#buchstabe-{L.lower()}">{L}</a>' for L in letters)
    n = len(terms)
    url = SITE_URL + GLOSSAR_PAGE
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "DefinedTermSet", "@id": url, "url": url, "name": "KI-Glossar der KI-Werkstatt", "inLanguage": "de-DE",
         "hasDefinedTerm": [{"@type": "DefinedTerm", "name": g["t"], "description": g["d"], "url": f"{url}#{slug(g['t'])}"} for g in terms]},
        crumbs(("KI-Glossar", GLOSSAR_PAGE))[1],
    ]}
    ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    lern_html = "".join(render_section(x, i + 1, {}, level=3) for i, x in enumerate(NAV["lernen"]))
    lern_band = f"""<section class="band" id="weiterlernen"><div class="wrap">
<p class="eyebrow">Weiterlernen</p><h2>Kurse, Leitfäden und andere Listen</h2>
<p class="intro">Wer nach den Vokabeln tiefer einsteigen will: kostenlose Kurse zu Prompting und Machine Learning, dazu Sammlungen, die andere Ecken der KI-Welt abdecken.</p>
{lern_html}</div></section>""" if lern_html else ""
    body = f"""{topbar("glossar")}
<section class="hero gl-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumbs(("KI-Glossar", GLOSSAR_PAGE))[0]}
<p class="kicker">{icon("abc")} <b>KI-Glossar</b> · {n} Begriffe von A bis Z</p>
<h1><em>KI-Glossar:</em> {n} Begriffe auf Deutsch erklärt</h1>
<p class="slogan">Ernst erklärt. Mit Augenzwinkern übersetzt.</p>
<p class="sub">{html.escape(GLOSSAR["intro"])}</p>
<div class="ctas"><a class="btn btn-lime" href="#begriffe">{icon("book")}Zu den Begriffen</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
</div></section>
<nav class="az" aria-label="Buchstaben"><div class="wrap in"><div class="az-letters">{az}</div>
<label class="sr" for="gq">Begriffe filtern</label><input type="search" id="gq" placeholder="Begriff filtern: Token, RAG, DSGVO …" autocomplete="off"><span id="gcount" aria-live="polite">{n} Begriffe</span></div></nav>
<div class="wrap gl" id="begriffe">{"".join(cards)}<div class="gl-empty hidden">{kurbel("kb-sm", wink=True)}<p><b>Die Schublade klemmt.</b> Diesen Begriff kennt Kurbel noch nicht. Fehlt einer? Schreib an {mail_link("Glossar")}.</p></div></div>
{lern_band}
<div class="wrap">{legal_note()}{pg_box("glossar")}</div>

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>Vokabeln sitzen. Und welches Tool jetzt?</h2>
<p class="intro">Wer weiß, was ein Token ist, stellt die besseren Fragen. Stell eine davon Jean und bekomm ein Setup, das zu deinem Vorhaben passt.</p>
<div class="kb-say">{hans("hm-md")}<p class="bubble">Ich hab das Glossar übrigens auswendig gelernt. Fast.</p></div></div>
<div>{lead_form("Glossar", "Stack-Check (Glossar) – KI-Werkstatt")}</div></div>
</div></section>
{footer()}
"""
    desc = f"{n} KI-Begriffe auf Deutsch erklärt, von Agent bis Zero-Shot: Token, RAG, MCP, DSGVO, AI Act. Jeder mit Werkstatt-Übersetzung und passenden Tools."
    (DOCS / GLOSSAR_PAGE).write_text(page_shell(seo_title(f"KI-Glossar: {n} Begriffe auf Deutsch erklärt"), body, desc, url,
                                                f'<script type="application/ld+json">{ld_js}</script>'), encoding="utf-8")
    return GLOSSAR_PAGE


# --------------------------------------------------------------------------- Trends und Neuzugänge
def de_date(iso):
    return date.fromisoformat(iso).strftime("%d.%m.%Y") if iso else ""


def tool_home(list_secs):
    """Name -> Kategorie-Seite mit Fach-Anker, wie in tools.json."""
    out = {}
    for s, sub, it in all_items(list_secs):
        out.setdefault(it["name"], cat_page(s["id"]) + (f"#{sub['id']}" if sub else ""))
    return out


def neu_band(list_secs):
    home = tool_home(list_secs)
    trend_ids = {t["id"]: t for t in TRENDS["trends"]}
    for t in NEU["tools"]:
        if t["name"] not in home:
            raise SystemExit(f"data/neu.json: '{t['name']}' steht in keiner Schublade von README.de.md")
        if t["trend"] not in trend_ids:
            raise SystemExit(f"data/neu.json: Trend '{t['trend']}' fehlt in data/trends.json")
    cards = "".join(f"""<a class="trend-card reveal" href="{TRENDS_PAGE}#{t['id']}"><span class="term-ico">{icon(t["icon"])}</span>
<span><span class="trend-no">Trend {i + 1:02d}</span><b>{html.escape(t["label"])}</b><small>{html.escape(t["kurz"])}</small></span></a>""" for i, t in enumerate(TRENDS["trends"][:4]))
    neu = "".join(f"""<li><a class="name" href="{home[t['name']]}">{html.escape(t["name"])}</a>{NEU_BADGE}<span class="desc">{html.escape(t["notiz"])}</span>
<a class="neu-trend" href="{TRENDS_PAGE}#{t['trend']}">{icon("spark")}{html.escape(trend_ids[t["trend"]]["label"])}</a></li>""" for t in NEU_AKTIV[:6])
    neu_html = f"""<div class="neu-box reveal"><h3>{icon("plus")}Frisch in den Schubladen</h3><ul class="neu-list">{neu}</ul></div>""" if neu else ""
    return f"""<section class="band" id="neu-und-trends"><div class="wrap">
<p class="eyebrow">Neu &amp; im Trend · Stand {de_date(TRENDS["stand"])}</p><h2>Frisch in der Werkstatt angekommen</h2>
<p class="intro">{ZAHLWORT.get(len(TRENDS["trends"]), str(len(TRENDS["trends"])))} Entwicklungen, die wir beim Hersteller nachgelesen haben, und die Tools, die deshalb neu in der Liste stehen. Die ausführliche Einordnung mit Quellen liegt auf der Trend-Seite.</p>
<div class="trend-cards">{cards}</div>
{neu_html}
<p style="margin-top:20px"><a class="btn btn-lime" href="{TRENDS_PAGE}">{icon("chart")}Alle {len(TRENDS["trends"])} Trends mit Quellen</a></p>
</div></section>"""


def gl_aliases():
    out = []
    for g in GLOSSAR["begriffe"]:
        for a in [g["t"]] + g.get("auch", []):
            out.append((a, g["t"]))
    return sorted(out, key=lambda x: -len(x[0]))


GL_ALIASES = gl_aliases()


def gl_autolink(txt, used):
    """Text escapen und das erste Vorkommen jedes Glossarbegriffs (oder Synonyms) auf der Seite verlinken."""
    out, slots = html.escape(txt), []
    for alias, term in GL_ALIASES:
        if term in used:
            continue
        m = re.search(r"(?<![\w-])" + re.escape(html.escape(alias)) + r"(?![\w-])", out)
        if not m:
            continue
        used.add(term)
        slots.append(f'<a class="gl-link" href="{GLOSSAR_PAGE}#{slug(term)}" title="Im Glossar: {html.escape(term)}">{m.group(0)}</a>')
        out = out[:m.start()] + f"\x00{len(slots) - 1}\x00" + out[m.end():]
    return re.sub("\x00(\\d+)\x00", lambda m: slots[int(m.group(1))], out)


def build_trends(tools_map, list_secs):
    stand = de_date(TRENDS["stand"])
    url = SITE_URL + TRENDS_PAGE
    n = len(TRENDS["trends"])
    ids = [t["id"] for t in TRENDS["trends"]]
    if len(set(ids)) != len(ids):
        raise SystemExit("data/trends.json: doppelte Trend-ID")
    links, arts, used = [f'<a href="#radar" data-js-only hidden>{icon("compass")}Radar</a>'], [], set()
    rollen = {r["id"] for r in TRENDS["rollen"]}
    for i, t in enumerate(TRENDS["trends"]):
        if set(t["radar"]) != rollen or not all(v in (0, 1, 2, 3) for v in t["radar"].values()):
            raise SystemExit(f"Trend '{t['id']}': radar braucht für jede Rolle einen Wert 0 bis 3")
        for name in t["tools"]:
            if name not in tools_map:
                raise SystemExit(f"Trend '{t['id']}': Tool '{name}' nicht in README.de.md gefunden")
        if not t["quellen"]:
            raise SystemExit(f"Trend '{t['id']}': keine Quelle")
        chips = "".join(tool_chip(name, tools_map) for name in t["tools"])
        chips_html = f'<div class="chips trend-tools"><span class="chips-lbl">Werkzeug dazu:</span>{chips}</div>' if chips else ""
        t_secs = secs_for_tools(t["tools"])
        if t_secs:
            chips_html += f'<div class="chips trend-tools" data-chrome><span class="chips-lbl">Schubladen dazu:</span>{"".join(cat_chip(x) for x in t_secs)}</div>'
        betrifft = [e for e in EINSATZ["seiten"] if t["radar"].get(e["rolle"], 0) >= 2]
        if betrifft:
            chips_html += ('<p class="tr-betrifft" data-chrome>Betrifft vor allem: '
                           + ", ".join(f'<a href="{e["page"]}">{html.escape(e["h1"])}</a>' for e in betrifft) + "</p>")
        quellen = "".join(f'<li><a href="{html.escape(check_url(u, "data/trends.json/" + t["id"]))}" target="_blank" rel="noopener">{html.escape(lbl)}</a>{f" <small>({de_date(d)})</small>" if d else ""}</li>'
                          for lbl, u, d in t["quellen"])
        text = "".join(f"<p>{gl_autolink(x, used)}</p>" for x in t["text"])
        links.append(f'<a href="#{t["id"]}">{icon(t["icon"])}{html.escape(t["label"])}</a>')
        arts.append(f"""<article class="trend reveal" id="{t['id']}">
<div class="trend-head"><span class="term-ico">{icon(t["icon"])}</span><div><p class="eyebrow">Trend {i + 1:02d} · {html.escape(t["label"])}</p><h2>{html.escape(t["titel"])}</h2></div></div>
<div class="trend-text">{text}</div>
<div class="trend-grid"><div class="fuer-dich"><h3>{icon("user")}Was heißt das für dich?</h3><p>{gl_autolink(t["fuer_dich"], used)}</p></div>
<div class="schritt"><h3>{icon("check")}Erster Schritt</h3><p>{html.escape(t["erster_schritt"])}</p></div>
<div class="urteil"><h3>{icon("wrench")}Werkstatt-Urteil</h3><p>{html.escape(t["urteil"])}</p></div></div>
{chips_html}
{rg_link(t.get("ratgeber"))}
<details class="quellen" data-chrome><summary>{icon("link")}Quellen ({len(t["quellen"])})</summary><ol>{quellen}</ol>{quellen_note()}</details>
</article>""")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": url, "url": url, "headline": TRENDS["titel"], "description": TRENDS["intro"], "inLanguage": "de-DE",
         "datePublished": TRENDS["stand"], "dateModified": TRENDS["stand"], "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": "KI-Werkstatt", "url": SITE_URL},
         "publisher": {"@type": "Organization", "name": "KI-Werkstatt", "url": SITE_URL},
         "citation": [u for t in TRENDS["trends"] for _, u, _ in t["quellen"]]},
        {"@type": "ItemList", "name": TRENDS["titel"], "numberOfItems": n,
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t["titel"], "url": f"{url}#{t['id']}"} for i, t in enumerate(TRENDS["trends"])]},
        crumbs(("KI-Trends", TRENDS_PAGE))[1],
    ]}
    ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    radar_btns = "".join(f'<button type="button" class="opt" data-rolle="{r["id"]}">{icon(r["icon"])}{html.escape(r["label"])}</button>' for r in TRENDS["rollen"])
    pages_by_rolle = {e["rolle"]: {"page": e["page"], "h1": e["h1"], "form": e["form_rolle"]} for e in EINSATZ["seiten"]}
    missing = [r["id"] for r in TRENDS["rollen"] if pages_by_rolle.get(r["id"], {}).get("form") not in ROLLEN_FORM]
    if missing:
        raise SystemExit(f"data/einsatz.json: form_rolle fehlt oder unbekannt für Rollen {missing}")
    radar_js = json.dumps({"rollen": [dict(r, **pages_by_rolle.get(r["id"], {})) for r in TRENDS["rollen"]], "trends": [{"id": t["id"], "label": t["label"], "schritt": t["erster_schritt"], "radar": t["radar"]}
                                                                for t in TRENDS["trends"]]}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""{topbar("trends")}
<section class="hero tr-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumbs(("KI-Trends", TRENDS_PAGE))[0]}
<p class="kicker">{icon("chart")} <b>{html.escape(TRENDS["titel"])}</b> · Stand {stand}</p>
<h1><em>{n} KI-Trends.</em><br>Beim Hersteller nachgelesen.<br>Für die Werkbank übersetzt.</h1>
<p class="sub">{html.escape(TRENDS["intro"])}</p>
<div class="ctas"><a class="btn btn-lime" href="#radar" data-js-only hidden>{icon("compass")}Trend-Radar starten</a><a class="btn" href="#{ids[0]}">{icon("chart")}Zum ersten Trend</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
</div></section>
<nav class="az tr-nav" aria-label="Trends"><div class="wrap in"><div class="tr-links">{"".join(links)}</div></div></nav>
<div class="wrap tr-wrap">
<aside class="tipp tr-method reveal">{kurbel("kb-sm", wink=True)}<p class="eyebrow">So haben wir sortiert</p><p>{html.escape(TRENDS["methode"])}</p></aside>
<section class="radar" id="radar" hidden><p class="eyebrow">Trend-Radar</p><h2>Welche dieser Trends treffen deine Arbeit?</h2>
<p class="radar-intro">Wähl, woran du hauptsächlich arbeitest. Das Radar sortiert die Trends nach unserer Einschätzung für diese Rolle und legt dir für die drei wichtigsten einen ersten Handgriff hin.</p>
<div class="radar-roles" role="group" aria-label="Deine Rolle">{radar_btns}</div>
<div class="radar-out" aria-live="polite"></div></section>
{"".join(arts)}
{pg_box("trends")}
</div>

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>Trends gelesen. Welcher davon zahlt bei dir ein?</h2>
<p class="intro">Nicht jede Neuheit gehört in deinen Werkzeugkasten. Schreib Jean, woran du gerade arbeitest, und du erfährst, welcher dieser Trends dir tatsächlich Arbeit abnimmt und welchen du getrost vorbeiziehen lässt.</p>
<div class="kb-say">{hans("hm-md")}<p class="bubble">Ich hab alle Quellen gelesen. Zweimal. Kurbel hatte danach trotzdem eine Schraube übrig.</p></div></div>
<div>{lead_form("Trends", "Stack-Check (Trends) – KI-Werkstatt")}</div></div>
</div></section>
{footer()}
<script type="application/json" id="kw-radar">{radar_js}</script>
"""
    desc = (f"{n} KI-Trends auf Deutsch eingeordnet, von günstigeren Spitzenmodellen über Agenten-Standards bis zum AI Act. "
            "Mit Herstellerquellen und Tools.")
    (DOCS / TRENDS_PAGE).write_text(page_shell(seo_title(f"{TRENDS['titel']}: {n} Entwicklungen eingeordnet"), body, desc, url,
                                               f'<script type="application/ld+json">{ld_js}</script>'), encoding="utf-8")
    return TRENDS_PAGE


# --------------------------------------------------------------------------- Einsatzgebiete
RADAR_TXT = ["kannst du auslassen", "am Rande", "lohnt einen Blick", "trifft dich direkt"]


def radar_bar(score):
    on = ' class="on"'
    return f'<span class="radar-bar" title="{RADAR_TXT[score]}">' + "".join(f'<i{on if j <= score else ""}></i>' for j in (1, 2, 3)) + "</span>"


def einsatz_band():
    tiles = "".join(f"""<a class="einsatz-tile reveal" href="{e['page']}"><span class="term-ico">{icon(e["icon"])}</span>
<span><b>{html.escape(e["h1"])}</b><small>{html.escape(e["teaser"])}</small><span class="drawer-cta">Ansehen{icon("arrow")}</span></span></a>""" for e in EINSATZ["seiten"])
    return f"""<section class="band" id="einsatz"><div class="wrap">
<p class="eyebrow">{html.escape(EINSATZ["titel"])}</p><h2>Sag, wo du arbeitest. Wir zeigen, wo KI anpackt.</h2>
<p class="intro">{ZAHLWORT.get(len(EINSATZ["seiten"]), str(len(EINSATZ["seiten"])))} Arbeitsfelder, jedes mit konkreten Aufgaben, passenden Werkzeugen, den Trends, die dort zählen, und den Fragen, die uns dazu am häufigsten erreichen.</p>
<div class="einsatz-grid">{tiles}</div>
<p style="margin-top:20px"><a class="btn" href="{EINSATZ_PAGE}">{icon("layers")}Alle Einsatzgebiete im Überblick</a></p>
</div></section>"""


def build_einsatz(tools_map, list_secs, sections):
    rollen = {r["id"]: r for r in TRENDS["rollen"]}
    kisten = {st["id"]: st for st in STACKS["stacks"]}
    sec_by_id = {x["id"]: x for x in sections}
    page_ids = {x["id"] for x in list_secs}
    terms = {g["t"]: g for g in GLOSSAR["begriffe"]}
    tasks = {a["id"]: a for a in RECHNER["aufgaben"]}
    pages = []
    for e in EINSATZ["seiten"]:
        where = f"data/einsatz.json/{e['id']}"
        if e["rolle"] not in rollen:
            raise SystemExit(f"{where}: Rolle '{e['rolle']}' fehlt in data/trends.json")
        for a in e["aufgaben"]:
            for name in a["tools"]:
                if name not in tools_map:
                    raise SystemExit(f"{where}: Tool '{name}' nicht in README.de.md gefunden")
        for k in e["kisten"]:
            if k not in kisten:
                raise SystemExit(f"{where}: Werkzeugkiste '{k}' fehlt")
        for c in e["kategorien"]:
            if c not in page_ids:
                raise SystemExit(f"{where}: Schublade '{c}' hat keine eigene Seite")
        for t in e["glossar"]:
            if t not in terms:
                raise SystemExit(f"{where}: Glossarbegriff '{t}' fehlt")
        if e["rechner"] and e["rechner"] not in tasks:
            raise SystemExit(f"{where}: Rechner-Aufgabe '{e['rechner']}' fehlt")
        url = SITE_URL + e["page"]
        n_tools = len({n for a in e["aufgaben"] for n in a["tools"]})

        def chip(name):
            return tool_chip(name, tools_map)
        auf = "".join(f"""<article class="aufgabe reveal"><span class="n">{i + 1}</span><h3>{html.escape(a["titel"])}</h3><p>{inline(a["text"], site=True)}</p>
<div class="chips">{"".join(chip(n) for n in a["tools"])}</div></article>""" for i, a in enumerate(e["aufgaben"]))
        ranked = sorted(enumerate(TRENDS["trends"]), key=lambda x: (-x[1]["radar"][e["rolle"]], x[0]))[:3]
        trend_cards = "".join(f"""<a class="trend-card reveal" href="{TRENDS_PAGE}#{t['id']}"><span class="term-ico">{icon(t["icon"])}</span>
<span><span class="trend-no">Trend {i + 1:02d}</span><b>{html.escape(t["label"])}</b>{radar_bar(t["radar"][e["rolle"]])}</span></a>""" for i, t in ranked)
        kiste_html = "".join(f'<a class="kiste-ref reveal" href="./#kiste-{k}">{icon(kisten[k]["icon"])}<span><b>{html.escape(kisten[k]["title"])}</b>'
                             f'<small>{len(kisten[k]["tools"])} Tools, fertig gepackt</small></span>{icon("arrow")}</a>' for k in e["kisten"])
        kat_chips = "".join(f'<a class="chip cat" href="{cat_page(c)}">{icon(CAT_ICON.get(c, "layers"))}{html.escape(sec_by_id[c]["title"])}</a>' for c in e["kategorien"])
        gl_chips = "".join(f'<a class="chip" href="{GLOSSAR_PAGE}#{slug(t)}">{icon(terms[t]["icon"])}{html.escape(t)}</a>' for t in e["glossar"])
        rechner = (f'<a class="btn btn-sm" href="./#rechner">{icon("calc")}Rechner: {html.escape(tasks[e["rechner"]]["label"])}</a>') if e["rechner"] else ""
        others = "".join(f'<a class="einsatz-mini" href="{o["page"]}">{icon(o["icon"])}{html.escape(o["h1"])}</a>' for o in EINSATZ["seiten"] if o is not e) \
            + f'<a class="einsatz-mini" href="{EINSATZ_PAGE}">{icon("layers")}Alle Einsatzgebiete</a>'
        crumb_html, crumb_ld = crumbs(("Einsatzgebiete", EINSATZ_PAGE), (e["h1"], e["page"]))
        faq = [tuple(x) for x in e["faq"]]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebPage", "@id": url, "url": url, "name": e["h1"], "description": e["meta"], "inLanguage": "de-DE",
             "isPartOf": {"@type": "WebSite", "name": "KI-Werkstatt", "url": SITE_URL}},
            crumb_ld,
            {"@type": "ItemList", "name": f"Aufgaben: {e['h1']}", "numberOfItems": len(e["aufgaben"]),
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": a["titel"]} for i, a in enumerate(e["aufgaben"])]},
            faq_ld(faq),
        ]}
        ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
        label = rollen[e["rolle"]]["label"]
        body = f"""{topbar("einsatz")}
<section class="hero cat-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumb_html}
<p class="kicker">{icon(e["icon"])} <b>Einsatzgebiet</b> · {len(e["aufgaben"])} Aufgaben · {n_tools} Tools</p>
<h1><em>{html.escape(e["h1"])}</em></h1>
<p class="sub">{html.escape(e["hero"])}</p>
<div class="ctas"><a class="btn btn-lime" href="#aufgaben">{icon("wrench")}Zu den Aufgaben</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
</div></section>

<section class="band cat-intro"><div class="wrap intro-grid">
<div class="intro-text reveal">{"".join(f"<p>{gl_autolink(x, set())}</p>" for x in e["intro"])}</div>
<aside class="tipp reveal">{kurbel("kb-sm", wink=True)}<p class="eyebrow">Werkstatt-Tipp</p><p>{html.escape(e["tipp"])}</p></aside>
</div></section>

<section class="band" id="aufgaben"><div class="wrap">
<p class="eyebrow">Wo KI mit anpackt · {html.escape(e["h1"])}</p><h2 data-chrome>{ZAHLWORT.get(len(e["aufgaben"]), str(len(e["aufgaben"])))} Aufgaben, die du abgeben kannst</h2>
<div class="aufgaben">{auf}</div>
</div></section>

<section class="band" id="trends"><div class="wrap">
<p class="eyebrow">Trend-Radar · {html.escape(label)}</p><h2 data-chrome>Die drei Trends mit dem meisten Hebel für dich</h2>
<div class="trend-cards">{trend_cards}</div>
<p style="margin-top:18px"><a class="btn" href="{TRENDS_PAGE}?rolle={e['rolle']}#radar">{icon("compass")}Ganzes Trend-Radar ansehen</a></p>
</div></section>

<section class="band" id="werkzeug"><div class="wrap">
<p class="eyebrow">Weiter in der Werkstatt</p><h2 data-chrome>Was sonst noch in die Kiste gehört</h2>
<div class="kisten-refs">{kiste_html}</div>
<div class="einsatz-more">
<div><h3>{icon("layers")}Passende Schubladen</h3><div class="chips">{kat_chips}</div></div>
<div><h3>{icon("abc")}Begriffe zum Nachschlagen</h3><div class="chips">{gl_chips}</div></div>
{f'<div><h3>{icon("clock")}Zeit nachrechnen</h3>{rechner}</div>' if rechner else ""}
{rg_more(e["rolle"])}
</div></div></section>

<section class="band faq" id="faq"><div class="wrap">
<p class="eyebrow">Fragen aus der Werkstatt · {html.escape(e["h1"])}</p><h2>Kurz gefragt, kurz beantwortet</h2>
<div class="faq-list">{faq_html(faq)}</div>
{legal_note()}
</div></section>

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>{html.escape(e["lead_hook"])}</h2>
<p class="intro">{html.escape(e["lead_text"])}</p>
<div class="kb-say">{speaker(e)}<p class="bubble">{html.escape(e["bubble"])}</p></div></div>
<div>{lead_form("Einsatz: " + e["h1"], "Stack-Check (" + e["h1"] + ") – KI-Werkstatt", rolle=e["form_rolle"])}</div></div>
</div></section>

<section class="band" id="weitere"><div class="wrap">
<p class="eyebrow">Andere Einsatzgebiete</p><div class="einsatz-minis" data-chrome>{others}</div>
</div></section>
{footer()}
"""
        (DOCS / e["page"]).write_text(page_shell(seo_title(e["seo_title"]), body, e["meta"], url,
                                                f'<script type="application/ld+json">{ld_js}</script>'), encoding="utf-8")
        pages.append(e["page"])
    return pages


# --------------------------------------------------------------------------- Ratgeber (Long-Form)
def rg_by_id():
    return {a["id"]: a for a in RATGEBER["artikel"]}


def rg_link(rid):
    if not rid:
        return ""
    a = rg_by_id().get(rid)
    if not a:
        raise SystemExit(f"data/trends.json: Ratgeber '{rid}' fehlt in data/ratgeber.json")
    return f'<p class="rg-link"><a class="btn btn-sm" href="{a["page"]}">{icon("book")}Ausführlich im Ratgeber: {html.escape(a["label"])}</a></p>'


def rg_more(rolle):
    """Höchstens vier Ratgeber zur Rolle; wo die Rolle weiter vorn steht (Hauptrolle), kommt der Ratgeber zuerst."""
    hits = sorted((a["rollen"].index(rolle), i, a) for i, a in enumerate(RATGEBER["artikel"]) if rolle in a["rollen"])
    if not hits:
        return ""
    links = "".join(f'<a class="chip cat" href="{a["page"]}">{icon(a["icon"])}{html.escape(a["label"])}</a>' for _, _, a in hits[:4])
    links += f'<a class="chip" href="{RATGEBER_PAGE}">{icon("book")}Alle Ratgeber</a>'
    return f'<div data-chrome><h3>{icon("book")}Zum Weiterlesen</h3><div class="chips">{links}</div></div>'


def rg_words(md):
    return len(re.findall(r"\w+", md))


def rg_total_words(a):
    """Wörter aus Text und FAQ; Grundlage für Lesezeit auf Karte und Seite."""
    md = (RG_DIR / f"{a['id']}.md").read_text(encoding="utf-8")
    return rg_words(md) + sum(rg_words(q + " " + x) for q, x in a["faq"])


def ratgeber_band():
    cards = "".join(f"""<a class="rg-card reveal" href="{a['page']}"><span class="term-ico">{icon(a["icon"])}</span>
<span><span class="trend-no">Ratgeber · {max(1, round(rg_total_words(a) / 200))} Min. Lesezeit</span><b>{html.escape(a["h1"])}</b><small>{html.escape(a["teaser"])}</small>
<span class="drawer-cta">Lesen{icon("arrow")}</span></span></a>""" for a in RATGEBER["artikel"][:4])
    return f"""<section class="band" id="ratgeber"><div class="wrap">
<p class="eyebrow">{html.escape(RATGEBER["titel"])}</p><h2>Zum Durchlesen statt Durchscrollen</h2>
<p class="intro">Ausführliche Anleitungen zu den Fragen, die uns gerade am häufigsten erreichen, mit Beispielen, Checklisten und allen Quellen zum Nachprüfen.</p>
<div class="rg-cards">{cards}</div>
<p style="margin-top:20px"><a class="btn btn-lime" href="{RATGEBER_PAGE}">{icon("book")}Alle {len(RATGEBER["artikel"])} Ratgeber</a></p>
</div></section>"""


def gl_autolink_html(markup, used):
    """Glossar-Begriffe im fertigen HTML verlinken, nur in Fließtext (nicht in Links, Code, Überschriften, Tabellenköpfen)."""
    parts = re.split(r"(<[^>]+>)", markup)
    skip = 0
    out = []
    for part in parts:
        if part.startswith("<"):
            m = re.match(r"<(/?)(a|code|h2|h3|th|strong)\b", part)
            if m:
                skip += -1 if m.group(1) else 1
            out.append(part)
        elif skip or not part.strip():
            out.append(part)
        else:
            out.append(gl_autolink(html.unescape(part), used))
    return "".join(out)


def render_md(md):
    """Kleines Markdown: ## Kapitel, ### Unterkapitel, > Kasten, - und 1. Listen, | Tabellen, Absätze."""
    blocks, toc = [], []
    lines = md.strip().split("\n")
    i = 0

    def para(buf):
        if buf:
            blocks.append(f"<p>{inline(' '.join(buf), site=True)}</p>")
    buf = []
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            para(buf)
            buf = []
            i += 1
            continue
        if ln.startswith("## "):
            para(buf)
            buf = []
            t = ln[3:].strip()
            toc.append((slug(t), t))
            blocks.append(f'<h2 id="{slug(t)}">{html.escape(t)}</h2>')
        elif ln.startswith("### "):
            para(buf)
            buf = []
            blocks.append(f"<h3>{inline(ln[4:].strip(), site=True)}</h3>")
        elif ln.startswith("> "):
            para(buf)
            buf = []
            box = []
            while i < len(lines) and lines[i].startswith("> "):
                box.append(lines[i][2:])
                i += 1
            blocks.append(f'<aside class="rg-box">{icon("spark")}<p>{inline(" ".join(box), site=True)}</p></aside>')
            continue
        elif ln.startswith("|"):
            para(buf)
            buf = []
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, *body = rows
            blocks.append(md_table(head, body, site=True))
            continue
        elif re.match(r"(- |\d+\. )", ln):
            para(buf)
            buf = []
            ordered = bool(re.match(r"\d+\. ", ln))
            items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            tag = "ol" if ordered else "ul"
            blocks.append(f'<{tag} class="plain">' + "".join(f"<li>{inline(x, site=True)}</li>" for x in items) + f"</{tag}>")
            continue
        else:
            buf.append(ln.strip())
        i += 1
    para(buf)
    return "\n".join(blocks), toc


def build_ratgeber(tools_map):
    terms = {g["t"]: g for g in GLOSSAR["begriffe"]}
    rollen = {r["id"]: r for r in TRENDS["rollen"]}
    trend_ids = {t["id"] for t in TRENDS["trends"]}
    pages = []
    for a in RATGEBER["artikel"]:
        where = f"data/ratgeber.json/{a['id']}"
        for n in a["tools"]:
            if n not in tools_map:
                raise SystemExit(f"{where}: Tool '{n}' nicht in README.de.md gefunden")
        for t in a["glossar"]:
            if t not in terms:
                raise SystemExit(f"{where}: Glossarbegriff '{t}' fehlt")
        for r in a["rollen"]:
            if r not in rollen:
                raise SystemExit(f"{where}: Rolle '{r}' fehlt in data/trends.json")
        if a.get("trend") and a["trend"] not in trend_ids:
            raise SystemExit(f"{where}: Trend '{a['trend']}' fehlt")
        if not a["quellen"]:
            raise SystemExit(f"{where}: keine Quellen")
        md = (RG_DIR / f"{a['id']}.md").read_text(encoding="utf-8")
        body_html, toc = render_md(md)
        body_html = gl_autolink_html(body_html, set())
        words = rg_total_words(a)
        minutes = max(1, round(words / 200))
        url = SITE_URL + a["page"]
        faq = [tuple(x) for x in a["faq"]]
        toc_html = "".join(f'<a href="#{i}">{html.escape(t)}</a>' for i, t in toc) + f'<a href="#faq">Fragen</a><a href="#quellen">Quellen</a>'
        tool_chips = "".join(tool_chip(n, tools_map) for n in a["tools"])
        sec_chips = "".join(cat_chip(x) for x in secs_for_tools(a["tools"]))
        gl_chips = "".join(f'<a class="chip" href="{GLOSSAR_PAGE}#{slug(t)}">{icon(terms[t]["icon"])}{html.escape(t)}</a>' for t in a["glossar"])
        einsatz = [e for e in EINSATZ["seiten"] if e["rolle"] in a["rollen"]]
        einsatz_chips = "".join(f'<a class="chip cat" href="{e["page"]}">{icon(e["icon"])}{html.escape(e["h1"])}</a>' for e in einsatz)
        quellen = "".join(f'<li><a href="{html.escape(check_url(u, where))}" target="_blank" rel="noopener">{html.escape(lbl)}</a>{f" <small>({de_date(d)})</small>" if d else ""}</li>'
                          for lbl, u, d in a["quellen"])
        # Weitere Ratgeber nach Nähe: gleicher Trend, gemeinsame Rollen, gemeinsame Tools; höchstens vier
        def near(o):
            return 2 * bool(a.get("trend") and o.get("trend") == a["trend"]) + len(set(o["rollen"]) & set(a["rollen"])) + len(set(o["tools"]) & set(a["tools"]))
        ranked = sorted((o for o in RATGEBER["artikel"] if o is not a), key=lambda o: -near(o))[:4]
        others = "".join(f'<a class="einsatz-mini" href="{o["page"]}">{icon(o["icon"])}{html.escape(o["label"])}</a>' for o in ranked) \
            + f'<a class="einsatz-mini" href="{RATGEBER_PAGE}">{icon("layers")}Alle Ratgeber</a>'
        crumb_html, crumb_ld = crumbs(("Ratgeber", RATGEBER_PAGE), (a["label"], a["page"]))
        trend_btn = ""
        if a.get("trend"):
            t = next(t for t in TRENDS["trends"] if t["id"] == a["trend"])
            trend_btn = f'<a class="btn" href="{TRENDS_PAGE}#{t["id"]}">{icon("chart")}Zum Trend: {html.escape(t["label"])}</a>'
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Article", "@id": url, "url": url, "headline": a["h1"], "description": a["meta"], "inLanguage": "de-DE",
             "datePublished": a["stand"], "dateModified": a["stand"], "wordCount": words, "mainEntityOfPage": url,
             "author": {"@type": "Organization", "name": "KI-Werkstatt", "url": SITE_URL},
             "publisher": {"@type": "Organization", "name": "KI-Werkstatt", "url": SITE_URL},
             "citation": [u for _, u, _ in a["quellen"]]},
            faq_ld(faq),
            crumb_ld,
        ]}
        ld_js = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
        body = f"""{topbar("ratgeber")}
<section class="hero rg-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumb_html}
<p class="kicker" data-chrome>{icon(a["icon"])} <b>Ratgeber</b> · Stand {de_date(a["stand"])} · {minutes} Min. Lesezeit</p>
<h1>{html.escape(a["h1"])}</h1>
<p class="sub">{html.escape(a["hero"])}</p>
<div class="ctas"><a class="btn btn-lime" href="#{toc[0][0] if toc else 'faq'}">{icon("book")}Lesen</a><a class="btn hide-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div>
</div></section>

<div class="wrap layout rg-layout">
<nav class="rail" aria-label="Inhalt" data-chrome><div class="in"><p class="rail-h">Inhalt</p>{toc_html}
<div class="lead-mini"><p>Kostet nichts außer zwei Minuten.</p><a class="btn btn-sm" href="#stack-check">{icon("mail")}Stack-Check anfragen</a></div></div></nav>
<article class="content rg-body">
<div class="print-head" data-chrome>{hans("hm-sm", label="")}<span>KI-Werkstatt · Ratgeber · Stand {de_date(a["stand"])}</span></div>
<details class="toc-m" data-chrome><summary>{icon("book")}Inhalt · {len(toc)} Abschnitte</summary><nav aria-label="Inhalt (kompakt)">{toc_html}</nav></details>
{body_html}
<section class="rg-extras">
<div><h3>{icon("wrench")}Werkzeug zum Thema</h3><div class="chips">{tool_chips}</div></div>
<div><h3>{icon("abc")}Begriffe zum Nachschlagen</h3><div class="chips">{gl_chips}</div></div>
<div><h3>{icon("layers")}Passende Einsatzgebiete</h3><div class="chips" data-chrome>{einsatz_chips}</div></div>
{f'<div><h3>{icon("box")}Passende Schubladen</h3><div class="chips" data-chrome>{sec_chips}</div></div>' if sec_chips else ""}
</section>
<p class="rg-trend">{trend_btn}</p>
<section id="faq" class="rg-faq"><h2>Häufige Fragen</h2><div class="faq-list">{faq_html(faq)}</div></section>
<section id="quellen" class="rg-quellen" data-chrome><h2>Quellen</h2><ol>{quellen}</ol>{quellen_note()}{legal_note(a["stand"])}</section>
<section class="rg-done reveal" id="geschafft" data-chrome>{hans("hm-md", label="Hans Moritz zeigt den Daumen hoch", thumb=True)}<div>
<h2>Geschafft. Respekt.</h2>
<p>Du hast dich durch {f"{words:,}".replace(",", ".")} Wörter Werkstatt-Wissen gearbeitet. Hol dir einen Kaffee, den hast du dir verdient.</p>
<div class="row"><span>War das hilfreich?</span><button type="button" class="btn btn-sm" data-hilf="ja">{icon("heart")}Ja</button><button type="button" class="btn btn-sm" data-hilf="nein">{icon("x")}Eher nicht</button>
<button type="button" class="btn btn-sm" data-share>{icon("share")}Weitersagen</button><button type="button" class="btn btn-sm" data-print>{icon("print")}Für die Werkstattwand drucken</button></div>
<p class="hilf-a" aria-live="polite"></p>
{pg_box("geschafft")}</div></section>
<p class="print-foot" data-chrome>Ausgedruckt aus der KI-Werkstatt. Die aktuelle Fassung steht unter {url}</p>
</article>
</div>

<section class="band lead" id="stack-check"><div class="wrap">
<div class="lead-grid"><div>
<p class="eyebrow">Stack-Check</p><h2>{html.escape(a["lead_hook"])}</h2>
<p class="intro">{html.escape(a["lead_text"])}</p>
<div class="kb-say">{speaker(a)}<p class="bubble">{html.escape(a["bubble"])}</p></div></div>
<div>{lead_form("Ratgeber: " + a["label"], "Stack-Check (Ratgeber " + a["label"] + ") – KI-Werkstatt")}</div></div>
</div></section>

<section class="band" id="weitere"><div class="wrap">
<p class="eyebrow">Weitere Ratgeber</p><div class="einsatz-minis" data-chrome>{others}</div>
</div></section>
{footer()}
"""
        (DOCS / a["page"]).write_text(page_shell(seo_title(a["seo_title"]), body, a["meta"], url,
                                                f'<script type="application/ld+json">{ld_js}</script>', og_type="article",
                                                published=a["stand"], modified=a["stand"]), encoding="utf-8")
        pages.append(a["page"])
    return pages


# --------------------------------------------------------------------------- Übersichtsseiten
def ld_json(ld):
    return json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")


def build_hubs():
    """ratgeber.html (alle Ratgeber, Filter nach Rolle ohne JavaScript) und ki-einsatz.html (alle Einsatzgebiete)."""
    rollen = TRENDS["rollen"]
    unknown = [r["id"] for r in rollen if r["id"] not in HUB_ROLLEN_CSS]
    if unknown:
        raise SystemExit(f"ratgeber.html: Rollen {unknown} fehlen in HUB_ROLLEN_CSS und in style.css (.rg-hub:has(#rolle-…:checked))")
    arts = RATGEBER["artikel"]
    n = len(arts)
    stand = max(a["stand"] for a in arts)
    rlabel = {r["id"]: r["label"] for r in rollen}
    used = [r for r in rollen if any(r["id"] in a["rollen"] for a in arts)]
    radios = f'<label class="chip rg-opt"><input type="radio" name="rolle" id="rolle-alle" checked><span>Alle ({n})</span></label>' + "".join(
        f'<label class="chip rg-opt"><input type="radio" name="rolle" id="rolle-{r["id"]}"><span>{icon(r["icon"])}{html.escape(r["label"])} '
        f'({sum(r["id"] in a["rollen"] for a in arts)})</span></label>' for r in used)
    cards = []
    for a in sorted(arts, key=lambda a: a["stand"], reverse=True):
        minutes = max(1, round(rg_total_words(a) / 200))
        cards.append(f"""<article class="rg-card hub-card reveal" data-rollen="{" ".join(a["rollen"])}"><span class="term-ico">{icon(a["icon"])}</span>
<div><p class="trend-no" data-chrome>Stand {de_date(a["stand"])} · {minutes} Min. Lesezeit</p><h2><a href="{a["page"]}">{html.escape(a["label"])}</a></h2>
<p>{html.escape(a["meta"])}</p>
<p class="hub-roles" data-chrome>Für: {", ".join(html.escape(rlabel[x]) for x in a["rollen"] if x in rlabel)}</p></div></article>""")
    crumb_html, crumb_ld = crumbs(("Ratgeber", RATGEBER_PAGE))
    url = SITE_URL + RATGEBER_PAGE
    zahl = ZAHLWORT.get(n, str(n))
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": "KI-Ratgeber der KI-Werkstatt", "inLanguage": "de-DE",
         "isPartOf": {"@type": "WebSite", "name": "KI-Werkstatt", "url": SITE_URL}},
        {"@type": "ItemList", "name": "Ratgeber", "numberOfItems": n,
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": a["h1"], "url": SITE_URL + a["page"]} for i, a in enumerate(arts)]},
        crumb_ld]}
    body = f"""{topbar("ratgeber-hub")}
<section class="hero cat-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumb_html}
<p class="kicker">{icon("book")} <b>Ratgeber</b> · {n} Anleitungen · Stand {de_date(stand)}</p>
<h1><em>KI-Ratgeber</em> auf Deutsch: Recht, Kosten, Praxis</h1>
<p class="sub">{zahl} Anleitungen für die Fragen, die gerade auf vielen Werkbänken liegen: was der AI Act verlangt, was Sprachmodelle kosten, wie Agenten sicher laufen. Jeder Ratgeber nennt seinen Stand und seine Quellen, damit du selbst nachprüfen kannst.</p>
</div></section>
<section class="band rg-hub"><div class="wrap">
<fieldset class="rg-filter"><legend>Nach Rolle filtern</legend><div class="chips">{radios}</div></fieldset>
<div class="rg-cards">{"".join(cards)}</div>
<p class="bridge" data-chrome>{icon("mail")}<span>Deine Frage ist nicht dabei? <a href="./#stack-check">Schreib sie Jean beim Stack-Check.</a></span></p>
</div></section>
{footer()}
"""
    desc = (f"{n} KI-Ratgeber auf Deutsch: AI Act und Kennzeichnung, Datenschutz, Modellpreise, sichere Agenten, lokale KI. "
            "Mit Stand, Quellen und Filter nach Rolle.")
    (DOCS / RATGEBER_PAGE).write_text(page_shell(seo_title("KI-Ratgeber: Recht, Kosten und Praxis"), body, desc, url,
                                                 f'<script type="application/ld+json">{ld_json(ld)}</script>'), encoding="utf-8")

    # Einsatzgebiete
    seiten = EINSATZ["seiten"]
    tiles = []
    for e in seiten:
        n_auf = len(e["aufgaben"])
        n_tools = len({x for a in e["aufgaben"] for x in a["tools"]})
        n_rg = sum(e["rolle"] in a["rollen"] for a in arts)
        auf = "".join(f"<li>{html.escape(a['titel'])}</li>" for a in e["aufgaben"])
        tiles.append(f"""<article class="einsatz-tile hub-card reveal"><span class="term-ico">{icon(e["icon"])}</span>
<div><p class="trend-no" data-chrome>{n_auf} Aufgaben · {n_tools} Tools · {n_rg} Ratgeber</p><h2><a href="{e["page"]}">{html.escape(e["h1"])}</a></h2>
<p>{html.escape(e["meta"])}</p>
<ul class="hub-list" data-chrome>{auf}</ul>
<p class="hub-roles" data-chrome><a href="{TRENDS_PAGE}?rolle={e["rolle"]}#radar">{icon("compass")}Trend-Radar: {html.escape(rlabel.get(e["rolle"], e["rolle"]))}</a></p></div></article>""")
    crumb_html, crumb_ld = crumbs(("Einsatzgebiete", EINSATZ_PAGE))
    url = SITE_URL + EINSATZ_PAGE
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": "KI nach Einsatzgebiet", "inLanguage": "de-DE",
         "isPartOf": {"@type": "WebSite", "name": "KI-Werkstatt", "url": SITE_URL}},
        {"@type": "ItemList", "name": "Einsatzgebiete", "numberOfItems": len(seiten),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": e["h1"], "url": SITE_URL + e["page"]} for i, e in enumerate(seiten)]},
        crumb_ld]}
    zahl = ZAHLWORT.get(len(seiten), str(len(seiten)))
    body = f"""{topbar("einsatz-hub")}
<section class="hero cat-hero"><div class="hero-art">{hero_floats()}</div><div class="wrap">
{crumb_html}
<p class="kicker">{icon("layers")} <b>Einsatzgebiete</b> · {len(seiten)} Arbeitsfelder</p>
<h1><em>KI im Einsatz:</em> {len(seiten)} Arbeitsfelder im Überblick</h1>
<p class="sub">Ob KI hilft, hängt weniger am Tool als an der Aufgabe. Deshalb sortiert die Werkstatt hier nach Arbeitsfeldern statt nach Produkten: {zahl} Bereiche, jeder mit konkreten Aufgaben, passendem Werkzeug und ehrlichen Antworten auf die üblichen Fragen.</p>
</div></section>
<section class="band"><div class="wrap">
<div class="einsatz-grid hub-grid">{"".join(tiles)}</div>
</div></section>
<section class="band"><div class="wrap">
<p class="eyebrow">Rollen, Trends, Ratgeber</p><h2>Wie die Arbeitsfelder mit dem Rest zusammenhängen</h2>
<p class="intro">Jedes Arbeitsfeld entspricht einer Rolle im Trend-Radar. Die Rolle bestimmt, welche drei Trends auf der Einsatzseite oben stehen und welche Ratgeber dort zum Weiterlesen auftauchen. Wer mehrere Hüte trägt, liest einfach zwei Seiten und nimmt von beiden das Passende mit.</p>
<p class="bridge" data-chrome>{icon("mail")}<span>Kein Feld passt genau? <a href="./#stack-check">Beschreib Jean deinen Alltag beim Stack-Check.</a></span></p>
</div></section>
{footer()}
"""
    desc = (f"KI nach Einsatzgebiet: {len(seiten)} Arbeitsfelder von Online-Shop bis Büro, jedes mit Aufgaben, passenden Tools, "
            "Trends und Ratgebern. Einstieg nach Rolle.")
    (DOCS / EINSATZ_PAGE).write_text(page_shell(seo_title(f"KI nach Einsatzgebiet: {len(seiten)} Arbeitsfelder"), body, desc, url,
                                                f'<script type="application/ld+json">{ld_json(ld)}</script>'), encoding="utf-8")
    return [RATGEBER_PAGE, EINSATZ_PAGE]


def build_feed(list_secs):
    home = tool_home(list_secs)
    # Nur bereits gestartete Neuzugänge; abgelaufene bleiben als Historie im Feed
    neu = [t for t in NEU["tools"] if date.fromisoformat(t["seit"]) <= date.today()]
    stamp = max([TRENDS["stand"]] + [t["seit"] for t in neu] + [a["stand"] for a in RATGEBER["artikel"]]) + "T00:00:00Z"
    x = html.escape
    entries = []
    for t in TRENDS["trends"]:
        u = f"{SITE_URL}{TRENDS_PAGE}#{t['id']}"
        entries.append(f'<entry><title>{x(t["titel"])}</title><link href="{x(u)}"/><id>{x(u)}</id><updated>{TRENDS["stand"]}T00:00:00Z</updated><summary>{x(t["kurz"])}</summary></entry>')
    for a in RATGEBER["artikel"]:
        u = SITE_URL + a["page"]
        entries.append(f'<entry><title>{x(a["h1"])}</title><link href="{x(u)}"/><id>{x(u)}</id><updated>{a["stand"]}T00:00:00Z</updated><summary>{x(a["teaser"])}</summary></entry>')
    for t in neu:
        u = SITE_URL + home[t["name"]]
        entries.append(f'<entry><title>Neu in der Liste: {x(t["name"])}</title><link href="{x(u)}"/><id>{x(SITE_URL)}neu/{slug(t["name"])}</id>'
                       f'<updated>{t["seit"]}T00:00:00Z</updated><summary>{x(t["notiz"])}</summary></entry>')
    (DOCS / "feed.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="de"><title>KI-Werkstatt: Trends und Neuzugänge</title>
<link href="{SITE_URL}feed.xml" rel="self"/><link href="{SITE_URL}{TRENDS_PAGE}"/><id>{SITE_URL}feed.xml</id><updated>{stamp}</updated>
<author><name>KI-Werkstatt</name></author>
{chr(10).join(entries)}
</feed>
""", encoding="utf-8")


def csv_safe(v):
    """Zellen, die wie eine Tabellenformel beginnen, bekommen ein führendes Hochkomma (CSV-Injection)."""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def build_search_index():
    """docs/seiten.json: kleiner Index für das Such-Panel (Schubladen, Einsatzgebiete, Ratgeber, Trends, Begriffe).
    t = Titel, d = Kurztext, u = Seite, k = Art, s = Suchtext."""
    def short(x, n=150):
        return x if len(x) <= n else x[:n].rsplit(" ", 1)[0] + " …"
    rows = []
    for sec in NAV["secs"]:
        rows.append({"k": "Schublade", "t": cat_h1(sec), "d": kat_text(sec, "teaser"), "u": cat_page(sec["id"]),
                     "s": " ".join([sec["title"], cat_h1(sec), kat_text(sec, "teaser")] + [x["title"] for x in sec["subs"]])})
    for e in EINSATZ["seiten"]:
        rows.append({"k": "Einsatz", "t": e["h1"], "d": e["teaser"], "u": e["page"],
                     "s": " ".join([e["h1"], e["teaser"], e["meta"]] + [a["titel"] for a in e["aufgaben"]])})
    for a in RATGEBER["artikel"]:
        rows.append({"k": "Ratgeber", "t": a["label"], "d": a["teaser"], "u": a["page"], "s": " ".join([a["h1"], a["label"], a["teaser"], a["meta"]] + a["glossar"])})
    for t in TRENDS["trends"]:
        rows.append({"k": "Trend", "t": t["label"], "d": t["kurz"], "u": f"{TRENDS_PAGE}#{t['id']}", "s": " ".join([t["label"], t["titel"], t["kurz"]])})
    for g in GLOSSAR["begriffe"]:
        rows.append({"k": "Begriff", "t": g["t"], "d": short(g["d"]), "u": f"{GLOSSAR_PAGE}#{slug(g['t'])}", "s": " ".join([g["t"], g["d"]] + g.get("auch", []))})
    for r in rows:
        r["s"] = r["s"].lower()
    (DOCS / "seiten.json").write_text(json.dumps({"seiten": rows}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


LASTMOD = ROOT / "data" / "lastmod.json"


def page_lastmod(pages):
    """lastmod je Seite aus einem Hash des Inhalts in <main>: Datum nur fortschreiben, wenn sich der Inhalt geändert hat.
    Ausgeblendet werden Build- und Link-Check-Datum sowie Asset-Versionen, die sich sonst bei jedem Lauf ändern.
    Der Stand liegt in data/lastmod.json (vom Build gepflegt, mit committen); neue Ratgeber starten mit ihrem Stand."""
    try:
        old = json.loads(LASTMOD.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        old = {}
    seed = {a["page"]: a["stand"] for a in RATGEBER["artikel"]}
    seed[TRENDS_PAGE] = TRENDS["stand"]
    today = date.today().isoformat()
    out, res = {}, {}
    for pg in pages:
        doc = (DOCS / pg).read_text(encoding="utf-8")
        m = re.search(r"<main\b.*?</main>", doc, re.S)
        txt = m.group(0) if m else doc
        for volatile in (LINK_CHECK, TODAY, f"{LINK_CHECK_N} Links"):
            txt = txt.replace(volatile, "")
        txt = re.sub(r"\?v=[0-9a-f]{8}", "", txt)
        h = hashlib.sha1(txt.encode("utf-8")).hexdigest()[:16]
        prev = old.get(pg, {})
        day = prev["date"] if prev.get("hash") == h else (today if prev else seed.get(pg, today))
        out[pg] = {"hash": h, "date": day}
        res[pg] = day
    if out != old:
        LASTMOD.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return res


def build_data(uniq, sections, pages=(), list_secs=()):
    page_ids = {s["id"] for s in list_secs}
    first = {}
    # Zuerst die Fundstelle in einer Kategorie (sachlicher Text, eigene Seite), Favoriten nur als Rückfall
    ordered = [x for x in all_items(sections) if x[0]["id"] != "empfehlungen-der-redaktion"] + \
              [x for x in all_items(sections) if x[0]["id"] == "empfehlungen-der-redaktion"]
    for s, sub, it in ordered:
        first.setdefault(it["url"], (s, sub, it))
    rows = []
    for url in uniq:
        s, sub, it = first[url]
        eu, oss, clean = item_meta(it)
        if s["id"] in page_ids:
            seite = cat_page(s["id"]) + "#" + tool_id(it["name"])
        elif s["id"] in LERNEN_IDS:
            seite = f"{GLOSSAR_PAGE}#{s['id']}"
        else:
            seite = f"./#{s['id']}"
        rows.append({"name": it["name"], "url": it["url"], "beschreibung": clean, "kategorie": s["title"], "bereich": sub["title"] if sub else "",
                     "eu": eu, "open_source": oss, "neu": it["name"] in NEU_NAMES, "seite": seite, "icon": fav_src(it["url"])})
    (DOCS / "tools.json").write_text(json.dumps({"gebaut": TODAY, "link_check": LINK_CHECK, "quelle": REPO_URL, "tools": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    with (DOCS / "tools.csv").open("w", encoding="utf-8-sig", newline="") as f:  # ohne Icon-Pfad: der hilft nur der Seite
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != "icon"], delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("ja" if v is True else "nein" if v is False else csv_safe(v)) for k, v in r.items()})
    build_search_index()
    lastmod = page_lastmod(("index.html",) + tuple(pages))
    urls = "".join(f"<url><loc>{SITE_URL}{pg}</loc><lastmod>{lastmod['index.html' if not pg else pg]}</lastmod></url>" for pg in ("",) + tuple(pages))
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      f"{urls}</urlset>\n", encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    (DOCS / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#D7FF3C"/>'
                                      '<g transform="translate(10 10) scale(1.83)" fill="none" stroke="#0E1116" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                                      + icon_body("wrench") + "</g></svg>", encoding="utf-8")


OG_SRC = ROOT / ".build" / "og.html"


def build_og(n_tools, n_cats):
    fonts = ASSETS / "fonts"
    face = "".join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url({(fonts / f).as_uri()}) format('woff2')}}"
                   for fam, w, f in (("IBM Plex Sans", "400 600", "IBMPlexSans.woff2"), ("Space Grotesk", "700", "SpaceGrotesk-700.woff2"),
                                     ("IBM Plex Mono", "500", "IBMPlexMono-500.woff2")))
    og = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>og.png</title><style>{face}
body{{margin:0;width:1200px;height:630px;background:#0E1116;color:#ECEAE3;font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden;
background-image:linear-gradient(rgba(215,255,60,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(215,255,60,.08) 1px,transparent 1px);background-size:40px 40px}}
.m{{position:absolute;left:72px;top:64px;display:flex;align-items:center;gap:16px;font:700 26px 'Space Grotesk';letter-spacing:.06em}}
.m i{{width:52px;height:52px;border-radius:14px;background:#D7FF3C;display:grid;place-items:center}}
h1{{position:absolute;left:72px;top:170px;margin:0;font:700 96px/1.02 'Space Grotesk';letter-spacing:-.03em;width:900px}}
h1 em{{font-style:normal;color:#D7FF3C}}
p{{position:absolute;left:72px;top:470px;margin:0;font:400 28px 'IBM Plex Sans';color:#B8BDC6;width:900px}}
.s{{position:absolute;right:72px;top:64px;font:500 18px 'IBM Plex Mono';color:#D7FF3C;letter-spacing:.1em}}
svg.w{{position:absolute;right:-60px;bottom:-80px;width:520px;height:520px;fill:none;stroke:#D7FF3C;stroke-width:.6;opacity:.35;stroke-linecap:round;stroke-linejoin:round}}
</style></head><body>{ICONS}
<div class="m"><i><svg width="30" height="30" fill="none" stroke="#0E1116" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><use href="#i-wrench"/></svg></i>KI-WERKSTATT</div>
<div class="s">LINK-CHECK {LINK_CHECK}</div>
<h1><em>{n_tools} KI-Tools.</em><br>Sortiert. Links geprüft.<br>Auf Deutsch.</h1>
<p>{html.escape(BRAND["tagline"])} Jedes Tool in einem Satz, EU-Anbieter markiert. {n_cats} Schubladen, Werkzeugkisten, Stack-Finder.</p>
<svg class="w" viewBox="0 0 24 24">{icon_body("wrench")}</svg>
</body></html>"""
    # Die Vorlage gehört nicht auf die Website: sie liegt im (ignorierten) Build-Ordner, render_og.js liest sie dort
    OG_SRC.parent.mkdir(exist_ok=True)
    OG_SRC.write_text(og, encoding="utf-8")
    (DOCS / "og.html").unlink(missing_ok=True)
    # og.png aus der Vorlage rendern, damit Social-Vorschau und Seite dieselben Zahlen zeigen
    if shutil.which("node"):
        env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH") or subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        r = subprocess.run(["node", str(ROOT / "scripts" / "render_og.js"), str(OG_SRC)], env=env, capture_output=True, text=True)
        if r.returncode:
            print("WARNUNG: og.png nicht aktualisiert (" + r.stderr.strip().splitlines()[-1] + "). Manuell: node scripts/render_og.js")
    else:
        print("WARNUNG: node fehlt, og.png nicht aktualisiert. Manuell: node scripts/render_og.js")


def main():
    sections, head_md = parse(SRC.read_text(encoding="utf-8"))
    uniq, n_tools, n_cats, list_secs, tools_map = build_index(sections, head_md)
    pages = build_category_pages(list_secs, tools_map)
    pages.append(build_glossar(tools_map, list_secs, sections))
    pages.append(build_trends(tools_map, list_secs))
    pages += build_einsatz(tools_map, list_secs, sections)
    pages += build_ratgeber(tools_map)
    pages += build_hubs()
    build_feed(list_secs)
    build_subpages(list_secs)
    build_data(uniq, sections, pages, list_secs)
    build_og(n_tools, n_cats)
    print(f"docs/index.html: {n_tools} Tools, {n_cats} Kategorien, {len(list(IMG.glob('cat-*.svg')))} Grafiken, {len(pages)} Unterseiten")
    from check_unique import find_duplicates
    dups = find_duplicates(DOCS)
    if dups:
        for sent, where in dups[:20]:
            print(f"  doppelt: {sent[:90]!r} in {', '.join(where)}")
        raise SystemExit(f"Abbruch: {len(dups)} Sätze stehen auf mehr als einer Seite (oder doppelt auf einer). Texte umschreiben.")
    print("Uniqueness-Check: kein Satz doppelt")
    if FAV_MISSING:
        WARN.append(f"{len(FAV_MISSING)} Hosts ohne lokales Favicon, Platzhalter geschrieben: {', '.join(sorted(FAV_MISSING)[:8])}. "
                    "Echte Icons holt python3 scripts/fetch_favicons.py --retry")
    for w in WARN:
        print("WARNUNG: " + w)


if __name__ == "__main__":
    main()
