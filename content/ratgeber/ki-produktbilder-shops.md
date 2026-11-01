> **Kurz gesagt:** KI kann Hintergründe tauschen, Produktfotos hochrechnen, Szenen bauen und kurze Clips erzeugen, für Cent-Beträge pro Bild. Für Shops entscheiden drei Fragen über Erfolg oder Ärger: Zeigt das Bild noch das echte Produkt? Bleiben die Herkunftsdaten in der Datei, die Google Merchant Center verlangt? Und weiß der Kunde, was er sieht, wenn die KI mehr als nur aufgeräumt hat? Dieser Ratgeber zeigt, was die großen Plattformen erlauben, was AI Act und Wettbewerbsrecht sagen, welche Werkzeuge was kosten und wie ein sauberer Bild-Workflow aussieht.

Die Fakten stammen aus den Hilfeseiten von Google Merchant Center, Amazon und eBay und den Preisseiten von Google, OpenAI, Black Forest Labs und Adobe. Dazu kommen das Gesetz gegen den unlauteren Wettbewerb und die Leitlinien der EU-Kommission zu Artikel 50 des AI Act, Stand 28. Oktober 2026. Das hier ist keine Rechtsberatung.

## Was KI bei Produktbildern gut kann

Die nützlichsten Einsätze sind unspektakulär: Hintergrund entfernen oder vereinheitlichen, Staub und Kratzer auf dem Foto retuschieren, ein zu kleines Bild hochrechnen, das Format für verschiedene Kanäle anpassen. Dazu kommen Szenenbilder, auf denen ein echtes Produkt vor einem erzeugten Hintergrund steht, und kurze Clips für Anzeigen und soziale Netzwerke.

Heikel wird es, sobald die KI das Produkt selbst verändert: eine glänzendere Oberfläche, ein fehlendes Teil, das plötzlich da ist, eine Farbe, die es so nicht gibt. Genau an dieser Grenze setzen Plattformregeln und Recht an.

## Google Merchant Center: Metadaten müssen drinbleiben

Google verlangt für alle mit generativer KI erstellten Bilder im Merchant Center einen Herkunftshinweis in der Datei, das IPTC-Feld DigitalSourceType mit dem Wert TrainedAlgorithmicMedia. Solche eingebetteten Angaben dürfen laut Google nicht entfernt werden, auch nicht bei Bildern aus Googles eigenem Werkzeug Product Studio. Neben TrainedAlgorithmicMedia nennt Google die Werte CompositeSynthetic für Montagen mit KI-Anteilen und AlgorithmicMedia als zu erhaltende Kennzeichnungen. Erlaubt sind KI-Bilder dann im Hauptbild, in zusätzlichen Bildern und in Lifestyle-Bildern.

Für KI-Texte gibt es eigene Felder: Ein mit KI erzeugter Titel gehört in das Attribut `structured_title`, eine Beschreibung in `structured_description`, jeweils mit der Angabe `trained_algorithmic_media`. Eine Falle steckt im Detail: Schickst du sowohl `title` als auch `structured_title`, nutzt Google nur das normale `title`. Ein sichtbares Label „KI-generiert“ verlangt Google dagegen nicht, die Kennzeichnung ist maschinenlesbar.

Die allgemeinen Bildregeln gelten weiter. Abgelehnt werden unter anderem Werbeaufdrucke wie Preise, Versandhinweise, „Neu“ oder Kompatibilitätsangaben, Wasserzeichen und Copyright-Zeichen, nachträglich eingefügte Logos sowie Platzhalter und Bilder mit Produkten, die nicht mitverkauft werden. Ab dem 31. Januar 2027 müssen Bilder mindestens 500 mal 500 Pixel groß sein, empfohlen sind rund 1.500 mal 1.500. Hochskalieren ist laut Produktdaten-Spezifikation ausdrücklich unerwünscht, das Bild soll das Produkt genau zeigen.

Eine gute Nachricht für Teile-Händler: Für die Kategorie Fahrzeuge und Teile erlaubt Google ausdrücklich generische Bilder, Grafiken oder Illustrationen. Ein sauber gezeichnetes Ersatzteil ist dort also kein Verstoß.

## Product Studio: Googles eigenes Werkzeug

Im Merchant Center steckt mit Product Studio ein kostenloses KI-Werkzeug. Es tauscht oder entfernt Hintergründe, erhöht die Auflösung, animiert Bilder und erzeugt neue Bilder aus einer Beschreibung und bis zu drei Vorlagen. Laut Google steht es allen Händlern außer in Russland und Frankreich zur Verfügung und funktioniert unter anderem mit deutschen Beschreibungen. Die Videoerzeugung gibt es dagegen nur für Händler in Australien, Kanada, Indien, Japan, Großbritannien und den USA, also nicht in Deutschland.

Drei Einschränkungen nennt Google selbst: Die Funktion ist als experimentell gekennzeichnet, Bilder mit Händen und regulierte Produkte sind ausgeschlossen, und menschliche Qualitätsprüfer können Eingaben und Ergebnisse sehen.

