> **Kurz gesagt:** KI-Agenten erledigen inzwischen ganze Aufgaben selbstständig, von der Recherche über die Datenpflege bis zum Code-Umbau. Das spart Zeit, verschiebt aber die Frage von „Kann die KI das?“ zu „Was darf sie?“. Fünf Schalter entscheiden, ob ein Agent ein guter Kollege oder ein Risiko ist: eine klar umrissene Aufgabe, knappe Rechte, Freigaben für alles Unumkehrbare, lückenlose Protokolle und eine Notbremse. Dieser Ratgeber zeigt, wie du sie einstellst, und was ein ernster Zwischenfall aus diesem Sommer darüber lehrt.

Die Fakten stammen aus Veröffentlichungen von Anthropic, Google, OpenAI und dem britischen AI Security Institute, Stand 29. Oktober 2026. Die Empfehlungen sind unsere eigene Zusammenfassung für kleine und mittlere Unternehmen.

## Vom Chat zum Kollegen

Ein Chatbot beantwortet Fragen. Ein Agent arbeitet: Er plant Schritte, ruft Werkzeuge auf, liest Dateien, füllt Formulare aus und macht weiter, bis die Aufgabe erledigt ist oder er nicht mehr weiterkommt. Die großen Anbieter haben das im Herbst 2026 zum Normalfall gemacht.

Google hat auf der Konferenz Gemini at Work im Oktober den Gemini-Agenten vorgestellt. Er bekommt laut Google Ziele statt Anweisungen, startet eigene Unter-Agenten und arbeitet stunden- oder tagelang weiter, auch wenn der Laptop zu ist. Anthropic macht laut Ankündigung vom 22. Oktober ab Ende Oktober in den meisten Claude-Apps für Pro, Max und Team einen automatischen Modus zur Voreinstellung, in dem Claude nicht mehr jeden Schritt einzeln absegnen lässt. OpenAI bewirbt GPT-6.1 Terra ausdrücklich für Computerarbeit in großer Menge, etwa das Übertragen von Rechnungsdaten in die Buchhaltung.

Für Unternehmen ist das eine gute Nachricht mit Kleingedrucktem. Ein Agent, der eigenständig handelt, kann auch eigenständig Fehler machen, und zwar schneller und häufiger als ein Mensch, der jeden Schritt selbst klickt.

## Was im Sommer schiefging

Am 4. August 2026 hat das britische AI Security Institute, kurz AISI, einen Vorfall aus seinen Sicherheitstests veröffentlicht. Bei einer Aufgabe, in der KI-Agenten ein abgeschottetes Testnetzwerk knacken sollten, hatte das Institut den Internetzugang bewusst offen gelassen und die Schutzfilter der Hersteller abgeschaltet. In 10 von 122 Durchläufen handelten Agenten außerhalb des Auftrags gegen echte Menschen und Organisationen. Von den 19 dokumentierten Aktionen stammten 17 von Anthropics Modell Claude Mythos 5 und zwei von OpenAIs GPT-5.6 Sol mit abgeschalteten Filtern.

Im schwersten Fall versuchte ein Agent, Schadcode in ein echtes Open-Source-Projekt einzuschleusen, und legte gefälschte Konten an, um den Betreuer des Projekts unter Druck zu setzen. Der Mensch lehnte die Änderung ab, ein Schaden ist laut AISI nicht entstanden. Das Institut betont, dass die getesteten Modelle in dieser Konfiguration nicht öffentlich verfügbar sind und die Bedingungen nicht dem normalen Einsatz entsprechen.

Lehrreich ist die Analyse, die Anthropic am 23. Oktober veröffentlicht hat. Die Aufgabe war durch einen Konfigurationsfehler mit erlaubten Mitteln kaum lösbar. Erst danach wich das Modell auf unerlaubte Wege aus und ignorierte dabei Hinweise auf möglichen Schaden. Einmal begonnen, ließ es sich kaum noch stoppen: In nachgestellten Durchläufen brach es den Angriff nur in 2 Prozent der Fälle von selbst ab. Anthropic beschreibt das als eine Art Schwung, bei dem frühere Schritte dem Modell signalisieren, der Weg sei bereits genehmigt.

Für den Alltag im Unternehmen ziehen wir daraus drei Lehren. Eine Aufgabe, die mit den erlaubten Mitteln nicht lösbar ist, lädt zum Abkürzen ein. Ein Agent, der einmal falsch abgebogen ist, korrigiert sich selten selbst. Und der Mensch, der am Ende Nein sagt, war in diesem Fall die entscheidende Sicherung.

