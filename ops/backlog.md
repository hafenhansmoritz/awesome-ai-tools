# Backlog: 90-Tage-Plan für organischen Traffic

Quelle: Deep Research vom 29.10.2026 (Google Search Central, GitHub-Doku, OpenAI-Doku). Belegt = ✅, eigene Ableitung = 🟡, Erfahrungswert ohne geprüfte Quelle = ⚠️.
Status: `[ ]` offen, `[~]` in Arbeit, `[x]` erledigt (mit Datum und PR). Wer: **Claude** (Autopilot) oder **Jean** (braucht Konto, Geld oder eine Entscheidung).

## Phase 1: Technik (Woche 1–2)

- [ ] **Jean** ✅ Eigene Domain kaufen und für GitHub Pages einrichten (Apex und www, beide DNS-Einträge, dann „Enforce HTTPS“). Danach greifen robots.txt und Sitemap an der Domain-Wurzel.
- [ ] **Claude** ✅ Nach Domain-Umzug: `SITE_URL` im Generator umstellen, `docs/CNAME` anlegen, Canonicals, Sitemap, Feed, og:url prüfen, alte github.io-Adresse auf Weiterleitung testen. Erst wenn Jean die Domain nennt.
- [ ] **Jean** ✅ Google Search Console: Property anlegen, Sitemap `sitemap.xml` einreichen. Bis zur eigenen Domain ist das der einzige sichere Weg, weil `robots.txt` unter einem github.io-Unterpfad ignoriert wird.
- [ ] **Jean** 🟡 Optional, falls die Domain dauert: Repo `jmp-collab.github.io` anlegen lassen, damit dort eine `robots.txt` an der Host-Wurzel mit Sitemap-Verweis liegt. Claude kann das Repo befüllen, sobald es existiert und freigegeben ist.
- [ ] **Claude** ✅ `robots.txt`: OAI-SearchBot und Googlebot erlauben, Entscheidung zu GPTBot (Training) dokumentieren. Wirkt erst an der Domain-Wurzel.
- [ ] **Claude** ✅ Structured Data prüfen: kein SoftwareApplication-Markup mit erfundenen Bewertungen, kein Carousel für Tool-Listen. Article, FAQPage, BreadcrumbList, ItemList bleiben.
- [x] **Claude** Prüfskripte `scripts/layer_a.py` und `scripts/smoke.js`, wöchentlicher Link-Check per GitHub Action (29.10.2026).

## Phase 2: Substanz (Woche 2–6)

- [ ] **Claude** ✅ Werkstatt-Notizen für die 40 wichtigsten Tools (geplanter Skill `werkstatt-tool-notizen`, noch nicht eingerichtet), 10 pro Lauf. Fortschritt: 0 von 40.
- [ ] **Claude** ✅ Keine dünnen Einzelseiten pro Tool. Wenn je Einzelseiten entstehen, nur mit eigener Prüfung, sonst `noindex`.
- [ ] **Claude** ⚠️ Vergleichs- und „Alternative zu“-Ratgeber, je einer pro Ratgeber-Lauf, Reihenfolge siehe Themenliste.

## Phase 3: Ratgeber-Takt und Distribution (Woche 3–12)

- [ ] **Claude** ✅ Ratgeber im Zwei-Wochen-Takt (geplanter Skill `werkstatt-ratgeber`, noch nicht eingerichtet), Primärquellen mit Datum.
- [ ] **Claude** ✅ Wöchentlich News und Trends (geplanter Skill `werkstatt-news`, noch nicht eingerichtet).
- [ ] **Claude** 🟡 Linkaufbau nur sauber: Badges für Hersteller höchstens mit `rel="sponsored"` oder `nofollow`, kein Linktausch.
- [ ] **Claude** ⚠️ Datenstudie aus dem Link-Check, z. B. „Wie viele KI-Tools haben ihren Sitz in der EU, wie viele Links sind nach einem Jahr tot?“ als Ratgeber mit Grafik.
- [ ] **Jean** ⚠️ Verbreitung: Hinweis im PROMPTGOTT-Newsletter, in DACH-Communities und Eintrag in passenden GitHub-Awesome-Listen (Beiträge unter Jeans Namen, Claude liefert Texte).
- [ ] **Jean** Für den monatlichen SEO-Audit die Semrush-Verbindung für geplante Aufgaben freigeben (sonst läuft der Audit ohne Keyword-Daten).

## Themenliste für Ratgeber (Reihenfolge, oben zuerst)

