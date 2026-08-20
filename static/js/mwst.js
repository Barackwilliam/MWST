/* ==========================================================================
   MWST MMS — shared behaviour
   Hakuna framework. Vanilla JS tu ili iwe rahisi kuhamishia Django templates.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------- Helpers ---------- */
  const $  = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  const css = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  /* ---------- Sidebar ---------- */
  const app = $(".app");

  function toggleSidebar() {
    if (!app) return;
    if (window.innerWidth <= 1024) {
      app.classList.toggle("is-mobileopen");
    } else {
      app.classList.toggle("is-collapsed");
      try {
        localStorage.setItem(
          "mwst.sidebar",
          app.classList.contains("is-collapsed") ? "collapsed" : "open"
        );
      } catch (e) {}
    }
  }

  $$("[data-toggle-sidebar]").forEach((b) =>
    b.addEventListener("click", toggleSidebar)
  );
  const scrim = $(".scrim");
  if (scrim) scrim.addEventListener("click", () => app.classList.remove("is-mobileopen"));

  try {
    if (localStorage.getItem("mwst.sidebar") === "collapsed" && window.innerWidth > 1024) {
      app && app.classList.add("is-collapsed");
    }
  } catch (e) {}

  /* ---------- Sub-menu groups ---------- */
  $$(".nav-group > .nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      const group = link.closest(".nav-group");
      if (!group) return;
      e.preventDefault();
      group.classList.toggle("is-open");
    });
  });

  /* ---------- Theme ---------- */
  const THEME_KEY = "mwst.theme";
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    $$("[data-theme-icon]").forEach((el) => {
      el.setAttribute("href", t === "dark" ? "#i-sun" : "#i-moon");
    });
  }
  let saved = "light";
  try { saved = localStorage.getItem(THEME_KEY) || "light"; } catch (e) {}
  applyTheme(saved);

  $$("[data-toggle-theme]").forEach((b) =>
    b.addEventListener("click", () => {
      const next =
        document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
      window.MWST.redrawCharts();
    })
  );

  /* ---------- Chart.js defaults & factory ---------- */
  const registry = [];

  function baseOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: css("--ink") || "#0f172a",
          titleFont: { family: "Inter", size: 12, weight: "600" },
          bodyFont: { family: "Inter", size: 12 },
          padding: 10,
          cornerRadius: 8,
          displayColors: true,
          boxWidth: 8,
          boxHeight: 8,
          boxPadding: 4,
        },
      },
    };
  }

  function axisOptions() {
    const grid = css("--line-soft") || "#eef2f6";
    const tick = css("--muted") || "#64748b";
    return {
      x: {
        grid: { display: false, drawBorder: false },
        ticks: { color: tick, font: { family: "Inter", size: 10.5 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: grid, drawBorder: false },
        border: { display: false },
        ticks: {
          color: tick,
          font: { family: "Inter", size: 10.5 },
          padding: 6,
          callback: (v) => window.MWST.shortNum(v),
        },
      },
    };
  }

  function make(canvas, cfg) {
    if (!canvas || typeof Chart === "undefined") return null;
    const chart = new Chart(canvas.getContext("2d"), cfg);
    registry.push({ canvas, cfg, chart });
    return chart;
  }

  /* ---------- Public API ---------- */
  window.MWST = {
    $, $$, css,

    shortNum(v) {
      const n = Number(v);
      if (!isFinite(n)) return v;
      const a = Math.abs(n);
      if (a >= 1e9) return (n / 1e9).toFixed(a % 1e9 === 0 ? 0 : 1) + "B";
      if (a >= 1e6) return (n / 1e6).toFixed(a % 1e6 === 0 ? 0 : 1) + "M";
      if (a >= 1e3) return (n / 1e3).toFixed(a % 1e3 === 0 ? 0 : 1) + "K";
      return String(n);
    },

    money(v) {
      return "TZS " + Number(v).toLocaleString("en-US");
    },

    /* Line / area chart — Ukuaji wa Wanachama, Mwenendo wa Michango */
    line(el, labels, series) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const datasets = series.map((s) => {
        const color = s.color || css("--c1");
        let fill = false;
        if (s.fill) {
          const g = canvas.getContext("2d").createLinearGradient(0, 0, 0, canvas.offsetHeight || 220);
          g.addColorStop(0, s.fillTop || "rgba(18,134,74,.20)");
          g.addColorStop(1, "rgba(18,134,74,0)");
          fill = { target: "origin", above: g };
        }
        return {
          label: s.label,
          data: s.data,
          borderColor: color,
          backgroundColor: color,
          borderWidth: 2.4,
          pointRadius: 2.6,
          pointHoverRadius: 5,
          pointBackgroundColor: "#fff",
          pointBorderColor: color,
          pointBorderWidth: 2,
          tension: 0.34,
          fill: s.fill ? fill : false,
        };
      });
      const opts = baseOptions();
      opts.scales = axisOptions();
      return make(canvas, { type: "line", data: { labels, datasets }, options: opts });
    },

    /* Bar chart — Muhtasari wa Mapato */
    bar(el, labels, series) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const datasets = series.map((s) => ({
        label: s.label,
        data: s.data,
        backgroundColor: s.color || css("--c1"),
        borderRadius: 5,
        borderSkipped: false,
        maxBarThickness: 26,
      }));
      const opts = baseOptions();
      opts.scales = axisOptions();
      return make(canvas, { type: "bar", data: { labels, datasets }, options: opts });
    },

    /* Donut — Wanachama kwa Kategoria, Michango kwa Aina */
    donut(el, labels, data, colors, cutout) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const opts = baseOptions();
      opts.cutout = cutout || "68%";
      opts.plugins.tooltip.callbacks = {
        label: (c) => " " + c.label + ": " + Number(c.raw).toLocaleString("en-US"),
      };
      return make(canvas, {
        type: "doughnut",
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: colors,
            borderWidth: 3,
            borderColor: css("--surface") || "#fff",
            hoverOffset: 6,
          }],
        },
        options: opts,
      });
    },

    redrawCharts() {
      registry.forEach((r) => {
        r.chart.destroy();
        r.chart = new Chart(r.canvas.getContext("2d"), r.cfg);
      });
    },
  };

  /* ---------- Animate progress bars on load ---------- */
  requestAnimationFrame(() => {
    $$("[data-prog]").forEach((el) => {
      el.style.width = el.getAttribute("data-prog") + "%";
    });
  });

  /* ---------- Gauge rings ---------- */
  $$("[data-gauge]").forEach((el) => {
    const pct = Number(el.getAttribute("data-gauge"));
    const circle = $(".gauge__fill", el);
    if (!circle) return;
    const r = circle.r.baseVal.value;
    const c = 2 * Math.PI * r;
    circle.style.strokeDasharray = c;
    circle.style.strokeDashoffset = c;
    requestAnimationFrame(() => {
      circle.style.strokeDashoffset = c - (pct / 100) * c;
    });
  });

  /* ---------- Live clock for topbar date pill ---------- */
  const clock = $("[data-clock]");
  if (clock) {
    const tick = () => {
      const d = new Date();
      clock.textContent = d.toLocaleTimeString("en-GB", {
        hour: "2-digit", minute: "2-digit", second: "2-digit",
      });
    };
    tick();
    setInterval(tick, 1000);
  }
})();

