#!/usr/bin/env python3
"""Footprint-Scan: technische, zeitliche, strukturelle und sprachliche Spuren automatisierter Erstellung
in einer gebauten Website finden (Skill anti-ki-footprint). Nur Standardbibliothek, Python 3.11.

Aufruf:
    python3 footprint_scan.py SITE_DIR                    # gebauter Webroot, z. B. docs/ oder dist/
    python3 footprint_scan.py SITE_DIR --repo .           # zusätzlich das Quell-Repo prüfen
    python3 footprint_scan.py SITE_DIR --json             # maschinenlesbar
    python3 footprint_scan.py SITE_DIR --accept FILE      # dokumentierte Entscheidungen (JSON-Liste)
    python3 footprint_scan.py SITE_DIR --floskel-md FILE  # Floskel-Treffer als Markdown-Liste (Layer B)

Optionen: --threshold 0.6 (Anteil identischer Datumswerte, ab dem Uniformität gemeldet wird),
          --today JJJJ-MM-TT (für Tests), --max-details 12.

Schweregrade: hoch (vor Release beheben, Exit 1), mittel (beheben oder bewusst entscheiden), niedrig (Hinweis).
Modus je Befund: auto = Layer A / Technik, ohne Rückfrage beheben; jean = Entscheidung nötig (Layer B, Recht, Daten).

Der Scan ändert keine Dateien. Er schreibt nie Text um und erfindet keine Daten: Datumsbefunde sagen nur,
dass Werte auffällig gleich sind. Behoben wird ausschließlich mit echten Daten (Git-Historie, echte Änderung).

--accept-Datei: [{"id": "date-sitemap-uniform", "file": "*", "grund": "..."}]; passende Befunde zählen
nicht für den Exit-Code und stehen gesondert im Bericht.
"""
import argparse
import fnmatch
import json
import re
import statistics
import struct
import subprocess
import sys
import zlib
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

SEV_ORDER = {"hoch": 0, "mittel": 1, "niedrig": 2}
TEXT_EXT = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".csv", ".svg", ".md", ".webmanifest", ".map"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".heic", ".svg"}

# Unsichtbare Zeichen (wie layer_a.py); BOM nur am Anfang von CSV erlaubt. NBSP (U+00A0) ist normale Typografie.
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff\u00ad\u180e\u2066-\u2069\u2028\u2029]")

AI_NAMES = (r"claude|chatgpt|gpt-?[345](?:\.\d)?o?|openai|anthropic|copilot|cursor(?:rules)?|codex|gemini|bard|llama|"
            r"mistral|perplexity|midjourney|dall[-·\s]?e|stable[\s-]?diffusion|comfyui|firefly|windsurf|aider|devin|"
            r"ai[\s-]generated|ki[\s-]generiert|generated (?:by|with)|erstellt mit|prompt|\bllm\b|as an ai|language model|sprachmodell")
AI_RE = re.compile(AI_NAMES, re.I)
# Für ausgelieferte CSS/JS-Kommentare nur Werkzeugnamen und Generator-Hinweise (Produktbegriffe wie „Prompt“ sind dort oft Feature-Namen)
AI_TOOL_RE = re.compile(r"\b(?:claude|chatgpt|gpt-?[345]|openai|anthropic|copilot|codex|gemini|midjourney|windsurf|aider|devin)\b|"
                        r"ai[\s-]generated|ki[\s-]generiert|generated (?:by|with)|as an ai", re.I)

# Floskeln, die in KI-Texten überdurchschnittlich oft stehen (DE/EN). Treffer sind Hinweise, keine Beweise.
FLOSKELN = [
    # Deutsch
    r"in der heutigen (?:digitalen |schnelllebigen |modernen )?(?:welt|zeit|ära)", r"in einer welt, in der", r"nahtlos\w*",
    r"es ist (?:wichtig|entscheidend|wesentlich) zu (?:beachten|betonen|verstehen)", r"es ist wichtig, (?:zu|dass)",
    r"zusammenfassend (?:lässt sich|kann man) sagen", r"abschließend lässt sich sagen", r"alles in allem",
    r"tauchen wir (?:tiefer )?ein", r"lass(?:t)? uns (?:tiefer )?eintauchen", r"eintauchen in", r"revolution(?:är|ier)\w*",
    r"game[\s-]?changer", r"bahnbrechend\w*", r"\brobust\w*", r"ganzheitlich\w*", r"im folgenden\b", r"nicht zuletzt",
    r"darüber hinaus", r"spielt eine (?:entscheidende|zentrale|wichtige|wesentliche) rolle", r"von entscheidender bedeutung",
    r"unerlässlich", r"maßgeschneidert\w*", r"facettenreich\w*", r"auf ein neues level", r"auf die nächste stufe",
    r"(?:das|ihr|sein|dein) (?:volles|ganzes) potenzial", r"potenzial (?:voll )?(?:entfalten|ausschöpfen)",
    r"ob (?:anfänger|einsteiger) oder (?:profi|experte)", r"hand in hand", r"mühelos\w*", r"im handumdrehen",
    r"zweifel(?:los|sohne)", r"unverzichtbar\w*", r"innovative lösung\w*", r"schlüssel zum erfolg", r"herzstück",
    r"eckpfeiler", r"dreh- und angelpunkt", r"\blandschaft\b", r"\bkurz gesagt\b", r"letztendlich", r"insgesamt lässt sich",
    r"es lohnt sich,? (?:zu|einen blick)", r"werfen wir einen blick", r"egal,? ob du", r"die welt der\b",
    r"unterm strich", r"am ende des tages", r"die gute nachricht", r"genau hier setzt", r"\bder clou\b", r"auf einen blick",
    r"schritt für schritt", r"\bspoiler\b", r"\bfazit\b", r"spannend\w*", r"\bentscheidend\w*",
    # Englisch
    r"\bdelv(?:e|es|ing)\b", r"\bleverag(?:e|es|ing)\b", r"\bseamless(?:ly)?\b", r"in today'?s (?:digital |fast-paced )?(?:world|landscape|age)",
    r"it'?s (?:important|worth|crucial) to note", r"it is (?:important|worth noting|crucial)", r"\bin conclusion\b",
    r"\bgame[\s-]changer\b", r"\brevolutioni[sz]\w*", r"unlock(?:ing)? the (?:full )?potential", r"navigat\w+ the (?:complex )?(?:landscape|world)",
    r"\btapestry\b", r"\btestament to\b", r"\belevate\b", r"\bembark\w*", r"\brealm\b", r"\bholistic\b", r"\bcutting-edge\b",
    r"\bever-evolving\b", r"\b(?:let'?s )?dive (?:deep )?into\b", r"\bfurthermore\b", r"\bmoreover\b", r"\bstreamlin\w+",
    r"\bempower\w*", r"\bfoster\w*", r"\bpivotal\b", r"\bcomprehensive guide\b", r"\bwhether you'?re a\b", r"\blook no further\b",
    r"plays? a (?:crucial|pivotal|vital|key) role",
]
FLOSKEL_RE = re.compile("|".join(f"(?:{p})" for p in FLOSKELN), re.I)
HEDGES = re.compile(r"\b(?:möglicherweise|eventuell|unter umständen|gegebenenfalls|potenziell|in der regel|tendenziell|"
                    r"might|perhaps|potentially|arguably|generally speaking)\b", re.I)
AI_LEAK = re.compile(r"as an ai(?: language model)?|als (?:ki|ein ki-)?sprachmodell|als künstliche intelligenz kann ich|"
                     r"my (?:knowledge )?cutoff|stand meines wissens|regenerate response|i hope this helps|ich hoffe, das hilft|"
                     r"gerne! hier ist|certainly! here|sure! here|\[insert\b|\[einfügen|lorem ipsum", re.I)
