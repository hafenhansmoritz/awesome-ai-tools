> **Kurz gesagt:** Mit KI ist ein Shop in wenigen Tagen in fünf Sprachen übersetzt. Ob daraus Umsatz wird, hängt an drei Dingen, die keine Maschine allein erledigt: ein Glossar für Fachbegriffe und Markennamen, eine Prüfung durch Muttersprachler an den richtigen Stellen und eine saubere Technik mit eigenen URLs und hreflang. Google hat nichts gegen maschinell übersetzte Seiten, wohl aber gegen massenhaft erzeugte Seiten ohne Mehrwert. Dieser Ratgeber zeigt, wie du beides auseinanderhältst, was die Übersetzung kostet und wie ein Projekt in vier Wochen läuft.

Die Fakten zu Suchmaschinen stammen aus der Dokumentation von Google Search Central, die zu Werkzeugen und Preisen von den Herstellerseiten, Stand 28. Oktober 2026. Rechenbeispiele beruhen auf offen genannten Annahmen.

## Warum gerade jetzt

Maschinelle Übersetzung ist nicht neu. Neu ist, dass große Sprachmodelle nicht mehr Satz für Satz übertragen, sondern den ganzen Kontext einer Seite verstehen. Sie erkennen, dass „Kolben“ im Motorradshop kein Laborgerät ist, dass eine Größentabelle Zahlen statt Wörter braucht und dass eine Produktbeschreibung auf Niederländisch anders klingen sollte als auf Schwedisch. Spezialisierte Dienste wie DeepL Übersetzer und allgemeine Modelle wie ChatGPT, Claude, Gemini oder Vibe von Mistral liefern dabei inzwischen Rohfassungen, die für viele Seitentypen fast fertig sind.

Fast fertig ist das Problem. Ein falsch übersetzter Fachbegriff in einer Einbauanleitung kostet Vertrauen, ein vertauschter Markenname kostet Rankings, und eine vollautomatisch übersetzte Seite, die niemand je gelesen hat, ist genau die Art Inhalt, vor der Google warnt.

## Was Google zu Übersetzungen sagt

Die wichtigste Stelle steht in den Spamrichtlinien von Google, im Abschnitt über Missbrauch durch skalierte Inhalte. Als Beispiel nennt Google dort das massenhafte Erzeugen von Seiten durch automatische Umformungen wie Synonymisieren oder Übersetzen, wenn dabei wenig Mehrwert für Nutzer entsteht. Verboten ist also nicht die Maschine, sondern die Masse ohne Nutzen. Eine geprüfte, vollständige Produktseite in der Sprache des Kunden ist Mehrwert. Zehntausend Seiten, die automatisch aus fremden Feeds übersetzt wurden, sind es nicht.

Die zweite wichtige Aussage betrifft Dubletten. Laut Google gelten Sprachversionen einer Seite nur dann als Duplikate, wenn der Hauptinhalt unübersetzt bleibt. Wer nur Navigation und Fußzeile übersetzt und die Produkttexte auf Deutsch lässt, produziert also genau das, was Google als doppelt ansieht. Google schreibt dazu, dass halb übersetzte Seiten eine schlechte Nutzererfahrung schaffen, wenn derselbe Inhalt mehrfach mit verschiedenen Sprachrahmen in den Ergebnissen auftaucht.

Drittens erkennt Google die Sprache einer Seite am sichtbaren Inhalt. Das `lang`-Attribut im Code und die URL nutzt Google dafür ausdrücklich nicht. Die Empfehlung lautet, pro Seite nur eine Sprache für Inhalt und Navigation zu verwenden und Übersetzungen nicht nebeneinander auf dieselbe Seite zu stellen.

## Die Technik: eigene URLs und hreflang

Google empfiehlt für jede Sprachversion eine eigene URL statt einer Umschaltung über Cookies oder Browsereinstellungen. Der Grund ist praktisch: Der Googlebot kommt meist aus den USA und schickt seine Anfragen ohne Sprachangabe im Header. Eine Seite, die ihre Sprache je nach Besucher wechselt, sieht er womöglich nur in einer Version.

