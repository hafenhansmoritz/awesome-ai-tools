> **Kurz gesagt:** KI-Telefonagenten nehmen inzwischen Anrufe an, beantworten Standardfragen, buchen Termine und leiten an Menschen weiter, mit Antwortzeiten unter einer Sekunde und für wenige Cent pro Minute. Für Shops und Dienstleister mit vielen wiederkehrenden Anrufen ist das ein echter Hebel. Drei Regeln entscheiden über einen sauberen Start: Der Agent sagt am Anfang klar, dass er eine KI ist. Aufgezeichnet wird nur mit ausdrücklicher Einwilligung vor der Aufnahme. Und jeder Anrufer kommt jederzeit zu einem Menschen. Dieser Ratgeber vergleicht Anbieter und Preise, erklärt die Pflichten aus AI Act und deutschem Recht und zeigt einen Fahrplan in vier Wochen.

Die Fakten stammen von den Preis- und Dokumentationsseiten von Mistral, Google, OpenAI und ElevenLabs, aus den Leitlinien der EU-Kommission zu Artikel 50 des AI Act, dem Strafgesetzbuch und Veröffentlichungen deutscher Datenschutzbehörden, Stand 29. Oktober 2026. Dieser Ratgeber ist keine Rechtsberatung.

## Was ein Telefonagent heute kann

Ein moderner Sprachagent besteht aus drei Teilen: Spracherkennung, ein Sprachmodell, das versteht und entscheidet, und Sprachausgabe. Neuere Modelle wie Gemini 3.8 Live von Google oder GPT-Realtime von OpenAI erledigen alles in einem Schritt und reagieren dadurch schneller. Mistral verspricht für das Agenten-Paket von Voxtral 3 Gesprächswechsel unter einer Sekunde und dass der Agent verstummt, sobald der Anrufer dazwischenredet.

Typische Aufgaben, die sich laut unserer Erfahrung gut eignen:

- **Erreichbarkeit außerhalb der Geschäftszeiten:** Anliegen aufnehmen, Rückruf vereinbaren, Dringendes markieren.
- **Standardfragen:** Öffnungszeiten, Lieferstatus, Rückgabe, Zahlungswege, sofern der Agent auf geprüfte Daten zugreift.
- **Terminvergabe:** Werkstatt, Praxis, Beratung, mit Zugriff auf den Kalender.
- **Vorqualifizierung:** Anliegen und Kundennummer erfassen, bevor ein Mensch übernimmt.

Weniger geeignet sind Reklamationen mit Emotionen, Verhandlungen über Preise und alles, wo eine falsche Zusage teuer wird. Hier sollte der Agent zuhören, zusammenfassen und weiterleiten.

## Anbieter und Preise im Überblick

Die Preise sind die Listenpreise der Anbieter in Dollar, ohne Telefonie, die der SIP- oder Telefonanbieter separat berechnet.

| Angebot | Preis laut Anbieter | Deutsch | Besonderheit |
|---|---|---|---|
| Mistral, Voice-Agent-API mit Mistral Small 4 | 0,04 Dollar pro Minute | Ja | EU-gehostete API oder eigener Betrieb, Telefonie über SIP, öffentliche Vorschau |
| Mistral, Voice-Agent-API mit größerem Modell | 0,08 Dollar pro Minute | Ja | Wie oben, für schwierigere Gespräche |
| ElevenLabs Agents, Tarif Pro | 99 Dollar im Monat inklusive 1.238 Minuten, danach 0,08 Dollar pro Minute | Ja | Kosten für das Sprachmodell kommen hinzu; Stille über 10 Sekunden mit 95 % Rabatt |
| Google Gemini 3.8 Live | Audio-Eingabe 0,005 Dollar, Audio-Ausgabe 0,018 Dollar pro Minute | Ja, rund 99 Sprachen | Kostenlose Stufe nutzt Daten zur Produktverbesserung, die bezahlte nicht |
| OpenAI GPT-Realtime-2.1 | Audio 32 Dollar Eingabe und 64 Dollar Ausgabe pro Million Token, Mini-Version 10 und 20 Dollar | Ja | SIP-Anbindung mit eigenem EU-Endpunkt |

Zusätzlich gibt es fertige Lösungen, die Telefonnummer, Oberfläche und Anbindung mitbringen, etwa Parloa aus Berlin oder Rosie und Cald.ai, die Anrufe entgegennehmen. Sie kosten mehr pro Minute, sparen aber Entwicklungsarbeit.

**Rechenbeispiel:** Ein Shop bekommt im Monat 1.000 Anrufe, die der Agent im Schnitt drei Minuten lang bearbeitet. Das sind 3.000 Minuten. Bei der Mistral-API mit Mistral Small 4 kostet das 120 Dollar. Bei ElevenLabs reicht der Tarif Pro: 99 Dollar plus 1.762 Zusatzminuten zu je 0,08 Dollar ergeben rund 240 Dollar, dazu kommen die Kosten des Sprachmodells. Der Tarif Scale für 299 Dollar mit 3.738 inklusiven Minuten lohnt sich erst ab etwa 3.740 Minuten im Monat. Bei Google und OpenAI hängt die Rechnung davon ab, wie viel Audio in beide Richtungen fließt; hier hilft nur ein Test mit echten Gesprächen. Telefonie kommt überall hinzu.

