> **Kurz gesagt:** KI-Anbieter holen deine Seiten aus drei Gründen ab: fürs Training ihrer Modelle, für ihre Suche und weil ein Mensch im Chat gerade nach einer Seite fragt. Für die ersten beiden Zwecke haben die meisten großen Anbieter getrennte Schalter, überwiegend direkt in der robots.txt. Training sperren und Suche erlauben geht also. Die robots.txt ist aber eine Bitte, kein Schloss, und für Abrufe, die ein Mensch auslöst, gilt sie nicht bei jedem Anbieter.

Grundlage sind die Crawler-Seiten von OpenAI, Google, Anthropic, Perplexity, Apple und Common Crawl, der Bing-Blog vom 30. Oktober 2026, der Entwurf zur gemeinsamen Trainingsgruppe bei der IETF und die Norm RFC 9309, die regelt, wie eine robots.txt gelesen wird. Stand ist der 2. November 2026. Was ein Anbieter nicht selbst dokumentiert, steht hier auch nicht drin.

## Drei Gründe, warum ein KI-Bot klopft

Bevor du Zeilen in die robots.txt schreibst, lohnt sich die Frage, welchen Zugriff du eigentlich regeln willst. OpenAI und Anthropic haben für jeden der drei Zwecke eine eigene Kennung, die übrigen Anbieter trennen weniger fein.

| Zweck | Was passiert | Folge einer Sperre |
|---|---|---|
| Training | Inhalte fließen in künftige Modelle ein | Deine Texte sollen nicht mehr in neue Trainingsdaten |
| Suche und Grounding | Ein Index liefert Quellen, aus denen ein Assistent seine Antwort baut und auf die er verlinkt | Deine Seiten fehlen als Quelle in KI-Antworten |
| Nutzergesteuerter Abruf | Jemand fragt im Chat nach einer Seite, der Assistent ruft sie in diesem Moment ab | Je nach Anbieter wirkungslos oder weniger Sichtbarkeit |

Grounding heißt, dass ein Modell beim Beantworten einer Frage frische Inhalte aus einem Suchindex bekommt, statt nur aus dem Gedächtnis zu antworten. Für Shops und Marken ist das der Teil, der Besuche bringt. Training dagegen bringt dir keinen Klick, sondern verbessert das Modell an sich. Viele Betriebe wollen deshalb genau das eine sperren und das andere behalten.

## Die Kennungen im Überblick

| Anbieter | Kennung | Zweck laut Anbieter |
|---|---|---|
| OpenAI | GPTBot | Training der Basismodelle |
| OpenAI | OAI-SearchBot | Suche in ChatGPT |
| OpenAI | ChatGPT-User | Abrufe, die Nutzer in ChatGPT oder über GPT Actions auslösen |
| Google | Googlebot | Google-Suche samt AI Overviews und AI Mode |
| Google | Google-Extended | Steuerung für Training und Grounding bei Gemini, ohne eigenen Crawler |
| Anthropic | ClaudeBot | Inhalte, die zum Training beitragen können |
| Anthropic | Claude-SearchBot | Indexierung für Suchergebnisse |
| Anthropic | Claude-User | Abrufe, wenn eine Frage in Claude es verlangt |
| Microsoft | Bingbot | Bing-Suche; Training und Grounding über eigene Angaben |
| Perplexity | PerplexityBot | Suchergebnisse in Perplexity, laut Anbieter kein Training |
| Perplexity | Perplexity-User | Abrufe auf Nutzerwunsch |
| Apple | Applebot | Suche in Spotlight, Siri und Safari, kann auch Apple-Modelle trainieren |
| Apple | Applebot-Extended | Steuerung für das Training, ohne eigenen Crawler |
| Common Crawl | CCBot | Offenes Archiv mit Webdaten |

Die Kennung in der Zeile `User-agent:` vergleicht ein Crawler laut RFC 9309 ohne Rücksicht auf Groß- und Kleinschreibung. Bei den Pfaden dahinter zählt die Schreibweise dagegen sehr wohl.

## Was die Anbieter im Einzelnen sagen

### OpenAI

OpenAI behandelt GPTBot und OAI-SearchBot unabhängig voneinander: Du kannst den einen sperren und den anderen zulassen, und sind beide erlaubt, nutzt OpenAI unter Umständen einen Abruf für beide Zwecke. Wer OAI-SearchBot sperrt, erscheint nicht mehr in den Suchantworten, kann aber als reiner Navigationslink auftauchen. ChatGPT-User crawlt laut OpenAI nicht automatisch, sondern ruft Seiten auf, wenn jemand im Chat danach fragt, und dafür gelten Regeln aus der robots.txt nach OpenAIs eigener Formulierung womöglich nicht. Außerdem führt OpenAI OAI-AdsBot, der nur Landingpages besucht, die als Anzeige in ChatGPT eingereicht wurden.

