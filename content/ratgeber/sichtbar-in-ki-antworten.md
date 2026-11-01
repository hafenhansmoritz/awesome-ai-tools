> **Kurz gesagt:** Für Google AI Overviews und AI Mode gibt es keinen Geheimtrick. Google sagt selbst, dass eine Seite nur indexiert und mit Snippet ausspielbar sein muss, und dass weder spezielle Markups noch KI-Textdateien nötig sind. Für ChatGPT entscheidet vor allem, ob du den Such-Crawler OAI-SearchBot zulässt, und bei Produkten, wie vollständig deine Produktdaten sind. Wer sauberes SEO macht, vollständige Produktdaten pflegt und Fragen wirklich beantwortet, ist für KI-Suchen schon gut aufgestellt. Der Rest ist Messen und bewusstes Entscheiden.

Dieser Ratgeber stützt sich auf die Dokumentation von Google Search Central, die Hilfeseiten der Search Console und die Entwicklerseiten von OpenAI, Stand 28. Oktober 2026. Wo wir eigene Erfahrungen oder Einschätzungen ergänzen, steht das dabei.

## Was sich geändert hat

Bei einem Teil der Suchanfragen steht heute vor der Liste mit zehn blauen Links eine Antwort, die ein Sprachmodell aus mehreren Quellen zusammenstellt. Bei Google heißen diese Formate AI Overviews und AI Mode, bei OpenAI ist es die Suche in ChatGPT, dazu kommen Antwortmaschinen wie Perplexity und Assistenten wie Gemini, die selbst im Web nachschlagen.

Für Shops und Marken bedeutet das zweierlei. Erstens zählt nicht mehr nur die Position, sondern ob die eigene Seite als Quelle verlinkt wird. Zweitens rücken Produktdaten näher an die Antwort heran, weil die Assistenten Preise, Verfügbarkeit und Bewertungen direkt vergleichen. Wer hier fehlt oder mit falschen Daten auftaucht, verliert den Kunden, bevor er überhaupt auf der Website landet.

## Was Google offiziell sagt

Google Search Central beschreibt die Lage ungewöhnlich klar: Für AI Overviews und AI Mode gelten die bekannten SEO-Grundlagen, und es gibt keine zusätzlichen Anforderungen. Damit eine Seite als unterstützender Link erscheinen kann, muss sie indexiert und berechtigt sein, in der Google-Suche mit einem Snippet angezeigt zu werden. Weitere technische Voraussetzungen nennt Google nicht.

Ausdrücklich heißt es dort, dass du keine neuen maschinenlesbaren Dateien, keine KI-Textdateien und kein spezielles Markup brauchst, auch keine besonderen schema.org-Auszeichnungen. Wer gerade eine llms.txt baut, nur um in Googles KI-Antworten aufzutauchen, kann sich die Arbeit also sparen. Für andere Systeme mag so eine Datei nützlich sein, für Google ist sie laut eigener Doku kein Kriterium.

Spannend ist eine technische Beschreibung: Beide Formate können eine Technik nutzen, die Google „Query Fan-out“ nennt. Dabei schickt das System zu einer Frage mehrere verwandte Suchen zu Unterthemen los und stellt daraus die Antwort zusammen. Für dich heißt das, dass nicht nur die eine Hauptseite zählt, sondern auch die Seiten zu Teilfragen, Vergleichen und Details.

Als Grundlagen, die sich weiterhin lohnen, nennt Google unter anderem: Crawling in der robots.txt und beim CDN erlauben, Inhalte über interne Links auffindbar machen und eine gute Nutzererfahrung bieten. Dazu kommen wichtige Inhalte als Text, strukturierte Daten passend zum sichtbaren Text und aktuelle Angaben im Merchant Center und im Unternehmensprofil. Das liest sich wie eine gewöhnliche SEO-Checkliste, und genau das ist die Botschaft.

## Der neue Schalter in der Search Console

Seit dem 31. August 2026 hat Google weltweit eine neue Einstellung in der Search Console ausgerollt. Unter Einstellungen findest du die Steuerung für generative KI in der Suche. Standardmäßig ist deine Website eingeschlossen, ihre Links und Inhalte können also in AI Overviews, AI Mode und den KI-Funktionen von Discover erscheinen und Antworten mit Quellen untermauern.

Schließt du deine Website aus, erscheinen ihre Links und Inhalte dort nicht mehr, und du bekommst aus diesen Funktionen weder Impressionen noch Besuche. Inhalte anderer Seiten bleiben natürlich verfügbar, auch wenn sie deinen ähneln. Laut Google ist die Einstellung kein Rankingsignal für die übrige Suche. Sie beeinflusst auch nicht das Training von KI-Modellen, dafür gibt es weiterhin Google-Extended.