## Datenschutz und Datenstandort

Gespräche enthalten fast immer personenbezogene Daten: Namen, Bestellnummern, Adressen, oft auch Dinge, die Anrufer gar nicht sagen wollten. Deshalb gelten dieselben Regeln wie bei jedem anderen KI-Werkzeug: Business-Tarif, Vertrag zur Auftragsverarbeitung, möglichst Verarbeitung in der EU.

Die Anbieter unterscheiden sich hier deutlich:

- **Mistral** bietet eine in der EU gehostete API und den Betrieb auf eigener Infrastruktur an. Laut Mistral lässt sich steuern, ob Audio gespeichert wird.
- **OpenAI** verarbeitet Realtime-Anfragen auf Wunsch im Europäischen Wirtschaftsraum und der Schweiz. Voraussetzung sind eine Freigabe durch den Vertrieb und Zusatzvereinbarungen zur Speicherung. Für Modelle ab dem 5. März 2026 berechnet OpenAI dafür 10 Prozent Aufschlag. Das Tracing für Realtime ist laut OpenAI derzeit nicht von der EU-Datenhaltung abgedeckt.
- **ElevenLabs** bietet eine isolierte EU-Umgebung nur Enterprise-Kunden an. Für die Telefonie über Twilio empfiehlt ElevenLabs die Region Irland.
- **Google** nutzt Daten aus der kostenlosen Stufe der Gemini-API zur Produktverbesserung, aus der bezahlten Stufe nicht.

Vor dem Start gehört die Anwendung zudem ins Verzeichnis der Verarbeitungstätigkeiten. Anrufer müssen nach Artikel 13 DSGVO zum Zeitpunkt der Erhebung informiert werden, unter anderem über Verantwortlichen, Zweck, Rechtsgrundlage, Empfänger und Speicherdauer. Am Telefon geht das in einer kurzen Ansage mit Verweis auf die ausführliche Datenschutzerklärung.

## Pflicht 1: Der Agent sagt, dass er eine KI ist

Seit dem 2. August 2026 gilt Artikel 50 des AI Act. Absatz 1 verpflichtet Anbieter, KI-Systeme für die direkte Interaktion mit Menschen so zu gestalten, dass diese erfahren, dass sie mit einer KI sprechen, es sei denn, das ist offensichtlich.

Für das Telefon sind die Leitlinien der EU-Kommission vom Juli 2026 erstaunlich konkret. Sie nennen als Beispiel eine ausdrückliche gesprochene Ansage zu Beginn, etwa „Dies ist ein KI-gestützter Assistent“, bei längeren Gesprächen ergänzt um Erinnerungen zwischendurch. Töne oder Signaltöne allein reichen laut Kommission nicht. Und eine menschlich klingende Stimme macht es weniger offensichtlich, dass eine KI spricht; die Ausnahme greift nur, wenn praktisch kein Zweifel bleibt.

Wer trägt die Pflicht? Rechtlich der Anbieter des Systems. Die Leitlinien stellen aber klar: Wer ein solches System selbst entwickelt und unter eigenem Namen für die eigene Nutzung in Betrieb nimmt, ist Anbieter. Das gilt auch für den Shop, der sich seinen Sprachagenten aus Bausteinen wie der Mistral- oder OpenAI-API zusammensetzt. Wer ein fertiges Produkt mietet, sollte prüfen, dass der Hinweis eingeschaltet ist und klar formuliert. Verstöße gegen Artikel 50 können laut Kommission Bußgelder bis 15 Millionen Euro oder 3 Prozent des weltweiten Jahresumsatzes nach sich ziehen, bei kleinen Unternehmen mit Blick auf die Verhältnismäßigkeit.

Unsere Empfehlung für die Ansage: kurz, im ersten Satz, ohne Ausrede. „Hallo, hier ist der digitale Assistent von Musterfirma, eine KI. Ich helfe dir bei Bestellungen und Terminen. Wenn du lieber mit einem Menschen sprechen möchtest, sag einfach Mitarbeiter.“

## Pflicht 2: Aufzeichnung nur mit Einwilligung

Das Mitschneiden von Telefonaten ist in Deutschland kein Datenschutzdetail, sondern Strafrecht. Nach § 201 Strafgesetzbuch macht sich strafbar, wer unbefugt das nichtöffentlich gesprochene Wort eines anderen auf einen Tonträger aufnimmt oder eine solche Aufnahme gebraucht oder weitergibt. Es drohen Geldstrafe oder Freiheitsstrafe bis zu drei Jahren.

Die Datenschutzkonferenz hat 2018 beschlossen, dass Aufzeichnungen von Telefongesprächen in aller Regel nur mit Einwilligung auch des externen Gesprächspartners zulässig sind. Die Frage muss vor Beginn der Aufzeichnung gestellt werden, die Bestätigung kann per „Ja“ oder Tastendruck erfolgen. Ausdrücklich nicht reicht es, nur auf eine Widerspruchsmöglichkeit hinzuweisen und das Gespräch dann fortzusetzen. Und die Einwilligung zur Aufzeichnung deckt keine biometrische Auswertung der Stimme ab.

