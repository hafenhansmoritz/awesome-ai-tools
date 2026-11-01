> **Kurz gesagt:** Im Herbst 2026 liegen zwischen dem günstigsten und dem teuersten Sprachmodell der großen Anbieter rund Faktor hundert beim Preis pro Token. Für die meiste Alltagsarbeit im Unternehmen reicht die Mittelklasse, für Sortieren, Extrahieren und Zusammenfassen oft ein Kleinmodell. Entscheidend ist nicht der Listenpreis, sondern was eine erledigte Aufgabe kostet. Dieser Ratgeber zeigt die aktuellen Preise, rechnet ein Beispiel durch und erklärt, wann ein lokales Modell die bessere Wahl ist.

Alle Preise stammen aus den Ankündigungen und Preisseiten der Hersteller, Stand 29. Oktober 2026, in US-Dollar pro Million Token. Leistungsvergleiche sind Herstellerangaben, die mit unterschiedlichen Einstellungen gemessen wurden. Wir geben sie wieder, damit du weißt, womit die Anbieter werben, nicht weil wir sie für neutral halten.

## Was ein Token ist und warum der Preis pro Token täuscht

Sprachmodelle rechnen in Token, also Wortstücken. Ein deutscher Satz mit zwölf Wörtern entspricht grob zwanzig bis dreißig Token. Bezahlt wird getrennt nach Eingabe, also allem, was du dem Modell schickst, und Ausgabe, also allem, was es zurückschreibt. Die Ausgabe kostet bei den großen Anbietern drei- bis fünfmal so viel wie die Eingabe.

Der Listenpreis sagt aber nur die halbe Wahrheit. Modelle mit Denkphase schreiben vor der eigentlichen Antwort interne Überlegungen, und diese Denk-Token werden in der Regel als Ausgabe abgerechnet. Ein Modell, das pro Token günstig ist, aber dreimal so viel denkt, kann am Ende teurer sein als ein teureres, das schneller zum Punkt kommt. Die Hersteller haben das erkannt und vergleichen inzwischen lieber Kosten pro Aufgabe.

Zwei Beispiele aus den Ankündigungen: Anthropic gibt an, dass Claude Sonnet 5.5 zum gleichen Listenpreis wie Sonnet 5 pro Aufgabe bis zu 30 Prozent weniger kostet, weil es weniger Token braucht. OpenAI wirbt damit, dass GPT-6.1 Terra in einem Test zur Computerarbeit bei maximaler Denktiefe dreimal so sparsam mit Token umgeht wie Claude Opus 5.5. Dazu koste es ein Viertel pro Token, zusammen also etwa ein Neuntel pro Aufgabe. Beides sind Werbeaussagen, aber sie zeigen, worauf es ankommt.

## Die Preisliste im Herbst 2026

| Modell | Anbieter | Eingabe | Ausgabe | Cache-Lesen |
|---|---|---|---|---|
| GPT-6 Astra | OpenAI | 10,00 | 50,00 | 1,00 |
| Claude Opus 5.5 | Anthropic | 4,00 | 20,00 | 0,20 |
| GPT-6.1 Sol | OpenAI | 2,00 | 10,00 | 0,10 |
| Claude Sonnet 5.5 | Anthropic | 2,00 | 10,00 | 0,10 |
| Gemini 4 Argon, Einführungspreis bis 30.11. | Google | 2,00 | 10,00 | 95 % Rabatt |
| Gemini 4 Argon, ab 1.12. | Google | 4,00 | 20,00 | 95 % Rabatt |
| GPT-6.1 Terra | OpenAI | 1,00 | 5,00 | 0,05 |
| Mistral Large 4, ab 29.10. | Mistral | 0,70 | 2,10 | 0,07 |
| Claude Haiku 5.5, Eingaben bis 100.000 Token | Anthropic | 0,10 | 0,50 | k. A. |
| GPT-6 Luna | OpenAI | 0,10 | 0,50 | 0,01 |

Drei Dinge fallen auf. Erstens kosten die Mittelklasse-Modelle von OpenAI, Anthropic und Google fast exakt dasselbe, der Wettbewerb läuft über Leistung und Token-Verbrauch. Zweitens liegt Mistral mit Large 4, einem Modell aus Europa mit offenen Gewichten, pro Token deutlich unter der Mittelklasse. Mit der Freigabe der Gewichte am 29. Oktober hat Mistral auch die API-Preise gesenkt. Drittens sind die Kleinmodelle so billig geworden, dass bei vielen Aufgaben die Entwicklungszeit teurer ist als der Betrieb.

## Rechenbeispiel: 2.000 Produkttexte