/* ==========================================================================
   BACKEND-PENDING MODAL
   Kila kitu chenye data-backend kinatoa popup nzuri badala ya kufa kimya.
   ========================================================================== */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  const box = document.getElementById("mwst-i18n");
  if (box && window.MWST) {
    try { window.MWST.i18n = JSON.parse(box.textContent); } catch (e) {}
  }
  const T = (window.MWST && window.MWST.i18n) || {};
  const t = (k, fb) => T[k] || fb;

  const scrim = document.createElement("div");
  scrim.className = "modal-scrim";
  scrim.setAttribute("role", "dialog");
  scrim.setAttribute("aria-modal", "true");
  scrim.innerHTML =
    '<div class="modal">' +
      '<div class="modal__top">' +
        '<button class="modal__x" data-close aria-label="Close">' +
          '<svg width="16" height="16"><use href="#i-x-circle"></use></svg></button>' +
        '<div class="modal__badge"><svg><use href="#i-lock"></use></svg></div>' +
        '<div class="modal__eyebrow"></div>' +
        '<div class="modal__title"></div>' +
      "</div>" +
      '<div class="modal__body">' +
        '<p class="modal__text"></p>' +
        '<span class="modal__chip"><svg><use href="#i-info"></use></svg><span></span></span>' +
      "</div>" +
      '<div class="modal__foot">' +
        '<button class="btn btn--ghost" data-close></button>' +
        '<button class="btn btn--primary" data-close></button>' +
      "</div>" +
    "</div>";
  document.body.appendChild(scrim);

  const elEyebrow = $(".modal__eyebrow", scrim);
  const elTitle = $(".modal__title", scrim);
  const elText = $(".modal__text", scrim);
  const elChip = $(".modal__chip span", scrim);
  const btns = $$(".modal__foot .btn", scrim);
  let lastFocus = null;

  function open(feature) {
    elEyebrow.textContent = t("pending_eyebrow", "Inakuja hivi karibuni");
    elTitle.textContent = feature || t("pending_title", "Kipengele hiki");
    elText.textContent = t(
      "backend_pending",
      "Kipengele hiki kitapatikana mfumo wa nyuma (backend) utakapokamilika. " +
      "Kwa sasa unaona muundo na taarifa za mfano."
    );
    elChip.textContent = t("pending_chip", "Muundo umekamilika — data ni ya mfano");
    btns[0].textContent = t("pending_close", "Sawa, nimeelewa");
    btns[1].textContent = t("pending_explore", "Endelea Kutazama");

    lastFocus = document.activeElement;
    scrim.classList.add("is-open");
    document.body.style.overflow = "hidden";
    setTimeout(() => btns[1].focus(), 60);
  }

  function close() {
    scrim.classList.remove("is-open");
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  scrim.addEventListener("click", (e) => {
    if (e.target === scrim || e.target.closest("[data-close]")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && scrim.classList.contains("is-open")) close();
  });

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-backend]");
    if (!el) return;
    e.preventDefault();
    open(el.getAttribute("data-backend"));
  });

  if (window.MWST) window.MWST.pending = open;
})();