Zusammen mit dem Schalter gibt es einen eigenen Leistungsbericht für generative KI. Er zeigt Impressionen und welche Seiten in KI-Antworten erscheinen, aufgeschlüsselt nach Ländern. Unser Rat: Schau dir diesen Bericht ein paar Wochen an, bevor du irgendetwas ausschaltest. Wer ohne Daten aussteigt, spart sich vielleicht ein ungutes Gefühl und verliert dafür Sichtbarkeit.

## Feiner steuern statt ganz aussteigen

Zwischen „alles drin“ und „alles raus“ gibt es die bekannten Snippet-Steuerungen, die Google ausdrücklich auch für KI-Funktionen nennt. Mit `nosnippet` verhinderst du Ausschnitte einer Seite, mit `data-nosnippet` schützt du einzelne Abschnitte, mit `max-snippet` begrenzt du die Länge und mit `noindex` nimmst du eine Seite ganz aus der Suche.

Damit lassen sich zum Beispiel Preise, die nur für eingeloggte Händler gelten, oder interne Konditionen aus Antworten heraushalten, ohne die ganze Seite zu verstecken. Google weist darauf hin, dass Änderungen erst nach dem nächsten Crawlen wirken, was Tage bis Monate dauern kann. Mit dem URL-Prüftool siehst du, ob Googlebot die Anweisung auch tatsächlich bekommt.

## ChatGPT: drei Crawler, drei Entscheidungen

OpenAI trennt seine Crawler sauber nach Zweck, und jeder lässt sich in der robots.txt einzeln steuern.

| Kennung | Wofür | Was ein Sperren bewirkt |
|---|---|---|
| OAI-SearchBot | Suche in ChatGPT | Deine Seite erscheint nicht mehr in Suchantworten, höchstens noch als Navigationslink |
| GPTBot | Training der Basismodelle | Deine Inhalte sollen nicht ins Training einfließen |
| ChatGPT-User | Abrufe, die ein Nutzer auslöst | Laut OpenAI gilt robots.txt hier unter Umständen nicht, weil ein Mensch den Abruf veranlasst |

Die Trennung ist für viele Unternehmen die eigentliche Nachricht. Du kannst in der Suche von ChatGPT auftauchen und trotzdem das Training mit deinen Texten untersagen: OAI-SearchBot erlauben, GPTBot sperren. OpenAI schreibt, dass Änderungen an der robots.txt für die Suche etwa 24 Stunden brauchen, bis sie greifen.

Prüf außerdem, ob dein CDN oder deine Firewall die Crawler aus Versehen blockiert. Bot-Schutz, der jeden unbekannten Besucher aussperrt, sperrt oft auch genau die Crawler, die du eigentlich haben willst. OpenAI veröffentlicht dafür die IP-Bereiche seiner Crawler, die du freigeben kannst.

## Einkaufen im Chat

OpenAI hat im März 2026 die Produktsuche in ChatGPT umgebaut. Nutzer vergleichen Produkte nebeneinander mit Preis, Bewertungen und Eigenschaften und können Bilder als Vorlage hochladen. Laut Hilfeseite wählt ChatGPT die Produktergebnisse selbst aus, sie sind keine Anzeigen und nicht von Partnerschaften beeinflusst. Berücksichtigt werden strukturierte Daten von Händlern und Drittanbietern, etwa Preis und Beschreibung.

Bei der Reihenfolge der Händler zu einem Produkt nennt OpenAI Verfügbarkeit, Preis, Qualität und ob ein Händler Hersteller oder Hauptverkäufer ist. Händler auf Shopify und Etsy sind laut OpenAI bereits angebunden, ohne dass sie etwas tun müssen. Alle anderen können sich für einen direkten Produkt-Feed bewerben. Die Einkaufsfunktion ist nach Angaben von OpenAI derzeit nur für Nutzer in den USA freigeschaltet, eine Ausweitung auf weitere Regionen ist angekündigt.

Ein Hinweis zum Kleingedruckten: Die Nutzungsbedingungen für Händler-Feeds verlangen unter anderem, dass du die Crawler von OpenAI nicht sperrst und für deine Website keinen Vorbehalt gegen Text- und Data-Mining gegenüber OpenAI geltend machst. Wer etwa per robots.txt oder Impressum einen solchen Vorbehalt erklärt hat, sollte vor einer Anmeldung genau prüfen, ob beides zusammenpasst. Das ist eine Frage für die Rechtsabteilung, nicht für das Marketing allein.

## Gemini, Perplexity und der Rest