Für Sprachagenten heißt das: Die Verarbeitung des Gesprächs in Echtzeit ist etwas anderes als eine gespeicherte Aufnahme. Wer Gespräche speichert, etwa zur Qualitätskontrolle oder zum Nachtrainieren, braucht die ausdrückliche Einwilligung vorab. Wer nur eine Zusammenfassung speichert, sollte das in der Ansage und der Datenschutzerklärung so beschreiben. Klär die Details mit der Person, die bei dir den Datenschutz verantwortet, bevor der erste echte Anruf läuft.

## Ein Fall aus der Praxis

Wie Aufsichtsbehörden auf Telefonassistenten schauen, zeigt ein Fall aus dem Tätigkeitsbericht 2024 der Datenschutzbeauftragten in Brandenburg. Eine Arztpraxis setzte einen digitalen Telefonassistenten ganztägig ein. Wer nicht einwilligte, konnte nur einen Rückruf anfordern. Die Behörde sah dadurch die Freiwilligkeit der Einwilligung wesentlich beeinträchtigt und empfahl, den Assistenten nur in Pausen- und Schließzeiten einzusetzen, was die Praxis umsetzte.

Die Lehre für alle Branchen: Wenn der KI-Agent der einzige Weg ist, dich zu erreichen, ist eine Einwilligung kaum noch freiwillig. Biete immer einen gleichwertigen Weg ohne KI an, etwa die Durchwahl zu einem Menschen oder ein Rückrufangebot zu Geschäftszeiten.

## Stimmen klonen: Vorsicht mit echten Menschen

Viele Anbieter klonen Stimmen aus wenigen Minuten Audio. Mistral nennt für Voxtral 3 sowohl Klone aus einer kurzen Probe als auch eine besonders hochwertige Variante aus rund 30 Minuten Material. Verlockend ist es, den Agenten mit der Stimme des Chefs oder einer bekannten Mitarbeiterin sprechen zu lassen.

Hier greift Artikel 50 Absatz 4 des AI Act: Wer KI-Audio erzeugt, das einer real existierenden Person ähnelt und fälschlich echt wirken würde, muss offenlegen, dass es künstlich ist. Die Leitlinien der Kommission nennen als Beispiel für einen solchen Deepfake ausdrücklich geklonte Stimmen bekannter Sprecher. Ein maschinenlesbares Wasserzeichen allein genügt dabei nicht, die Offenlegung muss für Hörer wahrnehmbar sein. Unser Rat: Nimm eine neutrale Stimme aus der Bibliothek des Anbieters. Wenn es eine echte Stimme sein soll, dann nur mit schriftlicher Zustimmung der Person und klarer Ansage.

## Die Übergabe an Menschen

Der wichtigste Baustein eines guten Telefonagenten ist nicht die Stimme, sondern der Ausgang. Leg vor dem Start fest:

1. **Stichwort für die Übergabe:** Ein Wort wie „Mitarbeiter“ führt immer und sofort zu einem Menschen oder zu einem Rückrufangebot.
2. **Automatische Übergabe:** Bei Beschwerden, bei Unsicherheit des Agenten und nach zwei Missverständnissen in Folge.
3. **Zusammenfassung mitgeben:** Der Mensch bekommt Anliegen, Kundennummer und bisherigen Verlauf, damit niemand alles zweimal erzählen muss.
4. **Grenzen definieren:** Keine Zusagen zu Preisen, Fristen, Kulanz oder Erstattungen, die nicht aus einer geprüften Datenquelle stammen.
5. **Keine Entscheidung über Menschen:** Die Datenschutzkonferenz betont, dass Entscheidungen mit Rechtswirkung nach Artikel 22 DSGVO grundsätzlich ein Mensch trifft.

## Dein Fahrplan in vier Wochen

1. **Woche 1:** Die häufigsten 20 Anrufgründe aus dem letzten Monat sammeln. Drei auswählen, die sich mit geprüften Daten beantworten lassen.
2. **Woche 2:** Anbieter wählen, Vertrag zur Auftragsverarbeitung abschließen, EU-Verarbeitung einstellen. Ansage mit KI-Hinweis und Datenschutzinfo schreiben, Übergaberegeln festlegen.
3. **Woche 3:** Intern testen, mit Kollegen als Anrufern, auch mit Dialekt, Hintergrundlärm und schwierigen Fragen. Datenschutzbeauftragten einbinden, Folgenabschätzung prüfen.
4. **Woche 4:** Zunächst nur außerhalb der Geschäftszeiten live schalten. Jede Woche zehn Gespräche nachhören, sofern eingewilligt, oder die Zusammenfassungen prüfen. Erst wenn die Ergebnisse stimmen, die Zeiten ausweiten.

Ein guter Telefonagent ist wie ein guter Pförtner: freundlich, schnell, ehrlich darüber, wer er ist, und er weiß genau, wann er jemanden holen muss.
