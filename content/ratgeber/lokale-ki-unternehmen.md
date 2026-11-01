> **Kurz gesagt:** Ein Sprachmodell auf dem eigenen Rechner kostet keine Token-Gebühren, funktioniert ohne Internet und lässt Kundendaten im Haus. Mit Ollama oder LM Studio läuft das erste Modell in einer Viertelstunde, mit Open WebUI bekommt das ganze Team eine Chat-Oberfläche. Die Grenzen sind Speicher, Qualität bei schweren Aufgaben und der eigene Betriebsaufwand. Dieser Ratgeber rechnet vor, wie viel Speicher ein Modell braucht, vergleicht die drei wichtigsten Werkzeuge, zeigt das Kleingedruckte in den Lizenzen und erklärt, wie ein Pilot in drei Wochen aussieht.

Die Angaben stammen aus den Dokumentationen von Ollama, LM Studio, Open WebUI und llama.cpp, den Modellkarten von Liquid AI und NVIDIA sowie Papieren der Datenschutzkonferenz und der Allianz für Cybersicherheit, Stand 29. Oktober 2026. Einschätzungen zur Qualität sind als unsere gekennzeichnet.

## Warum überhaupt lokal

Der stärkste Grund ist Datenschutz. Die Datenschutzkonferenz unterscheidet in ihrer Orientierungshilfe zu KI zwischen offenen Systemen, die ein Anbieter für einen unbestimmten Nutzerkreis in der Cloud betreibt, und geschlossenen Systemen in einer technisch abgegrenzten Umgebung. Ihr Fazit steht dort wörtlich: „Technisch geschlossene Systeme sind daher aus datenschutzrechtlicher Sicht vorzugswürdig.“ Ein Modell auf dem eigenen Server ist genau so ein System, sofern du es richtig abschottest.

Der zweite Grund ist Geld, allerdings mit Einschränkung. Lokal fällt keine Rechnung pro Token an, dafür Hardware, Strom und Arbeitszeit. Bei den heutigen Cloud-Preisen kleiner Modelle rechnet sich das selten über die Token-Kosten allein, sondern über Mengen, die sonst niemand freigeben würde: Tausende Support-E-Mails, interne Protokolle, Personalunterlagen.

Der dritte Grund ist Unabhängigkeit. Ein lokales Modell ändert sich nicht über Nacht, wird nicht abgekündigt und funktioniert auch, wenn der Anbieter gerade eine Störung hat.

Dagegen steht ein ehrlicher Nachteil: Kleine Modelle sind bei komplexen Aufgaben klar schwächer als die großen Cloud-Modelle. Liquid AI schreibt in der Modellkarte von LFM3 selbst, das Modell sei wegen seiner geringen Größe nicht für agentisches Programmieren und komplexes mehrstufiges Denken zu empfehlen.

## Was lokal heute gut funktioniert

Unsere Einschätzung aus der Praxis, nicht aus Benchmarks:

| Aufgabe | Lokal mit kleinem Modell | Anmerkung |
|---|---|---|
| Texte zusammenfassen, E-Mails vorsortieren | Gut | Klare, kurze Aufgaben liegen kleinen Modellen |
| Daten aus Dokumenten ziehen, etwa Rechnungsnummern | Gut | Ergebnis immer mit Stichproben prüfen |
| Fragen an eigene Dokumente, also RAG | Mittel bis gut | Hängt stark an Aufbereitung und Suche |
| Produkttexte entwerfen | Mittel | Stil und Fakten brauchen mehr Nacharbeit als bei großen Modellen |
| Übersetzen | Mittel | Für Rohfassungen brauchbar, für Veröffentlichung prüfen |
| Programmieren mit Agenten, lange Denkketten | Schwach | Hier spielen die großen Cloud-Modelle in einer anderen Liga |

Die Faustregel für den Einstieg: Lokal für alles mit sensiblen Daten und klarer Aufgabe, Cloud im Business-Tarif für die schweren Fälle ohne Personenbezug.

## Die Rechnung mit dem Speicher