Angenommen, ein Shop lässt 2.000 Produktbeschreibungen schreiben. Pro Text schickt er rund 600 Token Eingabe, also Datenblatt, Stilvorgaben und ein Beispiel, und bekommt rund 400 Token Ausgabe zurück. Das sind zusammen 1,2 Millionen Eingabe-Token und 0,8 Millionen Ausgabe-Token. Die Werte sind eine Annahme für die Rechnung, keine Messung, und Denk-Token sind nicht eingerechnet.

| Modell | Rechnung | Kosten für 2.000 Texte |
|---|---|---|
| GPT-6 Luna oder Claude Haiku 5.5 | 1,2 × 0,10 + 0,8 × 0,50 | 0,52 Dollar |
| Mistral Large 4 | 1,2 × 0,70 + 0,8 × 2,10 | 2,52 Dollar |
| GPT-6.1 Terra | 1,2 × 1,00 + 0,8 × 5,00 | 5,20 Dollar |
| GPT-6.1 Sol, Sonnet 5.5 oder Argon zum Einführungspreis | 1,2 × 2,00 + 0,8 × 10,00 | 10,40 Dollar |
| Claude Opus 5.5 oder Argon ab Dezember | 1,2 × 4,00 + 0,8 × 20,00 | 20,80 Dollar |
| GPT-6 Astra | 1,2 × 10,00 + 0,8 × 50,00 | 52,00 Dollar |

Selbst mit dem teuersten Modell kostet der komplette Katalog weniger als ein Abendessen für zwei. Die eigentlichen Kosten stecken woanders: in der Zeit für gute Vorgaben, im Gegenlesen und in den Retouren, wenn ein Modell ein Maß erfindet. Deshalb lohnt es sich, für Produkttexte das Modell nach Qualität zu wählen und nicht nach dem letzten Cent. Wer täglich Zehntausende Anfragen verarbeitet, etwa im Kundenservice, rechnet dagegen sehr genau, und dort zählt jeder Faktor zehn.

## Cache und Stapelverarbeitung: die unterschätzten Sparhebel

Viele Anfragen beginnen mit demselben Text: Stilvorgaben, Produktkatalog, Arbeitsanweisungen. Diesen wiederkehrenden Teil können die Anbieter zwischenspeichern, und das Lesen aus dem Cache kostet einen Bruchteil. Bei GPT-6.1 Sol sind es laut OpenAI 0,10 statt 2,00 Dollar, also 95 Prozent weniger. Anthropic hat den Cache-Preis für Sonnet 5.5 im Oktober halbiert und sagt selbst, dass Cache-Lesen bei Agenten und beim Programmieren den Großteil der Kosten ausmacht.

Damit der Cache greift, muss der gleichbleibende Teil am Anfang der Anfrage stehen und der wechselnde Teil am Ende. Wer das beim Aufbau seiner Prompts beachtet, spart ohne jeden Qualitätsverlust. Für Aufgaben ohne Zeitdruck bieten mehrere Anbieter außerdem Stapelverarbeitung an, bei der Anfragen gesammelt und später günstiger abgearbeitet werden. Mistral listet sie etwa ausdrücklich für Large 4.

## Drei Klassen und wofür sie taugen

**Kleinmodelle** wie GPT-6 Luna und Claude Haiku 5.5 sind gebaut für hohe Stückzahlen: Einordnen, Extrahieren, Zusammenfassen, Daten umformatieren, Support-Anfragen vorsortieren. Anthropic empfiehlt Haiku 5.5 zudem als Hilfsagenten, der für ein größeres Modell Teilaufgaben erledigt. Für schwierige Texte mit Haltung oder für verschachtelte Analysen sind sie zu knapp.

**Die Mittelklasse** mit GPT-6.1 Sol und Terra, Claude Sonnet 5.5, Gemini 4 Argon und Mistral Large 4 ist das Arbeitspferd. Hier entstehen Entwürfe, Auswertungen, Code-Änderungen und Agenten-Abläufe. OpenAI positioniert Terra ausdrücklich für Büro- und Computerarbeit in großer Menge, etwa das Abtippen von Rechnungen in die Buchhaltung. Für die meisten Unternehmen ist ein Modell aus dieser Klasse die richtige Grundausstattung.

**Spitzenmodelle** wie GPT-6 Astra und Claude Opus 5.5 lohnen sich für schwierige Programmierarbeit, lange Recherchen mit vielen Quellen und Aufgaben, bei denen ein Fehler richtig teuer wird. Wer sie für jede E-Mail nutzt, zahlt für einen Sportwagen im Stadtverkehr. Auch die Hersteller selbst empfehlen sie vor allem für die anspruchsvollsten Aufgaben.

## Lokal statt Cloud: wann sich das rechnet