/* ==========================================================================
   PUBLIC SITE — drawer, counters, reveal, accordion, tabs
   ========================================================================== */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  /* ---- Mobile drawer ---- */
  const drawer = $(".drawer");
  const dScrim = $(".drawer-scrim");
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    dScrim && dScrim.classList.toggle("is-open", open);
    document.body.style.overflow = open ? "hidden" : "";
  }
  $$("[data-drawer-open]").forEach((b) => b.addEventListener("click", () => setDrawer(true)));
  $$("[data-drawer-close]").forEach((b) => b.addEventListener("click", () => setDrawer(false)));
  dScrim && dScrim.addEventListener("click", () => setDrawer(false));

  /* ---- Scroll reveal ---- */
  const reveals = $$(".reveal");
  if (reveals.length) {
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => entries.forEach((en, i) => {
          if (!en.isIntersecting) return;
          setTimeout(() => en.target.classList.add("is-in"), (i % 6) * 70);
          io.unobserve(en.target);
        }),
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
      reveals.forEach((r) => io.observe(r));
    } else {
      reveals.forEach((r) => r.classList.add("is-in"));
    }
  }

  /* ---- Counters ---- */
  function animate(el) {
    const target = parseFloat(el.getAttribute("data-count"));
    const suffix = el.getAttribute("data-suffix") || "";
    const dur = 1400;
    const start = performance.now();
    function step(now) {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const v = target * eased;
      el.textContent =
        (target >= 1000 ? Math.round(v).toLocaleString("en-US") : v.toFixed(target % 1 ? 1 : 0)) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const io2 = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { animate(e.target); io2.unobserve(e.target); }
    }), { threshold: 0.4 });
    counters.forEach((c) => io2.observe(c));
  } else {
    counters.forEach(animate);
  }

  /* ---- Accordion ---- */
  $$(".acc__btn").forEach((b) =>
    b.addEventListener("click", () => {
      const item = b.closest(".acc__item");
      const open = item.classList.contains("is-open");
      $$(".acc__item", item.parentElement).forEach((i) => i.classList.remove("is-open"));
      if (!open) item.classList.add("is-open");
    })
  );

  /* ---- Filter tabs ---- */
  $$("[data-tabs]").forEach((group) => {
    const targetSel = group.getAttribute("data-tabs");
    group.addEventListener("click", (e) => {
      const tab = e.target.closest(".tab");
      if (!tab) return;
      $$(".tab", group).forEach((t) => t.classList.remove("is-active"));
      tab.classList.add("is-active");
      const key = tab.getAttribute("data-filter");
      $$(targetSel + " [data-cat]").forEach((card) => {
        const show = key === "all" || card.getAttribute("data-cat") === key;
        card.style.display = show ? "" : "none";
      });
    });
  });

  /* ---- Smooth scroll ---- */
  $$('a[href^="#"]:not([data-backend])').forEach((a) =>
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length < 2) return;
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    })
  );
})();

/* ==========================================================================
   FOMU — onyesha nenosiri, cascading dropdowns
   ========================================================================== */
(function () {
  "use strict";
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  /* Onyesha / ficha nenosiri */
  $$("[data-toggle-pw]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const field = btn.closest(".loginfield");
      const input = field && field.querySelector('input[type="password"], input[type="text"]');
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
    })
  );

  /* Mkoa -> Wilaya -> Kata */
  async function fill(select, url, placeholder) {
    select.innerHTML = `<option value="">${placeholder}</option>`;
    if (!url) return;
    try {
      const res = await fetch(url);
      const data = await res.json();
      data.results.forEach((r) => {
        const o = document.createElement("option");
        o.value = r.id;
        o.textContent = r.name;
        select.appendChild(o);
      });
    } catch (e) { /* kimya */ }
  }

  const region = document.querySelector("#id_region");
  const district = document.querySelector("#id_district");
  const ward = document.querySelector("#id_ward");

  if (region && district) {
    region.addEventListener("change", () => {
      fill(district, region.value ? `/api/wilaya/?region=${region.value}` : "", "—");
      if (ward) fill(ward, "", "—");
    });
  }
  if (district && ward) {
    district.addEventListener("change", () => {
      fill(ward, district.value ? `/api/kata/?district=${district.value}` : "", "—");
    });
  }
})();

/* ==========================================================================
   MAPENDELEO YA VIDAKUZI
   Kidirisha kidogo kinachotimiza ahadi iliyo kwenye Sera ya Vidakuzi.
   Uchaguzi unahifadhiwa kwenye localStorage kwa mwaka mmoja.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "mwst-cookie-consent";
  var MAX_AGE = 365 * 24 * 60 * 60 * 1000;
  var bar = document.getElementById("cookiebar");
  if (!bar) return;

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || !v.at || Date.now() - v.at > MAX_AGE) return null;
      return v;
    } catch (e) { return null; }
  }

  function show() { bar.hidden = false; requestAnimationFrame(function () { bar.classList.add("is-in"); }); }
  function hide() { bar.classList.remove("is-in"); setTimeout(function () { bar.hidden = true; }, 260); }

  function save(choice) {
    try {
      localStorage.setItem(KEY, JSON.stringify({ choice: choice, at: Date.now() }));
    } catch (e) { /* kivinjari kimezuia hifadhi — tunaendelea tu */ }
    document.documentElement.dataset.cookieConsent = choice;
    hide();
  }

  var saved = read();
  if (saved) {
    document.documentElement.dataset.cookieConsent = saved.choice;
  } else {
    show();
  }

  bar.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-cookie]");
    if (btn) save(btn.getAttribute("data-cookie"));
  });

  // Kitufe cha "Badilisha mapendeleo" kwenye ukurasa wa Sera ya Vidakuzi
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-cookie-reopen]")) {
      try { localStorage.removeItem(KEY); } catch (err) { /* kimya */ }
      delete document.documentElement.dataset.cookieConsent;
      show();
    }
  });
})();

/* ==========================================================================
   UKURASA WA KUINGIA
   Jukumu ni mwongozo wa maonyesho tu; ruhusa halisi zinatoka kwenye akaunti.
   Uwanja wa kwanza hubadilika: watumishi huingia kwa jina la mtumiaji,
   wanachama na wahisani kwa namba ya uanachama au barua pepe.
   ========================================================================== */
