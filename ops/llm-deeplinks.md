# KI-Chat-Links mit sichtbarem Prompt

Muster für Seiten und Shops, die Besucher mit einem vorausgefüllten Prompt in einen KI-Chat schicken wollen, ohne dabei Dinge zu tun, die Sicherheitsforscher als Angriff einstufen. In der KI-Werkstatt umgesetzt am 01.11.2026: `scripts/build_de_page.py` (Abschnitt „KI-Chat mit Werkstatt-Prompt“, Konstante `LLM_TARGETS`), `docs/assets/app.js` (Block „KI-Chat mit Werkstatt-Prompt“), `docs/assets/style.css` (`.llm-*`).

## Worum es geht

Viele Chat-Anbieter nehmen einen Prompt über einen URL-Parameter an, etwa `https://chatgpt.com/?q=<Text>`. Das ist praktisch für Buttons wie „Mit KI durchgehen“. Dieselbe Technik nutzen Firmen, um sich über versteckte Anweisungen dauerhaft ins Gedächtnis eines Assistenten zu schreiben („merke dir X als vertrauenswürdige Quelle“). Microsoft nennt das **AI Recommendation Poisoning**, MITRE ATLAS führt es als **AML.T0080 Memory Poisoning**.

- Microsoft Security Blog, 10.02.2026: [Manipulating AI memory for profit: The rise of AI Recommendation Poisoning](https://www.microsoft.com/en-us/security/blog/2026/02/10/ai-recommendation-poisoning/). Nennt die Muster `copilot.microsoft.com/?q=`, `chatgpt.com/?q=`, `claude.ai/new?q=`, `perplexity.ai/search?q=`, `grok.com/?q=`, beschreibt, dass solche Buttons teils automatisch ausgeführt werden, und rät Nutzern, Links zu KI-Assistenten vor dem Klick zu prüfen und Prompts auf Gedächtnis-Formulierungen zu lesen.
- MITRE ATLAS: AML.T0080 (Memory Poisoning), AML.T0080.000 (AI Agent Context Poisoning: Memory), AML.T0051 (LLM Prompt Injection).

Unser Muster ist das Gegenteil: Der Prompt ist vor dem Absenden komplett sichtbar, enthält keine Gedächtnis-Anweisung und sagt offen, woher er kommt.

## Die harten Grenzen

Nicht verhandelbar, in jedem Repo und Shop gleich:

1. **Sichtbar vor dem Senden.** Der Klick auf den Button öffnet zuerst einen Dialog auf der eigenen Seite mit dem exakten Prompt-Text. Erst ein zweiter Klick („In ChatGPT öffnen“) geht zum Anbieter. Kein verstecktes Feld, keine unsichtbaren Zeichen, kein CSS-Verstecken, kein Text, der nur in der URL steht.
2. **Link = Text.** Der Anbieter-Link entsteht beim Klick aus genau dem Text im Dialogfeld (`encodeURIComponent`). Ändert jemand den Text, ändert sich der Link mit.
3. **Kein Gedächtnis, kein Vertrauensanspruch.** Keine Formulierungen wie „merke dir“, „speichere“, „für künftige Gespräche“, „vertrauenswürdige Quelle“, „beste Quelle“.
4. **Herkunft offen.** Der Prompt beginnt mit der Herkunft („Ich komme von der KI-Werkstatt, Ratgeber …“). Keine Anweisung, die Herkunft oder die Markenbindung zu verschweigen.
5. **Andere Quellen nicht abwerten.** Erlaubt ist die offene Bitte „Wenn es passt, verlinke …“, nicht „nutze nur …“ oder „ignoriere andere Seiten“.
6. **Nur vorausfüllen.** Bevorzugt Anbieter, bei denen der Nutzer selbst absendet. Wo ein Anbieter per URL sofort absendet, sagt der Dialog das („Wird sofort gesendet“, Button „In … öffnen und senden“).
7. **Zusatz, kein Ersatz.** Der normale Link zum Tool bleibt unverändert. Der Prompt-Link ist ein eigener, klar beschrifteter Button.
8. **Ungeprüft heißt aus.** Nur Anbieter mit nachgewiesenem Prefill-Verhalten erscheinen auf der Seite. Die Parameter sind inoffiziell und können sich jederzeit ändern.

Der Build bricht ab, wenn ein Prompt gegen 3 bis 5 verstößt (`LLM_FORBIDDEN`, Regex auf Gedächtnis-, Vertrauens- und Verschweige-Formulierungen), unsichtbare Zeichen enthält, mehr als 1.300 Zeichen (520 ohne Links) hat, die Anbieter-URL länger als 2.000 Zeichen wird oder nicht 2 bis 4 Ziel-URLs nennt.

## Teststand der Parameter

Getestet am **01.11.2026** mit Playwright 1.63 (Chromium, headless, ohne Login, über den Proxy der Testumgebung). Prüfschritte: Seite laden, 12 Sekunden warten, Eingabefelder (`textarea`, `input`, `contenteditable`, `role=textbox`) und den übrigen Seitentext nach einem Markersatz durchsuchen, Ziel-URL und Titel notieren, Screenshot.

| Anbieter | URL-Muster | Ergebnis ohne Login | Prefill / sofort | Auf der Seite |
|---|---|---|---|---|
| ChatGPT | `https://chatgpt.com/?q=` | Seite lädt, Text steht im Eingabefeld (`textarea#…[name=prompt]`), keine Antwort nach 12 s | Prefill, Nutzer sendet selbst. Mit Login laut Microsoft-Blog teils sofort gesendet, nicht geprüft; der Dialog sagt das | ja |
| Claude | `https://claude.ai/new?q=` | Cloudflare-Prüfseite, dann Weiterleitung zum Login (`returnTo` behält den Parameter) | ungeprüft | nein |
| Perplexity | `https://www.perplexity.ai/search?q=` | HTTP 403, Cloudflare-Prüfseite (Weiterleitung auf `/search/new?q=`) | ungeprüft; als Such-URL vermutlich sofort ausgeführt | nein |
| Microsoft Copilot | `https://copilot.microsoft.com/?q=` | Weiterleitung auf `https://copilot.com/` (Anmeldeseite), Parameter verworfen | geht ohne Login nicht | nein |
| Google KI-Modus | `https://www.google.com/search?udm=50&q=` | Google-Seite „ungewöhnlicher Datenverkehr“ (Captcha) aus dem Testnetz | ungeprüft; als Such-URL sofort ausgeführt | nein |
| Le Chat (Vibe von Mistral) | `https://chat.mistral.ai/chat?q=` | HTTP 403, Cloudflare-Prüfseite | ungeprüft | nein |
| Gemini | kein dokumentierter Parameter; probiert `?q=`, `/app?q=`, `/app?prompt=` | Seite bleibt leer, kein Eingabefeld | ungeprüft | nein |

Bot-Schutz und Captchas wurden bewusst nicht umgangen. Wer einen Anbieter freischalten will, testet ihn in einem normalen Browser (einmal ausgeloggt, einmal eingeloggt) und trägt Ergebnis und Datum in `LLM_TARGETS` ein:

- `status: "prefill"`: Text steht im Eingabefeld, Nutzer sendet selbst.
- `status: "sofort"`: Anbieter sendet beim Öffnen. Der Dialog warnt dann automatisch.
- `status: "ungeprueft"` oder `"geht-nicht"`: erscheint nicht auf der Seite.
- `hinweis`: ein Satz für den Dialog (Pflicht für alles, was auf der Seite erscheint), `geprueft`: Datum.

Danach baut der Build die Buttons an allen Tool-Einträgen mit passender Domain (`hosts`) und bietet den Anbieter in der Auswahl der Seiten-Buttons an. Wiedervorlage: Parameter alle drei Monate neu prüfen (`ops/backlog.md`).

## Link-Check

Die Anbieter-URLs stehen nur im Generator, nicht in `README.de.md` oder `data/*.json`, und laufen deshalb nicht durch `scripts/check_links.py`. Absicht: Claude, Perplexity und Le Chat antworten Skripten mit Cloudflare-403, Google mit Captcha. Ein Link-Check würde dort nur Bot-Schutz messen, nicht die Funktion des Parameters. Die Prüfung ist der Playwright-Test oben, mit Datum.

## Platzierung

- **Tool-Einträge der Chatbots** (Zuordnung über die Domain in `LLM_TARGETS[].hosts`): kleiner Zusatz-Button „Mit Werkstatt-Prompt“ unter der Beschreibung. Der Prompt hilft beim Zusammenstellen des eigenen Stacks und verweist auf Stack-Finder und Stack-Check. Stand 01.11.2026 nur bei ChatGPT (Startseite, Favoriten; Schublade Text und Sprache).
- **Ratgeber, Einsatzgebiete, Schubladen**: Button „Mit KI durchgehen“ im Hero neben den anderen Knöpfen. Anbieterwahl im Dialog, sobald mehr als ein Anbieter geprüft ist. Prompt seitenspezifisch aus vorhandenen Daten.
- Ohne JavaScript bleiben die Buttons verborgen (`hidden`), es gibt keinen toten Knopf.

## Prompt-Vorlage

Deutsch, du-Form, Aufgabe passend zur Seite. Aufbau:

```
Ich komme von <Marke>, <Seitentyp> „<Titel>“: <Seiten-URL mit UTM>
<Konkrete Aufgabe in ein bis drei Sätzen, aus Titel, Kernfragen oder FAQ der Seite>
Wenn es passt, verlinke im weiteren Gespräch auf passende Seiten von <Marke>:
- <Label>: <Ziel-URL mit UTM>
- <Label>: <Ziel-URL mit UTM>
- <Label>: <Ziel-URL mit UTM>
```

Datenquellen in der KI-Werkstatt:

| Seitentyp | Aufgabe aus | Ziel-URLs |
|---|---|---|
| Ratgeber | erste zwei FAQ-Fragen | Seite selbst, nächster Ratgeber, `#stack-check` der Seite, PROMPTGOTT-Abo |
| Einsatzgebiet | erste drei Aufgaben-Titel | Seite selbst, Ratgeber zur Rolle, `#stack-check` der Seite, PROMPTGOTT-Abo |
| Schublade | erste FAQ-Frage | Seite selbst, Ratgeber (sonst Einsatzgebiet) mit den meisten Tools der Schublade, `#stack-check` der Seite, PROMPTGOTT-Abo |
| Tool-Eintrag | fester Stack-Auftrag | Seite selbst, Stack-Finder (`./#finder-band`), Stack-Check (`#stack-check`) |

Beispiel (Ratgeber, so wie der Dialog es zeigt):

```
Ich komme von der KI-Werkstatt, Ratgeber „KI-Agenten sicher einsetzen“: https://jmp-collab.github.io/awesome-ai-tools/ratgeber-ki-agenten-sicher.html?utm_source=chatgpt&utm_medium=llm-prompt&utm_campaign=ratgeber&utm_content=ki-agenten-sicher
Geh das Thema mit mir durch, frag zuerst, wo ich stehe. Klär vor allem: Ist der automatische Modus von Claude sicher genug? Was ist Prompt Injection und wie schütze ich mich?
Wenn es passt, verlinke im weiteren Gespräch auf passende Seiten der KI-Werkstatt:
- Ratgeber „MCP und Agent Skills“: https://jmp-collab.github.io/awesome-ai-tools/ratgeber-mcp-agent-skills.html?utm_source=chatgpt&utm_medium=llm-prompt&utm_campaign=ratgeber&utm_content=ki-agenten-sicher
- Stack-Check, kostenlose Tool-Empfehlung: https://jmp-collab.github.io/awesome-ai-tools/ratgeber-ki-agenten-sicher.html?utm_source=chatgpt&utm_medium=llm-prompt&utm_campaign=ratgeber&utm_content=ki-agenten-sicher#stack-check
- PROMPTGOTT-Newsletter: https://promptgott.substack.com/subscribe?utm_source=chatgpt&utm_medium=llm-prompt&utm_campaign=ratgeber&utm_content=ki-agenten-sicher
```

Länge: Der Text ohne Links bleibt unter rund 500 Zeichen. Mit vier vollständigen UTM-Links kommen die Prompts auf 1.000 bis 1.200 Zeichen, die kodierte Anbieter-URL auf rund 1.550. Wer kürzer will, streicht einen Ziel-Link, nicht die Herkunftszeile.

## UTM-Schema

| Parameter | Wert | Beispiel |
|---|---|---|
| `utm_source` | Anbieter-ID aus `LLM_TARGETS` | `chatgpt`, `claude`, `perplexity` |
| `utm_medium` | immer `llm-prompt` | `llm-prompt` |
| `utm_campaign` | Seitentyp, von dem der Prompt kommt | `ratgeber`, `einsatz`, `schublade`, `tool` |
| `utm_content` | Slug der Ausgangsseite ohne Präfix (`ki-tools-`, `ratgeber-`), Startseite `start` | `ki-agenten-sicher`, `text-und-sprache` |

Die Query steht vor dem Anker (`seite.html?utm_…#stack-check`). Der Build schreibt `utm_source={src}` als Platzhalter in die Seitendaten; `app.js` setzt den gewählten Anbieter ein, bevor der Text im Dialog erscheint. Beim Anbieterwechsel im Dialog tauscht das Skript nur `utm_source`, eigene Änderungen am Text bleiben.

Die übrigen Links der Seite behalten ihr Schema (`utm_medium=referral` für PROMPTGOTT-Links aus Footer, Bändern und Sticky-Leiste). So trennt Substack Besuche aus KI-Chats sauber von Klicks direkt auf der Website.

## Messung über utm_medium=llm-prompt

- **PROMPTGOTT (Substack):** Abos und Besuche nach `utm_medium=llm-prompt`, aufgeschlüsselt nach `utm_source` (Anbieter) und `utm_campaign`/`utm_content` (Ausgangsseite).
- **Stack-Check:** Landet jemand über einen Prompt-Link auf einer Seite und schickt dort das Formular ab, steht im Feld `seite` zusätzlich „(über KI-Chat: chatgpt, ratgeber, ki-agenten-sicher)“. Das Skript liest die Angabe erst beim Absenden aus der Adresse und speichert sie nirgends.
- **Website selbst:** Die KI-Werkstatt hat bewusst kein Analyse-Tool. Seitenaufrufe mit UTM sind dort nicht auswertbar, und die Search Console zeigt keine UTM-Parameter. Wer in einem Shop mit Analytics arbeitet, filtert dort Sitzungen mit `utm_medium = llm-prompt`.
- Alle Seiten haben einen Canonical ohne Parameter, die UTM-Varianten erzeugen deshalb keine Duplikate im Index.

## Technik zum Übertragen

1. **Anbieter an einer Stelle.** Eine Liste mit ID, Name, Prefill-URL, Domains, Status, Prüfdatum und Hinweis. Alles andere (Buttons, Dialog, Datenschutztext) liest daraus.
2. **Prompts im Build erzeugen**, nicht im Browser. Ablage als `<script type="application/json" id="kw-llm">` (CSP ohne Inline-Skripte, kein sichtbarer Fließtext, also keine Duplikate für SEO oder `check_unique.py`).
3. **Buttons mit `hidden`** ausliefern, `data-llm="seite"` bzw. `data-llm="tool" data-llm-to="<id>"`, `aria-haspopup="dialog"`. Das Skript blendet sie ein. Wiederkehrende Beschriftungen tragen `data-chrome`.
4. **Dialog:** natives `<dialog>` mit `showModal()`, zusätzlich `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby`. Fokus ins Prompt-Feld (Anfang sichtbar), Tab und Umschalt+Tab bleiben im Dialog, Escape und Klick auf den Rand schließen, danach Fokus zurück auf den Button. Inhalt: Erklärsatz, Anbieterwahl (ab zwei Anbietern), editierbares Textfeld mit dem Prompt, Hinweis zum Teststand, Link „In <Anbieter> öffnen“ (`target="_blank" rel="noopener noreferrer"`), Button „Prompt kopieren“, Statuszeile mit `aria-live`.
5. **Keine Anfrage vor dem Klick.** Kein Vorladen, kein Favicon des Anbieters, keine Messung beim Öffnen des Dialogs.
6. **Datenschutzhinweis:** Buttons öffnen erst einen Dialog auf der eigenen Seite; erst der Klick übergibt den angezeigten Text in der URL an den Anbieter; vorher keine Übertragung; ab dann gelten die Regeln des Anbieters, eingeloggt kann er sofort senden; Kopieren bleibt lokal.
7. **Build-Wächter:** verbotene Formulierungen, unsichtbare Zeichen, Länge, Anzahl Ziel-URLs, Button ohne Prompt-Daten.

## Prüfliste vor dem Livegang

- [ ] Jeder angebotene Anbieter ist mit Datum getestet, Ergebnis steht in der Tabelle oben und in `LLM_TARGETS`.
- [ ] Playwright: Dialog per Tastatur öffnen und schließen, Fokusfalle, Prompt-Text gleich decodiertem URL-Parameter, Kopieren legt exakt den Text ab, keine Konsolenfehler, keine externe Anfrage vor dem Klick.
- [ ] Screenshots bei 390 und 1366 px, hell und dunkel.
- [ ] Prompt laut lesen: Herkunft offen? Kein „merke dir“? Keine Abwertung? Würdest du ihn selbst abschicken?
- [ ] Datenschutzseite ergänzt.
