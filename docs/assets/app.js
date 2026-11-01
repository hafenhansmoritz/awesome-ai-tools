/* KI-Werkstatt – Seitenlogik. Kein Framework, keine Abhängigkeiten. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // localStorage nur nach einer Aktion der Nutzerin oder des Nutzers (TDDDG § 25): set/del stehen ausschließlich in Klick-Handlern
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };
  // Daten der Seite stehen als <script type="application/json"> im HTML (CSP ohne Inline-Skripte)
  function jsonData(id) { var el = document.getElementById(id); if (!el) return null; try { return JSON.parse(el.textContent); } catch (e) { return null; } }
  // Links aus Daten nur mit http(s), nie javascript: oder data:
  function safeUrl(u) { return /^https?:\/\//i.test(String(u)) ? String(u) : "#"; }

  /* content-visibility (style.css) überspringt ferne Bänder beim ersten Layout. Vor einem Sprung innerhalb der Seite
     wird kurz alles gerendert, damit das Ziel exakt sitzt; danach merkt sich der Browser die echten Höhen. */
  var cvT;
  function cvAll() { document.documentElement.classList.add("cv-all"); clearTimeout(cvT); cvT = setTimeout(function () { document.documentElement.classList.remove("cv-all"); }, 2500); }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href*='#']"); if (!a) return;
    var u = new URL(a.href, location.href);
    if (u.origin === location.origin && u.pathname === location.pathname && u.hash) cvAll();
  }, true);
  // Einstieg mit Anker (z. B. ./#rechner aus dem Footer einer anderen Seite): einmal alles rendern und das Ziel nachziehen
  if (location.hash.length > 1) {
    var cvTarget = null; try { cvTarget = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) {}
    if (cvTarget) {
      // Nachziehen, bis Schriften und Seite geladen sind, aber nur solange niemand selbst scrollt
      var cvUser = false, cvGo = function () { if (!cvUser) cvTarget.scrollIntoView({ block: "start", behavior: "instant" }); };
      ["wheel", "touchstart", "keydown", "mousedown"].forEach(function (ev) { window.addEventListener(ev, function () { cvUser = true; }, { once: true, passive: true }); });
      cvAll(); requestAnimationFrame(cvGo);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { requestAnimationFrame(cvGo); });
      window.addEventListener("load", function () { requestAnimationFrame(cvGo); });
    }
  }

  /* Theme-Umschalter: das gespeicherte Schema setzt schon das Snippet im Head (kein Flackern); hier nur Knopf und Zustand */
  var root = document.documentElement;
  var darkMq = window.matchMedia("(prefers-color-scheme: dark)");
  function isDark() { var t = root.getAttribute("data-theme"); return t === "dark" || (!t && darkMq.matches); }
  var tbtn = $("#theme");
  function tSync() { if (tbtn) tbtn.setAttribute("aria-pressed", isDark() ? "true" : "false"); }
  tSync();
  if (darkMq.addEventListener) darkMq.addEventListener("change", tSync);
  if (tbtn) tbtn.addEventListener("click", function () {
    var next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next); store.set("kw-theme", next); tSync();
  });

  /* Basis-URL aus dem eigenen Skript-Pfad: Such-Panel und Links funktionieren so auch auf der 404-Seite in beliebiger Tiefe */
  var SITE = (document.currentScript && document.currentScript.src || "").replace(/assets\/app\.js.*$/, "") || "./";
  // Favicons liegen lokal (img/fav/, Pfad aus tools.json bzw. den Finder-Daten); kein fremder Icon-Dienst
  function favImg(path, size) {
    if (!/^img\/fav\/[a-z0-9.-]+\.(png|jpg|svg)$/.test(String(path || ""))) return "";
    return '<img loading="lazy" alt="" width="' + size + '" height="' + size + '" src="' + SITE + path + '">';
  }

  /* Mobil-Menü: unter 1100 px klappt die Hauptnavigation unter der Kopfleiste auf */
  var menuBtn = $("#menubtn"), nav = $("#nav");
  if (menuBtn && nav) {
    var navOpen = function (open, backToBtn) {
      nav.classList.toggle("open", open); menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) { var first = nav.querySelector("a"); if (first) first.focus(); }
      else if (backToBtn) menuBtn.focus();
    };
    menuBtn.addEventListener("click", function () { navOpen(!nav.classList.contains("open")); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) navOpen(false, true); });
    document.addEventListener("click", function (e) { if (nav.classList.contains("open") && !nav.contains(e.target) && !menuBtn.contains(e.target)) navOpen(false); });
    // Fokus verlässt Menü und Knopf (Tab nach dem letzten Punkt): Menü schließt, damit es nichts verdeckt
    nav.addEventListener("focusout", function (e) { if (nav.classList.contains("open") && e.relatedTarget && !nav.contains(e.relatedTarget) && e.relatedTarget !== menuBtn) navOpen(false); });
    $$("a", nav).forEach(function (a) { a.addEventListener("click", function () { navOpen(false); }); });
    var wide = window.matchMedia("(min-width: 1100px)");
    var onWide = function () { if (wide.matches) navOpen(false); };
    if (wide.addEventListener) wide.addEventListener("change", onWide); else if (wide.addListener) wide.addListener(onWide);
  }

  /* Kategorie-Seiten: Filter innerhalb der Schublade (Suchwort, EU, Open Source) */
  var q = $("#q"), lq = $("#lq"), lcount = $("#lcount"), lqEmpty = $(".lq-empty"), items = $$("ul.tools li");
  var feu = $$("input.f-eu"), foss = $$("input.f-oss");
  function uniq(list) { var u = {}; list.forEach(function (li) { u[li.querySelector("a.name").href] = 1; }); return Object.keys(u).length; }
  function run() {
    if (!lq) return;
    var s = lq.value.trim().toLowerCase();
    var eu = feu.some(function (c) { return c.checked; }), oss = foss.some(function (c) { return c.checked; }), filtering = !!(s || eu || oss);
    items.forEach(function (li) {
      var ok = (!s || li.dataset.search.indexOf(s) > -1) && (!eu || li.dataset.eu === "1") && (!oss || li.dataset.oss === "1");
      li.classList.toggle("hidden", !ok);
    });
    $$("section.cat").forEach(function (sec) {
      var any = !!sec.querySelector("ul.tools li:not(.hidden)");
      sec.classList.toggle("hidden", filtering && !any);
      $$("ul.tools", sec).forEach(function (ul) {
        var has = !!ul.querySelector("li:not(.hidden)");
        ul.classList.toggle("hidden", filtering && !has);
        var hd = ul.previousElementSibling; // Fach-Überschrift (h2.sub auf Kategorie-Seiten)
        while (hd && !hd.classList.contains("sub") && !hd.classList.contains("cat-head")) hd = hd.previousElementSibling;
        if (hd && hd.classList.contains("sub")) hd.classList.toggle("hidden", filtering && !has);
      });
      $$("aside, p, .table, ul.plain, ol.plain, .cat-art", sec).forEach(function (el) { el.classList.toggle("hidden", filtering); });
    });
    var shown = uniq(items.filter(function (li) { return !li.classList.contains("hidden"); }));
    if (lcount) lcount.textContent = filtering ? shown + " von " + uniq(items) + " Tools" : uniq(items) + " Tools";
    // Nichts in dieser Schublade: Angebot, in allen Tools zu suchen (mit Trefferzahl, sobald tools.json da ist)
    if (lqEmpty) {
      lqEmpty.hidden = !(s && !shown);
      var all = $("#lq-all");
      if (s && !shown && all && window.kwPanelCount) window.kwPanelCount(s).then(function (n) {
        if (lq.value.trim().toLowerCase() === s) all.lastChild.textContent = n ? "In allen Tools suchen (" + n + " Treffer)" : "In allen Tools suchen";
      });
    }
    if (filtering && shown) {
      // Zum ersten sichtbaren Treffer scrollen, egal in welcher Liste er steht
      var first = items.filter(function (li) { return !li.classList.contains("hidden"); })[0];
      var r = first.getBoundingClientRect();
      if (r.top < 120 || r.bottom > window.innerHeight) window.scrollTo({ top: r.top + window.scrollY - 180, behavior: reduce ? "auto" : "smooth" });
    }
  }
  [lq].concat(feu, foss).forEach(function (el) { if (el) el.addEventListener("input", function (e) { if (e.target.type === "checkbox") { (e.target.classList.contains("f-eu") ? feu : foss).forEach(function (c) { c.checked = e.target.checked; }); } run(); }); });
  var lqAll = $("#lq-all");
  if (lqAll && q) lqAll.addEventListener("click", function (e) { e.stopPropagation(); q.value = lq.value; q.focus(); if (window.kwPanelRun) window.kwPanelRun(); });
  var sf = $("#searchform"); if (sf) sf.addEventListener("submit", function (e) { e.preventDefault(); if (window.kwPanelRun) window.kwPanelRun(); });
  run();

  /* Scroll: Fortschritt, Topbutton, Sticky-Leiste, Parallax */
  var prog = $("#progress"), totop = $("#totop"), bar = $("#stickybar");
  var floats = $$(".float");
  var barDone = store.get("kw-bar") === "1", barOn = false, barH = 0, blockers = [];
  var ticking = false;
  // Leiste: ab 60 % Scrolltiefe, weg erst unter 50 % (Hysterese gegen Flackern). Sie ändert weder Padding noch
  // Seitenhöhe; Knöpfe weichen per transform aus. Nie gleichzeitig mit einem Lead-Formular oder dem Footer im Bild.
  function barSet(show) {
    if (!bar || show === barOn) return;
    barOn = show;
    if (show && !barH) { barH = bar.offsetHeight; root.style.setProperty("--barh", barH + "px"); }
    bar.classList.toggle("show", show); root.classList.toggle("has-bar", show);
  }
  function barEval(p) {
    if (!bar) return;
    if (barDone || blockers.length) return barSet(false);
    barSet(barOn ? p > 0.5 : p > 0.6);
  }
  function scrollP() { var h = document.documentElement, max = h.scrollHeight - h.clientHeight; return max > 0 ? window.scrollY / max : 0; }
  var barWatch = function () {};
  if (bar && "IntersectionObserver" in window) {
    var bio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var i = blockers.indexOf(e.target);
        if (e.isIntersecting && i < 0) blockers.push(e.target); else if (!e.isIntersecting && i > -1) blockers.splice(i, 1);
      });
      barEval(scrollP());
    });
    barWatch = function (el) { if (el) bio.observe(el); };
    $$("form.form, .lead, footer").forEach(barWatch);
    window.addEventListener("resize", function () { if (barH) { barH = bar.offsetHeight; root.style.setProperty("--barh", barH + "px"); } }, { passive: true });
  }
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () {
      var y = window.scrollY, p = scrollP();
      if (prog) prog.style.transform = "scaleX(" + p.toFixed(4) + ")";
      if (totop) totop.classList.toggle("show", y > 900);
      barEval(p);
      if (!reduce) floats.forEach(function (f) {
        var d = parseFloat(f.dataset.depth || "0.2");
        f.style.transform = "translate3d(0," + (y * d * -0.4).toFixed(1) + "px,0) rotate(" + (y * d * 0.02).toFixed(2) + "deg)";
      });
      ticking = false;
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  if (totop) totop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });
  var barClose = $("#stickybar .close");
  if (barClose) barClose.addEventListener("click", function () { barDone = true; barSet(false); store.set("kw-bar", "1"); });

  /* Reveal beim Scrollen */
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else { $$(".reveal").forEach(function (el) { el.classList.add("in"); }); }

  /* Zähler in den Stat-Kacheln */
  function countUp(el) {
    var end = parseInt(el.dataset.count, 10), start = 0, t0 = null, dur = 1200;
    if (reduce || !end) { el.textContent = end; return; }
    function step(ts) { if (!t0) t0 = ts; var k = Math.min(1, (ts - t0) / dur); k = 1 - Math.pow(1 - k, 3); el.textContent = Math.round(start + (end - start) * k); if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  // Im HTML stehen die echten Zahlen (ohne JavaScript, für Crawler); die Animation zählt beim Einblenden ab 0 hoch
  if ("IntersectionObserver" in window) {
    var io2 = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); io2.unobserve(e.target); } }); });
    $$("[data-count]").forEach(function (el) { io2.observe(el); });
  } else { $$("[data-count]").forEach(countUp); }

  /* Scroll-Spy für die Seitenleiste */
  var railLinks = $$(".rail a[href^='#']"), secs = railLinks.map(function (a) { return $(a.getAttribute("href")); }).filter(Boolean);
  if (secs.length && "IntersectionObserver" in window) {
    var cur = null;
    var io3 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) cur = e.target.id; });
      railLinks.forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + cur); });
    }, { rootMargin: "-20% 0px -70% 0px" });
    secs.forEach(function (s) { io3.observe(s); });
  }

  /* Stack-Finder */
  var FD = jsonData("kw-finder"), F = FD && FD.finder, TOOLS = (FD && FD.tools) || {};
  var finder = $("#finder");
  if (F && finder) {
    var ans = {}, stepIdx = 0;
    var qEl = $(".finder-q", finder), optsEl = $(".opts", finder), dots = $(".dots", finder), back = $(".back", finder), res = $(".finder-result", finder), stepLbl = $(".steplbl", finder);
    qEl.setAttribute("tabindex", "-1"); stepLbl.setAttribute("aria-live", "polite");
    function icon(id) { return '<svg class="ico" aria-hidden="true"><use href="#i-' + esc(id) + '"/></svg>'; }
    function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
    // focus: nach einer Antwort springt der Fokus auf die nächste Frage, sonst landet er auf <body>
    function render(focus) {
      var step = F.questions[stepIdx];
      res.classList.add("hidden"); qEl.classList.remove("hidden"); optsEl.classList.remove("hidden");
      qEl.textContent = step.q;
      optsEl.innerHTML = step.options.map(function (o) {
        return '<button type="button" class="opt' + (ans[step.id] === o[0] ? " on" : "") + '" data-v="' + esc(o[0]) + '">' + icon(o[2]) + '<span>' + esc(o[1]) + '</span></button>';
      }).join("");
      dots.innerHTML = F.questions.map(function (_, i) { return "<i" + (i <= stepIdx ? ' class="on"' : "") + "></i>"; }).join("");
      stepLbl.textContent = "Frage " + (stepIdx + 1) + " von " + F.questions.length;
      back.classList.toggle("hidden", stepIdx === 0);
      $$(".opt", optsEl).forEach(function (b) {
        b.addEventListener("click", function () {
          ans[step.id] = b.dataset.v;
          if (stepIdx < F.questions.length - 1) { stepIdx++; render(true); } else { showResult(); }
        });
      });
      if (focus) qEl.focus();
    }
    function showResult() {
      var list = (F.base[ans.ziel] || []).slice();
      if (ans.daten === "eu") list = list.map(function (n) { return F.eu_swap[n] || n; });
      if (ans.team === "firma") F.firma_add.forEach(function (n) { if (list.indexOf(n) < 0) list.push(n); });
      list = list.filter(function (n, i) { return list.indexOf(n) === i; });
      var cards = list.map(function (n) {
        var t = TOOLS[n]; if (!t) return "";
        return '<a href="' + esc(safeUrl(t.u)) + '" target="_blank" rel="noopener">' + favImg(t.i, 28) + '<span><b>' + esc(n) + (t.eu ? ' <span class="badge eu">EU</span>' : "") + '</b><small>' + esc(t.d) + '</small></span></a>';
      }).join("");
      var notes = [F.notes[ans.team], ans.daten === "eu" ? F.notes.eu : ""].filter(Boolean).map(function (n) { return '<p class="note">' + esc(n) + "</p>"; }).join("");
      var stackText = list.join(", "), req = '<span class="req" aria-hidden="true"> *</span>';
      res.innerHTML = '<p class="eyebrow">Dein Setup</p><h3 class="finder-q" tabindex="-1">' + list.length + ' Tools, die zu deinem Fall passen</h3>' +
        '<div class="result-tools">' + cards + "</div>" + notes +
        '<form class="form" action="https://formsubmit.co/' + esc(F.to) + '" method="POST" style="margin-top:18px;box-shadow:none;border:1px solid var(--line)">' +
        '<input type="hidden" name="_subject" value="Stack-Check (Finder) – KI-Werkstatt"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false">' +
        '<input type="hidden" name="_next" value="' + esc(F.next) + '">' +
        '<div class="honey" aria-hidden="true"><label>Bitte leer lassen <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>' +
        '<input type="hidden" name="quelle" value="Stack-Finder"><input type="hidden" name="seite" value=""><input type="hidden" name="vorher" value="">' +
        '<input type="hidden" name="antworten" value="' + esc([ans.ziel, ans.daten, ans.team].join(" / ")) + '"><input type="hidden" name="vorschlag" value="' + esc(stackText) + '">' +
        '<p style="margin:0 0 4px;font:700 18px var(--font-d)">Soll Jean da noch mal drüberschauen?</p><p style="margin:0;color:#5B616B;font-size:14px">Du bekommst das Setup mit Anmerkungen zu deinem Fall per E-Mail. Kostenlos, ohne Pitch.</p>' +
        '<p class="req-note" style="margin-top:10px">Felder mit * sind Pflicht.</p>' +
        '<div class="row"><div><label for="f-name">Name (optional, Vorname reicht)</label><input id="f-name" name="name" autocomplete="given-name"></div><div><label for="f-mail">E-Mail' + req + '</label><input id="f-mail" type="email" name="email" required autocomplete="email"></div></div>' +
        '<label for="f-proj">Was baust du gerade? (optional)</label><textarea id="f-proj" name="projekt" rows="3"></textarea>' +
        '<label class="consent"><input type="checkbox" name="einwilligung" value="ja" required><span>Ich habe die <a href="datenschutz.html">Datenschutzhinweise</a> gelesen. Meine Angaben gehen über den Formulardienst FormSubmit per E-Mail an Jean Maurice Port und werden nur für die Antwort auf diese Anfrage genutzt. Dabei können sie in Länder ohne gleichwertigen Datenschutz wie die USA gelangen. Damit bin ich einverstanden; widerrufen kann ich das jederzeit per E-Mail.' + req + '</span></label>' +
        '<button class="btn" type="submit">' + icon("mail") + 'Stack-Check anfragen</button>' +
        '<p class="hint">Oder direkt: <a href="mailto:' + esc(F.to) + '?subject=Stack-Check">' + esc(F.to) + '</a></p></form>' +
        '<p style="margin-top:14px"><button type="button" class="btn btn-sm restart">' + icon("arrow") + 'Noch mal von vorn</button></p>';
      qEl.classList.add("hidden"); optsEl.classList.add("hidden"); res.classList.remove("hidden");
      dots.innerHTML = F.questions.map(function () { return '<i class="on"></i>'; }).join(""); stepLbl.textContent = "Fertig: " + list.length + " Tools vorgeschlagen"; back.classList.add("hidden");
      $(".restart", res).addEventListener("click", function () { ans = {}; stepIdx = 0; render(true); });
      barWatch($("form", res));
      $("h3.finder-q", res).focus();
    }
    back.addEventListener("click", function () { if (stepIdx > 0) { stepIdx--; render(true); } });
    render(false);
  }
  /* Gemeinsame Hilfen für Merkliste, Rechner und Formular-Anhänge */
  function escH(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function svg(id) { return '<svg class="ico" aria-hidden="true"><use href="#i-' + id + '"/></svg>'; }
  function attach(fieldId, text, label) {
    var f = document.getElementById(fieldId); if (!f) return false;
    f.value = text || "";
    var box = document.getElementById(fieldId.replace("l-", "l-attach-"));
    if (box) { $("span", box).textContent = label || ""; box.classList.toggle("hidden", !text); }
    return true;
  }
  $$(".attach button[data-clear]").forEach(function (b) {
    b.addEventListener("click", function () { attach(b.dataset.clear, "", ""); if (b.dataset.clear === "l-merk") store.set("kw-merk-attach", "0"); });
  });
  // Übergabe an das Formular: direkt zum Formular (nicht zum Bandanfang), Fokus aufs erste leere Pflichtfeld
  function goLead(prefill) {
    var ta = $("#l-proj");
    if (ta && prefill && !ta.value.trim()) ta.value = prefill;
    var target = (ta && ta.form) || $("#stack-check"); if (!target) return;
    cvAll();
    target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    var mail = $("#l-mail"), next = mail && !mail.value.trim() ? mail : ta;
    if (next) setTimeout(function () { next.focus({ preventScroll: true }); if (!reduce) target.scrollIntoView({ block: "start" }); }, reduce ? 0 : 700);
  }
  var leadForm = $("#l-merk") ? $("#l-merk").form : null;

  /* Merkliste: Lesezeichen an jedem Tool, Liste bleibt im Browser */
  var MK = "kw-merk";
  function mLoad() {
    try { var v = JSON.parse(store.get(MK) || "[]"); return Array.isArray(v) ? v.filter(function (x) { return x && typeof x.n === "string" && typeof x.u === "string" && /^https?:/.test(x.u); }).slice(0, 60) : []; }
    catch (e) { return []; }
  }
  var merk = mLoad();
  function mSave() { store.set(MK, JSON.stringify(merk)); }
  function mHas(u) { return merk.some(function (x) { return x.u === u; }); }
  function mText() { return merk.map(function (x) { return x.n + " (" + x.u + ")"; }).join("\n"); }
  function mLabel() { return merk.length + (merk.length === 1 ? " Tool" : " Tools") + " aus deiner Merkliste angehängt"; }
  var pill = $("#merk-pill"), panel = $("#merk"), mList = panel ? $(".merk-list", panel) : null;
  function addMerkBtn(li) {
    var a = li.querySelector("a.name"); if (!a || li.querySelector(".merk-btn")) return;
    var b = document.createElement("button");
    b.type = "button"; b.className = "merk-btn"; b.innerHTML = svg("bookmark");
    b.dataset.u = a.href; b.dataset.n = a.textContent;
    b.addEventListener("click", function () {
      if (mHas(a.href)) merk = merk.filter(function (x) { return x.u !== a.href; }); else merk.push({ n: a.textContent, u: a.href });
      mSave(); mRender();
      if (pill && merk.length) { pill.classList.remove("pop"); void pill.offsetWidth; pill.classList.add("pop"); }
    });
    li.appendChild(b);
  }
  $$("ul.tools li").forEach(addMerkBtn);
  window.kwAddMerk = function (root) { $$("li", root).forEach(addMerkBtn); mRender(); };
  function mRender() {
    $$(".merk-btn").forEach(function (b) {
      var on = mHas(b.dataset.u);
      b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
      b.setAttribute("aria-label", (on ? "Von der Merkliste nehmen: " : "Merken: ") + b.dataset.n); b.title = on ? "Gemerkt" : "Merken";
    });
    if (pill) { pill.classList.toggle("hidden", !merk.length); $("#merk-n").textContent = merk.length; }
    if (mList) {
      mList.innerHTML = merk.map(function (x, i) {
        return '<li><a href="' + escH(x.u) + '" target="_blank" rel="noopener">' + escH(x.n) + '</a><button type="button" data-i="' + i + '" aria-label="Entfernen: ' + escH(x.n) + '">' + svg("x") + "</button></li>";
      }).join("");
      $(".merk-empty", panel).classList.toggle("hidden", merk.length > 0);
      $(".merk-actions", panel).classList.toggle("hidden", !merk.length);
    }
    var f = $("#l-merk"); if (f && f.value) attach("l-merk", merk.length ? mText() : "", mLabel());
  }
  function mOpen(open) {
    if (!panel) return;
    panel.hidden = !open; if (pill) pill.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var c = $(".close", panel); if (c) c.focus(); }
  }
  if (pill && panel) {
    pill.addEventListener("click", function () { mOpen(panel.hidden); });
    $(".close", panel).addEventListener("click", function () { mOpen(false); pill.focus(); });
    mList.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-i]"); if (!b) return;
      merk.splice(parseInt(b.dataset.i, 10), 1); mSave(); mRender(); if (!merk.length) { mOpen(false); }
    });
    $("#merk-clear").addEventListener("click", function () { merk = []; mSave(); mRender(); mOpen(false); });
    $("#merk-copy").addEventListener("click", function (e) {
      var btn = e.currentTarget, txt = btn.lastChild;
      function done(t) { txt.textContent = t; setTimeout(function () { txt.textContent = "Kopieren"; }, 1600); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(mText()).then(function () { done("Kopiert"); }, function () { done("Ging nicht, bitte von Hand kopieren"); });
      else done("Ging nicht, bitte von Hand kopieren");
    });
    $("#merk-send").addEventListener("click", function () {
      store.set("kw-merk-attach", "1");
      if ($("#l-merk")) { attach("l-merk", mText(), mLabel()); mOpen(false); goLead("Meine Merkliste: " + merk.map(function (x) { return x.n; }).join(", ") + ". "); }
      else location.href = "./#stack-check";
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { mOpen(false); pill.focus(); } });
  }
  // Auf einer anderen Seite zum Senden vorgemerkt: hier ans Formular hängen
  if (store.get("kw-merk-attach") === "1" && merk.length && $("#l-merk")) attach("l-merk", mText(), mLabel());
  mRender();

  /* Zeitspar-Rechner */
  var calc = $("#calc");
  if (calc) {
    var wochen = parseFloat(calc.dataset.wochen) || 46, rate = $("#c-rate"), cRows = $$(".calc-row", calc), summary = "";
    var nf1 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 1 }), nf0 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 0 });
    function num(el, max) { var v = parseFloat(String(el.value).replace(",", ".")); return isFinite(v) && v > 0 ? Math.min(v, max) : 0; }
    function calcRun() {
      var total = 0, saved = 0, top = 0, parts = [];
      var vals = cRows.map(function (r) {
        var h = num($(".c-h", r), 60), pc = num($(".c-p", r), 100), sv = h * pc / 100;
        total += h; saved += sv; if (sv > top) top = sv;
        return { r: r, h: h, pc: pc, sv: sv };
      });
      vals.forEach(function (v) {
        $("output", v.r).textContent = v.pc + " %";
        $(".calc-bar i", v.r).style.width = (top ? v.sv / top * 100 : 0).toFixed(1) + "%";
        $(".calc-bar span", v.r).textContent = nf1.format(v.sv) + " h/Woche";
        if (v.h > 0) parts.push(v.r.dataset.label + ": " + nf1.format(v.h) + " h pro Woche, " + v.pc + " % Ersparnis");
      });
      var share = total ? saved / total * 100 : 0, year = saved * wochen, r = num(rate, 1000), eur = year * r;
      $("#c-share").textContent = nf0.format(share) + " %";
      $(".calc-ring .fg", calc).setAttribute("stroke-dasharray", share.toFixed(1) + " 100");
      $("#c-week").textContent = nf1.format(saved) + " h";
      $("#c-year").textContent = nf0.format(year) + " h";
      $("#c-eur").textContent = nf0.format(eur) + " €";
      summary = parts.join("; ") + ". Ergebnis: " + nf1.format(saved) + " h pro Woche, " + nf0.format(year) + " h pro Jahr (" + wochen + " Wochen), Gegenwert " + nf0.format(eur) + " € bei " + nf0.format(r) + " € pro Stunde.";
      var f = $("#l-rechner"); if (f && f.value) attach("l-rechner", summary, "Rechner-Ergebnis angehängt: " + nf1.format(saved) + " h pro Woche");
    }
    var cLive = $("#c-live"), cLiveT;
    calc.addEventListener("input", function () {
      calcRun();
      clearTimeout(cLiveT);
      cLiveT = setTimeout(function () { if (cLive) cLive.textContent = "Ergebnis: " + $("#c-week").textContent + " pro Woche, " + $("#c-year").textContent + " pro Jahr, Gegenwert " + $("#c-eur").textContent + "."; }, 900);
    });
    calcRun();
    $("#c-send").addEventListener("click", function () {
      var week = $("#c-week").textContent;
      if (attach("l-rechner", summary, "Rechner-Ergebnis angehängt: " + week + " pro Woche")) goLead("Laut Zeitspar-Rechner könnte ich rund " + week + " pro Woche sparen. ");
    });
  }

  /* KI-Glossar: Filter, aktiver Buchstabe, Sprungziel hervorheben */
  var gq = $("#gq");
  if (gq) {
    var terms = $$(".term"), heads = $$(".az-letter"), gcount = $("#gcount"), gEmpty = $(".gl-empty");
    function gRun() {
      var s = gq.value.trim().toLowerCase(), shown = 0;
      terms.forEach(function (t) { var ok = !s || t.dataset.search.indexOf(s) > -1; t.classList.toggle("hidden", !ok); if (ok) shown++; });
      heads.forEach(function (h) {
        var n = h.nextElementSibling, any = false;
        while (n && !n.classList.contains("az-letter")) { if (n.classList.contains("term") && !n.classList.contains("hidden")) any = true; n = n.nextElementSibling; }
        h.classList.toggle("hidden", !any);
      });
      if (gcount) gcount.textContent = s ? shown + " von " + terms.length : terms.length + " Begriffe";
      if (gEmpty) gEmpty.classList.toggle("hidden", shown > 0);
    }
    gq.addEventListener("input", gRun); gRun();
    var azLinks = $$(".az-letters a");
    if ("IntersectionObserver" in window) {
      var io4 = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { var id = e.target.id; azLinks.forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + id); }); } });
      }, { rootMargin: "-15% 0px -75% 0px" });
      heads.forEach(function (h) { io4.observe(h); });
    }
    function flash() {
      var id = location.hash ? decodeURIComponent(location.hash.slice(1)) : "", t = id && document.getElementById(id);
      if (t && t.classList.contains("term")) { t.classList.add("in", "flash"); setTimeout(function () { t.classList.remove("flash"); }, 1800); return t; }
    }
    window.addEventListener("hashchange", flash);
    // Beim Laden mit #begriff: nach dem Aufbau der Seite sicher hinspringen
    var t0 = flash(); if (t0) window.addEventListener("load", function () { t0.scrollIntoView({ block: "start", behavior: "instant" }); });
  }

  /* Trend-Seite: Radar nach Rolle; Ergebnis lässt sich an den Stack-Check hängen */
  $$("[data-js-only]").forEach(function (el) { el.hidden = false; });
  var radar = $("#radar"), RD = jsonData("kw-radar");
  if (radar && RD) {
    radar.hidden = false;
    var rdOut = $(".radar-out", radar), rdRole = null;
    var RD_TXT = ["kannst du auslassen", "am Rande", "lohnt einen Blick", "trifft dich direkt"];
    function rdRank(id) {
      return RD.trends.map(function (t, i) { return { t: t, s: t.radar[id], i: i }; }).sort(function (a, b) { return b.s - a.s || a.i - b.i; });
    }
    function rdRender(id) {
      rdRole = RD.rollen.filter(function (r) { return r.id === id; })[0];
      $$(".radar-roles .opt", radar).forEach(function (b) { var on = b.dataset.rolle === id; b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });
      var ranked = rdRank(id), top = ranked.filter(function (x) { return x.s > 0; }).slice(0, 3);
      rdOut.innerHTML = '<ol class="radar-list">' + ranked.map(function (x, k) {
        var bars = ""; for (var j = 1; j <= 3; j++) bars += "<i" + (j <= x.s ? ' class="on"' : "") + "></i>";
        return '<li class="s' + x.s + (k < top.length ? " top" : "") + '"><a href="#' + escH(x.t.id) + '">' + escH(x.t.label) + '</a><span class="radar-bar" title="' + RD_TXT[x.s] + '">' + bars + "</span><small>" + RD_TXT[x.s] + "</small>" +
          (k < top.length ? '<p class="radar-step">' + svg("check") + "<span>" + escH(x.t.schritt) + "</span></p>" : "") + "</li>";
      }).join("") + '</ol><p class="radar-cta"><button type="button" class="btn btn-lime btn-sm" id="radar-send">' + svg("mail") + 'Mit Radar zum Stack-Check</button><span>Jean schaut, welche Tools zu deinen drei Trends passen.</span></p>' +
        (rdRole.page ? '<p class="radar-page"><a href="' + escH(rdRole.page) + '">' + svg("arrow") + escH(rdRole.h1) + ": Aufgaben, Werkzeuge, Fragen</a></p>" : "");
      $("#radar-send").addEventListener("click", function () {
        var names = top.map(function (x) { return x.t.label; });
        var text = "Rolle: " + rdRole.label + "\n" + top.map(function (x, k) { return (k + 1) + ". " + x.t.label + ": " + x.t.schritt; }).join("\n");
        if (attach("l-radar", text, "Trend-Radar angehängt: " + rdRole.label)) {
          var sel = $("#l-rolle"); if (sel && rdRole.form) sel.value = rdRole.form; // jede Rolle hat eine Formular-Option (Build prüft das)
          goLead("Mein Trend-Radar (" + rdRole.label + ") sagt: " + names.join(", ") + ". Welche Tools passen dazu? ");
        }
      });
    }
    $$(".radar-roles .opt", radar).forEach(function (b) { b.setAttribute("aria-pressed", "false"); b.addEventListener("click", function () { rdRender(b.dataset.rolle); }); });
    // Einstieg von einer Einsatz-Seite: ki-trends.html?rolle=shop#radar zeigt das Radar gleich für diese Rolle
    var rdQ = new URLSearchParams(location.search).get("rolle");
    if (rdQ && RD.rollen.some(function (r) { return r.id === rdQ; })) rdRender(rdQ);
  }

  /* Trend-Seite: aktiven Trend in der Leiste markieren und sichtbar halten */
  var trLinks = $$(".tr-links a");
  if (trLinks.length && "IntersectionObserver" in window) {
    var io5 = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        trLinks.forEach(function (a) {
          var on = a.getAttribute("href") === "#" + e.target.id;
          a.classList.toggle("on", on);
          if (on) { var bar = a.parentNode; bar.scrollLeft = a.offsetLeft - (bar.clientWidth - a.offsetWidth) / 2; }
        });
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    $$("article.trend").forEach(function (t) { io5.observe(t); });
  }

  /* Such-Panel auf jeder Seite: alle Tools (tools.json) plus Ratgeber, Einsatzgebiete, Trends und Begriffe (seiten.json) */
  var sp = $("#searchpanel");
  if (sp && q) {
    var DATA = null, PAGES = [], loading = null, spGen = 0, spHits = [], spShown = 0, SP_STEP = 40, spList = $(".sp-list", sp), spCount = $("#sp-count"), spEmpty = $(".sp-empty", sp), spEu = $("#sp-eu"), spOss = $("#sp-oss"), spNeu = $("#sp-neu");
    var spPages = $(".sp-pages", sp), spPagesList = $(".sp-pages ul", sp), spToolsLbl = $(".sp-tools-lbl", sp), spNoReopen = false;
    function spLoad() {
      if (DATA) return Promise.resolve(DATA);
      // Seitenindex ist eine Zugabe: fehlt er, sucht das Panel wie bisher nur in den Tools
      var pagesP = fetch(SITE + "seiten.json").then(function (r) { return r.ok ? r.json() : { seiten: [] }; }).then(function (j) { PAGES = j.seiten || []; }, function () { PAGES = []; });
      if (!loading) loading = Promise.all([fetch(SITE + "tools.json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }), pagesP]).then(function (res) {
        DATA = res[0].tools.map(function (t, i) {
          t._i = i; t._n = t.name.toLowerCase(); t._c = (t.kategorie + " " + t.bereich).toLowerCase(); t._d = t.beschreibung.toLowerCase();
          t._s = [t._n, t._d, t._c].join(" "); return t;
        });
        return DATA;
      }, function (e) { loading = null; throw e; });
      return loading;
    }
    function spMatch(words) { return function (t) { return words.every(function (w) { return t._s.indexOf(w) > -1; }); }; }
    // Rangfolge: Treffer im Namen zählen am meisten, dann Schublade und Fach, dann Beschreibung; Namensanfang extra
    function spScore(t, words, s) {
      var sc = t._n.indexOf(s) === 0 ? 4 : 0;
      words.forEach(function (w) { sc += (t._n.indexOf(w) > -1 ? 3 : 0) + (t._c.indexOf(w) > -1 ? 2 : 0) + (t._d.indexOf(w) > -1 ? 1 : 0); });
      return sc;
    }
    function spOpen(open) { sp.hidden = !open; q.setAttribute("aria-expanded", open ? "true" : "false"); }
    // Trefferzahl für den Knopf "In allen Tools suchen" auf Kategorie-Seiten
    window.kwPanelCount = function (s) { return spLoad().then(function (rows) { return rows.filter(spMatch(s.split(/\s+/))).length; }, function () { return 0; }); };
    function spPagesRender(s, filt) {
      var words = s ? s.split(/\s+/) : [];
      var hits = (!s || filt) ? [] : PAGES.filter(function (p) { return words.every(function (w) { return p.s.indexOf(w) > -1; }); });
      hits.sort(function (a, b) { return (b.t.toLowerCase().indexOf(s) > -1) - (a.t.toLowerCase().indexOf(s) > -1); });
      hits = hits.slice(0, 6);
      spPagesList.innerHTML = hits.map(function (p) {
        return '<li><a href="' + escH(SITE + p.u) + '"><i>' + escH(p.k) + "</i><b>" + escH(p.t) + "</b><small>" + escH(p.d) + "</small></a></li>";
      }).join("");
      spPages.hidden = !hits.length;
      return hits.length;
    }
    function spHide() { spGen++; spOpen(false); } // spätere Antworten einer alten Suche verwerfen
    function spRun(keepOpen) {
      var s = q.value.trim().toLowerCase(), my = ++spGen, filt = spEu.checked || spOss.checked || spNeu.checked;
      if (!s && !filt) { // ohne Suchwort reicht ein gesetzter Filter
        if (keepOpen === true && !sp.hidden) { spCount.textContent = "Tipp ein Suchwort oder wähl einen Filter."; spList.innerHTML = ""; spPages.hidden = true; spToolsLbl.hidden = true; spEmpty.classList.add("hidden"); }
        else spOpen(false);
        return;
      }
      // Ladezustand: Panel sofort zeigen, solange tools.json noch unterwegs ist
      if (!DATA) {
        spCount.textContent = "Kurbel sucht in den Schubladen …"; spPages.hidden = true; spToolsLbl.hidden = true; spEmpty.classList.add("hidden");
        spList.innerHTML = '<li class="sp-skel" aria-hidden="true"></li><li class="sp-skel" aria-hidden="true"></li><li class="sp-skel" aria-hidden="true"></li>';
        spOpen(true);
      }
      spLoad().then(function (rows) {
        if (my !== spGen) return;
        var words = s ? s.split(/\s+/) : [], m = spMatch(words);
        var hits = rows.filter(function (t) { return m(t) && (!spEu.checked || t.eu) && (!spOss.checked || t.open_source) && (!spNeu.checked || t.neu); });
        if (s) {
          hits.forEach(function (t) { t._sc = spScore(t, words, s); });
          hits.sort(function (a, b) { return b._sc - a._sc || a._i - b._i; });
        }
        var np = spPagesRender(s, filt);
        spCount.textContent = (np ? np + (np === 1 ? " Seite, " : " Seiten, ") : "") + hits.length + " von " + rows.length + " Tools";
        spToolsLbl.hidden = !(np && hits.length);
        spHits = hits; spShown = 0; spList.innerHTML = "";
        spMore();
        spEmpty.classList.toggle("hidden", hits.length + np > 0);
        spOpen(true);
      }).catch(function () { if (my !== spGen) return; spCount.textContent = "Die Suche klemmt gerade. Lade die Seite neu."; spList.innerHTML = ""; spPages.hidden = true; spOpen(true); });
    }
    function spRow(t) {
      var badges = (t.eu ? '<span class="badge eu">EU</span>' : "") + (t.open_source ? '<span class="badge oss">OSS</span>' : "") + (t.neu ? '<span class="badge neu">NEU</span>' : "");
      return '<li>' + favImg(t.icon, 28) + '<div><a class="name" href="' + escH(safeUrl(t.url)) + '" target="_blank" rel="noopener">' + escH(t.name) + "</a> " + badges +
        '<span class="desc">' + escH(t.beschreibung) + '</span><a class="sp-cat" href="' + escH(SITE + t.seite.replace(/^\.\//, "")) + '">' + svg("layers") + escH(t.kategorie) + (t.bereich ? " · " + escH(t.bereich) : "") + "</a></div></li>";
    }
    // Treffer in Portionen anhängen; der Knopf am Ende holt die nächsten, bis alle sichtbar sind
    function spMore() {
      var old = $(".sp-more", spList); if (old) old.remove();
      var next = spHits.slice(spShown, spShown + SP_STEP); spShown += next.length;
      spList.insertAdjacentHTML("beforeend", next.map(spRow).join(""));
      var rest = spHits.length - spShown;
      if (rest > 0) spList.insertAdjacentHTML("beforeend", '<li class="sp-more"><button type="button" class="btn btn-sm">' + svg("layers") + "Noch " + Math.min(rest, SP_STEP) + " von " + rest + " weiteren zeigen</button></li>");
      if (window.kwAddMerk) window.kwAddMerk(spList);
    }
    // stopPropagation: der Knopf verschwindet beim Nachladen, sonst hielte der Außen-Klick-Handler ihn für "außerhalb"
    spList.addEventListener("click", function (e) { if (e.target.closest(".sp-more button")) { e.stopPropagation(); spMore(); } });
    // Sprunglinks auf diese Seite (z. B. zum Stack-Check) schließen das Panel, damit es das Ziel nicht verdeckt
    sp.addEventListener("click", function (e) {
      var a = e.target.closest("a[href]"); if (!a) return;
      var u = new URL(a.href, location.href);
      if (u.origin === location.origin && u.pathname === location.pathname && u.hash) spHide();
    });
    window.kwPanelRun = spRun;
    var spT; q.addEventListener("input", function () { clearTimeout(spT); spT = setTimeout(spRun, 120); });
    // Beim ersten Fokus schon laden: bis das erste Wort getippt ist, liegen die Daten meist bereit
    q.addEventListener("focus", function () {
      spLoad().catch(function () {});
      if (spNoReopen) { spNoReopen = false; return; } // Fokus kommt von Escape oder Schließen zurück: zu lassen
      if (q.value.trim()) spRun();
    });
    // Pfeil runter springt aus dem Suchfeld in die Treffer
    q.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowDown" || sp.hidden) return;
      var first = $(".sp-pages a, .sp-list a.name, .sp-head input", sp);
      if (first) { e.preventDefault(); first.focus(); }
    });
    [spEu, spOss, spNeu].forEach(function (c) { c.addEventListener("change", function () { spRun(true); }); });
    $$("[data-sp]").forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation(); // sonst schließt der Klick-außerhalb-Handler das Panel sofort wieder
        q.value = ""; // "Alle …" heißt alle, nicht die Schnittmenge mit einem alten Suchwort
        spEu.checked = b.dataset.sp === "eu"; spOss.checked = b.dataset.sp === "oss"; spNeu.checked = b.dataset.sp === "neu"; spRun();
      });
    });
    function spClose() { var open = !sp.hidden; spHide(); if (open) { spNoReopen = true; q.focus(); spNoReopen = false; } }
    $(".close", sp).addEventListener("click", spClose);
    // Escape verwirft auch eine Suche, deren Antwort noch unterwegs ist
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") spClose(); });
    document.addEventListener("click", function (e) { if (!sp.contains(e.target) && e.target !== q) spHide(); });
  }
  /* Formulare: im Hintergrund an FormSubmit senden, mit Status und Mail-Ausweg, falls der Dienst hängt.
     Ohne JavaScript bleibt der normale POST an FormSubmit. */
  var FS_SLOW = 15000, FS_GIVEUP = 60000;
  var FS_FIRST = ["name", "email", "website", "rolle", "projekt", "antworten", "vorschlag", "quelle", "seite", "vorher"]; // Kontakt vor Anhängen
  var FS_LONG = { merkliste: 600, rechner: 500, radar: 700 };
  // Gespeicherte Merker erst setzen, wenn die Anfrage sicher raus ist (oder der Mail-Weg gewählt wurde)
  function fsMark(form) {
    if (form.querySelector("#l-merk")) store.set("kw-merk-attach", "0");
  }
  // Seite und vorherige Seite erst beim Absenden eintragen: nichts wird dafür im Browser gespeichert
  function fsContext(form) {
    var here = location.pathname.split("/").pop() || "index.html", r = document.referrer, from = "direkt oder unbekannt";
    if (r) { try { var u = new URL(r); from = u.origin === location.origin ? (u.pathname.split("/").pop() || "index.html") : "extern: " + u.hostname; } catch (e) {} }
    var a = form.querySelector("[name=seite]"), b = form.querySelector("[name=vorher]");
    if (a) a.value = here; if (b) b.value = from;
  }
  function fsData(form) {
    var fd = new FormData(form), vals = {}, subject = "Anfrage – KI-Werkstatt";
    fd.forEach(function (v, k) {
      if (k === "_subject") subject = String(v);
      if (k.charAt(0) === "_" || k === "einwilligung" || !String(v).trim()) return;
      var t = String(v);
      if (FS_LONG[k] && t.length > FS_LONG[k]) t = t.slice(0, FS_LONG[k]) + " … (gekürzt)";
      vals[k] = t;
    });
    var keys = FS_FIRST.filter(function (k) { return k in vals; }).concat(Object.keys(vals).filter(function (k) { return FS_FIRST.indexOf(k) < 0; }));
    return { fd: fd, subject: subject, text: keys.map(function (k) { return k + ": " + vals[k]; }).join("\n") };
  }
  function fsStatus(form) {
    var st = form.querySelector(".form-status");
    if (!st) {
      st = document.createElement("div"); st.className = "form-status"; st.setAttribute("role", "status"); st.setAttribute("aria-live", "polite");
      var btn = form.querySelector("button[type=submit]");
      if (btn) btn.insertAdjacentElement("afterend", st); else form.appendChild(st);
    }
    return st;
  }
  function fsMailto(form, data) {
    var to = decodeURIComponent((form.action.split("formsubmit.co/")[1] || "").replace(/^ajax\//, ""));
    return { to: to, href: "mailto:" + to + "?subject=" + encodeURIComponent(data.subject) + "&body=" + encodeURIComponent(data.text.slice(0, 1800)) };
  }
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form || !form.action || form.action.indexOf("https://formsubmit.co/") !== 0) return;
    fsContext(form);
    if (!window.fetch || !window.FormData) { fsMark(form); return; } // alter Browser: normaler POST
    e.preventDefault();
    if (form.dataset.busy === "1") return;
    var data = fsData(form), st = fsStatus(form), btn = form.querySelector("button[type=submit]");
    var honey = form.querySelector("[name=_honey]");
    if (honey && honey.value) { st.className = "form-status ok"; st.textContent = "Danke."; return; } // Bot: still verwerfen
    var next = (form.querySelector("[name=_next]") || {}).value || "danke.html", mail = fsMailto(form, data), done = false;
    function offerMail(cls, msg, label, note) {
      done = true; form.dataset.busy = "0"; if (btn) btn.disabled = false;
      st.className = "form-status " + cls;
      st.innerHTML = "<p>" + escH(msg) + '</p><a class="mailbtn" href="' + escH(mail.href) + '">' + svg("mail") + escH(label) + "</a><small>" + escH(note) + "</small>";
      var mb = st.querySelector(".mailbtn");
      if (mb) { mb.addEventListener("click", function () { fsMark(form); }); mb.focus(); }
    }
    // Abgelehnt: die Anfrage ist sicher nicht angekommen, der Mail-Weg ist der Ersatz
    function failed(msg) {
      if (done) return;
      offerMail("warn", msg, "Anfrage per E-Mail-Programm senden", "Deine Angaben stehen schon drin, du musst nur noch auf Senden drücken. Oder schreib direkt an " + mail.to + ".");
    }
    // Keine Antwort: vielleicht angekommen, vielleicht nicht. Mail nur zur Sicherheit, mit Hinweis auf Doppelung
    function unknown(msg) {
      if (done) return;
      offerMail("unsure", msg, "Zur Sicherheit per E-Mail senden", "Kann sein, dass Jean die Anfrage dann doppelt bekommt. Das ist kein Problem, eine Antwort kommt trotzdem nur einmal.");
    }
    form.dataset.busy = "1"; if (btn) btn.disabled = true;
    st.className = "form-status busy"; st.textContent = "Wird gesendet … Kurbel trägt den Zettel rüber.";
    var ctrl = window.AbortController ? new AbortController() : null;
    var slow = setTimeout(function () { if (!done) st.textContent = "Dauert länger als üblich. Die Anfrage ist vermutlich schon unterwegs, Kurbel wartet noch auf die Quittung …"; }, FS_SLOW);
    var giveUp = setTimeout(function () {
      if (ctrl) ctrl.abort();
      unknown("Der Formulardienst hat nach einer Minute nicht geantwortet. Ob die Anfrage angekommen ist, wissen wir deshalb nicht.");
    }, FS_GIVEUP);
    fetch(form.action.replace("https://formsubmit.co/", "https://formsubmit.co/ajax/"), { method: "POST", body: data.fd, headers: { Accept: "application/json" }, signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) {
        return r.json().catch(function () { return { success: "false", message: "HTTP " + r.status }; }).then(function (j) { j._ok = r.ok; return j; });
      })
      .then(function (j) {
        clearTimeout(slow); clearTimeout(giveUp); if (done) return;
        if (j._ok && (j.success === true || j.success === "true")) {
          done = true; fsMark(form); st.className = "form-status ok"; st.textContent = "Angekommen. Du wirst gleich weitergeleitet."; location.href = next; return;
        }
        if (/activat/i.test(String(j.message || ""))) return failed("Das Formular ist noch nicht freigeschaltet: FormSubmit hat dafür eine Bestätigungs-E-Mail an Jean geschickt. Bis dahin klappt der Weg per E-Mail.");
        failed("Der Formulardienst hat die Anfrage gerade nicht angenommen. Per E-Mail geht es sofort.");
      })
      .catch(function () {
        clearTimeout(slow); clearTimeout(giveUp);
        unknown("Die Verbindung zum Formulardienst ist abgebrochen. Ob die Anfrage angekommen ist, wissen wir deshalb nicht.");
      });
  }, true);
  (function () {

  /* ---------------------------------------------------------------- Liebevolle Details */
  // Basis-URL aus dem eigenen Skript-Pfad, damit tools.json auch auf der 404-Seite (beliebige Tiefe) gefunden wird
  var BASE = (document.currentScript && document.currentScript.src || "").replace(/assets\/app\.js.*$/, "") || "./";
  var toolsP = null;
  function tools() {
    if (!toolsP) toolsP = fetch(BASE + "tools.json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (j) { return j.tools; });
    return toolsP;
  }

  // Hinweis unten am Rand, für Bildschirmleser per aria-live
  var toastEl, toastT;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "kw-toast"; toastEl.setAttribute("role", "status"); toastEl.setAttribute("aria-live", "polite"); document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add("show");
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove("show"); }, 3600);
  }

  // Funkenregen in Lime, Weiß und Stahl; bei reduzierter Bewegung bleibt es beim Hinweis
  function sparks(x, y, n) {
    if (reduce || !document.body.animate) return;
    x = x == null ? innerWidth / 2 : x; y = y == null ? innerHeight / 3 : y; n = n || 28;
    for (var i = 0; i < n; i++) {
      var s = document.createElement("i");
      s.className = "spark" + (i % 3 === 1 ? " s2" : i % 3 === 2 ? " s3" : "");
      s.style.left = x + "px"; s.style.top = y + "px";
      document.body.appendChild(s);
      var a = Math.random() * Math.PI * 2, d = 60 + Math.random() * 140;
      var dx = Math.cos(a) * d, dy = Math.sin(a) * d - 40;
      var anim = s.animate([
        { transform: "translate(0,0) rotate(0deg)", opacity: 1 },
        { transform: "translate(" + dx + "px," + (dy + 160) + "px) rotate(" + (Math.random() * 540) + "deg)", opacity: 0 }
      ], { duration: 900 + Math.random() * 700, easing: "cubic-bezier(.2,.7,.4,1)" });
      anim.onfinish = (function (el) { return function () { el.remove(); }; })(s);
    }
  }
  function sparksAt(el, n) { if (!el) return sparks(null, null, n); var r = el.getBoundingClientRect(); sparks(r.left + r.width / 2, r.top + r.height / 2, n); }

  var heroBtn = $("#hm-hero"), say = $("#hm-say");

  // 1 Tageszeit-Gruß und Saison (ohne Wiedererkennung: dafür würde etwas im Browser gespeichert)
  var now = new Date(), h = now.getHours(), m = now.getMonth() + 1, d = now.getDate();
  var season = (m === 10 && d >= 25) || (m === 11 && d <= 2) ? "halloween" : (m === 12 && d <= 26) ? "xmas" : ((m === 12 && d === 31) || (m === 1 && d === 1)) ? "nye" : "";
  if (season) root.classList.add("season-" + season);
  if (say) {
    var greet;
    if (season === "halloween") greet = "Moin. Der Kürbis ist von Kurbel. Gruselig ist hier nur der Linkfriedhof, und den haben wir geleert.";
    else if (season === "xmas") greet = "Moin! Die Mütze war Kurbels Idee. Ich trag sie trotzdem gern.";
    else if (season === "nye") greet = "Frohes Neues! Mein Vorsatz: weniger offene Tabs, mehr fertige Arbeit.";
    else if (h >= 22 || h < 5) greet = "Nachtschicht? Die Tools laufen morgen auch noch. Aber gut, ich bleib wach.";
    else if (h < 11) greet = "Moin! Ich bin Hans Moritz. Erst Kaffee, dann Kabel.";
    else if (h < 14) greet = "Mahlzeit! Ich bin Hans Moritz. Kurz was nachschlagen in der Mittagspause?";
    else if (h < 18) greet = say.textContent;
    else greet = "Feierabend in Sicht. Such dir noch ein Werkzeug aus, ich halt die Tür auf.";
    say.textContent = greet;
  }
  if (season === "nye") setTimeout(function () { sparksAt(heroBtn, 40); }, 600);

  // 4 Werkstatt-Weisheiten per Klick auf Hans
  // Jede Weisheit steht nur hier: nichts doppelt mit Gruß, Überschriften oder Seitentexten
  var WISDOM = ["Zweimal messen, einmal prompten.", "Das beste Tool ist das, das du morgen noch benutzt.", "Automatisier zuerst das Langweiligste. Das spart am meisten.",
    "Ein Prompt ist wie eine Bestellung an der Theke: je genauer, desto besser das Essen.", "Ein Werkzeug, das keiner wiederfindet, ist Deko.", "Panzertape hält erstaunlich lange. Ein Backup hält länger.",
    "Klingt die KI sehr sicher, frag nach der Quelle.", "Erst das Problem, dann das Tool.", "Lieber ein Werkzeug richtig als zehn halb.",
    "Kurbel sagt, die übrige Schraube gehört so. Ich glaub ihm kein Wort.", "Wer fragt, bevor er klickt, muss seltener aufräumen."];
  var wi = Math.floor(Math.random() * WISDOM.length);
  if (heroBtn && say) heroBtn.addEventListener("click", function () {
    wi = (wi + 1) % WISDOM.length; say.textContent = WISDOM[wi];
    heroBtn.classList.remove("wave"); void heroBtn.offsetWidth; heroBtn.classList.add("wave");
  });
  if (tbtn && say) tbtn.addEventListener("click", function () {
    var dark = root.getAttribute("data-theme") === "dark";
    say.textContent = dark ? "Licht aus, Stirnlampe an. Ich seh trotzdem alles." : "Ah, Licht. Jetzt seh ich auch die Krümel auf der Werkbank.";
  });

  // 3 Hans schaut dem Mauszeiger hinterher (nur mit Maus und ohne reduzierte Bewegung)
  if (heroBtn && !reduce && window.matchMedia("(pointer: fine)").matches) {
    var pupils = $$(".hm-pupil", heroBtn), pend = false, mx = 0, my = 0;
    document.addEventListener("mousemove", function (e) {
      mx = e.clientX; my = e.clientY; if (pend) return; pend = true;
      requestAnimationFrame(function () {
        pend = false; var r = heroBtn.getBoundingClientRect(); if (!r.width) return;
        var cx = r.left + r.width / 2, cy = r.top + r.height * .38, dx = mx - cx, dy = my - cy, len = Math.sqrt(dx * dx + dy * dy) || 1, k = Math.min(1, len / 300);
        var tx = (dx / len) * 1.6 * k, ty = (dy / len) * 1.1 * k;
        pupils.forEach(function (p) { p.style.transform = "translate(" + tx.toFixed(2) + "px," + ty.toFixed(2) + "px)"; });
      });
    }, { passive: true });
  }

  // 7 Werkzeug des Tages: jeden Tag ein anderes, für alle gleich
  // tools.json (die ganze Liste) erst nach dem Laden, im Leerlauf und wenn die Box in der Nähe ist; der Platz ist reserviert
  var wotd = $("#wotd");
  function wotdFill() {
    tools().then(function (list) {
      if (!list.length) return;
      var day = Math.floor((Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())) / 864e5);
      var t = list[(day * 37) % list.length];
      wotd.innerHTML = favImg(t.icon, 28) + '<div><span class="k">Hans’ Werkzeug des Tages</span><br><b><a href="' + escH(safeUrl(t.url)) + '" target="_blank" rel="noopener">' + escH(t.name) + '</a></b>' +
        '<p class="d">' + escH(t.beschreibung) + '</p><p><a href="' + escH(t.seite) + '">Zur Schublade</a> · Morgen liegt ein anderes auf der Werkbank.</p></div>';
    }).catch(function () { wotd.hidden = true; });
  }
  function whenIdle(fn) {
    var go = function () { if (window.requestIdleCallback) requestIdleCallback(fn, { timeout: 2500 }); else setTimeout(fn, 300); };
    if (document.readyState === "complete") go(); else window.addEventListener("load", go);
  }
  if (wotd) {
    if ("IntersectionObserver" in window) {
      var io7 = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io7.disconnect(); whenIdle(wotdFill); } }, { rootMargin: "600px 0px" });
      io7.observe(wotd);
    } else whenIdle(wotdFill);
  }

  // 8 Schraubenjagd: Kurbel hat auf sieben Seitenarten je eine Schraube verloren
  var path = location.pathname.split("/").pop() || "index.html";
  var ptype = document.title.indexOf("nicht gefunden") > -1 ? "verlaufen" : /^index\.html$|^$/.test(path) ? "start" : /^ki-tools-/.test(path) ? "schublade" : /^ki-(fuer|im)-/.test(path) ? "einsatz" : /^ratgeber-/.test(path) ? "ratgeber" :
    path === "ki-trends.html" ? "trends" : path === "ki-glossar.html" ? "glossar" : "";
  var SPOT = { start: "#faq h2", schublade: ".tipp .eyebrow", einsatz: ".tipp .eyebrow", ratgeber: "#quellen h2", trends: ".tr-method .eyebrow", glossar: "h1", verlaufen: ".page h1" };
  var SCREW = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="#B9BEC6" stroke="#0E1116" stroke-width="1.6"/><path d="M7.5 12h9M12 7.5v9" stroke="#0E1116" stroke-width="2" stroke-linecap="round"/></svg>';
  var ALL = ["start", "schublade", "einsatz", "ratgeber", "trends", "glossar", "verlaufen"];
  function got() { try { var v = JSON.parse(store.get("kw-screws") || "[]"); return Array.isArray(v) ? v.filter(function (x) { return ALL.indexOf(x) > -1; }) : []; } catch (e) { return []; } }
  function screwsRender() {
    var box = $("#screws"), g = got(); if (!box || !g.length) return;
    box.hidden = false;
    box.classList.toggle("meister", g.length === ALL.length);
    box.innerHTML = SCREW + (g.length === ALL.length ? "Meisterbrief in Schraubensuche: alle " + ALL.length + " Schrauben von Kurbel gefunden." : "Kurbels verlorene Schrauben: " + g.length + " von " + ALL.length + " gefunden. Die anderen liegen auf anderen Seiten.");
  }
  screwsRender();
  if (ptype && got().indexOf(ptype) < 0) {
    var spot = null; SPOT[ptype].split(", ").some(function (sel) { spot = $(sel); return !!spot; });
    if (spot) {
      var sb = document.createElement("button"); sb.type = "button"; sb.className = "screw"; sb.innerHTML = SCREW;
      sb.setAttribute("aria-label", "Eine verlorene Schraube von Kurbel aufheben"); sb.title = "Nanu, eine Schraube?";
      spot.appendChild(sb);
      sb.addEventListener("click", function () {
        var g = got(); if (g.indexOf(ptype) < 0) g.push(ptype); store.set("kw-screws", JSON.stringify(g));
        sparksAt(sb, g.length === ALL.length ? 60 : 14); sb.classList.add("got"); sb.disabled = true;
        setTimeout(function () { sb.remove(); }, 800);
        toast(g.length === ALL.length ? "Alle " + ALL.length + " Schrauben gefunden! Kurbel hat zum ersten Mal nichts übrig. Er ist sprachlos." :
          "Schraube " + g.length + " von " + ALL.length + " gefunden. Kurbel ist gerührt.");
        screwsRender();
      });
    }
  }

  // 10 „moin“ tippen, irgendwo außerhalb von Eingabefeldern
  var typed = "";
  document.addEventListener("keydown", function (e) {
    var t = e.target; if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (!e.key || e.key.length !== 1) return;
    typed = (typed + e.key.toLowerCase()).slice(-4);
    if (typed === "moin") { typed = ""; toast("Moin zurück! Schön, dass du da bist. Hans"); sparksAt(heroBtn, 30); if (say) say.textContent = "Moin! Du hast das Zauberwort gefunden. Es heißt einfach: Moin."; }
  });

  // 11 Hans macht beim Schreiben im Formular Mut
  $$("textarea#l-proj").forEach(function (ta) {
    var lead = ta.closest(".lead"), b = lead && $(".kb-say .bubble", lead); if (!b) return;
    var orig = b.textContent, last = -1;
    ta.addEventListener("input", function () {
      var n = ta.value.trim().length, lvl = n === 0 ? 0 : n < 40 ? 1 : n < 140 ? 2 : n < 320 ? 3 : 4;
      if (lvl === last) return; last = lvl;
      b.textContent = ["", "Guter Anfang. Erzähl ruhig mehr.", "Sehr gut, damit kann Jean schon arbeiten.", "Jetzt wird es richtig gut. Werkzeuge? Probleme? Alles rein.", "Perfekt. So eine Anfrage liest Jean am liebsten."][lvl] || orig;
    });
  });

  // 12 Danke-Seite: passende Fassung je Formular (?typ=check|finder) und einmal Funken zum Empfang
  var dk = $(".page-danke");
  if (dk) {
    var typ = new URLSearchParams(location.search).get("typ");
    if (typ && $("[data-typ='" + typ.replace(/[^a-z]/g, "") + "']", dk)) $$("[data-typ]", dk).forEach(function (el) { el.hidden = el.dataset.typ !== typ; });
    setTimeout(function () { sparksAt($(".page-danke .hans"), 36); }, 400);
  }

  // 13 Ratgeber: gelesene Kapitel abhaken (nur im Speicher der Seite). Dauerhaft gemerkt und als "Weiterlesen bei"
  //    angeboten wird der Stand erst, wenn jemand "Lesefortschritt merken" anklickt (TDDDG § 25)
  var rgBody = $(".rg-body");
  if (rgBody) {
    var heads = $$(".rg-body > h2[id]"), rk = "kw-read:" + path, saved = store.get(rk), keep = saved !== null;
    var best = keep ? parseInt(saved, 10) || 0 : 0;
    var rail = function (id) { return $$(".rail a[href='#" + id + "'], .toc-m a[href='#" + id + "']"); };
    function mark(i) { for (var j = 0; j < i && j < heads.length; j++) rail(heads[j].id).forEach(function (a) { a.classList.add("read"); }); }
    mark(best);
    if (keep && best > 0 && best < heads.length) {
      var ctas = $(".hero .ctas") || $(".hero");
      if (ctas) { var rs = document.createElement("a"); rs.className = "resume"; rs.href = "#" + heads[best].id; rs.innerHTML = svg("bookmark") + "Weiterlesen bei: " + escH(heads[best].textContent); ctas.insertAdjacentElement("afterend", rs); }
    }
    // Schalter im Inhaltsverzeichnis (Seitenleiste und mobil), beide zeigen denselben Zustand
    var saveBtns = [$(".rail .in"), $(".toc-m nav")].filter(Boolean).map(function (box) {
      var b = document.createElement("button"); b.type = "button"; b.className = "read-save";
      b.innerHTML = svg("bookmark") + "Lesefortschritt merken";
      var before = box.querySelector(".lead-mini"); if (before) box.insertBefore(b, before); else box.appendChild(b);
      return b;
    });
    function saveSync() { saveBtns.forEach(function (b) { b.setAttribute("aria-pressed", keep ? "true" : "false"); b.title = keep ? "Gemerkt. Noch mal klicken löscht den Stand." : "Merkt sich im Browser, bis wohin du gelesen hast"; }); }
    saveSync();
    saveBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        keep = !keep;
        if (keep) { store.set(rk, String(best)); toast("Gemerkt. Beim nächsten Besuch geht es an dieser Stelle weiter."); }
        else { store.del(rk); toast("Lesestand gelöscht. Gemerkt wird erst wieder, wenn du es einschaltest."); }
        saveSync();
      });
    });
    var rq = false;
    window.addEventListener("scroll", function () {
      if (rq) return; rq = true;
      requestAnimationFrame(function () {
        rq = false; var n = 0;
        heads.forEach(function (hd, i) { var nx = heads[i + 1] || $("#faq"); if (nx && nx.getBoundingClientRect().top < innerHeight * .5) n = i + 1; });
        if (n > best) { best = n; mark(best); if (keep) store.set(rk, String(best)); }
      });
    }, { passive: true });

    // 14 Geschafft-Karte: Funken, wenn sie zum ersten Mal ins Bild kommt
    var done = $("#geschafft");
    if (done && "IntersectionObserver" in window) {
      var io6 = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { sparksAt($(".hans", done), 24); io6.disconnect(); } }); }, { threshold: .6 });
      io6.observe(done);
    }
    // 15 War das hilfreich? Gezählt wird nichts, die Antwort bleibt im Browser
    var hk = "kw-hilf:" + path, ans = $(".hilf-a");
    function hilf(v) {
      if (!ans) return;
      if (v === "ja") ans.textContent = "Das freut uns sehr. Hans hat es sich ins Werkstattbuch geschrieben. Gezählt wird übrigens nichts.";
      else if (v === "nein") ans.innerHTML = "Danke für die Ehrlichkeit. Was hat gefehlt? <a href=\"mailto:" + escH(($("form[action^='https://formsubmit.co/']") || { action: "" }).action.replace("https://formsubmit.co/", "")) +
        "?subject=" + encodeURIComponent("Feedback zum Ratgeber: " + document.title) + "\">Schreib es Jean in zwei Sätzen</a>, die nächste Fassung wird besser.";
      $$("[data-hilf]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.hilf === v ? "true" : "false"); });
    }
    if (store.get(hk)) hilf(store.get(hk));
    $$("[data-hilf]").forEach(function (b) { b.addEventListener("click", function () { store.set(hk, b.dataset.hilf); hilf(b.dataset.hilf); if (b.dataset.hilf === "ja") sparksAt(b, 16); }); });
    // 16 Für die Werkstattwand drucken
    $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });
    // 17 Weitersagen: Teilen-Menü des Geräts oder Link in die Zwischenablage
    $$("[data-share]").forEach(function (b) {
      b.addEventListener("click", function () {
        var url = location.href.split("#")[0], title = document.title;
        if (navigator.share) { navigator.share({ title: title, url: url }).catch(function () {}); return; }
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { toast("Link kopiert. Weitersagen ist das schönste Lob für die Werkstatt."); }, function () { toast("Kopieren ging nicht. Der Link steht oben in der Adresszeile."); });
        else toast("Der Link steht oben in der Adresszeile.");
      });
    });
  }

  // 20 404: Überrasch mich mit einem zufälligen Tool
  var sBtn = $("#surprise-btn"), sBox = $("#surprise");
  if (sBtn && sBox) {
    sBtn.hidden = false;
    sBtn.addEventListener("click", function () {
      tools().then(function (list) {
        var t = list[Math.floor(Math.random() * list.length)];
        sBox.innerHTML = favImg(t.icon, 28) + '<div><span class="k">Kurbel hat stattdessen das hier gefunden</span><br><b><a href="' + escH(safeUrl(t.url)) + '" target="_blank" rel="noopener">' + escH(t.name) + '</a></b><p>' + escH(t.beschreibung) + ' <a href="' + escH(BASE + t.seite.replace(/^\.\//, "")) + '">Zur Schublade</a></p></div>';
        sBox.hidden = false; sBtn.lastChild.textContent = "Noch eins"; sparksAt(sBtn, 12);
      }).catch(function () { toast("Die Schublade klemmt gerade. Versuch es gleich noch mal."); });
    });
  }

  // 19 Skip-Link: Fokus wirklich auf den Inhalt setzen
  var skip = $(".skip"), wb = $("#werkbank");
  if (skip && wb) skip.addEventListener("click", function () { setTimeout(function () { wb.focus(); }, 0); });

  // 18 Für alle, die unter die Haube schauen
  try {
    console.log("%c KI-Werkstatt %c Moin! Schön, dass du unter die Haube schaust. Hans Moritz und Kurbel sagen Hallo. Tipp: Tipp mal „moin“ auf der Seite. Und es liegen sieben Schrauben herum.",
      "background:#D7FF3C;color:#0E1116;font-weight:700;padding:3px 6px;border-radius:4px", "color:inherit");
  } catch (e) {}

  })();
})();