(function () {
  "use strict";
  var pick = document.querySelector(".rolepick");
  if (!pick) return;

  var hint = document.querySelector("[data-role-hint]");
  var box = document.querySelector("[data-ident]");
  var identLabel = document.querySelector("[data-ident-label]");
  var identInput = document.querySelector("[data-ident-input]");
  var identHint = document.querySelector("[data-ident-hint]");
  var identIcon = document.querySelector("[data-ident-icon]");

  //: Majukumu ya ofisini. Yakiongezwa mapya, ongeza hapa na kwenye
  //: LOGIN_ROLES (core/views.py) — vinginevyo mtu ataulizwa barua pepe
  //: wakati anachotakiwa ni jina la mtumiaji.
  var STAFF = ["officer", "coordinator", "admin"];

  function paintIdentity(role) {
    if (!box) return;
    var kind = STAFF.indexOf(role) > -1 ? "staff" : "public";
    if (identLabel) identLabel.textContent = box.getAttribute("data-" + kind + "-label") || "";
    if (identHint) identHint.textContent = box.getAttribute("data-" + kind + "-hint") || "";
    if (identInput) identInput.placeholder = box.getAttribute("data-" + kind + "-ph") || "";
    if (identIcon) {
      var name = box.getAttribute("data-" + kind + "-icon");
      if (name) identIcon.setAttribute("href", "#i-" + name);
    }
  }

  pick.addEventListener("change", function (e) {
    var input = e.target.closest("input[name='as']");
    if (!input) return;
    Array.prototype.forEach.call(pick.querySelectorAll(".rolepick__item"), function (el) {
      el.classList.toggle("is-on", el.contains(input));
    });
    if (hint) {
      var label = input.closest(".rolepick__item");
      var text = label && label.getAttribute("data-hint");
      if (text) hint.textContent = text;
    }
    paintIdentity(input.value);
  });

  var current = pick.querySelector("input[name='as']:checked");
  if (current) paintIdentity(current.value);
})();

/* ==========================================================================
   KICHAGUA LUGHA
   Droplist inatuma fomu mara moja mtu anapochagua — hakuna kubonyeza.
   ========================================================================== */
(function () {
  "use strict";
  document.addEventListener("change", function (e) {
    var select = e.target.closest("[data-langform] select[name='language']");
    if (select) select.form.submit();
  });
})();

/* ==========================================================================
   FOMU YA MICHANGO
   - Muhtasari unaojirekebisha (hesabu ya kuonyesha tu; seva inahesabu upya)
   - Dropdown ya aina ya mchango: `<select>` ya kivinjari huamua yenyewe
     kufungua juu au chini kutegemea nafasi ya skrini. Hapa tunajenga yetu
     inayofunguka CHINI daima na kujisogeza yenyewe ikiwa haitoshi.
   ========================================================================== */