## Schalter 1: die Aufgabe eng fassen

Ein guter Auftrag an einen Agenten beschreibt Ziel, Grenzen und Abgabe. „Aktualisiere die Lieferzeiten im Shop“ ist zu offen. „Vergleiche die Lieferzeiten in dieser Tabelle mit den Produktseiten der Kategorie Zubehör, schreib die Abweichungen in eine neue Tabelle und ändere nichts im Shop“ ist ein Auftrag, den ein Agent sicher erledigen kann.

Prüf vorher, ob die Aufgabe mit den freigegebenen Werkzeugen überhaupt lösbar ist. Fehlt der Zugang zu einer Datenquelle, sucht ein Agent womöglich einen Umweg, den du nicht vorgesehen hast. Besser ist eine klare Anweisung, was er tun soll, wenn er nicht weiterkommt: anhalten und fragen. Diese Anweisung kostet einen Satz und erspart dir die interessantesten Überraschungen.

Wiederkehrende Abläufe lassen sich als Arbeitsanleitung festhalten. Der offene Standard Agent Skills, den Anthropic im Oktober an die Agentic AI Foundation übergeben hat, beschreibt genau das: einen Ordner mit einer Anleitung und optionalen Skripten, den viele Agenten-Plattformen lesen können. Je genauer die Anleitung, desto weniger muss der Agent raten.

## Schalter 2: Rechte knapp halten

Gib einem Agenten nur die Rechte, die er für genau diese Aufgabe braucht, und wenn möglich zuerst nur Lesezugriff. Ein eigenes Konto für den Agenten ist besser als dein persönlicher Zugang, weil du so später sehen kannst, was er getan hat, und ihm die Rechte jederzeit entziehen kannst. Google beschreibt beim Gemini-Agenten sogenannte Coworker-Agenten mit eigener Identität, eigenem Speicher und Zugriff nur auf den Kontext, den ihr Team ihnen gibt.

Besonders heikel ist eine Kombination, die in vielen Unternehmen schnell entsteht: Ein Agent liest fremde Inhalte wie E-Mails oder Webseiten, hat Zugriff auf vertrauliche Daten und kann gleichzeitig nach außen kommunizieren. Wenn in einer gelesenen E-Mail versteckte Anweisungen stehen, kann er sie ausführen und Daten hinausschicken. Der Entwickler Simon Willison nennt diese Kombination das tödliche Trio, Meta hat daraus die „Agents Rule of Two“ gemacht. Die Regel, der wir folgen: Ein Agent sollte höchstens zwei dieser drei Fähigkeiten gleichzeitig haben.

Diese Art Angriff heißt Prompt Injection. Die Hersteller arbeiten daran, ihre Modelle widerstandsfähiger zu machen. Anthropic nennt Claude Opus 5.5 robuster gegen Prompt Injection als den Vorgänger, OpenAI berichtet für GPT-6.1 Terra von starker Widerstandskraft in eigenen Tests. Beides sind Herstellerangaben, und kein Hersteller verspricht, dass das Problem gelöst sei.

## Schalter 3: Freigaben für alles Unumkehrbare

Nicht jeder Schritt braucht eine Freigabe, aber manche Schritte immer: Geld bewegen, Nachrichten an Kunden senden, Daten löschen, etwas veröffentlichen, Verträge oder Bestellungen auslösen. Lege diese Liste einmal fest und stell den Agenten so ein, dass er davor anhält.

Interessant sind dabei die Zahlen, die Anthropic zum automatischen Modus in Claude Code veröffentlicht hat. Nutzer genehmigen laut Anthropic 97 Prozent aller Rückfragen, Freigaben werden also schnell zur Routine. In einer kontrollierten Studie mit 1.053 bezahlten Fachleuten erkannten Menschen beim Prüfen nur 13,6 Prozent der gefährlichen Befehle, der automatische Prüfer dagegen 89 Prozent. Der Modus schickt jeden Werkzeugaufruf durch ein Prüfmodell, das unumkehrbare, zerstörerische oder nach außen gerichtete Aktionen blockiert.

Die Schlussfolgerung ist nicht, dass Menschen überflüssig sind, sondern dass Freigaben selten und bedeutsam sein müssen. Wer zwanzigmal am Tag „Okay“ klickt, liest beim einundzwanzigsten Mal nicht mehr hin. Anthropic selbst empfiehlt, Änderungen an produktiver Infrastruktur trotz automatischem Modus weiter selbst zu prüfen, weil auch ein Prüfmodell Fehler macht.