Ob ein Modell läuft, entscheidet vor allem der Speicher, bei Grafikkarten der Grafikspeicher, bei Apple-Rechnern der gemeinsame Arbeitsspeicher. Der Trick heißt Quantisierung: Die Gewichte des Modells werden mit weniger Bits gespeichert, etwa 4 statt 16 oder 32. Laut der Dokumentation von llama.cpp schrumpft das Modell dadurch und wird oft schneller, kann aber etwas an Genauigkeit verlieren.

Wie groß der Effekt ist, zeigen die Beispielzahlen aus derselben Dokumentation für die Modellfamilie Llama 3.1:

| Modell | Original | 4 Bit (Q4_K_M) |
|---|---|---|
| 8 Milliarden Parameter | 32,1 GB | 4,9 GB |
| 70 Milliarden Parameter | 280,9 GB | 43,1 GB |
| 405 Milliarden Parameter | 1.625,1 GB | 249,1 GB |

Eine 4-Bit-Variante braucht also grob ein Siebtel des Platzes. Laut Hugging Face liegt das verbreitete Format Q4_K bei etwa 4,5 Bit pro Gewicht, Q8_0 bei 8 Bit. Für kleine Firmen heißt das: Modelle bis etwa 8 Milliarden Parameter passen auf normale Rechner, 70 Milliarden brauchen eine Workstation mit viel Speicher.

Zum Modell selbst kommt der Kontext. Ollama weist ausdrücklich darauf hin, dass ein längerer Kontext mehr Speicher braucht. Die Voreinstellung passt sich deshalb dem Grafikspeicher an: unter 24 GB sind es 4.000 Token, zwischen 24 und 48 GB 32.000, darüber 256.000. Für Agenten und Programmieraufgaben empfiehlt Ollama mindestens 64.000 Token. Wer lange Dokumente verarbeiten will, plant deshalb Speicher über die reine Modellgröße hinaus ein.

## Drei Hardware-Stufen

**Stufe 1: der vorhandene Laptop.** LM Studio empfiehlt 16 GB Arbeitsspeicher, auf Windows dazu mindestens 4 GB eigenen Grafikspeicher. Auf Macs läuft LM Studio nur mit Apple-Chips ab macOS 14, Ollama unterstützt auf Apple-Chips Prozessor und Grafik, auf älteren Intel-Macs nur den Prozessor. Damit laufen Modelle wie LFM3, dessen Textmodell laut Liquid AI bei 4 Bit in rund 1 GB passt; die Datei auf Hugging Face ist 1,10 GB groß.

**Stufe 2: ein Arbeitsplatz mit Grafikkarte.** Ein Papier aus dem Expertenkreis KI-Sicherheit der Allianz für Cybersicherheit, die das BSI betreibt, nennt als Richtwert einen modernen Gaming-PC mit mindestens 6 GB Grafikspeicher für kleine Modelle und 12 GB für relativ komplexe Anwendungen. Das Papier stammt von externen Fachleuten und ist keine offizielle Position des BSI, gibt aber eine gute Orientierung. In diese Klasse fällt Nemotron 3.5 Bolt E4B von NVIDIA. In NVIDIAs Test auf einer RTX 5070 belegt es je nach Gesprächslänge 3,5 bis 4,3 GB Grafikspeicher, die 4-Bit-Datei auf Hugging Face ist mit 6,18 GB allerdings größer.

**Stufe 3: ein Server fürs Team.** Wer Modelle mit 70 Milliarden Parametern betreiben oder viele Nutzer gleichzeitig bedienen will, braucht entsprechend Grafikspeicher, nach der Tabelle oben mindestens gut 43 GB plus Kontext. Das ist der Punkt, an dem ein Gespräch mit einem Systemhaus oder ein gemieteter GPU-Server in einem europäischen Rechenzentrum sinnvoll wird.

## Die Werkzeuge im Vergleich