(function () {
  "use strict";
  var form = document.querySelector("[data-give]");
  if (!form) return;

  function $(sel) { return form.querySelector(sel); }
  function checked(name) { return form.querySelector("input[name='" + name + "']:checked"); }
  function money(n, sym) { return sym + " " + Math.round(n).toLocaleString("en-US"); }

  var select   = $("[data-purpose]");
  var wrap     = $("[data-purpose-wrap]");
  var amountEl = $("[data-amount]");
  var curEl    = $("[data-currency]");
  var iconEl   = $("[data-purpose-icon]");
  var noteEl   = $("[data-purpose-note]");
  var soonMsg  = $("[data-soon-msg]");

  /* ---------------- Dropdown ---------------- */
  var dd = null;

  function buildDropdown() {
    if (!select || !wrap) return;

    var box = document.createElement("div");
    box.className = "gv__dd";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "gv__dd__btn";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");

    var list = document.createElement("div");
    list.className = "gv__dd__list";
    list.setAttribute("role", "listbox");
    list.hidden = true;

    Array.prototype.forEach.call(select.children, function (node) {
      if (node.tagName === "OPTGROUP") {
        var head = document.createElement("div");
        head.className = "gv__dd__group";
        head.textContent = node.label;
        list.appendChild(head);
        Array.prototype.forEach.call(node.children, function (opt) {
          list.appendChild(makeOption(opt));
        });
      } else if (node.tagName === "OPTION") {
        list.appendChild(makeOption(node));
      }
    });

    box.appendChild(btn);
    box.appendChild(list);
    // Aikoni na kishale vinabaki vya `.gv__select`; tunaingiza dropdown
    // kati yao ili mpangilio ubaki ule ule.
    wrap.insertBefore(box, select);
    select.hidden = true;
    select.setAttribute("tabindex", "-1");

    dd = { box: box, btn: btn, list: list, cursor: -1 };
    syncButton();

    btn.addEventListener("click", function () { toggle(!isOpen()); });
    btn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
        e.preventDefault(); toggle(true);
      }
    });
    list.addEventListener("keydown", onListKeys);
    document.addEventListener("click", function (e) {
      if (isOpen() && !box.contains(e.target)) toggle(false);
    });
  }

  function makeOption(opt) {
    var el = document.createElement("button");
    el.type = "button";
    el.className = "gv__dd__opt";
    el.setAttribute("role", "option");
    el.dataset.value = opt.value;

    var icon = opt.getAttribute("data-icon");
    if (icon) {
      el.innerHTML = '<svg width="16" height="16"><use href="#i-' + icon + '"></use></svg>';
    }
    el.appendChild(document.createTextNode(opt.textContent));

    el.addEventListener("click", function () {
      select.value = opt.value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      toggle(false);
      dd.btn.focus();
    });
    return el;
  }

  function options() { return dd ? dd.list.querySelectorAll(".gv__dd__opt") : []; }
  function isOpen() { return dd && !dd.list.hidden; }

  function toggle(open) {
    if (!dd) return;
    dd.list.hidden = !open;
    dd.btn.setAttribute("aria-expanded", open ? "true" : "false");
    wrap.classList.toggle("is-open", open);
    if (!open) return;

    // Ikiwa orodha inatoka nje ya skrini, sogeza ukurasa kidogo badala ya
    // kuifungua juu — mtu anataka kuona chaguo, si kuruka.
    var rect = dd.list.getBoundingClientRect();
    var over = rect.bottom - window.innerHeight + 16;
    if (over > 0) window.scrollBy({ top: over, behavior: "smooth" });

    var on = dd.list.querySelector(".gv__dd__opt.is-on");
    if (on) on.scrollIntoView({ block: "nearest" });
    dd.cursor = -1;
  }

  function onListKeys(e) {
    var opts = options();
    if (!opts.length) return;
    if (e.key === "Escape") { toggle(false); dd.btn.focus(); return; }
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      dd.cursor += (e.key === "ArrowDown" ? 1 : -1);
      if (dd.cursor < 0) dd.cursor = opts.length - 1;
      if (dd.cursor >= opts.length) dd.cursor = 0;
      opts.forEach(function (o, i) { o.classList.toggle("is-cursor", i === dd.cursor); });
      opts[dd.cursor].scrollIntoView({ block: "nearest" });
    }
  }

  function syncButton() {
    if (!dd) return;
    var opt = select.options[select.selectedIndex];
    dd.btn.textContent = opt ? opt.textContent : "";
    options().forEach(function (o) {
      o.classList.toggle("is-on", o.dataset.value === select.value);
    });
  }

  /* ---------------- Muhtasari ---------------- */
  function paint() {
    var opt = curEl.options[curEl.selectedIndex];
    var rate = parseFloat(opt.getAttribute("data-rate")) || 1;
    var symbol = opt.getAttribute("data-symbol") || opt.value;
    var amount = parseFloat(amountEl.value) || 0;

    var chosen = select.options[select.selectedIndex];
    if (chosen) {
      $("[data-sum-purpose]").textContent = chosen.textContent;
      if (noteEl) noteEl.textContent = chosen.getAttribute("data-note") || "";
      if (iconEl) {
        var use = iconEl.querySelector("use");
        var name = chosen.getAttribute("data-icon");
        if (use && name) use.setAttribute("href", "#i-" + name);
      }
    }

    var recurrence = checked("recurrence");
    if (recurrence) {
      $("[data-sum-recurrence]").textContent =
        recurrence.closest(".gv__pill").querySelector("span").textContent;
    }

    // Kiasi alichoingiza ni cha MWEZI MMOJA. Jumla ni miezi × kiasi,
    // kasoro punguzo. Hesabu hii inalingana na `recurrence_total`
    // upande wa seva — seva ndiyo yenye kauli ya mwisho.
    var pill = recurrence ? recurrence.closest(".gv__pill") : null;
    var months = pill ? (parseInt(pill.getAttribute("data-months"), 10) || 1) : 1;
    var off = pill ? (parseInt(pill.getAttribute("data-discount"), 10) || 0) : 0;
    var total = Math.round(amount * months * (100 - off) / 100);

    $("[data-sum-amount]").textContent = money(amount, symbol);
    $("[data-sum-total]").textContent = money(total, symbol);

    var mRow = $("[data-sum-monthsrow]"), oRow = $("[data-sum-offrow]");
    if (mRow) {
      mRow.hidden = months <= 1;
      if (months > 1) $("[data-sum-months]").textContent = months;
    }
    if (oRow) {
      oRow.hidden = off <= 0;
      if (off > 0) {
        $("[data-sum-off]").textContent =
          "-" + off + "%  (" + money(Math.round(amount * months) - total, symbol) + ")";
      }
    }

    // Kiwango cha kubadilisha kinaonyeshwa tu kama si TZS.
    var fx = $("[data-sum-fx]");
    if (curEl.value !== "TZS" && amount > 0) {
      fx.hidden = false;
      fx.textContent = "\u2248 TSh " + Math.round(total * rate).toLocaleString("en-US");
    } else {
      fx.hidden = true;
    }

    form.querySelectorAll("[data-preset]").forEach(function (b) {
      b.classList.toggle("is-on",
        curEl.value === "TZS" && parseFloat(b.getAttribute("data-preset")) === amount);
    });
  }

  function mark(name, cls) {
    form.querySelectorAll("input[name='" + name + "']").forEach(function (el) {
      var box = el.closest("." + cls);
      if (box) box.classList.toggle("is-on", el.checked);
    });
  }

  form.addEventListener("change", function (e) {
    if (e.target === select) syncButton();
    if (e.target.name === "recurrence") mark("recurrence", "gv__pill");
    if (e.target.name === "provider") mark("provider", "gv__pay");
    paint();
  });
  form.addEventListener("input", function (e) {
    if (e.target === amountEl) paint();
  });

  form.addEventListener("click", function (e) {
    // Njia ya malipo isiyo tayari — mweleze badala ya kumwacha akihoji.
    var soon = e.target.closest("[data-soon]");
    if (soon && soonMsg) {
      soonMsg.hidden = false;
      soonMsg.textContent = soon.getAttribute("data-soon") + ": " +
        (soonMsg.getAttribute("data-text") || "njia hii inakuja hivi punde.");
      return;
    }
    var preset = e.target.closest("[data-preset]");
    if (!preset) return;
    // Viwango vya haraka ni vya TZS — rudisha fedha kwenye TZS.
    curEl.value = "TZS";
    amountEl.value = preset.getAttribute("data-preset");
    paint();
  });

  buildDropdown();
  paint();
})();

