#!/usr/bin/env python3
"""Build the themed proof-of-work pages into docs/.

Each theme is a standalone HTML file that fetches docs/data.json and renders it.
Markup + JS are shared here (single source of truth); only the <style> block and
loaded fonts differ per theme. Run: python3 build_site.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
USERNAME = "disha1202"

# (filename, key, label) — index.html is the default (techno).
THEMES = [
    ("index.html",        "techno", "techno"),
    ("index-pixels.html", "pixels", "pixels"),
    ("index-modern.html", "modern", "modern"),
    ("index-retro.html",  "retro",  "retro"),
]


def nav_html(current_key):
    links = []
    for fname, key, label in THEMES:
        cls = ' class="current"' if key == current_key else ""
        links.append(f'    <a href="{fname}"{cls}>{label}</a>')
    return "\n".join(links)


# Shared body markup. Class names are identical across themes so the JS works everywhere.
BODY = """<body>
<main>
  <nav class="switch">
{nav}
  </nav>

  <header class="head">
    <h1 class="title">proof of work</h1>
    <p class="subtitle">a collection of open-source contributions <span class="dot">·</span> <b id="user">{username}</b></p>
  </header>

  <div class="stats" id="stats">
    <div class="stat"><span class="v">—</span><span class="l">loading</span></div>
  </div>

  <div class="filters" id="filters" hidden>
    <button data-filter="all" class="active">All</button>
    <button data-filter="merged">Merged</button>
    <button data-filter="open">Open</button>
    <button data-filter="closed">Closed</button>
  </div>

  <div id="list"></div>

  <footer>
    <span id="generated">&nbsp;</span>
    <span>
      <a href="https://github.com/{username}" target="_blank" rel="noopener">github.com/{username}</a>
      &nbsp;·&nbsp;
      <a href="https://github.com/{username}/proof-of-work" target="_blank" rel="noopener">source</a>
    </span>
  </footer>
</main>