| Werkzeug | Lizenz | Für wen | Besonderheit |
|---|---|---|---|
| Ollama | MIT, quelloffen | Technisch Interessierte, Server | Kommandozeile und Programmierschnittstelle, teilweise kompatibel zur OpenAI-API |
| LM Studio | Proprietär, kostenlos auch für die Arbeit | Einzelne Nutzer ohne Kommandozeile | Grafische Oberfläche, Modellsuche, lokaler Server |
| Open WebUI | BSD-3 mit Marken-Zusatz | Teams | Chat-Oberfläche im Browser mit Benutzerverwaltung und Dokumentensuche |

**Ollama** läuft auf macOS ab Version 14, Windows 10 ab 22H2 und Linux. Auf Windows braucht es für NVIDIA-Karten einen Treiber ab Version 551.61, AMD-Karten laufen über ROCm, weitere Grafikkarten einschließlich Intel über Vulkan. Ollama lauscht standardmäßig nur auf dem eigenen Rechner unter Port 11434 und hält ein Modell nach der letzten Anfrage fünf Minuten im Speicher. Viele Programme, die eigentlich für die OpenAI-API gebaut sind, lassen sich über die kompatible Schnittstelle an Ollama hängen.

**LM Studio** ist die bequemste Lösung für Einzelne. Seit Juli 2025 ist die Nutzung im Unternehmen ohne eigene Lizenz erlaubt. Die Nutzungsbedingungen beschränken die Software auf persönliche und interne geschäftliche Zwecke und verbieten es, sie als Dienst für Dritte anzubieten. Laut Dokumentation kann LM Studio vollständig offline arbeiten, Chat, Dokumentenchat und lokaler Server brauchen kein Internet.

**Open WebUI** ist die Oberfläche, mit der aus einem lokalen Modell ein Werkzeug für alle wird. Es verbindet sich mit Ollama oder jeder OpenAI-kompatiblen Schnittstelle, bietet Rollen und Gruppen, Anmeldung über LDAP, Active Directory oder Single Sign-on und eine lokale Dokumentensuche. Die Installation läuft in der Regel über Docker mit einem einzigen Befehl.

## Lizenzen: das Kleingedruckte

Lokal heißt nicht lizenzfrei. Vier Beispiele zeigen, warum sich ein Blick lohnt:

- **LFM3 von Liquid AI** steht unter der LFM Open License, die auf Apache 2.0 aufbaut. Das Recht zur kommerziellen Nutzung endet aber, sobald der Jahresumsatz des Unternehmens 10 Millionen Dollar übersteigt. Darüber braucht es eine kaufpflichtige Lizenz.
- **Nemotron 3.5 Bolt** steht unter der OpenMDW-Lizenz 1.1, die Nutzung ohne Einschränkungen erlaubt, solange Lizenz und Hinweise erhalten bleiben. NVIDIA gibt das Modell ausdrücklich für kommerzielle Nutzung frei.
- **Open WebUI** stand bis Version 0.6.5 unter reiner BSD-3-Lizenz. Seit Version 0.6.6 vom April 2025 verbietet ein Zusatz, den Namen und das Logo zu entfernen oder zu ersetzen. Ausgenommen sind Installationen mit höchstens 50 Endnutzern in 30 Tagen, mit schriftlicher Erlaubnis oder mit Enterprise-Lizenz.
- **LM Studio** ist kein Open Source. Für interne Nutzung ist es frei, als Grundlage für ein Angebot an Kunden nicht.

Schreib die Lizenz jedes eingesetzten Modells in dein Verzeichnis der eingesetzten Software. Bei Modellen ändert sie sich mit neuen Versionen öfter als bei klassischer Software.

## Die Cloud-Hintertür

Ein lokales Werkzeug kann trotzdem Daten nach außen schicken, und zwar auf ganz legalem Weg. Ollama bietet neben lokalen Modellen auch Cloud-Modelle an, die auf den Servern von Ollama laufen und sich in der App und der Kommandozeile über eigene Kennungen auswählen lassen. Laut Ollama werden Prompts dort zwar weder gespeichert noch protokolliert noch fürs Training genutzt, sie verlassen aber den eigenen Rechner. Wer das ausschließen will, schaltet die Cloud-Funktionen ab, über die Umgebungsvariable `OLLAMA_NO_CLOUD=1` oder eine Einstellung in der Konfigurationsdatei.