/* ==========================================================================
   LIPA ADA — miezi na muhtasari
   Ada ni ya mwezi; mtu anachagua miezi anayolipia. Hesabu hapa ni ya
   kuonyesha tu — seva inahesabu upya kabla ya kuhifadhi, kwa hiyo mtu
   hawezi kubadilisha bei kwenye kivinjari.
   ========================================================================== */
(function () {
  "use strict";
  var form = document.querySelector("[data-pay]");
  if (!form) return;

  function money(n) { return "TZS " + Math.round(n).toLocaleString("en-US"); }
  function checked(name) { return form.querySelector("input[name='" + name + "']:checked"); }

  var moInput = form.querySelector("[data-mo-input]");
  var MIN = parseInt(moInput && moInput.min, 10) || 1;
  var MAX = parseInt(moInput && moInput.max, 10) || 60;

  /* Vipimo vya punguzo. Lazima vilingane na DISCOUNT_TIERS kwenye
     core/data/giving.py — hii ni ya kuonyesha, ile ndiyo ya kweli. */
  var TIERS = [[12, 15], [6, 10], [3, 5]];

  /* Muda wa uanachama. Lazima ulingane na Member.TERM_YEARS. */
  var TERM_YEARS = 3;

  function discountFor(m) {
    for (var i = 0; i < TIERS.length; i++) {
      if (m >= TIERS[i][0]) return TIERS[i][1];
    }
    return 0;
  }

  function clamp(m) {
    m = parseInt(m, 10);
    if (isNaN(m)) return MIN;
    return Math.max(MIN, Math.min(MAX, m));
  }

  /* Lebo ya muda. Kiswahili kinatofautisha umoja na wingi, kwa hiyo
     hatuwezi kubandika "s" tu kama Kiingereza. */
  var sw = (document.documentElement.lang || "sw").indexOf("en") !== 0;
  function monthsLabel(m) {
    if (m < 12) {
      if (!sw) return m + (m === 1 ? " month" : " months");
      return m === 1 ? "Mwezi 1" : "Miezi " + m;
    }
    var y = Math.floor(m / 12), r = m % 12, out;
    if (!sw) {
      out = y + (y === 1 ? " year" : " years");
      if (r) out += ", " + r + (r === 1 ? " month" : " months");
      return out;
    }
    out = y === 1 ? "Mwaka 1" : "Miaka " + y;
    if (r) out += ", miezi " + r;
    return out;
  }

  function feeFor(monthly, m) {
    var gross = monthly * m;
    var net = gross * (100 - discountFor(m)) / 100;
    return Math.round(net / 100) * 100;
  }

  function kind() {
    var k = checked("pay_kind");
    return k ? k.value : "ada";
  }

  function paint() {
    var packInput = checked("package");
    if (!packInput || !moInput) return;

    var label = packInput.closest(".pay__pack");
    var monthly = parseFloat(label.getAttribute("data-monthly")) || 0;
    var isRenew = kind() === "uhuisho";

    // Sehemu za michango na za kuhuisha hazionekani kwa pamoja —
    // zikichanganyika mtu angedhani miezi inanunua muda wa uanachama.
    form.querySelectorAll("[data-kind-dues]").forEach(function (el) {
      el.hidden = isRenew;
    });
    form.querySelectorAll("[data-kind-renew]").forEach(function (el) {
      el.hidden = !isRenew;
    });

    if (isRenew) {
      var reg0 = parseFloat(label.getAttribute("data-reg")) || 0;
      form.querySelector("[data-sum-pack]").textContent = label.getAttribute("data-name");
      form.querySelector("[data-sum-period]").textContent =
        (sw ? "Miaka " : "") + TERM_YEARS + (sw ? "" : " years");
      var mo0 = form.querySelector("[data-sum-monthly]");
      if (mo0) mo0.textContent = money(monthly);
      form.querySelector("[data-sum-fee]").textContent = money(reg0);
      form.querySelector("[data-sum-reg]").textContent = money(0);
      form.querySelector("[data-sum-total]").textContent = money(reg0);
      return;
    }

    var months = clamp(moInput.value);
    var fee = feeFor(monthly, months);
    var save = discountFor(months);
    var reg = form.querySelector("input[name='include_registration']").checked
      ? parseFloat(label.getAttribute("data-reg")) || 0 : 0;

    // Kifungo cha haraka kinachoendana na miezi aliyoandika
    form.querySelectorAll("[data-mo-set]").forEach(function (b) {
      b.classList.toggle("is-on",
        parseInt(b.getAttribute("data-mo-set"), 10) === months);
    });

    var lbl = form.querySelector("[data-mo-label]");
    var prc = form.querySelector("[data-mo-price]");
    var sav = form.querySelector("[data-mo-save]");
    if (lbl) lbl.textContent = monthsLabel(months);
    if (prc) prc.textContent = money(fee);
    if (sav) {
      sav.hidden = !save;
      sav.textContent = (sw ? "Hifadhi " : "Save ") + save + "%";
    }

    form.querySelector("[data-sum-pack]").textContent = label.getAttribute("data-name");
    form.querySelector("[data-sum-period]").textContent = monthsLabel(months);
    var mo = form.querySelector("[data-sum-monthly]");
    if (mo) mo.textContent = money(monthly);
    form.querySelector("[data-sum-fee]").textContent = money(fee);
    form.querySelector("[data-sum-reg]").textContent = money(reg);
    form.querySelector("[data-sum-total]").textContent = money(fee + reg);
  }

  function setMonths(m) {
    moInput.value = clamp(m);
    paint();
  }

  function mark(name, cls) {
    form.querySelectorAll("input[name='" + name + "']").forEach(function (el) {
      var box = el.closest("." + cls);
      if (box) box.classList.toggle("is-on", el.checked);
    });
  }

  form.addEventListener("change", function (e) {
    if (e.target.name === "package") mark("package", "pay__pack");
    if (e.target.name === "provider") mark("provider", "gv__pay");
    if (e.target.name === "pay_kind") mark("pay_kind", "kind__opt");
    paint();
  });
  form.addEventListener("input", function (e) {
    if (e.target === moInput) paint();
  });
  // Namba isiyo halali inarekebishwa mtu anapotoka kwenye kisanduku,
  // si anapoandika — vinginevyo "12" ingegeuzwa "1" akiwa bado anaandika.
  form.addEventListener("blur", function (e) {
    if (e.target === moInput) setMonths(moInput.value);
  }, true);

  form.addEventListener("click", function (e) {
    var set = e.target.closest("[data-mo-set]");
    if (set) { setMonths(set.getAttribute("data-mo-set")); return; }
    if (e.target.closest("[data-mo-up]")) { setMonths(clamp(moInput.value) + 1); return; }
    if (e.target.closest("[data-mo-down]")) { setMonths(clamp(moInput.value) - 1); return; }

    // Njia za malipo zinazokuja — mweleze badala ya kumwacha akihoji.
    var soon = e.target.closest("[data-soon]");
    var msg = form.querySelector("[data-soon-msg]");
    if (!soon || !msg) return;
    msg.hidden = false;
    msg.textContent = soon.getAttribute("data-soon") + ": " +
      (msg.getAttribute("data-text") || "njia hii inakuja hivi punde.");
  });

  paint();
})();

