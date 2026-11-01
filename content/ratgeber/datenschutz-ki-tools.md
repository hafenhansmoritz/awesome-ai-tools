> **Kurz gesagt:** Ob ein KI-Tool datenschutzrechtlich passt, entscheidet selten das Modell, sondern der Tarif. Die Business-Angebote von OpenAI, Anthropic und Google trainieren nach eigenen Angaben standardmäßig nicht mit deinen Eingaben und bieten einen Vertrag zur Auftragsverarbeitung. Bei kostenlosen und privaten Konten sieht das oft anders aus. Dieser Ratgeber zeigt, was die deutschen Aufsichtsbehörden erwarten, wo bei den großen Anbietern der Trainingsschalter sitzt, was „Datenstandort Europa“ wirklich abdeckt und welche zehn Fragen du jedem Anbieter vor dem Start stellst.

Grundlage sind die Orientierungshilfe der Datenschutzkonferenz vom Mai 2024 sowie die Datenschutzseiten von OpenAI, Anthropic, Google, Mistral und DeepL, Stand 29. Oktober 2026. Das hier ist keine Rechtsberatung, sondern eine Arbeitshilfe. Für Personal-, Gesundheits- oder Kundendaten in großem Umfang gehört die Person, die bei dir den Datenschutz verantwortet, von Anfang an mit an den Tisch.

## Die erste Frage: Sind Personendaten im Spiel?

Bevor es um Anbieter und Verträge geht, lohnt ein ehrlicher Blick auf den geplanten Einsatz. Die Datenschutzkonferenz, kurz DSK, rät, zuerst Einsatzfelder und Zwecke festzulegen. Nur dann lässt sich prüfen, ob personenbezogene Daten für den Zweck überhaupt nötig sind.

Manche Aufgaben kommen ganz ohne aus. Wer Produkttexte aus technischen Datenblättern schreiben lässt, Code ohne Kundendaten prüft oder eine Kategorieseite gliedert, bewegt sich meist außerhalb des Datenschutzrechts. Die DSK warnt aber vor einem verbreiteten Irrtum: Namen und Anschriften zu löschen reicht oft nicht. Ihr Beispiel ist die Bitte, ein befriedigendes Arbeitszeugnis für einen Kundenberater in einem bestimmten Autohaus zu entwerfen. Ohne einen einzigen Namen kann die Person trotzdem erkennbar sein, wenn klar ist, aus welchem Betrieb die Anfrage kam.

Auch die Antwort kann Personendaten enthalten, obwohl die Frage keine hatte. Wer ein Sprachmodell nach den besten Leuten für eine Aufgabe fragt, bekommt womöglich eine Liste echter Menschen. Spätestens wenn du so ein Ergebnis weiterverarbeitest, brauchst du dafür eine Rechtsgrundlage.

## Was die Aufsichtsbehörden erwarten

Die Orientierungshilfe „Künstliche Intelligenz und Datenschutz“ der DSK ist als Checkliste aufgebaut und richtet sich an Unternehmen, die KI-Anwendungen einsetzen. Für den Alltag in kleinen und mittleren Firmen sind diese Punkte am wichtigsten:

- **Geschlossene Systeme bevorzugen:** Die DSK hält technisch abgeschlossene Umgebungen für vorzugswürdig, in denen Eingaben nicht beim Anbieter ins Training wandern und nur ein begrenzter Kreis Zugriff hat.
- **Training ausschließen können:** Datenschutzrechtlich vorzugswürdig sind Anwendungen, die Ein- und Ausgaben nicht zum Training nutzen. Fehlt diese Wahl und sind Personendaten betroffen, braucht auch das Training eine eigene Rechtsgrundlage.
- **Eingabe-Historie steuerbar machen:** Nutzen mehrere Beschäftigte ein Konto, müssen sie wissen, dass ihre Eingaben gespeichert werden, und selbst entscheiden können.
- **Keine automatische Letztentscheidung:** Entscheidungen mit Rechtswirkung trifft ein Mensch. Die DSK nennt als Verstoß ausdrücklich eine KI, die Bewerbungen auswertet und selbstständig zu Gesprächen einlädt.
- **Vertrag zur Auftragsverarbeitung:** Läuft die Anwendung als Cloud-Dienst eines externen Anbieters, ist das häufig Auftragsverarbeitung nach Artikel 28 DSGVO, mit einem passenden Vertrag.
- **Datenschutz-Folgenabschätzung prüfen:** Beim KI-Einsatz wird laut DSK vielfach ein hohes Risiko vorliegen, das eine solche Abschätzung verlangt. Dafür brauchst du Informationen des Anbieters zur Funktionsweise.
- **Betriebliche Konten statt privater:** Arbeitgeber sollen Geräte und Konten stellen. Die Konten sollen keine Namen einzelner Beschäftigter tragen, sondern eine Funktionsadresse des Unternehmens.
- **Datenschutzfreundlich voreinstellen:** Training und Verlauf schon beim Einrichten eines Kontos abschalten, statt es jedem Nutzer selbst zu überlassen.
- **Ergebnisse prüfen:** Die DSK verlangt, Ergebnisse auf Richtigkeit und auf Diskriminierung zu prüfen, bevor sie genutzt werden.