### Google

Bei Google hängen AI Overviews und AI Mode am normalen Googlebot, weil sie Teil der Suche sind. Wer Googlebot sperrt, verschwindet also aus der ganzen Suche, nicht nur aus den KI-Antworten. Feiner geht es mit `nosnippet`, `data-nosnippet`, `max-snippet` und `noindex` oder mit der Einstellung für generative KI in der Search Console, die laut Google kein Rankingsignal für die übrige Suche ist.

Google-Extended ist kein eigener Crawler, sondern nur eine Kennung für die robots.txt. Sie regelt, ob Inhalte, die Google ohnehin abruft, künftige Gemini-Modelle trainieren und über Grounding in der Gemini-App und bei Vertex AI genutzt werden dürfen. Auf die Aufnahme in die Google-Suche hat sie laut Google keinen Einfluss. Umgekehrt schreibt Google, dass Websites, die Google-Extended ausdrücklich erlauben, über Grounding in Antworten der Gemini-App erscheinen und Klicks bekommen können.

### Anthropic

Anthropic nennt drei Bots. ClaudeBot sammelt Inhalte, die zum Training beitragen können; eine Sperre bedeutet laut Anthropic, dass künftige Inhalte aus Trainingsdaten herausbleiben sollen. Claude-SearchBot indexiert für die Suche, Claude-User ruft Seiten ab, wenn eine Frage in Claude das erfordert. Sperrst du einen der beiden, kann deine Website laut Anthropic in den Suchergebnissen für Claude-Nutzer weniger sichtbar sein.

Nach eigener Aussage halten sich alle drei an die robots.txt und an die nicht genormte Angabe `Crawl-delay`, und sie umgehen keine CAPTCHAs. Vom Sperren per IP-Adresse rät Anthropic ab, weil die Bots dann womöglich nicht einmal deine robots.txt lesen können. Für jede Subdomain brauchst du eine eigene Regel.

### Microsoft und Bing

Microsoft hat am 30. Oktober 2026 zwei neue Angaben angekündigt, die ab dem 1. Februar 2027 mit dem nächsten Crawl greifen. Das Nein zum Training setzt du entweder über die gemeinsame Gruppe `__usage_ai-training` in der robots.txt oder pro Seite mit `<meta name="Bingbot" content="ai-training:disallow">` beziehungsweise dem passenden X-Robots-Tag; die Angabe auf der Seite schlägt die robots.txt.

Für das Grounding gibt es nur die Angabe pro Seite: `ai-grounding:disallow` sperrt die Nutzung für KI-Antworten, `ai-grounding:disallowextended` erlaubt sie nur in Diensten, die Microsoft selbst betreibt. Ohne Angabe ist beides erlaubt. An der Bing-Suche ändert keine der beiden Angaben etwas, ein Nein beim Grounding kostet aber Sichtbarkeit in KI-Antworten.

NoArchive und NoCache verlieren nach dem 1. März 2027 ihre Bedeutung für Training und Grounding. Wer sie heute nutzt, kann ab dem 15. Dezember 2026 in den Bing Webmaster Tools eine vorläufige Grounding-Angabe hinterlegen, die bis zum 30. September 2027 gilt oder bis Bing die neue Angabe auf der Seite findet. Ohne diesen Schritt gelten solche Seiten fürs Grounding als freigegeben, bis Bing sie neu gecrawlt hat. Für das Training gibt es keine Übergangslösung in den Webmaster Tools.

### Perplexity

PerplexityBot sorgt dafür, dass Websites in den Suchergebnissen von Perplexity erscheinen und verlinkt werden, und wird laut Perplexity nicht für das Training von Basismodellen eingesetzt. Perplexity-User ruft Seiten ab, wenn jemand eine Frage stellt, und ignoriert die robots.txt nach Perplexitys eigener Angabe in der Regel, weil ein Mensch den Abruf ausgelöst hat. Änderungen brauchen laut Perplexity bis zu 24 Stunden.

### Apple