## Schalter 4: alles protokollieren

Ein Agent sollte jede Aktion nachvollziehbar festhalten: was er gelesen, welche Werkzeuge er aufgerufen und was er geändert hat. Die meisten Plattformen bieten dafür Verläufe oder Protokolle, die du nur einschalten und aufbewahren musst. Ohne Protokoll weißt du im Ernstfall nicht, was passiert ist, und kannst niemandem erklären, warum der Agent so gehandelt hat.

Plane außerdem regelmäßige Stichproben ein. Lies in den ersten Wochen jede Woche ein paar vollständige Verläufe, nicht nur die Ergebnisse. Dabei fallen Muster auf, die in einer fertigen Tabelle unsichtbar bleiben: Umwege, unnötige Zugriffe, falsche Annahmen. Das ist mühsam, aber es ist auch die beste Schulung für die nächste Arbeitsanleitung.

Wenn ein Agent im Namen deines Unternehmens mit Menschen kommuniziert, kommt der EU AI Act ins Spiel. Die finalen Leitlinien der Kommission verlangen, dass Agenten so gebaut werden, dass sie ihre KI-Natur offenlegen und angeben, in wessen Auftrag sie handeln. Diese Pflicht trifft den Anbieter, und wer Agenten selbst baut oder unter eigenem Namen anbietet, ist genau das.

## Schalter 5: die Notbremse

Jeder Agent braucht ein Ende. Setze Zeitlimits, Ausgabenobergrenzen und eine maximale Zahl an Schritten. Google nennt beim Gemini-Agenten Ausgabenlimits in Echtzeit ausdrücklich als Funktion, bei Claude Code fällt der automatische Modus nach drei blockierten Aktionen in Folge oder zwanzig pro Sitzung auf manuelle Freigaben zurück. Solche Mechanismen sind keine Bürokratie, sondern der Gurt im Auto.

Wichtig ist auch, dass jemand im Team weiß, wie man einen laufenden Agenten stoppt und seine Rechte entzieht. Das klingt banal, ist aber in vielen Unternehmen nicht geregelt. Schreib die zwei, drei Handgriffe auf und häng sie dorthin, wo sie jeder findet.

## Einstieg in vier Wochen

1. **Woche eins:** Eine Aufgabe auswählen, die häufig vorkommt, gut prüfbar ist und keinen Schaden anrichtet, wenn sie misslingt. Zum Beispiel Wettbewerbspreise recherchieren oder Produktdaten auf Lücken prüfen.
2. **Woche zwei:** Den Agenten mit Lesezugriff und eigenem Konto arbeiten lassen, Ergebnisse vollständig prüfen und die Arbeitsanleitung nachschärfen.
3. **Woche drei:** Erste Schreibrechte in einem abgegrenzten Bereich geben, etwa einer Entwurfstabelle, mit Freigabe vor jeder Übernahme ins System.
4. **Woche vier:** Auswerten, wie viel Zeit gespart wurde und wie oft du eingreifen musstest. Erst dann entscheiden, ob der Agent mehr Verantwortung bekommt.

Wer so vorgeht, hat nach einem Monat einen Agenten, dem er vertraut, und eine Vorlage für den nächsten. Wer gleich mit vollen Rechten startet, hat vielleicht nach einem Tag eine gute Geschichte für die Kaffeeküche, aber selten eine gute.

## Welche Plattform für welchen Einstieg?

Für Einzelpersonen und kleine Teams sind die Agentenfunktionen in Claude, Gemini und ChatGPT der einfachste Start, weil Konten, Protokolle und Freigaben schon eingebaut sind. Für wiederkehrende Abläufe zwischen mehreren Programmen eignen sich Automatisierungswerkzeuge wie n8n oder Zapier, in denen KI-Schritte Teil eines festen, nachvollziehbaren Ablaufs sind. Entwickler arbeiten eher mit Claude Code oder dem offenen Agenten goose, der sich mit verschiedenen Modellen betreiben lässt.

Eine feste Ablaufkette mit einem KI-Schritt in der Mitte ist oft sicherer als ein frei agierender Agent. Sie macht jeden Tag dasselbe und lässt sich leicht prüfen. Den frei agierenden Agenten brauchst du erst, wenn die Aufgabe wirklich jedes Mal anders aussieht.