Inzwischen hat die DSK nachgelegt. Im Juni 2025 kam eine Orientierungshilfe zu technischen und organisatorischen Maßnahmen bei KI-Systemen, im Oktober 2025 ein Papier zu den Besonderheiten von RAG, also KI-Systemen, die eigene Dokumente durchsuchen. Wer einen Chatbot auf das eigene Handbuch oder den Produktkatalog setzt, findet dort die passenden Hinweise.

## Privat-Abo oder Business-Tarif: der größte Unterschied

Die wichtigste Erkenntnis aus den Anbieterseiten ist schlicht: Dasselbe Modell kann je nach Tarif ganz unterschiedlich mit deinen Daten umgehen. Die folgende Übersicht fasst die Selbstauskünfte der Anbieter zusammen.

| Anbieter | Business-Tarife und API | Private und kostenlose Konten |
|---|---|---|
| OpenAI | Kein Training per Voreinstellung für ChatGPT Business, Enterprise, Edu und die API, außer du stimmst ausdrücklich zu | OpenAI nutzt laut eigener Auskunft auch Daten aus den Angeboten für Einzelpersonen zum Training |
| Anthropic | Kein Training per Voreinstellung für Claude for Work, also Team und Enterprise, und die API | Free, Pro und Max: Wahl beim Einrichten; mit Training fünf Jahre Speicherung, ohne 30 Tage |
| Google | Gemini in Workspace: Eingaben gelten als Kundendaten, kein Training ohne Erlaubnis, keine Prüfung durch Menschen | Wer Daten aus einem privaten Konto mit der Gemini-App teilt, unterliegt deren Bedingungen, Training ist dort möglich |
| Mistral | Enterprise standardmäßig ohne Training; im Teams-Tarif kann der Admin es für alle abschalten | Standard und kostenlos: Training per Voreinstellung, Widerspruch jederzeit möglich |
| DeepL | Pro: Texte werden nach der Übersetzung gelöscht und nicht zum Training genutzt | Kostenlose Version: Texte fließen ins Training, Personendaten sind laut Nutzungsbedingungen tabu |

Für den Alltag heißt das: Ein privates Abo, das ein Mitarbeiter mit der eigenen Kreditkarte bezahlt, ist für Kundendaten in aller Regel das falsche Werkzeug, auch wenn es dasselbe Modell nutzt wie der Firmentarif. Genau diese Schatten-KI meint die DSK, wenn sie schreibt, dass Beschäftigte KI-Anwendungen vielerorts eigenmächtig und unkontrolliert nutzen.

## Der Feedback-Knopf ist eine Ausnahme

Eine Falle steckt in einem unscheinbaren Symbol. Bei mehreren Anbietern gelten für den Daumen nach oben oder unten eigene Regeln, auch im Business-Tarif.

Anthropic speichert bei jedem Feedback das ganze zugehörige Gespräch bis zu fünf Jahre und kann es nach Trennung von Nutzer- und Kundenkennung für Training verwenden. Mistral schreibt, dass Bewertung, Eingabe und Ausgabe nach einem Feedback in jedem Tarif zur Verbesserung der Modelle genutzt werden dürfen, und rät, im Zweifel auf Feedback zu verzichten. OpenAI nennt solche Rückmeldungen ebenfalls als Weg, auf dem geteilte Daten ins Training gelangen können.

Die Konsequenz ist einfach: Schreib in eure KI-Regeln, dass Gespräche mit Kunden- oder Personaldaten nie bewertet werden. Es kostet nichts und schließt eine Lücke, die viele übersehen.

## Training abschalten: wo der Schalter sitzt

Wer trotz allem ein Einzelkonto nutzt, etwa für eigene Recherchen ohne Kundendaten, sollte den Trainingsschalter kennen.

- **Claude (Free, Pro, Max):** In den Einstellungen unter Privatsphäre den Punkt zur Verbesserung der KI-Modelle ausschalten. Laut Anthropic gilt das für neue und fortgesetzte Chats. Bereits laufendes oder abgeschlossenes Training bleibt davon unberührt, und Gespräche, die die Sicherheitsfilter markieren, können weiter für Sicherheitszwecke genutzt werden.
- **Vibe von Mistral, früher Le Chat:** Seit August 2026 heißt der Chat von Mistral Vibe, Adresse und Konto sind geblieben. Im Admin-Bereich unter Privatsphäre lässt sich die Nutzung der Interaktionen für Training abschalten, in den Apps über die Datenfreigabe in den Kontoeinstellungen. Wichtig: Der Schalter für Vibe und der für die API sind getrennt, beide müssen einzeln ausgeschaltet werden.
- **DeepL:** In der kostenlosen Version gibt es keinen solchen Schalter. Wer Texte mit Personenbezug übersetzen will, braucht laut Datenschutzerklärung einen Pro-Tarif.
- **OpenAI-API und Business:** Hier ist Training ohnehin aus, solange du nicht aktiv zustimmst, etwa über die Freigabe im API-Dashboard.