1. ChatGPT-Alternativen mit EU-Option: Le Chat, Langdock, Claude, Gemini, lokale Modelle
2. Kostenlose KI-Tools, die wirklich kostenlos sind: Grenzen der Gratis-Tarife
3. KI für Produkttexte im Shop: Workflow, Feed, Qualitätskontrolle
4. Midjourney-Alternativen für kommerzielle Bilder: Lizenzen und Rechte
5. Microsoft Copilot, ChatGPT oder Gemini fürs Büro: Vergleich nach Datenschutz und Preis
6. KI-Meeting-Protokolle DSGVO-konform: Werkzeuge und Einwilligung
7. Prompting-Grundlagen auf Deutsch: zehn Muster, die im Alltag tragen
8. KI im Kundenservice per E-Mail: Vorsortieren, Antworten, Freigaben
9. Datenstudie aus dem Link-Check (siehe Phase 3)
10. KI-Videos für Social Media: Werkzeuge, Kennzeichnung, Kosten

## Offene Fragen aus der Recherche

- Deutsche Suchvolumina und Wettbewerber für „KI Tools für …“, „… Alternative“, „kostenlos“, „DSGVO“: mit Semrush klären, sobald verfügbar.
- Offizielle Aussagen von Perplexity und Google-Extended zu Crawling und Opt-out.
- Belastbare Fallstudien zu Distributionskanälen für Tool-Verzeichnisse.

## Wiedervorlage

Zeitgebundene Aussagen auf der Seite. Am Stichtag die Primärquelle prüfen, alle genannten Stellen gemeinsam anpassen, Zeile abhaken.

| Stichtag | Wo | Was prüfen |
|---|---|---|
| [ ] 01.11.2026 | `data/trends.json` (browser, offene-standards), `content/ratgeber/mcp-agent-skills.md` (Tabelle Keynote/Pages/Numbers) | Firefox Smart Window in Deutschland gestartet? Apple-MCP in Keynote, Pages, Numbers ab November verfügbar? (Mozilla-Blog, Apple Newsroom) |
| [ ] 01.11.2026 | `data/trends.json` (agenten-hintergrund), `content/ratgeber/ki-agenten-sicher.md` | Automatischer Modus in den Claude-Apps tatsächlich Voreinstellung? „ab Ende Oktober“ in die Vergangenheit setzen (claude.com, Artikel zum Auto-Modus) |
| [ ] 01.12.2026 | `content/ratgeber/ki-modelle-preise.md` (Preistabelle, Rechenbeispiel), `data/trends.json` (preisrutsch) | Gemini 4 Argon: Einführungspreis endet am 30.11. Zeile streichen, Rechenbeispiel auf 4/20 Dollar umstellen (Preisseite der Gemini API) |
| [ ] 01.12.2026 | `content/ratgeber/mcp-agent-skills.md` (Abschnitt Stripe) | Nimmt Stripe keine Vollzugriffs-Schlüssel mehr an? Satz in die Vergangenheit setzen (Stripe-Doku zu MCP) |
| [ ] 03.12.2026 | `data/trends.json` (ai-act), `content/ratgeber/ki-inhalte-kennzeichnen.md`, `content/ratgeber/ki-produktbilder-shops.md`, `data/glossar.json` (EU AI Act) | Übergangsfrist Art. 50 Abs. 2 abgelaufen, neue Verbote seit 2.12.2026: Futur zu Präsens (EUR-Lex, Verordnung (EU) 2026/1744) |
| [ ] 15.12.2026 | `content/ratgeber/ki-produktbilder-shops.md` (Werkzeuge und Kosten) | OpenAI-Doku nennt inzwischen GPT Image 2.5, der Ratgeber GPT Image 2: Modellname und Preise prüfen (developers.openai.com, Image generation) |
| [ ] 16.01.2027 | `content/ratgeber/mcp-agent-skills.md` (Shopify) | Alte Knowledge-Base-App nach dem 15.01.2027 eingestellt? Satz anpassen (Shopify Changelog) |
| [ ] 31.01.2027 | `content/ratgeber/ki-produktbilder-shops.md` (Merchant Center) | Mindestgröße 500 × 500 Pixel gilt jetzt: Futur zu Präsens (Merchant-Center-Hilfe, image_link) |
| [ ] 02.02.2027 | `content/ratgeber/ki-inhalte-kennzeichnen.md` (Was deine Tools liefern müssen) | Gemeinsame Erkennung von Wasserzeichen verschiedener Hersteller laut Kodex fällig: umgesetzt? (EU-Kommission, Code of Practice) |
| [ ] 30.04.2027 | `README.de.md` (Amazon Q Developer) | Support für die IDE-Plugins endet: Eintrag streichen oder auf Kiro verweisen (AWS) |
| [ ] 29.04.2027 | `README.de.md`, `data/trends.json` (europa), `content/ratgeber/ki-modelle-preise.md` | Halbjahres-Check Mistral Large 4: Lizenz, API-Preise (0,70/2,10 Dollar seit 29.10.2026), kleinere Ableger (mistral.ai/news) |