Auch Google baut die Gemini-App zum Einkaufs- und Arbeitswerkzeug aus. Seit Oktober verbindet sich Gemini laut Google mit über 40 Apps, darunter Shopify, und für kleine Unternehmen gibt es eine eigene Startseite mit Anbindung an Unternehmensprofil, Google Ads, Workspace, Shopify und Wix. Für Händler bleibt der wichtigste Hebel bei Google trotzdem das Merchant Center: Wer dort vollständige, aktuelle Daten pflegt, versorgt Suche, Shopping und KI-Antworten aus einer Quelle.

Antwortmaschinen wie Perplexity zitieren ihre Quellen sichtbar und eignen sich deshalb gut, um die eigene Präsenz stichprobenartig zu prüfen. Stell die zehn Fragen, die deine Kunden wirklich stellen, und notiere, wer als Quelle genannt wird. Das ist kein wissenschaftlicher Test, aber ein ehrlicher Blick auf den Wettbewerb.

## Was Inhalte für KI-Antworten taugen lässt

Aus den offiziellen Hinweisen und unserer Erfahrung ergibt sich ein recht klares Bild. Die folgenden Punkte sind nach unserer Einschätzung die wichtigsten, weil sie Suche, KI-Antworten und Kunden gleichermaßen helfen.

1. **Fragen direkt beantworten:** Eine Seite, die eine konkrete Frage im ersten Absatz beantwortet und danach in die Tiefe geht, ist für Menschen und Modelle gleichermaßen nützlich.
2. **Teilfragen abdecken:** Weil KI-Systeme verwandte Suchen auffächern, lohnen sich Seiten zu Vergleichen, Kompatibilität, Pflege und typischen Problemen.
3. **Fakten maschinenlesbar und sichtbar halten:** Preise, Maße, Lieferzeiten und Varianten gehören als Text auf die Seite und in die strukturierten Daten, und zwar identisch.
4. **Produktdaten vollständig pflegen:** Merchant Center, Shop-Feed und gegebenenfalls ein direkter Feed an OpenAI sollten dieselben, aktuellen Angaben liefern.
5. **Echte Erfahrung zeigen:** Eigene Tests, Fotos, Messwerte und Antworten aus dem Kundenservice unterscheiden deine Seite von hundert gleich klingenden Zusammenfassungen.
6. **Technik nicht vergessen:** Crawling erlauben, Seiten intern verlinken, wichtige Inhalte nicht hinter Skripten verstecken, Duplikate reduzieren.

Fällt dir auf, dass hier nichts Exotisches steht? Genau das ist der Punkt. Die Werkzeuge für KI-Sichtbarkeit sind zu neunzig Prozent die alten Werkzeuge, nur mit einem neuen Bericht obendrauf.

## Messen statt raten

In der Search Console werden Klicks aus AI Overviews und AI Mode laut Google im Leistungsbericht unter dem Suchtyp „Web“ mitgezählt, dazu kommt der neue Bericht für generative KI. Google gibt an, dass Klicks von Ergebnisseiten mit AI Overviews hochwertiger seien, Nutzer also mehr Zeit auf der Seite verbringen. Das ist eine Aussage von Google und lässt sich in der eigenen Webanalyse leicht überprüfen.

Für ChatGPT und andere Assistenten gibt es noch keine vergleichbare offizielle Statistik. Zwei Wege funktionieren trotzdem: Besuche mit Herkunft chatgpt.com oder perplexity.ai in der Webanalyse auswerten und regelmäßig mit festen Testfragen prüfen, ob und wie die eigene Marke genannt wird. SEO-Suiten wie Semrush bieten dafür inzwischen eine Verfolgung der Sichtbarkeit in KI-Suchen an.

## Checkliste für die nächsten zwei Wochen

1. **Search Console öffnen:** den Bericht für generative KI ansehen und prüfen, ob die Website eingeschlossen ist.
2. **robots.txt prüfen:** Googlebot und OAI-SearchBot erlauben, über GPTBot und Google-Extended bewusst entscheiden.
3. **Firewall und CDN testen:** sicherstellen, dass Bot-Schutz die gewünschten Crawler durchlässt.
4. **Merchant Center abgleichen:** Preise, Verfügbarkeit und Varianten mit dem Shop vergleichen und Abweichungen beheben.
5. **Zehn Kundenfragen testen:** in ChatGPT, Gemini und Perplexity stellen und notieren, wer als Quelle erscheint.
6. **Drei Lückenseiten planen:** für die Fragen, bei denen du nicht genannt wirst, eine Seite schreiben, die sie besser beantwortet als die aktuelle Quelle.

Wer das einmal sauber aufsetzt, hat einen Prozess, der jeden Monat eine Stunde kostet. Mehr Zauberei steckt nicht dahinter, und wer dir mehr verspricht, verkauft meistens ein Abo.