Für den Aufbau der URLs nennt Google vier Varianten mit Vor- und Nachteilen:

| Aufbau | Beispiel | Einschätzung laut Google |
|---|---|---|
| Länderdomain | `shop.nl` | Klarstes Länder-Signal, aber teurer, mehr Infrastruktur, nur ein Land pro Domain |
| Subdomain | `nl.shop.com` | Leicht einzurichten, Nutzer erkennen aber nicht immer, ob Sprache oder Land gemeint ist |
| Unterverzeichnis | `shop.com/nl/` | Leicht einzurichten und wenig Pflege, alles auf einem Host |
| URL-Parameter | `shop.com?loc=nl` | Ausdrücklich nicht empfohlen |

Die Sprachversionen verbindest du mit hreflang-Angaben. Google akzeptiert sie auf drei gleichwertigen Wegen: im HTML-Kopf, im HTTP-Header oder in der Sitemap. Alle drei gleichzeitig bringen laut Google keinen Vorteil, nur mehr Pflegeaufwand. Für Shops mit vielen Seiten ist die Sitemap oft am einfachsten zu verwalten.

Die Regeln, an denen die meisten Umsetzungen scheitern:

- **Jede Version nennt sich selbst und alle anderen.** Die Liste ist auf jeder Sprachversion identisch.
- **Verweise müssen gegenseitig sein.** Zeigt Seite A auf Seite B, aber B nicht zurück auf A, ignoriert Google die Angaben.
- **Vollständige URLs mit Protokoll.** Also `https://shop.com/nl/kolben`, nicht `/nl/kolben`.
- **Ein Auffangziel für alle anderen Sprachen.** Mit `x-default` legst du fest, welche Seite Besucher bekommen, deren Sprache du nicht anbietest, typischerweise eine Sprachauswahl oder die Hauptversion.
- **Neue Sprachen an die starke Hauptversion anbinden.** Wird es zu aufwendig, alle Sprachen untereinander zu verknüpfen, ist laut Google die gegenseitige Verbindung mit der ursprünglichen Hauptsprache am wichtigsten.

Und eine Regel, die gegen den Reflex vieler Shopbetreiber geht: Leite Besucher nicht automatisch nach vermuteter Sprache oder IP-Adresse um. Google rät davon ab, weil Nutzer und Suchmaschinen dann nicht mehr alle Versionen sehen. Besser ist ein gut sichtbarer Sprachumschalter mit Links zu den anderen Versionen. Lokalisierte Wörter in der URL sind übrigens erlaubt, solange die URLs in UTF-8 kodiert sind.

## Das Glossar ist das halbe Projekt

Kein Modell kennt deine Produktnamen, deine Abkürzungen und die Begriffe, die in deiner Branche anders verwendet werden als im Alltag. Ein Glossar legt fest, wie ein Begriff in jeder Sprache heißt oder dass er unverändert bleibt.

Bei DeepL ist das eine eingebaute Funktion mit klaren Grenzen je Tarif. In der kostenlosen Version und im Tarif Individual gibt es ein Glossar mit fünf Einträgen je Sprachpaar, im Tarif Team fünf Glossare mit je 1.000 Einträgen, in Business und Enterprise keine feste Grenze. Dazu listet DeepL Funktionen wie den Upload von Glossaren per CSV, geteilte Glossare, Translation Memory und die Wahl zwischen formeller und informeller Anrede; welche davon in welchem Tarif steckt, zeigt die Preisseite. Für einen Shop mit Hunderten Fachbegriffen ist der kleinste Tarif damit zu knapp.

Bei allgemeinen Sprachmodellen gibst du das Glossar als Teil der Anweisung mit, etwa als Tabelle am Anfang des Prompts. Das funktioniert gut, kostet aber bei jeder Anfrage Eingabe-Token. Wer viele Seiten übersetzt, profitiert hier stark vom Cache, den die großen Anbieter für wiederkehrende Anweisungen günstiger abrechnen.

So baust du ein Glossar, das wirklich hilft:

1. **Markennamen und Modellbezeichnungen** sammeln, die nie übersetzt werden.
2. **Fachbegriffe** mit der gewünschten Übersetzung je Sprache festlegen, am besten von jemandem, der die Branche im Zielland kennt.
3. **Einheiten und Formate** regeln: Dezimalkomma oder Punkt, Maßeinheiten, Datumsformat.
4. **Verbotene Übersetzungen** notieren, die zwar wörtlich richtig, im Zielmarkt aber falsch oder peinlich sind.
5. **Anrede** festlegen: Du oder Sie, und das Gegenstück in jeder Zielsprache.

## Welche Seiten welche Prüfung brauchen

Nicht jede Seite verdient denselben Aufwand. Eine sinnvolle Staffelung spart Geld, ohne an den falschen Stellen zu sparen.

| Seitentyp | Vorschlag |
|---|---|
| Rechtstexte, AGB, Widerruf, Datenschutz | Nicht maschinell übersetzen und veröffentlichen, sondern im Zielland rechtlich erstellen oder prüfen lassen |
| Sicherheits- und Einbauhinweise | Maschine plus vollständige Prüfung durch Fachleute mit Muttersprache |
| Startseite, Kategorien, Bestseller | Maschine plus vollständige sprachliche Prüfung, hier entscheidet sich der erste Eindruck |
| Lange Produktbeschreibungen | Maschine mit Glossar, Stichproben und Prüfung aller Seiten mit viel Umsatz |
| Technische Datenblätter, Größentabellen | Maschine mit Glossar, automatische Prüfung von Zahlen und Einheiten |
| Kundenbewertungen | Klar als automatisch übersetzt kennzeichnen oder in der Originalsprache lassen |

Bei den Rechtstexten geht es nicht um Sprachqualität. Verbraucherrecht, Widerrufsfristen und Impressumspflichten unterscheiden sich von Land zu Land, eine noch so gute Übersetzung des deutschen Textes ist im Zielland womöglich schlicht falsch.

## Was die Übersetzung kostet

Für die Kosten bei Sprachmodellen hilft eine einfache Rechnung. Unsere Annahmen: 1.000 Produktseiten mit je 300 Wörtern Text, grob zwei Token pro Wort, dazu 400 Token Anweisung und Glossar pro Anfrage. Das ergibt pro Sprache rund eine Million Token Eingabe und 0,6 Millionen Token Ausgabe. Die Preise in Dollar pro Million Token stammen aus unserem Preisvergleich, Stand 28. Oktober 2026.

| Modell | Rechnung | Kosten je Sprache |
|---|---|---|
| Claude Haiku 5.5 oder GPT-6 Luna | 1,0 × 0,10 + 0,6 × 0,50 | 0,40 Dollar |
| GPT-6.1 Terra | 1,0 × 1,00 + 0,6 × 5,00 | 4,00 Dollar |
| GPT-6.1 Sol oder Claude Sonnet 5.5 | 1,0 × 2,00 + 0,6 × 10,00 | 8,00 Dollar |
| Claude Opus 5.5 | 1,0 × 4,00 + 0,6 × 20,00 | 16,00 Dollar |

Die Maschine ist also der kleinste Posten. Teuer ist die Prüfung durch Menschen, und genau deshalb lohnt die Staffelung aus dem vorigen Abschnitt. Mit Cache für Anweisung und Glossar sinken die Eingabekosten weiter.

Bei DeepL zahlst du statt nach Token nach Tarif. Der Tarif Individual kostet laut DeepL 7,49 Euro im Monat bei jährlicher Zahlung und enthält drei Dateiübersetzungen im Monat. Für die Anbindung an ein Shopsystem gibt es die DeepL API mit eigenen Preisen, die du vor dem Start auf der Herstellerseite prüfen solltest.

## Datenschutz nicht vergessen

Produkttexte enthalten selten Personendaten, Kundenbewertungen, Support-E-Mails und Händlerkorrespondenz dagegen schon. Hier kommt es wieder auf den Tarif an. Die kostenlose Version von DeepL nutzt eingegebene Texte und Korrekturen laut Datenschutzerklärung zum Training, und die Nutzungsbedingungen untersagen dort Texte mit personenbezogenen Daten. In den Pro-Tarifen werden Texte nach der Übersetzung gelöscht und nicht zum Training verwendet, für Personendaten ist ein Vertrag zur Auftragsverarbeitung vorgesehen. Dokumente verarbeitet DeepL nach eigener Angabe auf der eigenen Infrastruktur im Europäischen Wirtschaftsraum.