Im Oktober sind zwei Kleinmodelle erschienen, die auf normaler Hardware laufen. LFM3 von Liquid AI umfasst sechs offene Modelle um zwei Milliarden Parameter für Text, Bild, Audio und schnelle Entscheidungen. Das Textmodell braucht bei 4 Bit laut Hersteller rund ein Gigabyte Speicher und verarbeitet bis zu 256.000 Token Kontext. Die Modellkarte rät allerdings selbst davon ab, es für komplexes Programmieren oder vielstufiges Schlussfolgern zu nutzen.

Nemotron 3.5 Bolt E4B von NVIDIA ist auf Sprachassistenten und Werkzeugaufrufe zugeschnitten. In NVIDIAs Test belegt es auf einer Grafikkarte vom Typ RTX 5070 je nach Gesprächslänge 3,5 bis 4,3 Gigabyte Speicher und liefert bei kurzen Gesprächen gut 130 Token pro Sekunde. Über Ollama lässt es sich mit einem einzigen Befehl starten, und auch LM Studio führt solche Modelle ohne Kommandozeile aus.

Ein lokales Modell kostet keine Gebühren pro Token, dafür Hardware, Strom und vor allem Betreuung. Es lohnt sich, wenn drei Dinge zusammenkommen: vertrauliche Daten, die das Haus nicht verlassen sollen, eine eng umrissene Aufgabe und eine hohe Stückzahl. Ein lokales Kleinmodell, das Eingangsrechnungen nach Lieferant und Kostenstelle sortiert, ist ein gutes Beispiel. Ein lokales Modell als Ersatz für einen klugen Allround-Assistenten ist in der Regel eine Enttäuschung.

## Die Europa-Frage

Für Unternehmen mit strengen Datenschutzvorgaben zählt neben dem Preis, wo ein Modell betrieben wird. Mistral bietet Large 4 nach eigenen Angaben auch in einer europäischen Variante an, die das Unternehmen vollständig selbst betreibt, unabhängig von anderen Dienstleistern und unter europäischem Recht. Seit dem 29. Oktober liegen die offenen Gewichte bei Hugging Face, das Modell lässt sich also auch auf eigenen Servern betreiben. Die Lizenz ist eine abgewandelte MIT-Lizenz: Frei nutzen, anpassen und kommerziell einsetzen darfst du es, nur wer es als Dienst an Dritte verkauft, braucht eine eigene Lizenz von Mistral.

Ein europäischer Firmensitz ersetzt dabei keine Prüfung. Auch bei Mistral brauchst du einen Vertrag zur Auftragsverarbeitung und solltest die Einstellungen zur Datennutzung kontrollieren. Umgekehrt lassen sich Modelle der US-Anbieter teils auch über europäische Cloud-Regionen beziehen. Was zählt, ist der Vertrag und nicht die Flagge auf der Website.

## In einer Stunde zum richtigen Modell

1. **Zwanzig echte Fälle sammeln:** keine erfundenen Testfragen, sondern zwanzig Aufgaben aus der letzten Woche, inklusive zwei, drei schwieriger.
2. **Drei Modelle auswählen:** ein Kleinmodell, ein Modell aus der Mittelklasse und eines aus einer anderen Familie, damit du nicht nur einen Anbieter vergleichst.
3. **Gleiche Vorgaben verwenden:** derselbe Prompt, dieselben Beispiele, dieselbe Länge. Sonst vergleichst du Prompts und keine Modelle.
4. **Ergebnisse blind bewerten:** Lass jemanden die Antworten ohne Modellnamen in gut, brauchbar und unbrauchbar sortieren.
5. **Kosten pro 1.000 Aufgaben ausrechnen:** Die meisten Konsolen zeigen den Token-Verbrauch pro Anfrage. Mal tausend, fertig.
6. **Das günstigste Modell nehmen, das gut genug ist:** und in drei Monaten erneut testen, denn die Preise fallen weiter.

Wer diesen Ablauf einmal gemacht hat, diskutiert nicht mehr über Benchmarks, sondern über Ergebnisse. Das spart Meetings, und Meetings sind bekanntlich das teuerste Modell von allen.

## Abo oder Programmierschnittstelle?

Für die tägliche Arbeit am Bildschirm ist ein Abo meist die bessere Wahl. ChatGPT, Claude und Gemini bündeln dort mehrere Modelle, Werkzeuge und Speicher zu einem festen Monatspreis. Die Programmierschnittstelle, kurz API, lohnt sich, sobald Abläufe automatisch laufen sollen: Texte für den ganzen Katalog, Tickets im Minutentakt, nächtliche Auswertungen.

Viele Teams kombinieren beides. Die Menschen arbeiten im Abo, die Automatisierung läuft über die API mit einem günstigeren Modell. Google treibt diese Arbeitsteilung mit dem Gemini-Agenten weiter, der laut Google je Aufgabe selbst das passende Modell auswählt, darunter auch Modelle von Anthropic, und dabei Ausgabenlimits einhält.