Applebot liefert die Daten für die Suche in Spotlight, Siri und Safari und kann laut Apple auch Apple-Modelle für Funktionen wie Apple Intelligence trainieren. Das Training lehnst du über Applebot-Extended ab, das selbst keine Seiten crawlt. Wer Applebot-Extended sperrt, bleibt laut Apple trotzdem in den Suchergebnissen. Eine Eigenheit: Findet Applebot keine Regeln für sich, aber welche für Googlebot, folgt er denen.

### Common Crawl

CCBot sammelt für Common Crawl, eine gemeinnützige Organisation, die ein offenes Archiv mit Webdaten pflegt. Laut Common Crawl ist dieses Archiv für alle zugänglich und auswertbar. Wer dort nicht landen will, sperrt CCBot. Weil sich manche Crawler fälschlich als CCBot ausgeben, nennt Common Crawl eigene IP-Bereiche und einen Abgleich über den Reverse-DNS-Eintrag.

## Die gemeinsame Gruppe für das Training

Mit `User-agent: __usage_ai-training` gibt es seit dem 30. Oktober 2026 einen Entwurf für eine Gruppe, die nicht einen Crawler anspricht, sondern einen Zweck. Angekündigt haben die Unterstützung bisher Google, Microsoft und OpenAI. OpenAI nennt als Zeitraum die kommenden Monate, Microsoft den 1. Februar 2027, Google im Blog das Jahr 2027 und in der Crawler-Dokumentation Anfang 2027. In der Crawler-Hilfe von Anthropic (Stand 7. April 2026) kommt sie nicht vor. Für alle übrigen Crawler brauchst du weiter die einzelnen Regeln.

Der Entwurf ist ein Einzelentwurf ohne offiziellen Status bei der IETF. Inhaltlich gilt: Ein `Disallow` drückt den Wunsch aus, dass die Inhalte unter diesem Pfad nicht für KI-Training genutzt werden, ein `Allow` das Gegenteil. Die Gruppe steuert nicht, wer crawlen darf, und Regeln unter `User-agent: *` zählen nicht als Präferenz. Fehlt die Gruppe ganz, hast du nach dem Entwurf schlicht keine Präferenz geäußert. Google wertet ein Nein über die Gruppe wie eine Sperre für Google-Extended, solange du Google-Extended nicht selbst regelst. OpenAI und Google betonen, dass ihre bestehenden Kennungen weiter gelten.

## Drei Beispiele für deine robots.txt

Die Datei liegt immer unter `/robots.txt` im Wurzelverzeichnis und gilt nur für den Host, auf dem sie liegt; `shop.example.de` braucht also eine eigene. Mehrere `User-agent`-Zeilen dürfen sich laut RFC 9309 eine Gruppe teilen. Ganz wichtig: Hat ein Crawler eine eigene Gruppe, liest er nur diese und nicht zusätzlich die Gruppe unter `*`. Die Beispiele sind Vorlagen, Domain und Pfade setzt du selbst ein.

### Ziel 1: Alles erlauben

- `User-agent: *`
- `Allow: /`
- `Sitemap: https://www.example.de/sitemap.xml`

Diese drei Zeilen erlauben jedem Crawler alles und nennen die Sitemap. Eine leere oder fehlende robots.txt hat für folgsame Crawler fast dieselbe Wirkung, die ausdrückliche Fassung ist aber leichter zu lesen. Für Microsoft und das Grounding brauchst du nichts zu tun, Erlauben ist dort die Voreinstellung.

### Ziel 2: Training sperren, Suche erlauben

- `User-agent: GPTBot`
- `User-agent: ClaudeBot`
- `User-agent: Google-Extended`
- `User-agent: Applebot-Extended`
- `User-agent: CCBot`
- `Disallow: /`

- `User-agent: __usage_ai-training`
- `Disallow: /`

- `User-agent: *`
- `Allow: /`

Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot und PerplexityBot fallen hier unter die letzte Gruppe und dürfen weiter crawlen. Die gemeinsame Gruppe steht schon drin, damit du sie nicht vergisst, wenn die Anbieter sie umsetzen; bis dahin tragen die einzelnen Kennungen die Last. Bedenke den Preis von Google-Extended: Damit fällt auch das Grounding in der Gemini-App weg, denn Training und Grounding hängen bei Google an derselben Kennung. Wer dort gefunden werden will, nimmt Google-Extended aus der ersten Gruppe und gibt ihm eine eigene mit `Allow: /`. Nur dann liest Google das Nein der gemeinsamen Gruppe nicht als Sperre für Google-Extended, Gemini darf deine Inhalte dann aber auch fürs Training nutzen.