## Datenstandort: Was „in Europa“ abdeckt

Viele Anbieter werben inzwischen mit europäischen Rechenzentren. Wie weit das reicht, steht im Kleingedruckten.

OpenAI bietet für berechtigte Kunden von ChatGPT Enterprise, Edu und der API eine Speicherung in Europa an, wobei Europa hier den Europäischen Wirtschaftsraum und die Schweiz meint. Die Zusage gilt für Inhalte wie Prompts, Dateien und Antworten. Ausdrücklich ausgenommen sind Kontodaten, Rechnungsdaten, Nutzungsstatistiken und Protokolle ohne Inhalt. In der API lässt sich die europäische Verarbeitung nur für neu angelegte Projekte einstellen, bestehende Projekte können nicht nachträglich umziehen. Für solche Projekte verspricht OpenAI, Anfragen ohne Speicherung auf den eigenen Servern zu verarbeiten.

Google lässt Kunden die Verarbeitung von Gemini in Workspace auf die USA oder die EU begrenzen und bietet für besonders kritische Daten eine clientseitige Verschlüsselung, deren Schlüssel nur beim Kunden liegen. DeepL verarbeitet Dokumentübersetzungen nach eigener Angabe auf der eigenen Infrastruktur im Europäischen Wirtschaftsraum.

Zwei Dinge bleiben trotzdem zu prüfen. Erstens: Wer ist dein Vertragspartner? Eine europäische Tochter eines US-Konzerns ist etwas anderes als ein Anbieter mit Sitz in der EU. Zweitens: Welche Unterauftragnehmer sind beteiligt, und wo sitzen sie? Für Übermittlungen in Länder außerhalb der EU gelten die Regeln aus Kapitel V der DSGVO, auf die auch die DSK ausdrücklich hinweist.

## Der Vertrag zur Auftragsverarbeitung

Der Vertrag zur Auftragsverarbeitung, kurz AVV oder englisch DPA, regelt, dass der Anbieter deine Daten nur nach deiner Weisung verarbeitet. OpenAI, Google und Mistral nennen solche Verträge auf ihren Datenschutzseiten ausdrücklich, Google etwa das Cloud Data Processing Addendum, unter das auch die Prompts in Workspace fallen. Bei allen anderen Anbietern fragst du gezielt danach. Bei DeepL Pro ist der Abschluss in den Bedingungen vorgesehen und läuft über das Datenschutzteam des Anbieters.

Ein AVV allein macht den Einsatz nicht rechtmäßig, aber ohne ihn fehlt bei Cloud-Diensten mit Personendaten meist die Grundlage. Lies ihn nicht Wort für Wort, aber such gezielt nach fünf Stellen: Zweck und Art der Daten, Liste der Unterauftragnehmer, Ort der Verarbeitung, Fristen für Löschung, und wie schnell der Anbieter dich bei einer Datenpanne informiert.

## Was ein Datenleck bei Cloudflare lehrt

Wie real die letzte Frage ist, zeigt ein Bericht, den Cloudflare am 26. Oktober veröffentlicht hat. Beim Dienst Workers AI erhielten zwischen dem 27. August und dem 9. September einige Kunden des Modells GLM-5.3 Antworten, die Daten aus Anfragen anderer Kunden enthielten. Betroffen waren 155 Antworten, alle auf extrem lange Prompts mit mehr als 681.280 Token.

Ursache war laut Cloudflare eine Kombination aus einer Fehlkonfiguration und einem Fehler in der quelloffenen Software, die das Modell ausliefert. Ein Sicherheitsforscher meldete das Problem am 8. September. Cloudflare nahm das Modell am nächsten Morgen vom Netz und stellte den Dienst noch am selben Tag mit korrigierter Konfiguration und gepatchter Software wieder her. Hinweise auf gezielten Missbrauch fand das Unternehmen nicht.

Für dich als Kunde heißt das nicht, Cloud-KI zu meiden. Es heißt, dass auch gut betriebene Dienste Fehler haben, die Daten zwischen Kunden durchlassen können. Darum gehören Meldefristen in den Vertrag, darum sollten sensible Daten nur dort landen, wo sie wirklich gebraucht werden, und darum lohnt es sich, Anbieter zu wählen, die solche Vorfälle offen dokumentieren.

