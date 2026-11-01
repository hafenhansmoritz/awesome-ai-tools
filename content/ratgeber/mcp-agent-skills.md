> **Kurz gesagt:** Das Model Context Protocol, kurz MCP, ist der Stecker, über den KI-Assistenten wie Claude, ChatGPT, Gemini oder GitHub Copilot auf Shop, Warenwirtschaft, Zahlungsdienst und Wissensdatenbank zugreifen. Agent Skills sind die Arbeitsanleitungen, die einem Agenten sagen, wie er eine Aufgabe in deinem Haus erledigt. Beide Standards liegen inzwischen bei einer neutralen Stiftung unter dem Dach der Linux Foundation. Dieser Ratgeber erklärt, wie die Bausteine zusammenpassen, welche Shop- und Zahlungsanbieter schon Anschlüsse liefern, wo die Sicherheitsrisiken liegen und wie du in drei Wochen den ersten Anschluss sauber in Betrieb nimmst.

Grundlage sind die Spezifikation auf modelcontextprotocol.io, die Seite agentskills.io sowie die Dokumentationen von Anthropic, OpenAI, Google, Microsoft, GitHub, Shopify, Shopware, Stripe, PayPal, Zapier und n8n, Stand 28. Oktober 2026.

## Zwei Standards, zwei Aufgaben

Die Spezifikation beschreibt MCP als offenes Protokoll, das Anwendungen mit Sprachmodellen an externe Datenquellen und Werkzeuge anbindet. Technisch gibt es drei Rollen: Der Host ist die KI-Anwendung, etwa Claude Desktop oder VS Code. Für jeden angeschlossenen Dienst erzeugt der Host einen Client mit einer eigenen Verbindung. Und der Server ist das Programm, das einen Dienst wie den Shop oder die Buchhaltung für die KI zugänglich macht.

Ein Server bietet drei Arten von Bausteinen an. Werkzeuge sind Funktionen, die das Modell ausführen kann, etwa „Bestellung suchen“. Ressourcen sind Inhalte und Daten, die als Kontext dienen. Prompts sind vorbereitete Vorlagen für wiederkehrende Abläufe. Lokale Server laufen über die Standardein- und -ausgabe auf demselben Rechner, entfernte Server über HTTP.

Agent Skills lösen ein anderes Problem. Ein Skill ist laut Spezifikation ein Ordner mit einer Datei namens SKILL.md und optional Skripten, Nachschlagewerken und Vorlagen. Im Kopf der Datei stehen ein Name und eine Beschreibung, was der Skill tut und wann er zum Einsatz kommt. Der Agent liest beim Start nur diese Kurzbeschreibung, rund 100 Token pro Skill, und lädt den vollen Inhalt erst, wenn er ihn braucht. Die Spezifikation empfiehlt, die SKILL.md unter 500 Zeilen zu halten.

Die Arbeitsteilung in einem Satz: MCP gibt dem Agenten Hände, ein Skill gibt ihm das Handbuch.

## Wer dahintersteht

Anthropic hat MCP im Dezember 2025 an die Agentic AI Foundation übergeben, einen Fonds unter dem Dach der Linux Foundation, den Anthropic, Block und OpenAI gemeinsam gegründet haben. Zu den Platin-Mitgliedern zählen AWS, Bloomberg, Cloudflare, Google und Microsoft, Shopify und SAP sind Gold-Mitglieder. Am 22. Oktober 2026 folgte Agent Skills. Laut Anthropic haben seit Dezember 2025 mehr als 70 Agenten-Plattformen den Standard eingebaut, darunter ChatGPT, Cursor, GitHub Copilot und VS Code, und es wurden eine Million Skills veröffentlicht.

Die aktuelle MCP-Spezifikation trägt das Datum 28. Juli 2026. Sie macht das Protokoll im Kern zustandslos und führt eine Regel ein, dass Funktionen mindestens zwölf Monate vor ihrer Abschaffung angekündigt werden. Für Unternehmen ist das ein gutes Zeichen: Ein Standard mit geregelten Übergangsfristen lässt sich planen.

## Welche Programme MCP sprechen

Fast jedes große KI-Werkzeug kann inzwischen MCP-Server einbinden. Die wichtigsten laut Herstellerangaben:

| Programm | Was geht | Zu beachten |
|---|---|---|
| Claude, Claude Desktop | Eigene Konnektoren über entfernte MCP-Server in allen Tarifen | Im kostenlosen Tarif nur ein eigener Konnektor; die Verbindung läuft aus der Cloud von Anthropic, der Server muss erreichbar sein |
| ChatGPT | Apps und Plugins auf MCP-Basis, eigene Server mit Lese- und Schreibwerkzeugen | OpenAI warnt, dass nicht vertrauenswürdige Server Daten ändern oder löschen lassen können |
| Google Gemini Enterprise | Eigene MCP-Server als Datenquelle | In der Business-Edition noch Vorabversion |
| Microsoft Copilot Studio | Assistent zum Einbinden bestehender Server mit API-Schlüssel oder OAuth | Für Agenten, die Firmen selbst bauen |
| GitHub Copilot, VS Code, Cursor | MCP in Editor, Kommandozeile und Cloud-Agent | In Business- und Enterprise-Tarifen muss der Admin MCP freischalten |
| Keynote, Pages, Numbers | Externe Agenten lesen und bearbeiten Dokumente | Laut Apple ab macOS 27 |

