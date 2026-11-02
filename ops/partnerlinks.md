# Partnerlinks (Affiliate-Links)

Infrastruktur für Partnerlinks in der KI-Werkstatt, eingebaut am 02.11.2026. **Standardmäßig aus.** Solange `data/partner.json` `"aktiv": false` hat, sieht die Seite Byte für Byte so aus wie ohne diese Funktion, und alle Transparenztexte behalten ihren bisherigen Wortlaut („Keine Affiliate-Links, keine bezahlten Platzierungen“).

Beteiligt: `data/partner.json` (Schalter und Links), `scripts/build_de_page.py` (Abschnitt „Partnerlinks“, Funktionen `tool_href` und `tool_a`, Texte `FOOT_PARTNER`, `FOOT_VERBINDUNG`, `STEP_PARTNER`, Impressum und Datenschutz in `build_subpages`), `docs/assets/style.css` (`.badge.partner`, `.partner-note`).

## Die Regel

**Ein Partnerprogramm entscheidet nie über Aufnahme, Reihenfolge oder Beschreibung eines Tools.** Ein Tool kommt in die Liste, weil es nützlich ist und der Link funktioniert, und steht dort, wo man es zuerst sucht. Ob es ein Partnerprogramm gibt, wird erst danach angeschaut. Kein Tool rückt nach oben, landet in den Favoriten, in einer Werkzeugkiste oder im Stack-Finder, weil es Provision zahlt. Fällt ein Tool aus der Liste, fällt sein Partnerlink mit.

Das passt zur Marke: Der „Feind“ in `brand/ki-werkstatt.json` sind Affiliate-Links, die als Empfehlung getarnt sind. Ein gekennzeichneter Partnerlink an einem Tool, das ohnehin in der Liste stünde, ist das Gegenteil davon.

## Aktivieren

1. Partnerprogramm abschließen (Jean). Bedingungen lesen: Manche Programme verbieten Links auf Vergleichsseiten oder verlangen bestimmte Hinweise.
2. In `data/partner.json` eintragen, Schlüssel = Tool-Name **exakt wie in `README.de.md`**, Wert = Partner-URL:
   ```json
   {"_hinweis": "…", "aktiv": true, "links": {"n8n": "https://partner.example.com/n8n?ref=kw"}}
   ```
   Steht dasselbe Tool unter zwei Namen in der Liste (etwa „DeepL“ in den Favoriten und „DeepL Übersetzer“ in der Schublade), reicht ein Name: Der Build ordnet den Partnerlink über die ursprüngliche URL allen Einträgen dieses Tools zu.
3. **`README.de.md` anpassen** (nur in der Spur, die die Liste pflegt): Zeile 10 („Affiliate- und Referral-Parameter bei Tool-Links auch“) und die Mitmachen-Regel („Ohne Affiliate- oder Referral-Parameter“) beschreiben den Zustand ohne Partnerlinks. Die README wird nicht auf die Website gerendert, steht aber auf GitHub. Vorschlag: „Fremde Affiliate- und Referral-Parameter fliegen raus; eigene Partnerlinks stehen nur auf der Website, gekennzeichnet.“ Beiträge per PR bleiben ohne Partnerparameter.
4. `python3 scripts/build_de_page.py`, dann Smoke-Test und die Prüfliste unten.

Ausschalten: `"aktiv": false`. Die Links dürfen stehen bleiben, sie werden dann ignoriert (aber weiter auf http(s) geprüft).

## Was der Build macht

- **Prüfung:** Jede URL in `links` muss mit `http://` oder `https://` beginnen, sonst bricht der Build ab (auch bei `aktiv: false`). Tool-Namen, die es in `README.de.md` nicht gibt, brechen den Build ebenfalls ab.
- **Links:** Nur bei `aktiv: true` zeigen die statischen Tool-Links auf die Partner-URL: Schubladen, Favoriten, Werkzeugkisten und Tool-Chips (Glossar, Trends, Einsatzgebiete, Ratgeber). Sie tragen `rel="sponsored noopener"` statt `rel="noopener"`.
- **Kennzeichnung:** Direkt am Tool steht das Badge „Partnerlink*“ (sichtbarer Text, Tooltip mit der Erklärung; beim Pfeil-Link der Chips steht „Partnerlink“ zusätzlich im `aria-label`). Jede Seite mit mindestens einem Badge bekommt vor der Fußzeile die Legende: „* Partnerlink: Kaufst du darüber, bekommt die KI-Werkstatt eine Provision; für dich ändert sich der Preis nicht. Auswahl und Beschreibung hängen nicht davon ab.“ mit Link ins Impressum (`#unabhaengigkeit`). Die Legende trägt `data-chrome`, damit der Uniqueness-Check sie nicht als doppelten Satz zählt.
- **Texte:** Fußzeile, Impressum („Unabhängigkeit und Werbung“) und der Schritt „Prüfen“ auf der Startseite nennen dann die Zahl der Partnerlinks, sagen, dass Auswahl, Reihenfolge und Beschreibung unabhängig davon sind, und dass es keine bezahlten Platzierungen gibt.
- **Datenschutz:** Ein eigener Abschnitt „Partnerlinks“ erscheint nur bei aktiven Partnerlinks: Weiterleitung über Anbieter oder Partnernetzwerk, dort ggf. Cookies, erst nach dem Klick, diese Seite speichert nichts.
- **Export:** `tools.json` und `tools.csv` haben das Feld `partner` (true/false bzw. ja/nein). `url` bleibt immer die ursprüngliche Anbieter-URL, auch im JSON-LD.

