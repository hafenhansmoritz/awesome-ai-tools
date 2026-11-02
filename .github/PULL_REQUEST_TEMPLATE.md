## Was ändert sich?
<!-- Neues Tool, toter Link, bessere Beschreibung oder Änderung an Seite und Generator -->

## Neues Tool (falls zutreffend)
- **Name:**
- **URL:** (ohne Affiliate- oder Referral-Parameter)
- **Ein Satz auf Deutsch:**
- **Kategorie:**

## Checkliste
- [ ] Link geprüft: erreichbar und nutzbar
- [ ] Tool steht noch nicht in der Liste
- [ ] Am Ende der passenden Kategorie eingetragen
- [ ] 🇪🇺 nur bei Firmensitz in der EU, `OSS` nur bei echtem Open-Source-Code
- [ ] `python3 scripts/check_links.py`, `python3 scripts/build_de_page.py` und `python3 scripts/seo_check.py` laufen durch
- [ ] `python3 scripts/footprint_scan.py docs --repo . --accept data/footprint_accept.json` ohne hohe Befunde (Datum je Seite aus der Git-Historie, keine Build- oder Arbeitsdateien in `docs/`)
- [ ] Nach dem Merge: `python3 scripts/publish.py --ref origin/main --remote https://github.com/jmp-collab/awesome-ai-tools --dir <ordner>` spiegelt docs/, die beiden READMEs und LICENSE ins öffentliche Publish-Repo