Ein Server, den du einmal baust oder einrichtest, funktioniert also in mehreren dieser Programme. Genau das ist der Wert eines Standards: Du wechselst den KI-Anbieter, ohne die Anbindung an deine Systeme neu zu bauen.

## Fertige Anschlüsse für Shops und Zahlungen

Für den Handel gibt es schon eine Reihe offizieller Server der Anbieter selbst. Eine Auswahl:

- **Shopify:** Die Server für Katalog, Warenkorb, Kundenfragen und Bestellungen laufen inzwischen über eine neue, an den Standard UCP angepasste Adresse; die alten Katalog- und Warenkorb-Werkzeuge hat Shopify entfernt. Wer vor dem Sommer etwas gebaut hat, sollte das prüfen. Für Kundenkonten gibt es einen eigenen Server mit OAuth-Anmeldung. Seit dem 26. Oktober liegt außerdem die Knowledge Base mit Fakten über den Shop direkt im Admin, unter den Vertriebskanälen im Bereich Agentic. Fakten, die Shopify aus dem Shop vorschlägt, bleiben unveröffentlicht, bis der Händler sie freigibt, und die bisherige App endet nach dem 15. Januar 2027.
- **Shopware:** Seit Version 6.7.11 bringt Shopware einen eigenen MCP-Server im Kern mit, bis Version 6.8 als experimentell gekennzeichnet. Jeder Aufruf prüft Zugriffsrechte, erlaubte Werkzeuge pro Integration und ein Anfragelimit, Schreibwerkzeuge laufen standardmäßig im Probemodus. Die Dokumentation rät ausdrücklich zu einer eigenen Rolle mit knappen Rechten statt vollem Admin-Zugriff.
- **Google Merchant Center:** Ein Server in der Alpha-Phase beschränkt sich auf Lesezugriffe und Schreibvorgänge mit geringem Risiko, gedacht etwa für abgelehnte Produkte und Berichte. Der Server für Google Analytics ist ebenfalls nur lesend.
- **Stripe:** Ein entfernter Server mit OAuth oder speziellen Agenten-Schlüsseln. Ab Dezember 2026 nimmt Stripe keine Vollzugriffs-Schlüssel mehr an. Stripe rät, im KI-Programm die Freigabe für jeden Werkzeugaufruf einzuschalten.
- **PayPal:** Ein lokaler und ein entfernter Server, etwa zum Auflisten von Rechnungen.
- **Zapier und n8n:** Zapier macht laut eigener Angabe über 9.000 Apps per MCP erreichbar. In n8n lassen sich Workflows als MCP-Werkzeuge freigeben, und zwar jeder einzeln.

Für Shopsysteme wie JTL, plentymarkets oder WooCommerce haben wir keine offiziellen Server geprüft. Hier lohnt die Frage beim Anbieter oder ein Umweg über n8n und Zapier.

## Ein Skill für deinen Shop

Wo MCP den Zugriff regelt, regelt ein Skill das Vorgehen. Ein Beispiel aus dem Alltag eines Teile-Shops: Ein Skill namens `produktdaten-pruefen` beschreibt, welche Felder jede Artikelseite braucht, wie Fahrzeugzuordnungen geschrieben werden, welche Maßeinheiten gelten und wann ein Artikel an einen Menschen zur Prüfung geht. Dazu legt das Team eine Tabelle mit erlaubten Herstellernamen in den Ordner und ein kleines Skript, das Pflichtfelder zählt.

So schreibst du einen Skill, der funktioniert:

1. **Name klein und mit Bindestrichen**, höchstens 64 Zeichen, identisch mit dem Ordnernamen.
2. **Beschreibung mit Auslöser:** nicht nur, was der Skill tut, sondern wann der Agent ihn nehmen soll, etwa „bei neuen oder geänderten Artikeln im Shop“.
3. **Schritte statt Prosa:** nummerierte Arbeitsschritte, klare Abbruchregeln, ein Beispiel für ein gutes Ergebnis.
4. **Wissen auslagern:** lange Tabellen und Regelwerke in eigene Dateien, auf die die SKILL.md verweist.
5. **Grenzen nennen:** was der Agent ausdrücklich nicht tun darf, etwa Preise ändern.

Ein gut geschriebener Skill ist übrigens auch für neue Kollegen eine ordentliche Einarbeitung. Wer seine Abläufe einmal so aufschreibt, gewinnt doppelt.