## Amazon und eBay: das echte Produkt zählt

Für das Hauptbild bei Amazon gelten strenge Regeln: reinweißer Hintergrund mit den Farbwerten 255, 255, 255, und das Produkt füllt mindestens 85 Prozent der Fläche. Text, Logos, Rahmen und Wasserzeichen sind tabu, und das Bild zeigt das tatsächliche Produkt, keine Grafik oder Illustration. Eine eigene Regel speziell für KI-Bilder im Katalog haben wir in den Hilfeseiten von Amazon nicht gefunden. In der Werbung bietet Amazon selbst einen kostenlosen Bildgenerator an, der seit April 2024 auch in Deutschland verfügbar ist, mit dem Hinweis, dass KI-Ergebnisse Fehler enthalten können. Anzeigen dürfen Produkte laut Amazon nicht falsch darstellen.

eBay verbietet unter anderem Fotos, die den Artikel nicht genau zeigen, Platzhalter, Stockfotos bei gebrauchten oder beschädigten Artikeln, eingefügte Texte und Wasserzeichen jeder Art. Die Nutzungsvereinbarung stellt klar, dass Verkäufer für Richtigkeit und Rechtmäßigkeit ihrer Angebote verantwortlich sind, ausdrücklich auch für Inhalte, die mit Bildbearbeitung und generativer KI erstellt wurden.

Für Gebrauchtteile heißt das ohne Umweg: Hier gehört ein echtes Foto des konkreten Teils ins Angebot, kein erzeugtes Idealbild.

## Was das Recht sagt

Zwei Regelwerke greifen ineinander. Das deutsche Wettbewerbsrecht verbietet irreführende geschäftliche Handlungen, unter anderem über wesentliche Merkmale einer Ware wie Ausführung, Zusammensetzung, Zubehör, Verwendungsmöglichkeit oder Beschaffenheit. § 5 Absatz 4 UWG stellt dabei klar, dass auch bildliche Darstellungen solche Angaben sein können. Ein Bild, das ein Produkt besser zeigt, als es ist, kann also abgemahnt werden, ganz unabhängig davon, ob eine KI im Spiel war.

Der AI Act ergänzt das seit dem 2. August 2026 um Transparenzpflichten. Die Anbieter von Bildgeneratoren müssen ihre Ergebnisse maschinenlesbar kennzeichnen. Für Systeme, die vor dem Stichtag auf dem Markt waren, gilt diese Pflicht erst ab dem 2. Dezember 2026. Ausgenommen sind Werkzeuge mit unterstützender Funktion für Standardbearbeitung. Die Leitlinien der Kommission nennen dafür Beispiele, die im Shop-Alltag ständig vorkommen: leichtes Zuschneiden, kleine Farbkorrekturen, Aufhellen, Schärfen und das Entfernen von Staubflecken. Ebenso zählen das Entfernen oder Verdecken eines im Original sichtbaren Hintergrunds und das Auffüllen von Rändern für ein anderes Seitenverhältnis dazu. Eine Kennzeichnung braucht es dagegen, wenn Objekte so entfernt, ersetzt oder eingefügt werden, dass sich Bedeutung und Aussage ändern.

Für dich als Händler ist vor allem die Deepfake-Regel in Absatz 4 wichtig. Die Kommission ordnet Farbkorrekturen, Hintergrundwechsel aus ästhetischen Gründen, Arrangements echter Produkte und das Skalieren von Bildern in der Produktwerbung als voraussichtlich geringfügig ein. Ein echtes Produkt vor einem KI-Hintergrund ist laut Leitlinien kein Deepfake, solange die Anzeige nicht irreführt. Als Deepfake nennt die Kommission dagegen ein KI-Bild, das über Aussehen, Eigenschaften oder Gebrauch des echten Produkts täuschen kann, etwa weil es ansprechender oder hochwertiger wirkt als in Wirklichkeit. Dann muss das Bild beim ersten Kontakt sichtbar gekennzeichnet sein; ein maschinenlesbarer Hinweis allein reicht nicht.

Und noch eine Klarstellung der Leitlinien: Ein Unternehmen, das nur eine Agentur beauftragt, ohne selbst über den KI-Einsatz zu entscheiden, ist nicht selbst Betreiber im Sinne der Regel. Wer die Werkzeuge im eigenen Team nutzt, ist es.

## Die Ampel für deinen Bild-Workflow

Aus Plattformregeln und Leitlinien ergibt sich eine einfache Einteilung, als Arbeitshilfe, nicht als Rechtsrat:

| Bearbeitung | Einschätzung | Was zu tun ist |
|---|---|---|
| Freistellen, weißer Hintergrund, Staub entfernen, leichte Farbkorrektur, Zuschnitt | Grün | Normal verwenden, Metadaten des Werkzeugs nicht löschen |
| Echtes Produkt vor erzeugtem Hintergrund oder in erzeugter Szene | Gelb | Produkt unverändert lassen, Herkunftsdaten erhalten, nicht als Hauptbild bei Amazon |
| Produkt selbst verändert, ergänzt oder komplett erzeugt | Rot | Nur wenn es exakt dem echten Produkt entspricht, sonst gar nicht; im Zweifel sichtbar kennzeichnen |
| KI-Menschen, die ein Produkt vorführen oder testen | Rot | Laut Kommission ein Deepfake, sichtbare Kennzeichnung nötig |
| Gebrauchtteile, Einzelstücke | Rot für KI-Ersatz | Immer echtes Foto des konkreten Artikels |

## Werkzeuge und Kosten

Die Preise pro Bild sind inzwischen so niedrig, dass sie in der Kalkulation kaum noch auftauchen. Teuer ist die Zeit für Auswahl und Kontrolle.

| Werkzeug | Preis laut Anbieter | Herkunftskennzeichnung |
|---|---|---|
| Google Nano Banana 2.1 über die Gemini-API | rund 0,034 Dollar pro Bild in 1K, 0,113 Dollar in 4K | Wasserzeichen SynthID in allen Bildern, auf Googles Cloud-Plattform zusätzlich Content Credentials |
| Google Product Studio im Merchant Center | kostenlos | Metadaten in der Datei, die nicht entfernt werden dürfen |
| OpenAI GPT Image 2 | 0,006 bis 0,211 Dollar pro Bild in 1024 Pixeln, je nach Qualitätsstufe | Content Credentials und SynthID |
| FLUX 3 Image von Black Forest Labs | 0,048 Dollar pro Bild in 1K | C2PA bei Nutzung über die Dienste von Black Forest Labs |
| FLUX 3 Image Klein | 0,009 Dollar pro Bild in 1K, offene Gewichte | Über die API mit C2PA, beim Selbstbetrieb nicht |
| Gemini Omni Flash für Video | rund 0,10 Dollar pro Sekunde in 720p | SynthID in allen Videos |
| Adobe Firefly | im Abo | Content Credentials für vollständig erzeugte Inhalte; Freistellung von IP-Ansprüchen in berechtigten Tarifen |

Zwei Punkte aus dem Kleingedruckten: Die frei herunterladbaren Gewichte von FLUX 3 Image Klein stehen unter einer Lizenz, die kommerzielle Nutzung nur bis 5 Millionen Dollar Jahresumsatz kostenlos erlaubt. Größere Firmen nutzen die API oder kaufen eine Lizenz. Und Adobe begründet seine Freistellung damit, dass Firefly auf lizenzierten Inhalten wie Adobe Stock und gemeinfreien Werken trainiert wurde, schließt aber veränderte Ergebnisse und Partnermodelle anderer Hersteller davon aus.

Google hat Imagen und die Vorschau von Veo 3.1 in der Gemini-API abgeschaltet. Wer noch Abläufe mit diesen Modellen betreibt, muss auf die Nachfolger umstellen.

## Herkunftsdaten: der unterschätzte Teil

Die meisten großen Generatoren schreiben inzwischen Herkunftsdaten in ihre Dateien, entweder nach dem Standard C2PA, bekannt als Content Credentials, oder als IPTC-Angabe, oft beides. Das Problem entsteht danach: Viele Bildbearbeitungen, Kompressionswerkzeuge und Shop-Systeme entfernen Metadaten beim Speichern oder Hochladen, und OpenAI wie Black Forest Labs weisen selbst darauf hin, dass sich solche Daten entfernen lassen.

Für Google Shopping ist das kein Detail, sondern eine Regel. Prüf deshalb einmal die ganze Kette: Bild erzeugen, bearbeiten, komprimieren, ins Shopsystem laden, in den Feed exportieren. Mit dem kostenlosen Prüfwerkzeug auf contentcredentials.org siehst du, ob die Angaben am Ende noch drin sind. Wenn nicht, liegt das Leck meist beim Komprimieren oder beim Export.

## Dein Fahrplan in drei Wochen

1. **Woche 1:** Bildtypen im Shop sortieren: Hauptbilder, Detailbilder, Szenen, Anzeigen. Für jeden Typ nach der Ampel festlegen, was KI darf. Gebrauchtteile und Einzelstücke ausnehmen.
2. **Woche 2:** Ein Werkzeug pro Aufgabe wählen und mit 20 Produkten testen. Bei jedem Bild gegen das echte Produkt prüfen: Farbe, Teile, Oberfläche, Größenverhältnis.
3. **Woche 3:** Die Metadaten-Kette durchtesten und reparieren, KI-Texte im Feed auf die strukturierten Attribute umstellen und eine kurze Regel für das Team aufschreiben, wer Bilder freigibt.

Ein gutes KI-Produktbild erkennt man daran, dass der Kunde beim Auspacken nicht überrascht ist. Alles andere kostet am Ende mehr, als die schönste Szene einbringt.
