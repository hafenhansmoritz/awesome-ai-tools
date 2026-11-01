#!/usr/bin/env node
/* Browser-Smoke-Test für docs/: jede Seite bei 390 und 1366 px, hell und dunkel, ohne Overflow, ohne JS-Fehler
   ohne Verstoß gegen die Content-Security-Policy und ohne eine einzige Anfrage an einen fremden Server
   (Favicons liegen lokal; jede externe Anfrage, etwa an icons.duckduckgo.com, lässt den Test scheitern).
   Dazu Stichproben der Kernfunktionen (Hans, Werkzeug des Tages, Ratgeber-Abschluss, 404-Überraschung).

   Aufruf aus dem Repo-Root (Playwright global installiert):
       NODE_PATH=$(npm root -g) node scripts/smoke.js
   Exit-Code 1, wenn etwas kaputt ist. */
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs"), os = require("os"), path = require("path");

const ROOT = path.resolve(__dirname, "..");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "kw-smoke-"));
fs.symlinkSync(path.join(ROOT, "docs"), path.join(tmp, "awesome-ai-tools"));
// Port 0: das Betriebssystem vergibt einen freien Port, der Server nennt ihn in seiner Startzeile
let BASE = "";
const server = spawn("python3", ["-u", "-m", "http.server", "0", "--bind", "127.0.0.1", "--directory", tmp], { stdio: ["ignore", "pipe", "pipe"] });
const ready = new Promise((resolve, reject) => {
  const t = setTimeout(() => reject(new Error("Testserver nicht gestartet")), 8000);
  server.stdout.on("data", (d) => {
    const m = String(d).match(/port (\d+)/);
    if (m) { clearTimeout(t); BASE = `http://127.0.0.1:${m[1]}/awesome-ai-tools/`; resolve(); }
  });
  server.stderr.resume(); // Zugriffsprotokoll verwerfen, sonst läuft die Pipe voll und der Server blockiert
  server.on("exit", (code) => { clearTimeout(t); reject(new Error("Testserver beendet mit Code " + code)); });
});

const pages = fs.readdirSync(path.join(ROOT, "docs")).filter((f) => f.endsWith(".html") && f !== "og.html");
const bad = [];
function fail(msg) { bad.push(msg); console.log("FEHLER " + msg); }

(async () => {
  await ready;
  const browser = await chromium.launch();
  for (const [w, scheme] of [[390, "light"], [1366, "dark"], [1366, "light"], [390, "dark"]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 820 }, colorScheme: scheme });
    // Alles, was nicht vom Testserver kommt, wird abgebrochen und als Fehler gezählt
    let external = [];
    await ctx.route((u) => !u.href.startsWith(BASE) && !/^(data|blob|about):/.test(u.protocol), (r) => { external.push(r.request().url()); r.abort(); });
    for (const pg of pages) {
      const p = await ctx.newPage(); const errs = []; external = [];
      p.on("pageerror", (e) => errs.push(e.message));
      p.on("console", (m) => { if (m.type() === "error" && !/ERR_FAILED|net::|favicon/.test(m.text())) errs.push(m.text()); });
      await p.addInitScript(() => { window.__csp = []; document.addEventListener("securitypolicyviolation", (e) => window.__csp.push(e.violatedDirective + " " + (e.blockedURI || "inline"))); });
      const r = await p.goto(BASE + pg, { waitUntil: "load" });
      if (!r || r.status() !== 200) fail(`${pg}: HTTP ${r && r.status()}`);
      await p.waitForTimeout(150);
      const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (ov > 0) fail(`${pg} @${w}${scheme[0]}: ${ov}px horizontaler Overflow`);
      if (errs.length) fail(`${pg} @${w}${scheme[0]}: ${errs.join(" | ")}`);
      const csp = await p.evaluate(() => window.__csp);
      if (csp.length) fail(`${pg} @${w}${scheme[0]}: CSP-Verstoß ${csp.slice(0, 3).join(" | ")}`);
      if (external.length) fail(`${pg} @${w}${scheme[0]}: ${external.length} externe Anfragen, z. B. ${external.slice(0, 2).join(" | ")}`);
      const brokenImg = await p.evaluate(() => [...document.images].filter((i) => i.complete && i.getAttribute("loading") !== "lazy" && !i.naturalWidth).map((i) => i.src));
      if (brokenImg.length) fail(`${pg} @${w}${scheme[0]}: Bilder nicht geladen ${brokenImg.slice(0, 3).join(" | ")}`);
      await p.close();
    }
    await ctx.close();
  }
  // Kernfunktionen
  const p = await browser.newPage({ viewport: { width: 1366, height: 860 } });
  await p.goto(BASE + "index.html"); await p.waitForTimeout(800);
  if (!(await p.textContent("#hm-say")).trim()) fail("Hans-Gruß leer");
  await p.waitForFunction(() => document.querySelector("#wotd a"), null, { timeout: 5000 }).catch(() => {});
  if (await p.$eval("#wotd", (e) => e.hidden || !e.querySelector("a"))) fail("Werkzeug des Tages fehlt");
  const rg = pages.find((x) => x.startsWith("ratgeber-"));
  if (rg) { await p.goto(BASE + rg); if (!(await p.$("#geschafft"))) fail(`${rg}: Geschafft-Karte fehlt`); }
  await p.goto(BASE + "404.html"); await p.click("#surprise-btn"); await p.waitForTimeout(800);
  if (await p.$eval("#surprise", (e) => e.hidden)) fail("404-Überraschung lädt nicht");
  await browser.close(); server.kill();
  console.log(`${pages.length} Seiten × 4 Ansichten geprüft, ${bad.length} Fehler`);
  process.exit(bad.length ? 1 : 0);
})().catch((e) => { console.error(e); server.kill(); process.exit(1); });