## Die Sicherheitsregeln

MCP verbindet ein Sprachmodell, das sich von Texten beeinflussen lässt, mit Systemen, in denen echtes Geld und echte Kundendaten liegen. Die Spezifikation formuliert deshalb klare Grundsätze: Nutzer müssen ausdrücklich zustimmen, bevor ein Werkzeug aufgerufen wird. Beschreibungen von Werkzeugen gelten als nicht vertrauenswürdig, solange sie nicht von einem vertrauenswürdigen Server stammen. Und es soll immer einen Menschen geben, der einen Werkzeugaufruf ablehnen kann.

Die wichtigsten Angriffswege, die Microsoft, OWASP und die Hersteller beschreiben:

- **Vergiftete Werkzeuge:** Versteckte Anweisungen in der Beschreibung eines Werkzeugs, die das Modell befolgt, ohne dass der Nutzer sie sieht. Microsoft nennt dazu den Fall, dass ein Server seine Werkzeuge nach der Freigabe still verändert.
- **Prompt Injection über Inhalte:** Ein Agent liest eine Kunden-E-Mail oder Produktbewertung mit eingeschleusten Befehlen und führt sie mit seinen Rechten aus. Stripe warnt ausdrücklich davor, seinen Server zusammen mit anderen Servern zu nutzen, ohne diese Gefahr zu bedenken.
- **Zu viele Rechte:** Die OWASP-Liste der zehn größten Risiken für agentische Anwendungen von 2026 nennt Missbrauch von Werkzeugen sowie von Identitäten und Rechten auf den Plätzen zwei und drei. Als Gegenmittel empfiehlt sie eine menschliche Bestätigung für folgenreiche Aktionen, mit Probelauf und Vorher-nachher-Vergleich.
- **Lokale Server mit Schadcode:** VS Code fragt beim ersten Start eines lokalen Servers nach, weil solche Server beliebigen Code auf dem Rechner ausführen können, und rät, nur Server aus vertrauenswürdigen Quellen einzubinden.
- **Weitergereichte Zugangsdaten:** Die Spezifikation verbietet es Servern, Token anzunehmen, die nicht ausdrücklich für sie ausgestellt wurden.

Für Skills gilt dasselbe. Anthropic rät, Skills nur aus vertrauenswürdigen Quellen zu nutzen, alle Dateien vorher zu prüfen und die Installation eines Skills wie die Installation von Software zu behandeln. Ein bösartiger Skill kann den Agenten nämlich dazu bringen, Werkzeuge aufzurufen oder Code auszuführen.

## Woran du vertrauenswürdige Server erkennst

Seit September 2025 gibt es ein offizielles MCP-Register, das sich laut Dokumentation weiter in der Vorschauphase befindet. Es prüft, ob ein Eintrag wirklich zu der Domain oder dem GitHub-Konto gehört, unter dessen Namen er auftritt, scannt den Code aber nicht selbst. Anthropic kennzeichnet Konnektoren als verifiziert, aus der Community oder selbst eingerichtet und betont, dass auch verifiziert keine Sicherheitsprüfung bedeutet.

Praktische Prüfliste vor dem Einbinden:

1. Stammt der Server vom Anbieter des Dienstes selbst, also Shopware vom Shopware-Projekt, Stripe von Stripe?
2. Welche Werkzeuge bietet er an, und lassen sich die schreibenden einzeln abschalten?
3. Welche Rechte verlangt er bei der Anmeldung, und reichen weniger?
4. Gibt es einen Lesemodus oder einen Probelauf für Schreibvorgänge?
5. Lässt sich die Freigabe pro Aufruf einschalten, und klickst du „immer erlauben“ nur bei Werkzeugen, denen du wirklich vertraust?

## Dein erster Anschluss in drei Wochen

1. **Woche 1:** Eine Aufgabe wählen, die nur Lesen braucht, etwa „Welche Produkte wurden im Merchant Center abgelehnt, und warum?“ oder „Zeig mir die Bestellungen von gestern mit Lieferproblemen“. Den offiziellen Server des Anbieters mit einem Konto mit Leserechten anbinden.
2. **Woche 2:** Einen Skill schreiben, der beschreibt, wie das Ergebnis aussehen soll und was danach passiert. Mit drei Kollegen testen, Antworten gegen die Daten im System prüfen.
3. **Woche 3:** Eine erste schreibende Funktion freischalten, mit Freigabe pro Aufruf und Probelauf, etwa das Anlegen eines Entwurfs statt einer Veröffentlichung. Protokolle eine Woche lang prüfen, bevor du weitere Rechte vergibst.

Der Rest ergibt sich aus der Praxis. Wer erst einmal einen lesenden Anschluss und einen guten Skill im Einsatz hat, merkt schnell, welche Abläufe als nächstes dran sind, und welche besser in Menschenhand bleiben.