/* ==========================================================================
   NUKUU ZINAZOTELEZA
   Hujisogeza yenyewe, lakini husimama mtu akiweka kishale au akitumia
   kibodi — nukuu ndefu zinahitaji muda wa kusoma.
   ========================================================================== */
(function () {
  "use strict";
  var root = document.querySelector("[data-verses]");
  if (!root) return;

  var slides = Array.prototype.slice.call(root.querySelectorAll(".verse"));
  var dots = Array.prototype.slice.call(root.querySelectorAll("[data-verse-go]"));
  if (slides.length < 2) return;

  var index = 0;
  var timer = null;
  var DELAY = 9000;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach(function (el, i) {
      var on = i === index;
      el.classList.toggle("is-on", on);
      if (on) { el.removeAttribute("aria-hidden"); }
      else { el.setAttribute("aria-hidden", "true"); }
    });
    dots.forEach(function (d, i) {
      d.classList.toggle("is-on", i === index);
      d.setAttribute("aria-selected", i === index ? "true" : "false");
    });
  }

  function start() {
    if (still) return;
    stop();
    timer = setInterval(function () { show(index + 1); }, DELAY);
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  /* ---- Dirisha la picha kubwa ----
     Poster ina maandishi madogo yasiyosomeka ikiwa ndani ya slaidi.
     Hapa ndipo yanaposomeka: picha kamili, skrini nzima. */
  var box = root.querySelector("[data-verse-lightbox]");
  var boxImg = root.querySelector("[data-verse-lightbox-img]");
  var opener = null;

  function openShot(btn) {
    if (!box || !boxImg) return;
    opener = btn;
    boxImg.src = btn.getAttribute("data-verse-open");
    boxImg.alt = btn.getAttribute("data-verse-alt") || "";
    box.hidden = false;
    // Ukurasa usisogee nyuma ya dirisha
    document.body.style.overflow = "hidden";
    stop();
    var close = box.querySelector("[data-verse-close]");
    if (close) close.focus();
  }

  function closeShot() {
    if (!box || box.hidden) return;
    box.hidden = true;
    document.body.style.overflow = "";
    // Rudisha umakini pale ulipotoka — muhimu kwa anayetumia kibodi
    if (opener) { opener.focus(); opener = null; }
    start();
  }

  root.addEventListener("click", function (e) {
    var shot = e.target.closest("[data-verse-open]");
    if (shot) { openShot(shot); return; }
    if (e.target.closest("[data-verse-close]")) { closeShot(); return; }
    // Kubofya nje ya picha kunafunga pia
    if (box && !box.hidden && e.target === box) { closeShot(); return; }

    var go = e.target.closest("[data-verse-go]");
    if (go) { show(parseInt(go.getAttribute("data-verse-go"), 10)); start(); return; }
    if (e.target.closest("[data-verse-next]")) { show(index + 1); start(); return; }
    if (e.target.closest("[data-verse-prev]")) { show(index - 1); start(); }
  });

  root.addEventListener("mouseenter", stop);
  root.addEventListener("mouseleave", function () { if (!box || box.hidden) start(); });
  root.addEventListener("focusin", stop);
  root.addEventListener("focusout", function () { if (!box || box.hidden) start(); });

  // Mishale ya kibodi ikiwa sehemu hii ndiyo yenye umakini
  root.addEventListener("keydown", function (e) {
    if (box && !box.hidden) {
      if (e.key === "Escape") closeShot();
      return;  // dirisha likiwa wazi, mishale isibadilishe nukuu
    }
    if (e.key === "ArrowRight") { show(index + 1); start(); }
    if (e.key === "ArrowLeft") { show(index - 1); start(); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeShot();
  });

  show(0);
  start();
})();

/* ==========================================================================
   UKANDA WA MATANGAZO
   ========================================================================== */
(function () {
  "use strict";
  var bar = document.querySelector("[data-alertbar]");
  if (!bar) return;

  var items = Array.prototype.slice.call(bar.querySelectorAll(".alertbar__item"));
  var count = bar.querySelector("[data-alert-count]");
  if (items.length < 2) return;

  var i = 0, timer = null;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function show(n) {
    i = (n + items.length) % items.length;
    items.forEach(function (el, k) {
      var on = k === i;
      el.classList.toggle("is-on", on);
      el.tabIndex = on ? 0 : -1;
      if (on) el.removeAttribute("aria-hidden");
      else el.setAttribute("aria-hidden", "true");
    });
    if (count) count.textContent = (i + 1) + "/" + items.length;
  }

  function start() { if (!still) { stop(); timer = setInterval(function () { show(i + 1); }, 6000); } }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  bar.addEventListener("mouseenter", stop);
  bar.addEventListener("mouseleave", start);
  bar.addEventListener("focusin", stop);
  bar.addEventListener("focusout", start);

  show(0);
  start();
})();

/* ==========================================================================
   SLIDESHOW YA HERO (ukurasa wa nyumbani)
   Picha tatu za MUWESTA zinazobadilishana. Zinasimama mtu akiwa ameelekeza
   mshale juu yake au akiwa ameondoka kwenye tab — hakuna sababu ya kuendesha
   animation kwa mtu asiyeitazama, na inapunguza matumizi ya betri.
   ========================================================================== */
(function () {
  "use strict";
  var hero = document.querySelector("[data-hero-slides]");
  if (!hero) return;

  var slides = hero.querySelectorAll(".hero__slide");
  var dots = hero.querySelectorAll(".hero__dot");
  if (slides.length < 2) return;

  var index = 0;
  var timer = null;
  var DELAY = 6500;

  // Anayeomba mwendo mdogo abaki na picha ya kwanza tu.
  var still = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (still.matches) return;

  function show(next) {
    index = (next + slides.length) % slides.length;
    Array.prototype.forEach.call(slides, function (el, i) {
      // Kuondoa na kurudisha darasa kunaanzisha upya animation ya kusogea.
      el.classList.remove("is-on");
      if (i === index) {
        void el.offsetWidth;
        el.classList.add("is-on");
      }
    });
    Array.prototype.forEach.call(dots, function (d, i) {
      d.classList.toggle("is-on", i === index);
    });
  }

  function play() { stop(); timer = setInterval(function () { show(index + 1); }, DELAY); }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  Array.prototype.forEach.call(dots, function (d) {
    d.addEventListener("click", function () {
      show(parseInt(d.getAttribute("data-slide"), 10) || 0);
      play();   // anza upya kuhesabu ili picha aliyoichagua ikae muda kamili
    });
  });

  hero.addEventListener("mouseenter", stop);
  hero.addEventListener("mouseleave", play);
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else play();
  });

  play();
})();