### Ziel 3: Nur bestimmte Bereiche sperren

- `User-agent: GPTBot`
- `User-agent: ClaudeBot`
- `User-agent: Google-Extended`
- `User-agent: Applebot-Extended`
- `User-agent: CCBot`
- `Disallow: /ratgeber/`
- `Disallow: /bilder/`

- `User-agent: __usage_ai-training`
- `Disallow: /ratgeber/`
- `Disallow: /bilder/`

- `User-agent: *`
- `Allow: /`

So bleiben etwa deine Ratgebertexte und eigenen Fotos aus dem Training, während Produktseiten und Pressebereich offen sind. Umgekehrt geht es auch: `Disallow: /` sperrt alles, ein zusätzliches `Allow: /presse/` gibt einen einzelnen Ordner wieder frei, denn laut RFC 9309 gewinnt die längste passende Regel. Sind eine Allow- und eine Disallow-Regel gleich lang, soll die Allow-Regel gelten.

## Wo die robots.txt an Grenzen stößt

**Freiwillig.** RFC 9309 sagt ausdrücklich, dass die Regeln keine Zugangskontrolle sind; Crawler werden gebeten, sie zu befolgen. Wer sich nicht daran hält, wird von der Datei nicht aufgehalten.

**Nutzergesteuerte Abrufe.** OpenAI schreibt zu ChatGPT-User, dass die robots.txt womöglich nicht greift, Perplexity sagt zu Perplexity-User, dass sie in der Regel ignoriert wird. Anthropic gibt dagegen an, dass auch Claude-User sich an die Regeln hält.

**Was schon gesammelt ist.** Anthropic spricht bei einer Sperre von ClaudeBot ausdrücklich von künftigen Inhalten. Der IETF-Entwurf legt fest, dass für eine Seite die Präferenz gilt, die beim Abruf in der robots.txt stand. Eine Zusage, bereits genutzte Inhalte aus fertigen Modellen zu entfernen, steht in keiner der hier zitierten Quellen.

**Verzögerung.** Crawler sollen eine gespeicherte robots.txt laut RFC 9309 höchstens 24 Stunden nutzen. OpenAI nennt für die Suche rund 24 Stunden, Perplexity bis zu 24 Stunden, die Einstellung in der Search Console braucht laut Google meist einige Tage.

**Sichtbare Pfade.** Jeder Pfad in der robots.txt ist öffentlich lesbar und damit leichter zu finden, darauf weist auch RFC 9309 hin. Interne Bereiche schützt du mit Login, nicht mit einer Zeile in der robots.txt.

**Fehlerseiten.** Antwortet `/robots.txt` mit einem Fehler zwischen 400 und 499, darf ein Crawler nach RFC 9309 alles abrufen. Bei Serverfehlern ab 500 muss er dagegen von einer vollständigen Sperre ausgehen. Ein kaputter Server kann dich also unfreiwillig aus allen Suchen werfen.

## Checkliste

1. **Bestand aufnehmen:** die aktuelle robots.txt jeder Domain und Subdomain öffnen und notieren, welche KI-Kennungen schon geregelt sind.
2. **Ziel festlegen:** pro Zweck entscheiden, also Training, Suche und Grounding getrennt, und die Entscheidung mit Datum festhalten.
3. **Gruppen schreiben:** eine der drei Vorlagen anpassen und dabei prüfen, dass Googlebot und Bingbot nicht versehentlich mitgesperrt sind.
4. **Testen:** im robots.txt-Bericht der Search Console nachsehen, ob Google die Datei abrufen konnte und Fehler meldet, und kontrollieren, dass `/robots.txt` mit Status 200 antwortet.
5. **Bing vormerken:** wer NoArchive oder NoCache nutzt, ab dem 15. Dezember 2026 die vorläufige Grounding-Angabe eintragen und bis zum 1. März 2027 die neuen Angaben auf die Seiten bringen.
6. **Logs ansehen:** nach einer Woche in den Server-Logs nachsehen, welche Bots trotz Sperre kommen, und verdächtige Besucher über die veröffentlichten IP-Listen gegenprüfen.
7. **Nachjustieren:** die gemeinsame Gruppe prüfen, sobald OpenAI, Google oder Microsoft die Umsetzung melden.

Eine robots.txt ist schnell geschrieben und schnell vergessen. Leg dir einen Termin im Kalender an, die Liste der Kennungen wächst schneller als ein Kabelbinder-Vorrat schrumpft.