PLACEHOLDER = re.compile(r"\[(?:[A-ZÄÖÜ][A-ZÄÖÜ0-9 ,./_-]{3,}|TODO|TBD|NEEDS_REVIEW[^\]]*)\]|\bTODO:|\{\{\s*\w+\s*\}\}")
DISCLOSURE = re.compile(
    r"(?:entsteh\w*|erstellt|geschrieben|verfasst|generiert|produziert|übersetzt)\s+(?:\w+\s+){0,3}(?:mit|durch|von)\s+(?:einer\s+)?"
    r"(?:KI|künstliche[rn]? Intelligenz|ChatGPT|Claude|Gemini)\b|mit KI-Unterstützung|KI-unterstützt (?:erstellt|geschrieben)|"
    r"(?:Recherche|Entwürfe|Textentwürfe)[^.]{0,60}\bmit (?:Hilfe von )?KI\b|"
    r"\b(?:this|the) (?:article|page|content|post|text) (?:was|is|has been) (?:\w+ ){0,2}(?:generated|written|created|drafted) "
    r"(?:with|by|using) (?:the help of )?(?:AI|ChatGPT|Claude|an AI)", re.I)
# Ein Entstehungshinweis bezieht sich nur dann auf die eigene Seite, wenn der Satz sie anspricht (sonst Tool-Beschreibung o. ä.)
SELF_REF = re.compile(r"\b(?:diese[rsnm]?|unsere?[rsnm]?|wir|hier|Recherche|Entw[üu]rfe|Textentw[üu]rfe|Seiten?|Beitr[aä]g\w*|Artikel|"
                      r"Inhalte?|Beschreibung\w*|Redaktion|this|our|we)\b", re.I)
HUMAN_CLAIM = re.compile(r"von Hand (?:\w+ ){0,3}(?:geschrieben|verfasst|formuliert|getextet)|handgeschrieben|"
                         r"von (?:echten )?Menschen (?:geschrieben|verfasst)|(?:100\s?%|komplett|rein) menschlich|ohne KI (?:geschrieben|erstellt)|"
                         r"hand-?written|hand-checked|written by (?:a |real )?humans?|human-written|no AI (?:was )?used", re.I)
EXPERIENCE = re.compile(r"\b(?:ich habe|wir haben|haben wir|habe ich) (?:\w+ ){0,3}(?:getestet|ausprobiert|gemessen|verglichen|eingesetzt|genutzt)|"
                        r"\bin unserem (?:test|praxistest|vergleich)|\bwe (?:tested|measured|tried)\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")
TRIAD = re.compile(r"\b[\wÄÖÜäöüß-]+, [\wÄÖÜäöüß-]+(?: [\wÄÖÜäöüß-]+)? (?:und|oder|and|or) [\wÄÖÜäöüß-]+")
STAND_RE = re.compile(r"\b(?:Stand|Aktualisiert|Zuletzt aktualisiert|Letzte Änderung|Updated|Last updated)\b[:\s]+(?:am\s+)?"
                      r"(\d{1,2}\.\s?\d{1,2}\.\s?\d{4}|\d{4}-\d{2}-\d{2})", re.I)
