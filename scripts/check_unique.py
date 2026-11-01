#!/usr/bin/env python3
"""Prüft, dass kein Inhaltssatz auf zwei Seiten steht (und keiner doppelt auf einer Seite).

Aufruf aus dem Repo-Root:
    python3 scripts/check_unique.py

Geprüft wird der sichtbare Text jeder Seite in docs/. Nicht geprüft wird Bedien-Chrome, das auf jeder
Seite gleich sein muss: Kopfleiste, Fußzeile, Navigation, Formulare, Buttons, Sticky-Leiste, Merkliste,
Skripte und SVG. Ein Satz zählt ab sechs Wörtern; kürzere Bausteine wie "Open Source" oder
"Tools in dieser Schublade" sind Beschriftungen, keine Inhalte.
"""
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

MIN_WORDS = 6
SKIP_TAGS = {"header", "footer", "nav", "form", "script", "style", "svg", "noscript", "template", "button", "select", "textarea", "title", "head"}
SKIP_IDS = {"merk", "merk-pill", "stickybar", "totop", "searchpanel"}
SKIP_CLASSES = {"stickybar", "merk", "btn", "filters"}  # Buttons und Filter sind Bedienung, kein Inhalt
# Nur echte Block-Grenzen beenden einen Satz; Inline-Elemente (a, b, em, span, small …) gehören zum Satz
BLOCK = {"p", "li", "ol", "ul", "dl", "dd", "dt", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "tr", "table", "summary", "details",
         "div", "aside", "section", "article", "main", "blockquote", "figure", "figcaption", "body", "html"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
IGNORE_PAGES = {"og.html"}


class TextBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, skip)
        self.buf = []
        self.blocks = []

    def _skipping(self):
        return any(sk for _, sk in self.stack)

    def _flush(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if t:
            self.blocks.append(t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        skip = tag in SKIP_TAGS or a.get("id") in SKIP_IDS or bool(cls & SKIP_CLASSES) or "data-chrome" in a or "hidden" in a
        if tag in BLOCK:
            self._flush()
        self.stack.append((tag, skip))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        # bis zum passenden Tag abbauen (robust gegen nicht geschlossene Elemente)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                if tag in BLOCK:
                    self._flush()
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not self._skipping():
            self.buf.append(data)


def sentences(text):
    for part in re.split(r"(?<=[.!?…])\s+", text):
        part = part.strip()
        if len(re.findall(r"\w+", part)) >= MIN_WORDS:
            yield part


def find_duplicates(docs):
    seen = defaultdict(list)
    for f in sorted(Path(docs).glob("*.html")):
        if f.name in IGNORE_PAGES:
            continue
        parser = TextBlocks()
        parser.feed(f.read_text(encoding="utf-8"))
        parser._flush()
        for block in parser.blocks:
            for sent in sentences(block):
                seen[sent.lower()].append(f.name)
    return sorted(((s, w) for s, w in seen.items() if len(w) > 1), key=lambda x: (-len(x[1]), x[0]))


def main():
    docs = Path(__file__).resolve().parent.parent / "docs"
    dups = find_duplicates(docs)
    for sent, where in dups:
        print(f"{len(where)}x  {sent[:110]}\n     {', '.join(where)}")
    print(f"{len(dups)} doppelte Sätze")
    sys.exit(1 if dups else 0)


if __name__ == "__main__":
    main()