**Bewusst ohne Partnerlink:** Was `app.js` aus `tools.json` baut (Such-Panel, Werkzeug des Tages, 404-Überraschung, Stack-Finder-Ergebnis), verlinkt den Anbieter direkt. So steht nirgends ein Partnerlink ohne Badge, und die Merkliste speichert keine Partner-URLs aus diesen Quellen.

## Kennzeichnungspflicht

Kurzfassung, keine Rechtsberatung:

- **UWG § 5a Abs. 4:** Der kommerzielle Zweck einer geschäftlichen Handlung muss kenntlich gemacht werden, wenn er sich nicht aus den Umständen ergibt. Ein Link mit Provision an einem redaktionellen Eintrag ist so ein Fall. Die Kennzeichnung muss **am Link** stehen, nicht nur im Impressum.
- **DDG § 6 / MStV § 22:** Kommerzielle Kommunikation muss klar als solche erkennbar sein.
- **Google:** Bezahlte Links bekommen `rel="sponsored"` (Google Search Central, „Qualify your outbound links“). Das setzt der Build automatisch.
- Die Kennzeichnung muss ohne Hover verständlich sein (Mobilgeräte), deshalb sichtbarer Text am Tool plus Legende auf derselben Seite, nicht nur ein Tooltip.
- **[NEEDS_REVIEW]** Wortlaut vor dem ersten Livegang mit aktiven Partnerlinks rechtlich prüfen lassen, ebenso die Bedingungen des jeweiligen Partnerprogramms.

## Prüfliste vor dem Livegang

- [ ] Regel oben eingehalten: Kein Tool wurde wegen des Partnerprogramms neu aufgenommen, verschoben oder umformuliert (Diff von `README.de.md` und `data/stacks.json` prüfen).
- [ ] `README.de.md` angepasst (siehe Schritt 3).
- [ ] Build läuft, `scripts/smoke.js` 0 Fehler, `scripts/layer_a.py` sauber.
- [ ] Stichprobe im Browser bei 390 und 1366 px, hell und dunkel: Badge sichtbar, Legende vor der Fußzeile, Link mit `rel="sponsored noopener"`.
- [ ] Impressum, Fußzeile und Datenschutz zeigen den Partner-Text, die Zahl stimmt.
- [ ] Partner-URL einmal von Hand geöffnet: landet beim richtigen Produkt.
- [ ] `scripts/check_links.py` prüft nur die ursprünglichen URLs aus `README.de.md`. Partner-URLs stattdessen bei jeder Wiedervorlage von Hand prüfen und in `ops/backlog.md` (Wiedervorlage) einen Termin setzen.

## Getestet

02.11.2026: Build einmal mit `aktiv: true` und zwei Dummy-Links (`n8n`, `DeepL` auf `partner.example.*`). Ergebnis: Partner-URL und `rel="sponsored noopener"` an allen statischen Fundstellen (Favoriten, Schublade, Werkzeugkisten, Chips in Glossar, Trends, Einsatzgebieten und Ratgebern), Badge sichtbar bei 390 und 1366 px, Legende auf genau den Seiten mit Badge, Fußzeile, Impressum und Datenschutz mit Partner-Text, `tools.json`/`tools.csv` mit `partner` für beide Tools (DeepL über die URL auch unter „DeepL Übersetzer“), Smoke-Test 0 Fehler. Danach wieder aus; im Aus-Zustand unterscheidet sich die Ausgabe vom Stand davor nur durch die Anker-ID `unabhaengigkeit` im Impressum und die Spalte `partner` im Export.
