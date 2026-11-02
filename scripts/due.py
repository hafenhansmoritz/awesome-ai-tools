#!/usr/bin/env python3
"""Fällige Wiedervorlagen aus ops/backlog.md (Tabelle unter „## Wiedervorlage“).

Zeilenformat: | [ ] TT.MM.JJJJ | Dateien | Aufgabe |   ([ ] offen, [~] in Arbeit, [x] erledigt)

Aufruf aus dem Repo-Root, nur Standardbibliothek:
    python3 scripts/due.py                 # offene Punkte mit Stichtag bis heute
    python3 scripts/due.py --tage 14       # ... bis heute + 14 Tage
    python3 scripts/due.py --monat         # ... bis Ende des laufenden Monats (so läuft der Workflow)
    python3 scripts/due.py --markdown      # Liste als Markdown für ein Issue; ohne fällige Punkte keine Ausgabe
    python3 scripts/due.py --titel         # nur den Issue-Titel ausgeben, z. B. „Wiedervorlage November 2026“
    python3 scripts/due.py --heute 2026-12-01   # Stichtag zum Testen

Exit-Code immer 0: fällige Punkte sind eine Erinnerung, kein Fehler. Zeilen mit unlesbarem Datum werden mit
ausgegeben, damit sie jemand repariert. .github/workflows/wiedervorlage.yml legt daraus monatlich ein Issue an.
"""
import argparse
import calendar
import re
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "ops" / "backlog.md"
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
ROW = re.compile(r"^\|\s*\[(?P<st>[ ~xX])\]\s*(?P<datum>[^|]*?)\s*\|(?P<wo>[^|]*)\|(?P<was>.*)\|\s*$")


def rows(text):
    """Zeilen der Tabelle im Abschnitt „## Wiedervorlage“ (bis zur nächsten Überschrift)."""
    sec = re.search(r"^## Wiedervorlage\s*$(.*?)(?=^#{1,2} |\Z)", text, re.M | re.S)
    if not sec:
        raise SystemExit("ops/backlog.md: Abschnitt „## Wiedervorlage“ nicht gefunden")
    out = []
    for line in sec.group(1).splitlines():
        m = ROW.match(line.strip())
        if not m:
            continue
        try:
            d = datetime.strptime(m["datum"], "%d.%m.%Y").date()
        except ValueError:
            d = None
        out.append({"status": m["st"].lower(), "datum": d, "datum_txt": m["datum"], "wo": m["wo"].strip(), "was": m["was"].strip()})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tage", type=int, default=0, help="auch Punkte bis heute + N Tage")
    ap.add_argument("--monat", action="store_true", help="auch Punkte bis Ende des laufenden Monats")
    ap.add_argument("--markdown", action="store_true", help="Markdown-Liste für ein Issue, leer wenn nichts fällig")
    ap.add_argument("--titel", action="store_true", help="nur den Issue-Titel ausgeben")
    ap.add_argument("--heute", type=date.fromisoformat, default=date.today(), help="Stichtag JJJJ-MM-TT (Test)")
    ap.add_argument("--datei", type=Path, default=BACKLOG)
    a = ap.parse_args()

    heute = a.heute
    if a.titel:
        print(f"Wiedervorlage {MONATE[heute.month - 1]} {heute.year}")
        return
    bis = heute + timedelta(days=max(0, a.tage))
    if a.monat:
        bis = max(bis, heute.replace(day=calendar.monthrange(heute.year, heute.month)[1]))
    offen = [r for r in rows(a.datei.read_text(encoding="utf-8")) if r["status"] != "x"]
    faellig = sorted((r for r in offen if r["datum"] and r["datum"] <= bis), key=lambda r: r["datum"])
    kaputt = [r for r in offen if not r["datum"]]

    if a.markdown:
        if not faellig and not kaputt:
            return
        print(f"Fällige Punkte aus der Wiedervorlage in `ops/backlog.md`, Stichtag bis {bis:%d.%m.%Y} (Stand {heute:%d.%m.%Y}).")
        print("Am Stichtag die Primärquelle prüfen, alle genannten Stellen gemeinsam anpassen, Zeile in `ops/backlog.md` abhaken.\n")
        def safe(t):  # @name und #123 aus der Tabelle sollen im Issue niemanden anpingen und nichts verlinken
            return re.sub(r"#(?=\d)", "&#35;", t).replace("@", "&#64;")  # erst #, sonst trifft es das # in &#64;
        for r in faellig:
            ueber = " **(überfällig)**" if r["datum"] < heute else ""
            arbeit = " _(in Arbeit)_" if r["status"] == "~" else ""
            print(f"- [ ] **{r['datum']:%d.%m.%Y}**{ueber}{arbeit}: {safe(r['was'])}\n  Wo: {safe(r['wo'])}")
        for r in kaputt:
            print(f"- [ ] Datum nicht lesbar ({r['datum_txt']!r}), bitte im Format TT.MM.JJJJ eintragen: {safe(r['was'][:120])}")
        return

    if not faellig:
        print(f"Nichts fällig bis {bis:%d.%m.%Y}. Offen insgesamt: {len(offen)}.")
    for r in faellig:
        flag = "überfällig " if r["datum"] < heute else ""
        print(f"{r['datum']:%d.%m.%Y} {flag}[{r['status']}] {r['wo']}\n    {r['was']}")
    for r in kaputt:
        print(f"Datum nicht lesbar: {r['datum_txt']!r} | {r['was'][:100]}")


if __name__ == "__main__":
    main()