## Zehn Fragen an jeden Anbieter

Diese Fragen kannst du per E-Mail an den Vertrieb schicken oder auf den Datenschutzseiten nachschlagen. Fehlen Antworten, ist das bereits eine Antwort.

1. Werden Ein- und Ausgaben in unserem Tarif für Training genutzt, und lässt sich das zentral für alle Konten abschalten?
2. Gibt es Ausnahmen, etwa für Feedback, Fehlerberichte oder markierte Inhalte?
3. Wie lange werden Gespräche, Dateien und Protokolle gespeichert, und können wir das selbst festlegen?
4. Wer ist unser Vertragspartner, und wo hat er seinen Sitz?
5. Wo werden Inhalte gespeichert und wo verarbeitet, und welche Daten fallen nicht unter diese Zusage?
6. Gibt es einen Vertrag zur Auftragsverarbeitung, und wie schließen wir ihn ab?
7. Welche Unterauftragnehmer sind beteiligt, und wie erfahren wir von Änderungen?
8. Wie schnell informiert ihr uns über eine Datenpanne?
9. Welche Informationen zur Funktionsweise stellt ihr für unsere Datenschutz-Folgenabschätzung bereit?
10. Können Admins Konnektoren zu Postfach, Ablage und Kalender einzeln freigeben oder sperren?

Die letzte Frage wird mit Agenten wichtiger. Je mehr Quellen ein KI-Assistent selbst lesen darf, desto mehr Daten laufen durch ihn, ohne dass jemand sie bewusst eingetippt hat. Mehr dazu steht im Ratgeber über sichere KI-Agenten.

## Lokal statt Cloud

Die sicherste Datenübertragung ist die, die nicht stattfindet. Kleine Modelle laufen inzwischen auf normalen Laptops, etwa über Ollama oder LM Studio, und mit Open WebUI bekommt ein ganzes Team eine Chat-Oberfläche auf dem eigenen Server. Das entspricht ziemlich genau dem geschlossenen System, das die DSK bevorzugt.

Der Preis dafür ist Aufwand. Jemand muss den Rechner betreiben, Updates einspielen und die Zugänge verwalten, und die kleinen Modelle erreichen bei schwierigen Aufgaben nicht das Niveau der großen Cloud-Modelle. Ein guter Mittelweg für viele Firmen: lokale Modelle für alles mit Personal- oder Kundendaten, Business-Tarife der großen Anbieter für den Rest. Wie viel ein lokales Modell kann und was es kostet, steht im Preis-Ratgeber.

## Eine Seite Regeln fürs Team

Die DSK empfiehlt klare interne Weisungen, am besten mit Beispielen für erlaubte und verbotene Einsätze. Eine Seite reicht, wenn sie konkret ist:

- **Erlaubte Tools:** Welche Anwendungen in welchem Tarif genutzt werden dürfen, und dass private Konten für Firmendaten tabu sind.
- **Rote Daten:** Was nie eingegeben wird, etwa Gesundheitsdaten, Bankverbindungen, Zugangsdaten, Personalakten.
- **Gelbe Daten:** Was nur in freigegebenen Business-Tools mit AVV erlaubt ist, etwa Kundenanfragen ohne sensible Inhalte.
- **Grüne Daten:** Was überall unproblematisch ist, etwa öffentliche Produktinformationen.
- **Feedback-Regel:** Gespräche mit Personendaten werden nicht bewertet.
- **Prüfpflicht:** Kein Ergebnis geht ungeprüft an Kunden oder in Entscheidungen über Menschen.
- **Ansprechpartner:** Wer Fragen beantwortet und neue Tools freigibt.

Binde Betriebsrat und Datenschutzbeauftragten früh ein. Laut DSK kann die Einführung einer KI-Anwendung in einigen Fällen ein Mitbestimmungsrecht des Betriebsrats auslösen.

## Dein Fahrplan für die nächsten zwei Wochen

1. Frag im Team ab, welche KI-Tools tatsächlich genutzt werden, auch privat bezahlte.
2. Ordne jede Anwendung einem Zweck und einer Datenfarbe zu.
3. Wähle für jeden Zweck ein freigegebenes Tool in einem Business-Tarif oder lokal.
4. Schließ die Verträge zur Auftragsverarbeitung ab und leg sie zum Verzeichnis der Verarbeitungstätigkeiten.
5. Richte Konten mit Funktionsadressen ein, schalte Training und Verlauf zentral ab.
6. Verteil die Regelseite und sprich sie in einer kurzen Runde durch.
7. Prüf mit dem Datenschutzbeauftragten, ob eine Folgenabschätzung nötig ist.
8. Setz dir eine Erinnerung für ein halbes Jahr, denn Tarife und Bedingungen ändern sich schneller als jede Richtlinie.