Für allgemeine Sprachmodelle gilt dasselbe Muster: Business-Tarif oder API ja, privates Konto nein. Die Details stehen im Ratgeber zum Datenschutz bei KI-Tools.

## Qualität prüfen, ohne jede Sprache zu sprechen

Du musst nicht Finnisch können, um eine finnische Übersetzung zu prüfen. Diese Kontrollen laufen mit wenig Aufwand:

- **Rückübersetzung als Stichprobe:** Lass zehn zufällige Seiten von einem anderen Modell zurück ins Deutsche übersetzen. Grobe Sinnfehler fallen sofort auf.
- **Zahlen und Einheiten maschinell vergleichen:** Ein kleines Skript prüft, ob in Original und Übersetzung dieselben Zahlen stehen. Gerade bei Maßen, Preisen und Drehmomenten ist das der wichtigste Test.
- **Glossar-Treffer zählen:** Steht der festgelegte Begriff wirklich in der Übersetzung, und ist der Markenname unverändert?
- **Länge vergleichen:** Ist eine Übersetzung deutlich kürzer als das Original, fehlt oft ein Absatz.
- **Muttersprachler für die Top-Seiten:** Für Startseite, Kategorien und Bestseller lohnt eine Prüfung durch jemanden aus dem Zielmarkt, etwa über Partner, Händler oder Freelancer.
- **Suchbegriffe prüfen:** Eine korrekte Übersetzung ist nicht automatisch der Begriff, nach dem Kunden im Zielland suchen. Prüf für die wichtigsten Kategorien, wie sie dort tatsächlich gesucht werden, und pass die Titel an.

## Typische Fehler

Aus den Vorgaben von Google und der Praxis mehrsprachiger Shops ergeben sich wiederkehrende Fallen:

- **Nur das Gerüst übersetzt:** Navigation in fünf Sprachen, Produkttexte auf Deutsch. Für Google sind das Dubletten, für Kunden eine Enttäuschung.
- **Automatische Weiterleitung nach IP:** Der Googlebot sieht dann womöglich nur die englische Version, und Nutzer im Urlaub landen im falschen Shop.
- **Einseitige hreflang-Angaben:** Die neue Sprachversion zeigt auf die deutsche, die deutsche aber nicht zurück. Google ignoriert die Verbindung.
- **Relative URLs in hreflang:** Ohne `https://` und Domain sind die Angaben ungültig.
- **Sprachen gemischt:** Englische Produkttexte auf der niederländischen Seite, weil die Übersetzung noch läuft. Lieber eine Kategorie später veröffentlichen als halb fertig.
- **Übersetzt, aber nicht verknüpft:** Ohne Links von der Hauptversion und ohne Sitemap findet Google neue Sprachversionen nur langsam.

## Dein Fahrplan in vier Wochen

1. **Woche 1:** Zielmärkte festlegen, Seiten nach Typ einteilen, URL-Aufbau entscheiden, Glossar beginnen.
2. **Woche 2:** Werkzeug wählen und mit 50 Seiten testen, Glossar nachschärfen, Prüfroutine für Zahlen und Begriffe aufsetzen.
3. **Woche 3:** Alle Seiten übersetzen, Top-Seiten von Muttersprachlern prüfen lassen, Rechtstexte separat erstellen lassen.
4. **Woche 4:** hreflang über die Sitemap ausspielen, Sprachumschalter einbauen, in der Search Console die Indexierung je Sprache beobachten.

Nach dem Start lohnt ein Blick in die Suchdaten pro Land. Seiten, die Impressionen, aber kaum Klicks bekommen, haben oft einen Titel, der wörtlich stimmt, aber nicht dem Suchbegriff im Zielmarkt entspricht. Genau dort lohnt die nächste Runde menschlicher Arbeit.