/* ==========================================================================
   KUSUBIRI MALIPO YA SIMU (Selcom)
   Ukurasa unauliza hali kila sekunde 4. Ukikamilika, unampeleka mtu
   kwenye risiti yake. Kuuliza kunasimama baada ya dakika 3 — kidokezo
   cha Selcom chenyewe huisha, kwa hiyo kuendelea kuuliza ni bure.
   ========================================================================== */
(function () {
  "use strict";
  var box = document.querySelector("[data-wait]");
  if (!box) return;

  var msg = box.querySelector("[data-wait-msg]");
  var retry = box.querySelector("[data-wait-retry]");
  var url = box.getAttribute("data-url");
  var done = box.getAttribute("data-done");

  var EVERY = 4000;
  var GIVE_UP = 3 * 60 * 1000;
  var RETRY_AFTER = 45000;
  var started = Date.now();
  var timer = null;

  // Kitufe cha "jaribu tena" kinaonekana baada ya sekunde 45 tu, ili mtu
  // asikibofye mapema na kuanzisha malipo mawili kwa mchango mmoja.
  setTimeout(function () { if (retry) retry.hidden = false; }, RETRY_AFTER);

  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  function check() {
    if (Date.now() - started > GIVE_UP) {
      stop();
      if (msg) {
        msg.classList.add("is-fail");
        msg.textContent = "Muda umeisha. Kama umelipa, risiti yako itathibitishwa hivi punde.";
      }
      return;
    }

    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.status === "confirmed") {
          stop();
          if (msg) msg.textContent = "Malipo yamekamilika. Tunakupeleka kwenye risiti...";
          window.location.href = done;
        } else if (data.status === "failed" || data.status === "cancelled") {
          stop();
          if (msg) {
            msg.classList.add("is-fail");
            msg.textContent = "Malipo hayakukamilika. Unaweza kujaribu tena.";
          }
          if (retry) retry.hidden = false;
        }
      })
      .catch(function () { /* mtandao umekatika — jaribio lijalo litaendelea */ });
  }

  timer = setInterval(check, EVERY);
  // Mtu akirudi kwenye tab baada ya kulipa, tusimsubirishe mzunguko mzima.
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden && timer) check();
  });
})();
