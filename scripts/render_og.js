// Rendert die OG-Vorlage nach docs/og.png (1200x630). Braucht Playwright + Chromium.
// Wird von scripts/build_de_page.py aufgerufen; manuell: node scripts/render_og.js [.build/og.html]
// Die Vorlage liegt bewusst nicht in docs/: sie ist keine Seite der Website.
const path = require("path");
const { chromium } = require("playwright");
(async () => {
  const root = path.resolve(__dirname, "..");
  const src = path.resolve(process.argv[2] || path.join(root, ".build", "og.html"));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto("file://" + src);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(root, "docs", "og.png") });
  await b.close();
  console.log("docs/og.png gerendert");
})().catch((e) => { console.error("og.png nicht gerendert:", e.message); process.exit(1); });