<script>
  const STATE_LABEL = { "Merged":"merged","Merged (indirect)":"merged","Open":"open","Closed":"closed" };
  let currentFilter = "all";
  let data = null;

  function render() {
    const list = document.getElementById("list");
    list.innerHTML = "";
    const orgs = data.orgs.map(org => {
      const visible = org.prs.filter(pr => currentFilter === "all" || STATE_LABEL[pr.state] === currentFilter);
      return { ...org, visible };
    }).filter(org => org.visible.length > 0);

    if (orgs.length === 0) {
      list.innerHTML = '<div class="empty">No entries match this filter.</div>';
      return;
    }

    orgs.forEach(org => {
      const card = document.createElement("div");
      card.className = "org";
      const header = document.createElement("div");
      header.className = "org-header";
      header.innerHTML = `
        <span class="chev">&#9654;</span>
        <img class="org-logo" alt="" src="https://github.com/${org.name}.png?size=64" onerror="this.style.visibility='hidden'">
        <span class="org-name">${escapeHtml(org.name)}</span>
        <span class="org-meta"><b>${org.visible.length}</b> ${org.visible.length === 1 ? "PR" : "PRs"}<span class="pill">${org.merged} merged</span></span>
      `;
      const prs = document.createElement("div");
      prs.className = "prs";
      org.visible.forEach(pr => {
        const row = document.createElement("div");
        row.className = "pr";
        const label = STATE_LABEL[pr.state] || "open";
        const date = pr.merged_at || pr.created_at;
        const display = label === "merged" && pr.state.includes("indirect") ? "merged*" : label;
        row.innerHTML = `
          <span class="pr-status ${label}">${display}</span>
          <span class="pr-title">${pr.number ? `<span class="pr-num">#${pr.number}</span>` : ""}<a href="${pr.url}" target="_blank" rel="noopener">${escapeHtml(pr.title)}</a></span>
          <span class="pr-date">${date || ""}</span>
        `;
        prs.appendChild(row);
      });
      header.onclick = () => card.classList.toggle("open");
      card.appendChild(header);
      card.appendChild(prs);
      list.appendChild(card);
    });
  }

  function renderStats() {
    const s = data.totals;
    document.getElementById("stats").innerHTML = `
      <div class="stat"><span class="v">${s.prs}</span><span class="l">total</span></div>
      <div class="stat merged"><span class="v">${s.merged}</span><span class="l">merged</span></div>
      <div class="stat open"><span class="v">${s.open}</span><span class="l">open</span></div>
      <div class="stat closed"><span class="v">${s.closed}</span><span class="l">closed</span></div>
      <div class="stat"><span class="v">${data.orgs.length}</span><span class="l">orgs</span></div>
    `;
    if (data.generated_at) document.getElementById("generated").textContent = "Generated " + data.generated_at;
    if (data.username) document.getElementById("user").textContent = data.username;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
  }

  document.querySelectorAll("#filters button").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#filters button").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      render();
    });
  });

  fetch("./data.json", { cache: "no-store" })
    .then(r => { if (!r.ok) throw new Error("data.json not found"); return r.json(); })
    .then(json => { data = json; document.getElementById("filters").hidden = false; renderStats(); render(); })
    .catch(err => {
      document.getElementById("stats").innerHTML =
        `<div class="empty">Failed to load data.json — ${escapeHtml(err.message)}</div>`;
    });
</script>
</body>
</html>"""


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{username} · proof of work</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
  <style>
{css}
  </style>
</head>
{body}"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: TECHNO — neon cyberpunk, dark, glow, grid, monospace/display
# ─────────────────────────────────────────────────────────────────────────────
TECHNO_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">"""
TECHNO_CSS = """    :root {
      --bg: #05070d;
      --bg-2: #0b1120;
      --paper: #0d1424;
      --ink: #d7f5ff;
      --ink-soft: #7fa6c4;
      --ink-faint: #4d6b85;
      --line: #14304a;
      --accent: #00f0ff;
      --accent-2: #ff2bd6;
      --merged: #39ff14;
      --open: #ffd23f;
      --closed: #ff5470;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      background-image:
        linear-gradient(rgba(0,240,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,240,255,0.045) 1px, transparent 1px),
        radial-gradient(ellipse 800px 500px at 15% -10%, rgba(0,240,255,0.14), transparent 70%),
        radial-gradient(ellipse 700px 400px at 100% 10%, rgba(255,43,214,0.12), transparent 70%);
      background-size: 42px 42px, 42px 42px, 100% 100%, 100% 100%;
      background-attachment: fixed;
    }
    main { max-width: 920px; margin: 0 auto; padding: 60px 24px 96px; }

    .switch { display: flex; gap: 8px; margin-bottom: 40px; flex-wrap: wrap; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; }
    .switch a {
      color: var(--ink-soft); text-decoration: none; padding: 6px 14px;
      border: 1px solid var(--line); background: rgba(13,20,36,0.6);
      font-family: 'Share Tech Mono', monospace; transition: all 0.15s;
      clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
    }
    .switch a:hover { color: var(--accent); border-color: var(--accent); box-shadow: 0 0 12px rgba(0,240,255,0.4); }
    .switch a.current { color: var(--bg); background: var(--accent); border-color: var(--accent); box-shadow: 0 0 18px rgba(0,240,255,0.6); }

    .title {
      font-family: 'Orbitron', sans-serif; font-weight: 900;
      font-size: clamp(2.6rem, 8vw, 4.4rem); letter-spacing: 0.04em; line-height: 1;
      margin: 0 0 10px; text-transform: uppercase; color: #fff;
      text-shadow: 0 0 8px rgba(0,240,255,0.8), 0 0 28px rgba(0,240,255,0.5), 3px 3px 0 rgba(255,43,214,0.55);
    }
    .subtitle { margin: 0 0 34px; color: var(--ink-soft); font-size: 0.95rem; letter-spacing: 0.02em; }
    .subtitle b { color: var(--accent); font-weight: 700; }
    .subtitle .dot { color: var(--accent-2); margin: 0 6px; }

    .stats {
      display: flex; flex-wrap: wrap; gap: 28px; padding: 22px 26px; margin-bottom: 28px;
      background: linear-gradient(135deg, rgba(13,20,36,0.9), rgba(11,17,32,0.9));
      border: 1px solid var(--accent); border-radius: 4px;
      box-shadow: 0 0 22px rgba(0,240,255,0.18), inset 0 0 30px rgba(0,240,255,0.05);
    }
    .stat { display: flex; flex-direction: column; gap: 4px; }
    .stat .v { font-family: 'Orbitron', sans-serif; font-size: 1.7rem; font-weight: 700; line-height: 1; color: var(--accent); text-shadow: 0 0 10px rgba(0,240,255,0.5); }
    .stat .l { font-size: 0.66rem; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.12em; }
    .stat.merged .v { color: var(--merged); text-shadow: 0 0 10px rgba(57,255,20,0.5); }
    .stat.open .v { color: var(--open); text-shadow: 0 0 10px rgba(255,210,63,0.5); }
    .stat.closed .v { color: var(--closed); text-shadow: 0 0 10px rgba(255,84,112,0.5); }

    .filters { display: flex; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }
    .filters button {
      background: rgba(13,20,36,0.6); color: var(--ink-soft); border: 1px solid var(--line);
      padding: 8px 18px; font-family: 'Share Tech Mono', monospace; font-size: 0.82rem;
      cursor: pointer; border-radius: 2px; text-transform: uppercase; letter-spacing: 0.08em; transition: all 0.15s;
    }
    .filters button:hover { color: var(--accent); border-color: var(--accent); box-shadow: 0 0 10px rgba(0,240,255,0.35); }
    .filters button.active { color: var(--bg); background: var(--accent); border-color: var(--accent); box-shadow: 0 0 14px rgba(0,240,255,0.5); }

    .org {
      border: 1px solid var(--line); background: rgba(13,20,36,0.55); border-radius: 4px;
      margin-bottom: 12px; overflow: hidden; transition: all 0.2s;
    }
    .org:hover { border-color: var(--accent); box-shadow: 0 0 18px rgba(0,240,255,0.22); }
    .org.open { border-color: var(--accent); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 16px 20px; cursor: pointer; user-select: none; }
    .org-header:hover { background: rgba(0,240,255,0.05); }
    .chev { color: var(--accent); font-size: 0.8rem; transition: transform 0.2s; width: 14px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 30px; height: 30px; border-radius: 3px; object-fit: cover; background: var(--bg-2); border: 1px solid var(--line); filter: saturate(1.2); }
    .org-name { flex: 1; font-family: 'Orbitron', sans-serif; font-weight: 700; font-size: 1.02rem; color: var(--ink); letter-spacing: 0.02em; }
    .org-meta { font-size: 0.8rem; color: var(--ink-soft); font-family: 'Share Tech Mono', monospace; }
    .org-meta b { color: var(--accent); }
    .org-meta .pill { display: inline-block; padding: 2px 10px; border-radius: 2px; background: rgba(57,255,20,0.12); color: var(--merged); margin-left: 8px; font-size: 0.72rem; border: 1px solid rgba(57,255,20,0.3); }

    .prs { display: none; border-top: 1px solid var(--line); background: rgba(5,7,13,0.5); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 88px 1fr auto; gap: 16px; align-items: baseline; padding: 12px 20px 12px 50px; font-size: 0.88rem; border-bottom: 1px solid var(--line); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-size: 0.64rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 8px; border-radius: 2px; text-align: center; }
    .pr-status.merged { background: rgba(57,255,20,0.12); color: var(--merged); border: 1px solid rgba(57,255,20,0.35); }
    .pr-status.open { background: rgba(255,210,63,0.12); color: var(--open); border: 1px solid rgba(255,210,63,0.35); }
    .pr-status.closed { background: rgba(255,84,112,0.12); color: var(--closed); border: 1px solid rgba(255,84,112,0.35); }
    .pr-title a { color: var(--ink); text-decoration: none; transition: color 0.15s; }
    .pr-title a:hover { color: var(--accent); text-shadow: 0 0 8px rgba(0,240,255,0.5); }
    .pr-num { color: var(--accent-2); margin-right: 6px; font-size: 0.82rem; }
    .pr-date { color: var(--ink-faint); font-size: 0.76rem; white-space: nowrap; font-family: 'Share Tech Mono', monospace; }

    .empty { color: var(--ink-faint); padding: 16px; font-family: 'Share Tech Mono', monospace; }
    footer { margin-top: 56px; padding-top: 22px; border-top: 1px solid var(--line); color: var(--ink-faint); font-size: 0.78rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; font-family: 'Share Tech Mono', monospace; }
    footer a { color: var(--ink-soft); text-decoration: none; border-bottom: 1px solid var(--line); }
    footer a:hover { color: var(--accent); border-bottom-color: var(--accent); }
    @media (max-width: 600px) { main { padding: 32px 18px 64px; } .pr { grid-template-columns: 78px 1fr; padding-left: 26px; } .pr-date { grid-column: 2; } }"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: PIXELS — 8-bit retro game, hard edges, pixel font, stepped shadows
# ─────────────────────────────────────────────────────────────────────────────
PIXELS_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">"""
PIXELS_CSS = """    :root {
      --bg: #1a1c2c;
      --bg-2: #29366f;
      --paper: #262b44;
      --ink: #f4f4f4;
      --ink-soft: #a7b7d6;
      --ink-faint: #6c7ba5;
      --line: #3b5dc9;
      --accent: #ffcd75;
      --accent-2: #ef7d57;
      --merged: #38b764;
      --open: #ffcd75;
      --closed: #b13e53;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'VT323', ui-monospace, monospace; font-size: 20px;
      background-image:
        linear-gradient(rgba(59,93,201,0.10) 2px, transparent 2px),
        linear-gradient(90deg, rgba(59,93,201,0.10) 2px, transparent 2px);
      background-size: 32px 32px; background-attachment: fixed;
      image-rendering: pixelated;
    }
    .pixel { font-family: 'Press Start 2P', monospace; }
    main { max-width: 900px; margin: 0 auto; padding: 56px 24px 96px; }

    .switch { display: flex; gap: 10px; margin-bottom: 40px; flex-wrap: wrap; }
    .switch a {
      font-family: 'Press Start 2P', monospace; font-size: 0.6rem;
      color: var(--ink); text-decoration: none; padding: 10px 12px;
      background: var(--paper); border: none; box-shadow: 0 4px 0 #11131f, inset 0 0 0 3px var(--line);
      transition: transform 0.08s, box-shadow 0.08s;
    }
    .switch a:hover { color: var(--accent); transform: translateY(2px); box-shadow: 0 2px 0 #11131f, inset 0 0 0 3px var(--accent); }
    .switch a.current { color: var(--bg); background: var(--accent); box-shadow: 0 4px 0 #b8791f, inset 0 0 0 3px var(--bg); }

    .title { font-family: 'Press Start 2P', monospace; font-size: clamp(1.4rem, 5vw, 2.6rem); line-height: 1.3; margin: 0 0 18px; color: var(--accent); text-shadow: 4px 4px 0 var(--accent-2), 8px 8px 0 #11131f; }
    .subtitle { margin: 0 0 34px; color: var(--ink-soft); font-size: 1.25rem; }
    .subtitle b { color: var(--accent); }
    .subtitle .dot { color: var(--accent-2); margin: 0 6px; }

    .stats { display: flex; flex-wrap: wrap; gap: 20px; padding: 22px 24px; margin-bottom: 28px; background: var(--paper); box-shadow: 0 6px 0 #11131f, inset 0 0 0 4px var(--line); }
    .stat { display: flex; flex-direction: column; gap: 4px; }
    .stat .v { font-family: 'Press Start 2P', monospace; font-size: 1.2rem; line-height: 1.1; color: var(--accent); }
    .stat .l { font-size: 1rem; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.06em; }
    .stat.merged .v { color: var(--merged); }
    .stat.open .v { color: var(--open); }
    .stat.closed .v { color: var(--closed); }

    .filters { display: flex; gap: 12px; margin-bottom: 22px; flex-wrap: wrap; }
    .filters button {
      font-family: 'Press Start 2P', monospace; font-size: 0.62rem; color: var(--ink);
      background: var(--paper); border: none; padding: 12px 16px; cursor: pointer;
      box-shadow: 0 4px 0 #11131f, inset 0 0 0 3px var(--line); transition: transform 0.08s, box-shadow 0.08s;
    }
    .filters button:hover { color: var(--accent); transform: translateY(2px); box-shadow: 0 2px 0 #11131f, inset 0 0 0 3px var(--accent); }
    .filters button.active { color: var(--bg); background: var(--accent); box-shadow: 0 4px 0 #b8791f, inset 0 0 0 3px var(--bg); }

    .org { background: var(--paper); margin-bottom: 16px; box-shadow: 0 5px 0 #11131f, inset 0 0 0 4px var(--line); }
    .org.open { box-shadow: 0 5px 0 #11131f, inset 0 0 0 4px var(--accent); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 16px 18px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg-2); }
    .chev { color: var(--accent); font-family: 'Press Start 2P', monospace; font-size: 0.7rem; transition: transform 0.15s; width: 16px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 32px; height: 32px; object-fit: cover; background: var(--bg-2); box-shadow: inset 0 0 0 3px var(--line); image-rendering: pixelated; }
    .org-name { flex: 1; font-family: 'Press Start 2P', monospace; font-size: 0.78rem; color: var(--ink); }
    .org-meta { font-size: 1.05rem; color: var(--ink-soft); }
    .org-meta b { color: var(--accent); }
    .org-meta .pill { display: inline-block; padding: 3px 10px; background: var(--merged); color: var(--bg); margin-left: 8px; font-size: 0.9rem; box-shadow: 0 3px 0 #1c5a33; }

    .prs { display: none; border-top: 4px solid var(--line); background: var(--bg); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 96px 1fr auto; gap: 16px; align-items: baseline; padding: 12px 18px 12px 44px; font-size: 1.1rem; border-bottom: 2px solid var(--paper); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-family: 'Press Start 2P', monospace; font-size: 0.5rem; text-transform: uppercase; padding: 6px 6px; text-align: center; color: var(--bg); }
    .pr-status.merged { background: var(--merged); box-shadow: 0 3px 0 #1c5a33; }
    .pr-status.open { background: var(--open); box-shadow: 0 3px 0 #b8791f; }
    .pr-status.closed { background: var(--closed); box-shadow: 0 3px 0 #6e2333; color: var(--ink); }
    .pr-title a { color: var(--ink); text-decoration: none; }
    .pr-title a:hover { color: var(--accent); }
    .pr-num { color: var(--accent-2); margin-right: 6px; }
    .pr-date { color: var(--ink-faint); font-size: 0.95rem; white-space: nowrap; }

    .empty { color: var(--ink-faint); padding: 16px; font-size: 1.1rem; }
    footer { margin-top: 56px; padding-top: 22px; border-top: 4px solid var(--line); color: var(--ink-faint); font-size: 1rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    footer a { color: var(--ink-soft); text-decoration: none; }
    footer a:hover { color: var(--accent); }
    @media (max-width: 600px) { main { padding: 32px 16px 64px; } .pr { grid-template-columns: 84px 1fr; padding-left: 24px; } .pr-date { grid-column: 2; } }"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: MODERN — clean, light, minimal, generous whitespace, single accent
# ─────────────────────────────────────────────────────────────────────────────
MODERN_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">"""
MODERN_CSS = """    :root {
      --bg: #fbfbfd;
      --bg-2: #f2f3f7;
      --paper: #ffffff;
      --ink: #0f172a;
      --ink-soft: #475569;
      --ink-faint: #94a3b8;
      --line: #e7e9ef;
      --accent: #4f46e5;
      --accent-soft: #eef2ff;
      --merged: #059669;
      --open: #d97706;
      --closed: #e11d48;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body { font-family: Inter, ui-sans-serif, system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
    .mono { font-family: 'JetBrains Mono', ui-monospace, monospace; }
    main { max-width: 860px; margin: 0 auto; padding: 72px 24px 110px; }

    .switch { display: flex; gap: 4px; margin-bottom: 48px; flex-wrap: wrap; font-size: 0.82rem; background: var(--bg-2); padding: 4px; border-radius: 12px; width: fit-content; }
    .switch a { color: var(--ink-soft); text-decoration: none; padding: 7px 16px; border-radius: 8px; font-weight: 500; transition: all 0.15s; }
    .switch a:hover { color: var(--ink); }
    .switch a.current { color: var(--accent); background: var(--paper); box-shadow: 0 1px 3px rgba(15,23,42,0.08); }

    .title { font-weight: 800; font-size: clamp(2.6rem, 7vw, 4rem); letter-spacing: -0.035em; line-height: 1.02; margin: 0 0 12px; color: var(--ink); }
    .subtitle { margin: 0 0 40px; color: var(--ink-soft); font-size: 1.08rem; line-height: 1.5; }
    .subtitle b { color: var(--ink); font-weight: 600; }
    .subtitle .dot { color: var(--ink-faint); margin: 0 8px; }

    .stats { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 40px; }
    .stat { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 120px; padding: 18px 20px; background: var(--paper); border: 1px solid var(--line); border-radius: 16px; }
    .stat .v { font-size: 1.8rem; font-weight: 700; line-height: 1; letter-spacing: -0.02em; }
    .stat .l { font-size: 0.76rem; color: var(--ink-faint); font-weight: 500; text-transform: capitalize; letter-spacing: 0.01em; }
    .stat.merged .v { color: var(--merged); }
    .stat.open .v { color: var(--open); }
    .stat.closed .v { color: var(--closed); }

    .filters { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
    .filters button { background: var(--paper); color: var(--ink-soft); border: 1px solid var(--line); padding: 8px 18px; font-family: inherit; font-size: 0.88rem; font-weight: 500; cursor: pointer; border-radius: 999px; transition: all 0.15s; }
    .filters button:hover { border-color: var(--ink-faint); color: var(--ink); }
    .filters button.active { color: #fff; background: var(--accent); border-color: var(--accent); }

    .org { border: 1px solid var(--line); background: var(--paper); border-radius: 18px; margin-bottom: 12px; overflow: hidden; transition: all 0.2s; }
    .org:hover { border-color: #d7dae4; box-shadow: 0 10px 30px rgba(15,23,42,0.06); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 18px 22px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg); }
    .chev { color: var(--ink-faint); font-size: 0.8rem; transition: transform 0.2s; width: 14px; }
    .org.open .chev { transform: rotate(90deg); color: var(--accent); }
    .org-logo { width: 32px; height: 32px; border-radius: 8px; object-fit: cover; background: var(--bg-2); border: 1px solid var(--line); }
    .org-name { flex: 1; font-weight: 700; font-size: 1.08rem; color: var(--ink); letter-spacing: -0.01em; }
    .org-meta { font-size: 0.86rem; color: var(--ink-soft); }
    .org-meta b { color: var(--ink); font-weight: 600; }
    .org-meta .pill { display: inline-block; padding: 3px 10px; border-radius: 999px; background: #ecfdf5; color: var(--merged); margin-left: 8px; font-size: 0.76rem; font-weight: 600; }

    .prs { display: none; border-top: 1px solid var(--line); background: var(--bg); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 84px 1fr auto; gap: 16px; align-items: baseline; padding: 14px 22px 14px 52px; font-size: 0.94rem; border-bottom: 1px solid var(--line); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-size: 0.7rem; font-weight: 600; text-transform: capitalize; padding: 4px 10px; border-radius: 999px; text-align: center; }
    .pr-status.merged { background: #ecfdf5; color: var(--merged); }
    .pr-status.open { background: #fffbeb; color: var(--open); }
    .pr-status.closed { background: #fff1f2; color: var(--closed); }
    .pr-title a { color: var(--ink); text-decoration: none; font-weight: 500; transition: color 0.15s; }
    .pr-title a:hover { color: var(--accent); }
    .pr-num { font-family: 'JetBrains Mono', monospace; color: var(--ink-faint); margin-right: 6px; font-size: 0.82rem; }
    .pr-date { font-family: 'JetBrains Mono', monospace; color: var(--ink-faint); font-size: 0.78rem; white-space: nowrap; }

    .empty { color: var(--ink-faint); padding: 16px; }
    footer { margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--line); color: var(--ink-faint); font-size: 0.84rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    footer a { color: var(--ink-soft); text-decoration: none; }
    footer a:hover { color: var(--accent); }
    @media (max-width: 600px) { main { padding: 40px 18px 72px; } .pr { grid-template-columns: 74px 1fr; padding-left: 28px; } .pr-date { grid-column: 2; } }"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: RETRO — 70s vintage, warm cream/orange/avocado, groovy serif
# ─────────────────────────────────────────────────────────────────────────────
RETRO_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Space+Grotesk:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">"""
RETRO_CSS = """    :root {
      --bg: #f2e4c9;
      --bg-2: #e8d5ad;
      --paper: #fbf3df;
      --ink: #3a2718;
      --ink-soft: #6b4f34;
      --ink-faint: #9c7c56;
      --line: #d8c199;
      --accent: #d1622a;
      --accent-2: #7a8b3c;
      --merged: #5e7d2a;
      --open: #cf9526;
      --closed: #b5462f;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
      background-image:
        radial-gradient(circle at 20% -5%, rgba(209,98,42,0.20), transparent 45%),
        radial-gradient(circle at 90% 8%, rgba(122,139,60,0.18), transparent 42%),
        repeating-linear-gradient(45deg, rgba(154,124,86,0.05) 0 2px, transparent 2px 8px);
      background-attachment: fixed;
    }
    .serif { font-family: 'DM Serif Display', Georgia, serif; }
    main { max-width: 900px; margin: 0 auto; padding: 60px 24px 96px; }

    .switch { display: flex; gap: 8px; margin-bottom: 40px; flex-wrap: wrap; font-size: 0.82rem; }
    .switch a { color: var(--ink-soft); text-decoration: none; padding: 7px 16px; border: 2px solid var(--ink); border-radius: 999px; background: var(--paper); font-weight: 500; box-shadow: 3px 3px 0 var(--ink); transition: all 0.12s; }
    .switch a:hover { color: var(--accent); transform: translate(-1px,-1px); box-shadow: 4px 4px 0 var(--ink); }
    .switch a.current { color: var(--paper); background: var(--accent); border-color: var(--ink); }

    .title { font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; font-style: italic; font-size: clamp(3rem, 9vw, 5rem); letter-spacing: -0.01em; line-height: 0.95; margin: 0 0 12px; color: var(--accent); text-shadow: 3px 3px 0 var(--bg-2); }
    .subtitle { margin: 0 0 36px; color: var(--ink-soft); font-size: 1.05rem; }
    .subtitle b { color: var(--ink); font-weight: 600; }
    .subtitle .dot { color: var(--accent); margin: 0 6px; }

    .stats { display: flex; flex-wrap: wrap; gap: 28px; padding: 22px 26px; margin-bottom: 28px; background: var(--paper); border: 2px solid var(--ink); border-radius: 22px; box-shadow: 5px 5px 0 var(--ink); }
    .stat { display: flex; flex-direction: column; gap: 3px; }
    .stat .v { font-family: 'DM Serif Display', Georgia, serif; font-size: 2rem; line-height: 1; color: var(--ink); }
    .stat .l { font-size: 0.72rem; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.1em; }
    .stat.merged .v { color: var(--merged); }
    .stat.open .v { color: var(--open); }
    .stat.closed .v { color: var(--closed); }

    .filters { display: flex; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }
    .filters button { background: var(--paper); color: var(--ink-soft); border: 2px solid var(--ink); padding: 8px 18px; font-family: inherit; font-size: 0.86rem; font-weight: 600; cursor: pointer; border-radius: 999px; box-shadow: 3px 3px 0 var(--ink); transition: all 0.12s; }
    .filters button:hover { color: var(--accent); transform: translate(-1px,-1px); box-shadow: 4px 4px 0 var(--ink); }
    .filters button.active { color: var(--paper); background: var(--accent); }

    .org { border: 2px solid var(--ink); background: var(--paper); border-radius: 18px; margin-bottom: 16px; overflow: hidden; box-shadow: 4px 4px 0 var(--ink); transition: all 0.15s; }
    .org:hover { transform: translate(-1px,-1px); box-shadow: 6px 6px 0 var(--ink); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 16px 20px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg-2); }
    .chev { color: var(--accent); font-size: 0.85rem; transition: transform 0.2s; width: 14px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; background: var(--bg-2); border: 2px solid var(--ink); }
    .org-name { flex: 1; font-family: 'DM Serif Display', Georgia, serif; font-size: 1.3rem; color: var(--ink); }
    .org-meta { font-size: 0.86rem; color: var(--ink-soft); font-family: 'DM Mono', monospace; }
    .org-meta b { color: var(--ink); font-weight: 500; }
    .org-meta .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; background: var(--accent-2); color: var(--paper); margin-left: 8px; font-size: 0.74rem; }

    .prs { display: none; border-top: 2px solid var(--ink); background: var(--bg); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 84px 1fr auto; gap: 16px; align-items: baseline; padding: 12px 20px 12px 50px; font-size: 0.94rem; border-bottom: 1px solid var(--line); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-size: 0.66rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; padding: 4px 10px; border-radius: 999px; text-align: center; color: var(--paper); }
    .pr-status.merged { background: var(--merged); }
    .pr-status.open { background: var(--open); }
    .pr-status.closed { background: var(--closed); }
    .pr-title a { color: var(--ink); text-decoration: none; transition: color 0.15s; }
    .pr-title a:hover { color: var(--accent); }
    .pr-num { font-family: 'DM Mono', monospace; color: var(--ink-faint); margin-right: 6px; font-size: 0.82rem; }
    .pr-date { font-family: 'DM Mono', monospace; color: var(--ink-faint); font-size: 0.78rem; white-space: nowrap; }

    .empty { color: var(--ink-faint); padding: 16px; }
    footer { margin-top: 56px; padding-top: 22px; border-top: 2px solid var(--ink); color: var(--ink-faint); font-size: 0.84rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; font-family: 'DM Mono', monospace; }
    footer a { color: var(--ink-soft); text-decoration: none; border-bottom: 2px solid var(--line); }
    footer a:hover { color: var(--accent); border-bottom-color: var(--accent); }
    @media (max-width: 600px) { main { padding: 36px 18px 64px; } .pr { grid-template-columns: 74px 1fr; padding-left: 26px; } .pr-date { grid-column: 2; } }"""


STYLES = {
    "techno": (TECHNO_FONTS, TECHNO_CSS),
    "pixels": (PIXELS_FONTS, PIXELS_CSS),
    "modern": (MODERN_FONTS, MODERN_CSS),
    "retro":  (RETRO_FONTS,  RETRO_CSS),
}


def build():
    os.makedirs(DOCS, exist_ok=True)
    for fname, key, label in THEMES:
        fonts, css = STYLES[key]
        body = BODY.replace("{nav}", nav_html(key)).replace("{username}", USERNAME)
        html = (PAGE.replace("{username}", USERNAME)
                    .replace("{fonts}", fonts)
                    .replace("{css}", css)
                    .replace("{body}", body))
        path = os.path.join(DOCS, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"wrote {path}  ({key})")


if __name__ == "__main__":
    build()