BUILD_RE = re.compile(r"\b(?:gebaut|generiert|build|built|generated|kompiliert|deployed)\b(?:\s+(?:am|on|at))?[:\s]+\d{1,4}[.\-/]\d", re.I)
WORD = re.compile(r"[A-Za-zÄÖÜäöüß0-9][\wÄÖÜäöüß'’-]*")
ABBR = re.compile(r"\b(?:z|d|u|o|s|v|bzw|ca|Nr|Abs|Art|Kap|vgl|ggf|inkl|zzgl|evtl|etc|usw|Dr|Prof|bzw|e|i)\.(?:\s?[a-zäöü]\.)?", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?!(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\b)(?=[A-ZÄÖÜ„\"0-9])")

AI_FILENAME = re.compile(r"dall[-_·\s]?e|midjourney|^mj[_-]|chatgpt[ _-]?image|generated[ _-]image|gemini[_-]generated|firefly|"
                         r"stable[-_]?diffusion|sdxl|leonardo[_-]|ideogram|^flux[-_]|imagefx|^imagen[_-]|"
                         r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
# Favicons/Logos, die nach der Domain des Anbieters heißen (www.midjourney.com.png), sind keine Generator-Ausgaben
HOST_NAME = re.compile(r"^(?:[a-z0-9-]+\.)+(?:com|ai|io|net|org|de|eu|app|co|dev|so|gg|me|tv|fr|nl|at|ch|uk|us|xyz|tech|tools)\.(?:png|jpe?g|webp|svg|ico|gif)$", re.I)
MEDIA_AI_BYTES = (b"trainedAlgorithmicMedia", b"compositeSynthetic", b"urn:c2pa", b"c2pa.", b"Midjourney", b"DALL-E", b"DALL\xc2\xb7E",
                  b"OpenAI", b"Adobe Firefly", b"Stable Diffusion", b"ComfyUI", b"Made with Google AI", b"SynthID", b"Imagen",
                  b"\"prompt\"", b"Negative prompt", b"sd-metadata", b"invokeai")

# Webroot-Dateien: (Muster, Schweregrad, Erklärung)
WEBROOT_RULES = [
    (r"(^|/)\.env(\.|$)", "hoch", "Umgebungsdatei (Zugangsdaten möglich)"),
    (r"(^|/)\.git(/|$)", "hoch", "Git-Ordner im Webroot (ganze Historie abrufbar)"),
    (r"(^|/)(CLAUDE|AGENTS|GEMINI|COPILOT)\.md$|(^|/)\.cursorrules$|(^|/)\.windsurfrules$|(^|/)copilot-instructions\.md$", "hoch", "Anweisungsdatei für KI-Assistenten"),
    (r"(^|/)\.(claude|cursor|aider[^/]*|continue|codex)(/|$)", "hoch", "Konfiguration eines KI-Assistenten"),
    (r"(^|/)[^/]*prompts?[^/]*\.(md|txt|json|ya?ml|jsonl)$|(^|/)prompts?/", "hoch", "Prompt-Datei"),
    (r"\.(ipynb|jsonl)$", "hoch", "Notebook / Log mit Rohdaten"),
    (r"(^|/)llms?[-_](debug|log|dump|raw|test)[^/]*$", "hoch", "LLM-Debug-Datei"),
    (r"\.map$", "mittel", "Source-Map (legt Quellcode und Kommentare offen)"),
    (r"\.(py|ts|tsx|scss|sass|less|sh|rb|php\.bak|toml)$", "mittel", "Quell- oder Build-Datei"),
    (r"(^|/)(package(-lock)?\.json|yarn\.lock|pnpm-lock\.yaml|requirements\.txt|Makefile|Dockerfile|\.gitignore|\.editorconfig)$", "mittel", "Build-Konfiguration"),
    (r"\.md$", "mittel", "Markdown-Rohdatei (Arbeitsnotiz/README)"),
    (r"(^|/)(\.build|build|node_modules|\.github|\.vscode|\.idea|src|ops)/", "mittel", "Build-/Arbeitsordner"),
    (r"\.(bak|orig|tmp|old|swp|log)$|~$", "mittel", "Zwischen- oder Logdatei"),
    (r"(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini)$", "niedrig", "Betriebssystem-Rest"),
]
ALLOWED_WEB = {"llms.txt", "llms-full.txt", "robots.txt", "humans.txt", "security.txt", "CNAME", ".nojekyll", "ads.txt"}


def finding(fid, sev, area, file, msg, fix, mode, details=None):
    return {"id": fid, "schwere": sev, "bereich": area, "datei": file, "befund": msg, "fix": fix, "modus": mode,
            "details": details or []}


# --------------------------------------------------------------------------- HTML
class Page(HTMLParser):
    SKIP = {"script", "style", "svg", "template", "noscript"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "blockquote", "dd", "dt", "figcaption", "summary",
             "div", "section", "article", "header", "footer", "nav", "aside", "main", "pre", "br", "tr", "label", "button", "title"}
    PROSE = {"p", "li", "blockquote", "dd"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.stack = []
        self.in_main = 0
        self.in_footer = 0
        self.has_main = False
        self.comments, self.ld, self.metas = [], [], {}
        self.blocks = []          # (tag, text, in_main, in_footer)
        self.cur = None
        self.headings = []        # (level, text)
        self.h2 = 0
        self.links = []           # (href, in_main)
        self.title = ""
        self._script_type = None
        self._script_buf = []
        self.inline_code = []     # Inhalt von <script>/<style> ohne JSON-LD

    def _flush(self):
        if self.cur and self.cur[1].strip():
            tag, txt = self.cur[0], re.sub(r"\s+", " ", self.cur[1]).strip()
            self.blocks.append((tag, txt, bool(self.in_main), bool(self.in_footer)))
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self.headings.append((int(tag[1]), txt))
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.metas.setdefault(key, []).append(a.get("content") or "")
            return
        if tag in ("script", "style"):
            self._script_type = (a.get("type") or tag).lower()
            self._script_buf = []
        if tag in self.SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "main":
            self.in_main += 1
            self.has_main = True
        if tag == "footer":
            self.in_footer += 1
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], bool(self.in_main)))
        if tag in self.BLOCK:
            self._flush()
            self.cur = [tag, ""]
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            body = "".join(self._script_buf)
            if self._script_type == "application/ld+json":
                self.ld.append(body)
            elif body.strip():
                self.inline_code.append((tag, body))
            self._script_type = None
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in self.BLOCK:
            self._flush()
            if self.stack:
                self.stack.pop()
            if self.stack:
                self.cur = [self.stack[-1], ""]
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        if tag == "footer":
            self.in_footer = max(0, self.in_footer - 1)

    def handle_data(self, data):
        if self._script_type is not None:
            self._script_buf.append(data)
            return
        if self.skip:
            return
        if self.stack and self.stack[-1] == "title" and not self.title:
            self.title = data.strip()
        if self.cur is None:
            self.cur = [self.stack[-1] if self.stack else "body", ""]
        self.cur[1] += data

    def handle_comment(self, data):
        self.comments.append(data.strip())

    def close(self):
        super().close()
        self._flush()


def words(text):
    return WORD.findall(text)


def sentences(text):
    t = ABBR.sub(lambda m: m.group(0).replace(".", "§"), text)
    return [s.replace("§", ".").strip() for s in SENT_SPLIT.split(t) if s.strip()]


def walk_ld(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("datePublished", "dateModified", "uploadDate", "dateCreated") and isinstance(v, str):
                out[k].append(v[:10])
            walk_ld(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_ld(v, out)


def ld_types(obj, out):
    if isinstance(obj, dict):
        t = obj.get("@type")
        for x in (t if isinstance(t, list) else [t]):
            if isinstance(x, str):
                out.append((x, obj))
        for v in obj.values():
            ld_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            ld_types(v, out)


def cv(values):
    values = [v for v in values if v is not None]
    if len(values) < 2 or statistics.mean(values) == 0:
        return None
    return statistics.pstdev(values) / statistics.mean(values)


def top_share(values):
    c = Counter(values)
    if not c:
        return None, 0, 0.0
    val, n = c.most_common(1)[0]
    return val, n, n / len(values)


# --------------------------------------------------------------------------- Bilder
def png_meta(data):
    i, out = 8, []
    while i + 8 <= len(data):
        ln, typ = struct.unpack(">I4s", data[i:i + 8])
        typ = typ.decode("latin-1")
        body = data[i + 8:i + 8 + ln]
        if typ in ("tEXt", "zTXt", "iTXt", "eXIf", "caBX", "tIME", "iCCP") and typ not in ("iCCP",):
            txt = body
            if typ == "zTXt":
                try:
                    k, rest = body.split(b"\0", 1)
                    txt = k + b" " + zlib.decompress(rest[1:])
                except Exception:
                    pass
            out.append((typ, txt[:4000]))
        i += 12 + ln
        if typ == "IEND":
            break
    return out


def jpeg_meta(data):
    i, out = 2, []
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker = data[i + 1]
        if marker in (0xD9, 0xDA):
            break
        ln = struct.unpack(">H", data[i + 2:i + 4])[0]
        body = data[i + 4:i + 2 + ln]
        if marker == 0xE1 and body.startswith(b"Exif"):
            out.append(("EXIF", body[:4000]))
        elif marker == 0xE1 and b"ns.adobe.com/xap" in body[:64]:
            out.append(("XMP", body[:20000]))
        elif marker == 0xEB:
            out.append(("APP11/JUMBF (C2PA)", body[:4000]))
        elif marker == 0xED:
            out.append(("APP13/IPTC", body[:4000]))
        elif marker == 0xFE:
            out.append(("COM", body[:2000]))
        i += 2 + ln
    return out


def webp_meta(data):
    i, out = 12, []
    while i + 8 <= len(data):
        typ = data[i:i + 4].decode("latin-1")
        ln = struct.unpack("<I", data[i + 4:i + 8])[0]
        if typ in ("EXIF", "XMP "):
            out.append((typ.strip(), data[i + 8:i + 8 + min(ln, 20000)]))
        i += 8 + ln + (ln & 1)
    return out


def scan_image(path, rel):
    res = []
    data = path.read_bytes()
    ext = path.suffix.lower()
    if AI_FILENAME.search(path.name) and not HOST_NAME.match(path.name):
        res.append(finding("media-filename", "mittel", "Medien", rel, "Dateiname nach Muster eines Bildgenerators",
                           "Sprechend umbenennen (Motiv statt Generator-Name) und Links anpassen. Pflichtkennzeichnung bleibt davon unberührt.",
                           "jean"))
    if ext == ".svg":
        txt = data.decode("utf-8", "replace")
        hits = [m.group(0) for m in AI_RE.finditer(" ".join(re.findall(r"<!--(.*?)-->", txt, re.S)) + " " +
                                                   " ".join(re.findall(r"<metadata>(.*?)</metadata>", txt, re.S)))]
        gen = re.findall(r"Generator: [^\n>]{0,80}|inkscape:version|sodipodi:docname|Created with [^\n<]{0,60}", txt)
        if hits:
            res.append(finding("media-meta-ai", "hoch", "Medien", rel, f"SVG-Kommentar/Metadaten nennen KI-Werkzeug: {', '.join(sorted(set(hits))[:5])}",
                               "Kommentare und <metadata> entfernen (svgo o. ä.), sofern keine Pflichtkennzeichnung darin steckt.", "auto"))
        elif gen:
            res.append(finding("media-meta", "niedrig", "Medien", rel, f"SVG mit Editor-Metadaten ({gen[0][:60]})",
                               "Mit svgo o. ä. bereinigen.", "auto"))
        return res
    chunks = []
    try:
        if data.startswith(b"\x89PNG"):
            chunks = png_meta(data)
        elif data[:2] == b"\xff\xd8":
            chunks = jpeg_meta(data)
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            chunks = webp_meta(data)
    except Exception:
        pass
    ai = sorted({m.decode("latin-1") for m in MEDIA_AI_BYTES if m in data})
    if not ai:
        for _, body in chunks:
            if AI_RE.search(body.decode("latin-1")) or re.search(rb"^parameters\0|Software\0.*(?:AI|Diffusion)", body):
                ai = ["Textfeld mit KI-Angabe"]
                break
    if ai:
        res.append(finding("media-meta-ai", "hoch", "Medien", rel, f"KI-Herkunftsangabe in den Metadaten: {', '.join(ai[:5])}",
                           "Erst prüfen: Deepfake/realistische Darstellung (AI Act Art. 50 Abs. 4) oder Produktbild im Merchant Center "
                           "(IPTC DigitalSourceType Pflicht)? Dann Metadaten BEHALTEN und sichtbar kennzeichnen. Sonst Metadaten entfernen (Layer A).",
                           "jean", [c for c, _ in chunks]))
    elif chunks:
        kinds = sorted({c for c, _ in chunks})
        sev = "mittel" if any(k in ("EXIF", "XMP", "eXIf", "APP13/IPTC", "APP11/JUMBF (C2PA)", "caBX") for k in kinds) else "niedrig"
        res.append(finding("media-meta", sev, "Medien", rel, f"Metadaten-Blöcke: {', '.join(kinds)}",
                           "Metadaten entfernen (Layer A), z. B. exiftool -all= oder PNG ohne Text-Chunks neu schreiben; "
                           "GPS-/Kameradaten sind auch ein Datenschutzthema.", "auto"))
    return res


# --------------------------------------------------------------------------- Scan
class Scan:
    def __init__(self, site, repo=None, threshold=0.6, today=None, max_details=12):
        self.site = Path(site).resolve()
        self.repo = Path(repo).resolve() if repo else None
        self.thr = threshold
        self.today = today or date.today().isoformat()
        self.maxd = max_details
        self.f = []
        self.pages = {}       # rel -> dict
        self.stats = {}
        self.floskel_rows = []  # (seite, satz, floskel)

    def add(self, *a, **k):
        self.f.append(finding(*a, **k))

    def rel(self, p):
        return p.relative_to(self.site).as_posix()

    # ---- Dateien im Webroot
    def files(self):
        out = []
        for p in sorted(self.site.rglob("*")):
            if p.is_file() or (p.is_dir() and p.name == ".git"):
                out.append(p)
        return out

    def check_webroot(self, files):
        hits = defaultdict(list)
        for p in files:
            r = self.rel(p)
            if r in ALLOWED_WEB or re.search(r"(^|/)\.git/", r):
                continue
            for pat, sev, why in WEBROOT_RULES:
                if re.search(pat, r, re.I):
                    hits[(sev, why)].append(r)
                    break
        for (sev, why), rs in sorted(hits.items(), key=lambda x: SEV_ORDER[x[0][0]]):
            self.add("webroot-file", sev, "Technik", rs[0] if len(rs) == 1 else f"{len(rs)} Dateien", f"{why} im Webroot",
                     "Aus dem Veröffentlichungsordner entfernen bzw. vom Deployment ausschließen (Build-Ausgabe nur mit Besucher-Dateien).",
                     "auto", rs[:self.maxd])
        if (self.site / "llms.txt").exists():
            self.stats["llms_txt"] = "vorhanden (normaler Webstandard, bleibt)"

    def check_text_files(self, files):
        inv = []
        for p in files:
            if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
                continue
            try:
                txt = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            r = self.rel(p)
            body = txt[1:] if p.suffix.lower() == ".csv" and txt.startswith("\ufeff") else txt
            n = len(INVISIBLE.findall(body))
            if n:
                inv.append(f"{r}: {n}")
            if p.suffix.lower() in (".js", ".css", ".mjs"):
                if "sourceMappingURL=" in txt:
                    self.add("sourcemap", "mittel", "Technik", r, "Verweis auf Source-Map (sourceMappingURL)",
                             "Source-Maps im Produktions-Build abschalten und Kommentar entfernen.", "auto")
                comments = re.findall(r"/\*.*?\*/", txt, re.S) + re.findall(r"(?<![:\"'\w\\])//[^\n]*", txt)
                ai = sorted({m.group(0).lower() for c in comments for m in AI_TOOL_RE.finditer(c)})
                if ai:
                    self.add("asset-comment-ai", "mittel", "Technik", r, f"Kommentare in ausgeliefertem Code nennen: {', '.join(ai[:8])}",
                             "Kommentare beim Build entfernen (Minifier) oder neutral formulieren.", "auto")
                elif len(comments) >= 20:
                    self.add("asset-comment", "niedrig", "Technik", r, f"{len(comments)} Kommentare in ausgeliefertem Code",
                             "Optional minifizieren; inhaltlich unkritisch, wenn keine Tool-/Prompt-Hinweise drinstehen.", "auto")
        if inv:
            self.add("text-invisible", "hoch", "Sprache", f"{len(inv)} Dateien", "Unsichtbare Unicode-Zeichen (Zero-Width, Bidi, Soft Hyphen, BOM)",
                     "Layer A: Zeichen entfernen (layer_a.py --fix o. ä.).", "auto", inv[:self.maxd])

    # ---- HTML-Seiten
    def parse_pages(self, files):
        for p in files:
            if p.is_file() and p.suffix.lower() in (".html", ".htm"):
                pg = Page()
                try:
                    pg.feed(p.read_text(encoding="utf-8", errors="replace"))
                    pg.close()
                except Exception as e:  # kaputtes HTML nicht verschlucken
                    self.add("html-parse", "niedrig", "Technik", self.rel(p), f"HTML nicht vollständig lesbar: {e}", "HTML prüfen.", "auto")
                    continue
                robots = " ".join(pg.metas.get("robots", [])).lower()
                ld = []
                for raw in pg.ld:
                    try:
                        ld.append(json.loads(raw))
                    except ValueError:
                        pass
                main_blocks = [b for b in pg.blocks if b[2]] if pg.has_main else [b for b in pg.blocks if not b[3]]
                text = " ".join(b[1] for b in main_blocks)
                self.pages[self.rel(p)] = {"pg": pg, "noindex": "noindex" in robots, "ld": ld, "main": main_blocks, "text": text,
                                           "words": len(words(text))}

    def check_html_tech(self):
        gen_meta, comments_ai, comments_other, ai_meta = [], [], Counter(), []
        for r, d in self.pages.items():
            pg = d["pg"]
            for g in pg.metas.get("generator", []):
                gen_meta.append(f"{r}: {g}")
            for k in pg.metas:
                if re.search(r"ai-(?:generated|content)|ki-generiert|ai-disclosure|ai-content-declaration", k):
                    ai_meta.append(f"{r}: {k}")
            for c in pg.comments:
                if not c or c.startswith("[if") or c.startswith("<!["):
                    continue
                if AI_RE.search(c) or re.search(r"\bTODO\b|FIXME|generated|generiert", c, re.I):
                    comments_ai.append(f"{r}: <!--{c[:70]}-->")
                else:
                    comments_other[c[:40]] += 1
            for tag, code in pg.inline_code:
                cm = re.findall(r"/\*.*?\*/", code, re.S) + re.findall(r"(?<![:\"'\w\\])//[^\n]*", code)
                if any(AI_RE.search(c) for c in cm):
                    comments_ai.append(f"{r}: Kommentar in inline-<{tag}>")
        if gen_meta:
            sev = "hoch" if any(AI_RE.search(g) for g in gen_meta) else "mittel"
            self.add("generator-meta", sev, "Technik", f"{len(gen_meta)} Seiten", "<meta name=\"generator\"> verrät das Werkzeug",
                     "Meta-Tag im Template entfernen.", "auto", gen_meta[:self.maxd])
        if ai_meta:
            self.add("disclosure-meta", "mittel", "Recht/Hinweise", f"{len(ai_meta)} Seiten", "Maschinenlesbarer KI-Hinweis im <head>",
                     "Freiwilliger Hinweis: darf weg. Pflichtfall (Deepfake, Merchant Center): bleibt.", "jean", ai_meta[:self.maxd])
        if comments_ai:
            self.add("comment-ai", "hoch", "Technik", f"{len(comments_ai)} Stellen", "HTML-Kommentare mit Tool-/KI-/Prompt-/TODO-Hinweisen",
                     "Kommentare aus der Ausgabe entfernen (Template oder Post-Processing).", "auto", comments_ai[:self.maxd])
        if comments_other:
            total = sum(comments_other.values())
            self.add("comment", "niedrig", "Technik", f"{total} Kommentare", "HTML-Kommentare in der Ausgabe (Template-Marker o. ä.)",
                     "Beim Schreiben der Seiten entfernen; sie helfen Besuchern nicht.", "auto",
                     [f"{n}x <!--{c}-->" for c, n in comments_other.most_common(self.maxd)])

    def check_text(self):
        disc, claims, leaks, placeholders, build = [], [], [], [], []
        for r, d in self.pages.items():
            full = " ".join(b[1] for b in d["pg"].blocks) + " " + d["pg"].title
            for b in d["pg"].blocks:
                for s in sentences(b[1]):
                    if DISCLOSURE.search(s) and SELF_REF.search(s):
                        disc.append(f"{r}: {s[:160]}")
            for m in HUMAN_CLAIM.finditer(full):
                claims.append(f"{r}: …{full[max(0, m.start() - 50):m.end() + 30]}…")
            for m in AI_LEAK.finditer(full):
                leaks.append(f"{r}: {m.group(0)}")
            for m in PLACEHOLDER.finditer(full):
                placeholders.append(f"{r}: {m.group(0)[:50]}")
            foot = " ".join(b[1] for b in d["pg"].blocks if b[3])
            for m in BUILD_RE.finditer(foot):
                build.append(f"{r}: {m.group(0)}")
        if claims:
            self.add("claim-human", "hoch", "Recht/Hinweise", f"{len(claims)} Stellen", "Behauptung menschlicher Handarbeit (muss nachweislich stimmen)",
                     "Wenn nicht belegbar: durch wahre neutrale Beschreibung ersetzen (z. B. „auf Deutsch formuliert, an der Herstellerseite abgeglichen“). "
                     "Nie durch eine andere falsche Behauptung.", "auto", claims[:self.maxd])
        if disc:
            self.add("disclosure-voluntary", "mittel", "Recht/Hinweise", f"{len(disc)} Stellen", "Freiwilliger Hinweis auf KI-Entstehung im Text",
                     "Darf entfallen, wenn keine Pflicht besteht (AI Act Art. 50 Abs. 4: Deepfakes; Texte zu Themen öffentlichen Interesses ohne "
                     "redaktionelle Verantwortung). Redaktionelle Verantwortung/Impressum bleibt stehen. Kontext prüfen: Fachtexte ÜBER KI sind kein Hinweis.",
                     "jean", disc[:self.maxd])
        if leaks:
            self.add("lang-ai-leak", "hoch", "Sprache", f"{len(leaks)} Stellen", "Typische Chatbot-Reste im Text",
                     "Satz löschen oder neu formulieren (Inhalt prüfen).", "jean", leaks[:self.maxd])
        by_page = defaultdict(list)  # je Seite ein Befund, damit --accept auf einzelne Seiten zielen kann
        for x in placeholders:
            by_page[x.split(": ", 1)[0]].append(x)
        for r, xs in sorted(by_page.items()):
            self.add("lang-placeholder", "hoch", "Sprache", r, f"{len(xs)} Platzhalter oder Prüfmarker im sichtbaren Text",
                     "Mit echten Angaben füllen oder entfernen; nichts erfinden.", "jean", xs[:self.maxd])
        if build:
            self.add("date-build-visible", "mittel", "Datum", f"{len(build)} Seiten", "Build-/Generierungsdatum in der Fußzeile",
                     "Entfernen oder durch ein inhaltlich echtes Datum ersetzen (letzte Änderung der Seite).", "auto", build[:self.maxd])

    def check_language(self):
        per_page = []
        flo_total = Counter()
        cvs, emd, triads_s, sent_total, hedges_n, words_total = [], 0, 0, 0, 0, 0
        emoji_h = []
        for r, d in sorted(self.pages.items()):
            if d["noindex"]:
                continue
            prose = [b[1] for b in d["main"] if b[0] in Page.PROSE]
            text = d["text"]
            nw = d["words"]
            words_total += nw
            hits = []
            for b in d["main"]:
                for s in sentences(b[1]):
                    for m in FLOSKEL_RE.finditer(s):
                        hits.append((m.group(0), s))
            for fl, s in hits:
                flo_total[fl.lower()] += 1
                self.floskel_rows.append((r, s, fl))
            if nw >= 150 and len(hits) * 1000 / nw > 5:
                per_page.append(f"{r}: {len(hits)} Treffer auf {nw} Wörter")
            emd += text.count("—")
            sl = [len(words(s)) for p in prose for s in sentences(p) if len(words(s)) >= 3]
            sent_total += len(sl)
            if len(sl) >= 20:
                c = cv(sl)
                if c is not None:
                    cvs.append((r, round(c, 2), len(sl)))
            triads_s += sum(1 for p in prose for s in sentences(p) if TRIAD.search(s))
            hedges_n += len(HEDGES.findall(text))
            for lvl, h in d["pg"].headings:
                if lvl <= 3 and EMOJI.match(h):
                    emoji_h.append(f"{r}: {h[:50]}")
        self.stats["floskeln"] = {"gesamt": sum(flo_total.values()), "top": flo_total.most_common(15)}
        if flo_total:
            sev = "mittel" if per_page else "niedrig"
            self.add("lang-floskeln", sev, "Sprache", f"{len(per_page)} Seiten über 5/1000 Wörter",
                     f"{sum(flo_total.values())} Floskel-Treffer gesamt; häufigste: " + ", ".join(f"{k} ({v})" for k, v in flo_total.most_common(8)),
                     "Layer B: NUR markieren und Jean fragen. Nicht automatisch umschreiben (--floskel-md erzeugt die Liste).", "jean", per_page[:self.maxd])
        if words_total:
            dens = emd * 1000 / words_total
            self.stats["geviertstrich_je_1000_woerter"] = round(dens, 2)
            if dens > 2:
                self.add("lang-emdash", "mittel", "Sprache", "gesamt", f"Geviertstrich (—) {dens:.1f}× je 1000 Wörter",
                         "Layer B: markieren; im Deutschen meist Halbgeviertstrich, Komma oder Punkt. Nur nach Rückfrage ändern.", "jean")
        if cvs:
            med = statistics.median(c for _, c, _ in cvs)
            low = [f"{r}: CV {c} ({n} Sätze)" for r, c, n in sorted(cvs, key=lambda x: x[1]) if c < 0.35]
            self.stats["satzlaengen_cv_median"] = med
            if low:
                self.add("lang-burstiness", "mittel", "Sprache", f"{len(low)} Seiten", "Sehr gleichförmige Satzlängen (Variationskoeffizient < 0,35)",
                         "Layer B: markieren; Jean entscheidet über Überarbeitung (kurze und lange Sätze mischen).", "jean", low[:self.maxd])
        if sent_total >= 50 and triads_s / sent_total > 0.2:
            self.add("lang-triads", "niedrig", "Sprache", "gesamt", f"{triads_s / sent_total:.0%} der Sätze enthalten Dreier-Aufzählungen",
                     "Layer B: markieren.", "jean")
        if words_total and hedges_n * 1000 / words_total > 6:
            self.add("lang-hedging", "niedrig", "Sprache", "gesamt", f"Hedging {hedges_n * 1000 / words_total:.1f}× je 1000 Wörter",
                     "Layer B: markieren; klare Aussagen, wo die Quelle es trägt.", "jean")
        if emoji_h:
            self.add("lang-emoji-heading", "niedrig", "Struktur", f"{len(emoji_h)} Überschriften", "Emoji am Anfang von Überschriften",
                     "Emoji aus Überschriften nehmen (Template), Inhalt unverändert.", "auto", emoji_h[:self.maxd])

    def check_structure(self):
        idx = {r: d for r, d in self.pages.items() if not d["noindex"]}
        if len(idx) < 8:
            return
        h2 = {r: sum(1 for l, _ in d["pg"].headings if l == 2) for r, d in idx.items()}
        val, n, share = top_share(list(h2.values()))
        self.stats["h2_verteilung"] = dict(Counter(h2.values()).most_common(8))
        if share >= self.thr:
            self.add("struct-h2", "mittel", "Struktur", f"{n} von {len(idx)} Seiten", f"{share:.0%} der Seiten haben genau {val} H2-Überschriften",
                     "Gliederung je Seite am Inhalt ausrichten (Jean-Entscheidung, keine Füll-Abschnitte).", "jean")
        faq = {}
        for r, d in idx.items():
            items = []
            for obj in d["ld"]:
                ld_types(obj, items)
            q = sum(len(o.get("mainEntity", [])) for t, o in items if t == "FAQPage" and isinstance(o.get("mainEntity"), list))
            if q:
                faq[r] = q
        if len(faq) >= 5:
            val, n, share = top_share(list(faq.values()))
            self.stats["faq_verteilung"] = dict(Counter(faq.values()).most_common(8))
            if share >= self.thr:
                self.add("struct-faq", "mittel", "Struktur", f"{n} von {len(faq)} FAQ-Seiten", f"{share:.0%} der FAQ-Blöcke haben genau {val} Fragen",
                         "FAQ-Anzahl nach echten Nutzerfragen richten; keine Fragen erfinden, schwache streichen (Jean).", "jean")
        paras = [sum(1 for b in d["main"] if b[0] == "p") for d in idx.values()]
        c = cv(paras)
        if c is not None and c < 0.15:
            self.add("struct-paragraphs", "niedrig", "Struktur", "gesamt", f"Absatzanzahl kaum unterschiedlich (CV {c:.2f})",
                     "Layer B/Jean: Seitenlänge am Thema ausrichten.", "jean")
        dl = [len(d["pg"].metas.get("description", [""])[0]) for d in idx.values() if d["pg"].metas.get("description")]
        c = cv(dl)
        self.stats["meta_desc_laenge"] = {"min": min(dl) if dl else 0, "max": max(dl) if dl else 0, "cv": round(c, 3) if c else None}
        if c is not None and c < 0.06 and len(dl) >= 8:
            self.add("struct-meta-len", "niedrig", "Struktur", "gesamt", f"Meta-Descriptions fast gleich lang (CV {c:.3f})",
                     "Länge am Inhalt ausrichten; kein Auffüllen auf Zielwert.", "jean")
        titles = [d["pg"].title for d in idx.values() if d["pg"].title]
        if titles:
            suf = titles[0]
            for t in titles[1:]:
                while suf and not t.endswith(suf):
                    suf = suf[1:]
            core = [t[:len(t) - len(suf)] if suf and len(suf) < len(t) else t for t in titles]
            shapes = [re.sub(r"[^:|–—\-#?!]", "", re.sub(r"\d+", "#", x)) for x in core]
            val, n, share = top_share(shapes)
            if share >= self.thr and val:
                self.add("struct-title-pattern", "niedrig", "Struktur", f"{n} Titel", f"{share:.0%} der Titel folgen demselben Muster ({val!r})",
                         "Titel je Seite formulieren; Muster ist kein Fehler, nur auffällig in der Masse.", "jean")
        blk_pages = defaultdict(set)
        for r, d in idx.items():
            for b in d["pg"].blocks:
                if len(b[1]) >= 25:
                    blk_pages[b[1]].add(r)
        common = {t for t, ps in blk_pages.items() if len(ps) >= 0.8 * len(idx)}
        shares = []
        for r, d in idx.items():
            tot = sum(len(words(b[1])) for b in d["pg"].blocks) or 1
            boil = sum(len(words(b[1])) for b in d["pg"].blocks if b[1] in common)
            shares.append(boil / tot)
        mean = statistics.mean(shares)
        self.stats["boilerplate_anteil"] = round(mean, 3)
        if mean > 0.35:
            self.add("struct-boilerplate", "mittel" if mean > 0.5 else "niedrig", "Struktur", "gesamt",
                     f"Im Schnitt {mean:.0%} des Seitentexts stehen auf ≥ 80 % aller Seiten (Navigation, Fußzeile, Formulare)",
                     "Wiederholte Blöcke kürzen oder auf eine Seite verlinken; Hauptinhalt je Seite stärken.", "jean")

    def check_dates(self):
        thr = self.thr
        future = []
        # Sitemap
        lm = []
        for sm in sorted(self.site.glob("*sitemap*.xml")):
            xml = sm.read_text(encoding="utf-8", errors="replace")
            for u in re.findall(r"<url>(.*?)</url>", xml, re.S):
                m = re.search(r"<lastmod>\s*([^<\s]+)", u)
                if m:
                    lm.append(m.group(1)[:10])
        if lm:
            dist = Counter(lm)
            self.stats["sitemap_lastmod"] = dict(sorted(dist.items()))
            val, n, share = top_share(lm)
            future += [f"sitemap: {x}" for x in set(lm) if x > self.today]
            if len(lm) >= 5 and share >= thr:
                extra = " (= heutiges Datum, wahrscheinlich Build-Datum)" if val == self.today else ""
                self.add("date-sitemap-uniform", "hoch", "Datum", "sitemap.xml", f"{share:.0%} der lastmod-Werte sind {val}{extra}",
                         "lastmod je Seite aus echten Ereignissen ableiten: letzter Commit, der den Inhalt der Quelle änderte "
                         "(Domain-/URL-/Chrome-/Rebuild-Commits ignorieren). Nie streuen oder rückdatieren. Bleibt die Häufung echt, Jean informieren.",
                         "auto")
        # JSON-LD und article:*-Meta
        ld_dates = defaultdict(dict)
        for r, d in self.pages.items():
            if d["noindex"]:
                continue
            acc = defaultdict(list)
            for obj in d["ld"]:
                walk_ld(obj, acc)
            for k in ("datePublished", "dateModified"):
                if acc.get(k):
                    ld_dates[k][r] = max(acc[k])
            for meta, k in (("article:published_time", "datePublished"), ("article:modified_time", "dateModified")):
                if d["pg"].metas.get(meta) and r not in ld_dates[k]:
                    ld_dates[k][r] = d["pg"].metas[meta][0][:10]
        for k, sev in (("dateModified", "hoch"), ("datePublished", "mittel")):
            vals = list(ld_dates[k].values())
            future += [f"{k}: {r} {v}" for r, v in ld_dates[k].items() if v > self.today]
            if vals:
                self.stats[f"ld_{k}"] = dict(sorted(Counter(vals).items()))
            val, n, share = top_share(vals)
            if len(vals) >= 5 and share >= thr:
                self.add(f"date-ld-{k[4:].lower()}-uniform", sev, "Datum", f"{n} Seiten", f"{share:.0%} der {k}-Werte (JSON-LD/Meta) sind {val}",
                         "Aus der Git-Historie der jeweiligen Quelle ableiten (erstes Erscheinen / letzte inhaltliche Änderung). Nichts erfinden.",
                         "auto")
        pub = list(ld_dates["datePublished"].values())
        if len(pub) >= 10:
            val, n, share = top_share(pub)
            if share > 0.5:
                self.add("date-mass-publish", "mittel", "Datum", f"{n} Seiten", f"{n} Seiten am selben Tag veröffentlicht ({val})",
                         "Nicht rückdatieren. Künftige Inhalte gestaffelt veröffentlichen (Redaktionsplan), wenn das zum Projekt passt.", "jean")
        mod = ld_dates["dateModified"]
        same = [r for r, v in mod.items() if ld_dates["datePublished"].get(r) == v]
        if len(mod) >= 5 and len(same) == len(mod):
            self.add("date-ld-same", "niedrig", "Datum", f"{len(same)} Seiten", "datePublished = dateModified auf allen Seiten",
                     "Nur ein Hinweis: stimmt es (nie geändert), bleibt es. Sonst echte Daten aus der Historie einsetzen.", "auto")
        # Feed
        feed_dates = []
        for fx in sorted(self.site.glob("*.xml")):
            xml = fx.read_text(encoding="utf-8", errors="replace")
            if "<feed" not in xml and "<rss" not in xml:
                continue
            for e in re.findall(r"<(?:entry|item)\b.*?</(?:entry|item)>", xml, re.S):
                # Änderungsdatum zuerst: genau dort steht ein einheitliches Build-Datum, auch wenn published variiert
                m = re.search(r"<(?:updated|lastBuildDate)>\s*([^<]+)", e) or re.search(r"<(?:pubDate|published)>\s*([^<]+)", e)
                if m:
                    feed_dates.append(m.group(1).strip()[:16])
        if feed_dates:
            self.stats["feed_daten"] = dict(sorted(Counter(x[:10] if x[:4].isdigit() else x for x in feed_dates).items()))
            val, n, share = top_share(feed_dates)
            if len(feed_dates) >= 5 and share >= thr:
                self.add("date-feed-uniform", "mittel", "Datum", "Feed", f"{share:.0%} der Feed-Einträge tragen denselben Zeitstempel ({val})",
                         "Je Eintrag das echte Datum (erstes Erscheinen / letzte Änderung des Eintrags) setzen.", "auto")
        # Sichtbare Stand-Daten
        stand = {}
        for r, d in self.pages.items():
            if d["noindex"]:
                continue
            ds = STAND_RE.findall(d["text"])
            if ds:
                stand[r] = Counter(ds).most_common(1)[0][0]
        if len(stand) >= 5:
            val, n, share = top_share(list(stand.values()))
            if share >= thr:
                self.add("date-stand-uniform", "mittel", "Datum", f"{n} Seiten", f"Sichtbares „Stand“-Datum auf {share:.0%} der Seiten gleich ({val})",
                         "Je Seite das Datum der letzten inhaltlichen Änderung zeigen (dasselbe wie dateModified).", "auto")
        if future:
            self.add("date-future", "hoch", "Datum", f"{len(future)} Werte", "Datumswerte in der Zukunft",
                     "Auf das echte Datum korrigieren.", "auto", future[:self.maxd])

    def check_experience(self):
        idx = {r: d for r, d in self.pages.items() if not d["noindex"]}
        if not idx:
            return
        all_links = [h.lower() for d in self.pages.values() for h, _ in d["pg"].links]
        if not any(re.search(r"impressum|imprint|legal-notice|legal", h) for h in all_links):
            self.add("exp-impressum", "hoch", "Erfahrung/Vertrauen", "gesamt", "Kein Link auf Impressum/Anbieterkennzeichnung gefunden",
                     "Impressum mit echten Angaben verlinken (DDG § 5).", "jean")
        arts, no_author, no_src, no_data = [], [], [], []
        exp_hits = 0
        for r, d in idx.items():
            items = []
            for obj in d["ld"]:
                ld_types(obj, items)
            is_art = any(t in ("Article", "BlogPosting", "NewsArticle", "TechArticle") for t, _ in items) or \
                "article" in d["pg"].metas.get("og:type", [""])[0]
            if not is_art:
                continue
            arts.append(r)
            persons = [o for t, o in items if t in ("Article", "BlogPosting", "NewsArticle", "TechArticle")
                       for a in ([o.get("author")] if isinstance(o.get("author"), dict) else o.get("author") or [])
                       if isinstance(a, dict) and a.get("@type") == "Person"]
            if not persons and not re.search(r"\b(?:Autor(?:in)?|Von|By)\s*:?\s+[A-ZÄÖÜ][a-zäöüß]+ [A-ZÄÖÜ][a-zäöüß]+", d["text"]):
                no_author.append(r)
            ext = [h for h, m in d["pg"].links if m and h.startswith("http")]
            if d["words"] > 600 and not ext:
                no_src.append(r)
            if d["words"] > 600 and len(re.findall(r"\d", d["text"])) < 10:
                no_data.append(r)
            exp_hits += len(EXPERIENCE.findall(d["text"]))
        if no_author:
            self.add("exp-author", "niedrig", "Erfahrung/Vertrauen", f"{len(no_author)} Artikel", "Artikel ohne Personen-Byline",
                     "Nur eine ECHTE Person mit echter Biografie nennen, wenn es sie gibt (Jean). Keine Persona erfinden; "
                     "Organisation als Autor ist zulässig.", "jean", no_author[:self.maxd])
        if no_src:
            self.add("exp-sources", "niedrig", "Erfahrung/Vertrauen", f"{len(no_src)} Artikel", "Lange Artikel ohne externe Quelle",
                     "Echte Primärquellen verlinken.", "jean", no_src[:self.maxd])
        if no_data:
            self.add("exp-data", "niedrig", "Erfahrung/Vertrauen", f"{len(no_data)} Artikel", "Lange Artikel fast ohne Zahlen/Daten",
                     "Belegbare Zahlen ergänzen, keine erfundenen.", "jean", no_data[:self.maxd])
        if arts and exp_hits == 0:
            self.add("exp-experience", "niedrig", "Erfahrung/Vertrauen", f"{len(arts)} Artikel", "Keine Formulierungen eigener Erfahrung (getestet, gemessen …)",
                     "Nur ECHTE Eigenbeobachtungen ergänzen (Jean). Keine erfundenen Tests.", "jean")

    def check_repo(self):
        repo = self.repo
        if not repo or not (repo / ".git").exists():
            return
        try:
            tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True).stdout.decode("utf-8", "replace").split("\0")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return
        tracked = [t for t in tracked if t]
        conspicuous = [t for t in tracked if re.search(
            r"(^|/)(CLAUDE|AGENTS|GEMINI)\.md$|(^|/)\.(claude|cursor|aider|codex)|copilot-instructions|(^|/)prompts?/|prompt[^/]*\.(md|txt)$|"
            r"BRAND-VOICE|(^|/)ops/|audit|\.ipynb$", t, re.I)]
        if conspicuous:
            self.add("repo-files", "mittel", "Repo", f"{len(conspicuous)} Dateien", "Arbeits-/Steuerdateien im Quell-Repo (bei öffentlichem Repo für Google sichtbar)",
                     "Nicht eigenmächtig löschen. Optionen: privates Quell-Repo + öffentliches Publish-Repo nur mit Webroot; Pages aus privatem Repo (GitHub Pro); "
                     "Hosting über Vercel/Netlify/Cloudflare Pages aus privatem Repo.", "jean", conspicuous[:self.maxd])
        trail = re.compile(r"Co-Authored-By:\s*(?:Claude|Copilot|ChatGPT|Codex|Cursor|Devin|Aider|Gemini)|Claude-Sess(?:ion):|claude\.ai/code|"
                           r"Generated with \[Claude|\U0001F916 Generated|session_[0-9A-Za-z]{12,}|Codex(?:-| )(?:findings|review)", re.I)
        txt_hits = []
        for t in tracked:
            p = repo / t
            if p.suffix.lower() not in TEXT_EXT | {".py", ".yml", ".yaml", ".sh", ""} or not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            try:
                n = len(trail.findall(p.read_text(encoding="utf-8")))
            except (UnicodeDecodeError, OSError):
                continue
            if n:
                txt_hits.append(f"{t}: {n}")
        claims = []
        for t in tracked:
            if t.lower().endswith(".md") and (repo / t).is_file():
                try:
                    claims += [f"{t}: {m.group(0)}" for m in HUMAN_CLAIM.finditer((repo / t).read_text(encoding="utf-8"))]
                except (UnicodeDecodeError, OSError):
                    pass
        if claims:
            self.add("repo-claim-human", "mittel", "Repo", f"{len(claims)} Stellen", "Behauptung menschlicher Handarbeit in Markdown-Dateien des Repos",
                     "Nur stehen lassen, wenn belegbar; sonst wahr und neutral formulieren.", "auto", claims[:self.maxd])
        if txt_hits:
            self.add("repo-text", "mittel", "Repo", f"{len(txt_hits)} Dateien", "Dateien im Repo nennen KI-Sitzungen/Trailer",
                     "Bei öffentlichem Repo sichtbar; Jean entscheidet (neutralisieren oder Repo privat).", "jean", txt_hits[:self.maxd])
        try:
            log = subprocess.run(["git", "-C", str(repo), "log", "--format=%an|%ae|%B%x1e"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
            commits = [c for c in log.split("\x1e") if c.strip()]
            who = re.compile(r"claude|anthropic|copilot|codex|cursor|devin|aider|openai|chatgpt|gemini", re.I)
            ai_c = [c for c in commits if who.search("|".join(c.strip().split("|", 2)[:2])) or trail.search(c)]
        except (subprocess.CalledProcessError, FileNotFoundError):
            commits, ai_c = [], []
        if ai_c:
            self.stats["commits_ki_markiert"] = f"{len(ai_c)} von {len(commits)}"
            self.add("repo-commits", "mittel", "Repo", f"{len(ai_c)} von {len(commits)} Commits", "Commit-Autor oder -Trailer nennt einen KI-Assistenten",
                     "Historie nicht ohne Jean umschreiben (Force-Push, bricht Forks/PRs). Wirksamer: Quell-Repo privat, Publish-Repo ohne Historie.", "jean")
        try:
            remote = subprocess.run(["git", "-C", str(repo), "remote", "-v"], capture_output=True, text=True).stdout
        except FileNotFoundError:
            remote = ""
        inside = str(self.site).startswith(str(repo))
        if inside and "github.com" in remote:
            self.add("repo-public-build", "mittel", "Repo", "Repo", "Webroot liegt im selben GitHub-Repo wie Generator, Daten und Arbeitsdateien",
                     "Falls das Repo öffentlich ist: Build-Skripte, Quellen und Historie sind für jeden (auch Google) lesbar. Optionen siehe repo-files.", "jean")

    def run(self, accept=None):
        files = self.files()
        self.check_webroot(files)
        self.check_text_files(files)
        for p in files:
            if p.is_file() and p.suffix.lower() in IMG_EXT:
                self.f.extend(scan_image(p, self.rel(p)))
        self.parse_pages(files)
        self.check_html_tech()
        self.check_text()
        self.check_language()
        self.check_structure()
        self.check_dates()
        self.check_experience()
        self.check_repo()
        # Medienbefunde je Art zusammenfassen
        merged, media = [], defaultdict(list)
        for x in self.f:
            if x["id"] in ("media-meta", "media-filename") and x["schwere"] != "hoch":
                media[(x["id"], x["schwere"], x["befund"].split(":")[0])].append(x)
            else:
                merged.append(x)
        for (fid, sev, _), xs in media.items():
            y = dict(xs[0])
            if len(xs) > 1:
                y["datei"] = f"{len(xs)} Dateien"
                y["details"] = [f"{x['datei']}: {x['befund']}" for x in xs[:self.maxd]]
            merged.append(y)
        self.f = merged
        for x in self.f:
            x["akzeptiert"] = None
            for a in accept or []:
                if a.get("id") == x["id"] and fnmatch.fnmatch(x["datei"], a.get("file", "*")):
                    x["akzeptiert"] = a.get("grund", "akzeptiert")
        self.f.sort(key=lambda x: (x["akzeptiert"] is not None, SEV_ORDER[x["schwere"]], x["bereich"], x["id"]))
        return self.f


def floskel_markdown(rows, out):
    by_page = defaultdict(list)
    for r, s, fl in rows:
        by_page[r].append((s, fl))
    lines = ["# Floskel-Treffer (Layer B, nur markiert)", "",
             f"{len(rows)} Treffer auf {len(by_page)} Seiten. Nichts wurde umgeschrieben; Entscheidung je Treffer: behalten / umformulieren.", ""]
    for r in sorted(by_page):
        lines += [f"## {r} ({len(by_page[r])})", "", "| Floskel | Satz |", "|---|---|"]
        for s, fl in by_page[r]:
            lines.append(f"| {fl} | {s.replace('|', '/')[:300]} |")
        lines.append("")
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="KI-/Generator-Footprints in einer gebauten Website finden.")
    ap.add_argument("site", help="gebauter Webroot (z. B. docs, dist, public)")
    ap.add_argument("--repo", help="Quell-Repository zusätzlich prüfen")
    ap.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    ap.add_argument("--threshold", type=float, default=0.6, help="Anteil gleicher Werte für Uniformitäts-Befunde (Standard 0.6)")
    ap.add_argument("--accept", help="JSON-Datei mit dokumentierten Entscheidungen")
    ap.add_argument("--floskel-md", help="Floskel-Treffer als Markdown schreiben (Layer-B-Liste)")
    ap.add_argument("--today", help="Datum für Tests (JJJJ-MM-TT)")
    ap.add_argument("--max-details", type=int, default=12)
    a = ap.parse_args(argv)
    site = Path(a.site)
    if not site.is_dir():
        sys.exit(f"footprint_scan: {site} ist kein Ordner")
    accept = json.loads(Path(a.accept).read_text(encoding="utf-8")) if a.accept else []
    sc = Scan(site, a.repo, a.threshold, a.today, a.max_details)
    res = sc.run(accept)
    if a.floskel_md:
        floskel_markdown(sc.floskel_rows, a.floskel_md)
    open_ = [x for x in res if not x["akzeptiert"]]
    summ = {s: sum(1 for x in open_ if x["schwere"] == s) for s in SEV_ORDER}
    summ["akzeptiert"] = sum(1 for x in res if x["akzeptiert"])
    if a.json:
        print(json.dumps({"zusammenfassung": summ, "statistik": sc.stats, "befunde": res}, ensure_ascii=False, indent=1))
    else:
        print(f"Footprint-Scan {site} ({len(sc.pages)} HTML-Seiten)" + (f", Repo {a.repo}" if a.repo else ""))
        for x in res:
            tag = f"[{x['schwere'].upper()}]" + (" [akzeptiert]" if x["akzeptiert"] else "")
            print(f"\n{tag} {x['id']} · {x['bereich']} · {x['datei']} · {x['modus']}")
            print(f"  Befund: {x['befund']}")
            print(f"  Fix:    {x['fix']}")
            if x["akzeptiert"]:
                print(f"  Grund:  {x['akzeptiert']}")
            for d in x["details"][:a.max_details]:
                print(f"    - {d}")
        st = sc.stats
        print("\nStatistik: " + "; ".join(x for x in (
            f"Floskeln {st['floskeln']['gesamt']}" if "floskeln" in st else "",
            f"Satzlängen-CV Median {st['satzlaengen_cv_median']:.2f}" if "satzlaengen_cv_median" in st else "",
            f"Geviertstriche je 1000 Wörter {st['geviertstrich_je_1000_woerter']}" if "geviertstrich_je_1000_woerter" in st else "",
            f"Boilerplate {st['boilerplate_anteil']:.0%}" if "boilerplate_anteil" in st else "",
            f"H2-Verteilung {st['h2_verteilung']}" if "h2_verteilung" in st else "",
            f"FAQ-Verteilung {st['faq_verteilung']}" if "faq_verteilung" in st else "") if x))
        if "sitemap_lastmod" in sc.stats:
            print("\nsitemap lastmod: " + ", ".join(f"{k}: {v}" for k, v in sc.stats["sitemap_lastmod"].items()))
        print(f"\nErgebnis: {summ['hoch']} hoch, {summ['mittel']} mittel, {summ['niedrig']} niedrig, {summ['akzeptiert']} akzeptiert")
    return 1 if summ["hoch"] else 0


if __name__ == "__main__":
    sys.exit(main())