Dazu kommen Updates und Modell-Downloads. Ollama lädt auf macOS und Windows Updates automatisch herunter, LM Studio prüft auf Updates und sucht Modelle im Netz. Für den Betrieb heißt das: Modelle einmal laden und prüfen, danach den Rechner vom Internet trennen oder per Firewall nur die nötigen Verbindungen zulassen.

## Sicher betreiben

Das Papier der Allianz für Cybersicherheit warnt, dass lokaler Betrieb mehr Eigenverantwortung bedeutet. Seine Empfehlungen lassen sich in fünf Schritte fassen:

1. **Nur im internen Netz betreiben.** Zugriffe von außen per Firewall sperren. Ollama ist ab Werk nur lokal erreichbar; wer es mit `OLLAMA_HOST` im Netzwerk freigibt, braucht davor eine Absicherung, denn die Schnittstelle selbst prüft keine Zugangsdaten.
2. **Telemetrie und Updates bewusst steuern.** Prüfen, welche Verbindungen ein Werkzeug aufbaut, und Updates kontrolliert einspielen.
3. **Datenschutz dokumentieren.** Eine Schwellwertanalyse für die Datenschutz-Folgenabschätzung machen und die Verarbeitung ins Verzeichnis nach Artikel 30 DSGVO aufnehmen.
4. **Bestehende Sicherheitsregeln anwenden.** Ein KI-Server ist ein Server. Für die Bundesverwaltung verlangt das BSI bei lokal betriebenen Modellen ausdrücklich klassische IT-Sicherheitsmaßnahmen nach IT-Grundschutz, für Unternehmen ist das ein guter Maßstab.
5. **Zugänge personalisieren.** In Open WebUI jedem Nutzer ein eigenes Konto mit passender Rolle geben, statt ein gemeinsames Passwort zu verteilen.

## Lokal im Browser: der nächste Schritt

Am 27. Oktober hat Opera mit WebAI eine Vorschau gestartet, die KI-Modelle direkt im Browser ausführt. Webseiten und Erweiterungen können damit über neue Schnittstellen Texte erzeugen, Entscheidungen treffen oder Inhalte vergleichen, ohne Server, ohne API-Schlüssel und ohne Kosten pro Anfrage. Opera beschreibt WebAI als vorgeschlagenen Webstandard, den unter anderem Google und Microsoft unterstützen.

Die Funktion ist zunächst in Opera One verfügbar, für Opera GX und Neon angekündigt, und läuft auf 64-Bit-Windows mit Intel- oder AMD-Prozessor sowie auf Macs mit Apple-Chip. Nichts wird heruntergeladen, bevor Nutzer die Funktion in den Einstellungen einschalten, und jede Seite braucht eine eigene Erlaubnis. Für Shops ist das noch Zukunftsmusik, zeigt aber die Richtung: KI-Funktionen, bei denen die Daten den Rechner des Kunden nie verlassen.

## Dein Pilot in drei Wochen

1. **Woche 1:** Eine Aufgabe mit sensiblen Daten und klarer Erfolgsmessung wählen, etwa das Vorsortieren von Support-E-Mails. LM Studio auf einem vorhandenen Rechner installieren und zwei bis drei kleine Modelle mit 30 echten, aber anonymisierten Beispielen testen.
2. **Woche 2:** Das beste Modell über Ollama auf einem Rechner im internen Netz bereitstellen, Cloud-Funktionen abschalten, Open WebUI davorsetzen und fünf Kollegen Konten geben.
3. **Woche 3:** Ergebnisse gegen die Arbeit von Hand vergleichen, Zeitersparnis und Fehlerquote notieren, Lizenzen und Datenschutz dokumentieren. Dann entscheiden: ausbauen, auf ein größeres Modell wechseln oder diese Aufgabe doch einem Business-Tarif in der Cloud geben.

Der wichtigste Erfolgsfaktor ist dabei nicht die Hardware, sondern die Auswahl der Aufgabe. Ein kleines Modell, das eine klar umrissene Arbeit zuverlässig erledigt, ist mehr wert als ein großes, das alles ein bisschen kann.
