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

# (filename, key, label) — index.html is the default theme.
# CSS for techno/pixels/modern is retained below (STYLES) but unused; to re-add a
# theme, just add its row back here.
THEMES = [
    ("index.html",       "notebook", "notebook"),
    ("index-comic.html", "comic",    "comic"),
    ("index-retro.html", "retro",    "retro"),
    ("index-news.html",  "news",     "newspaper"),
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

  <section class="bento" id="bento">
    <a class="tile tile-avatar" id="avatarLink" target="_blank" rel="noopener" title="View GitHub profile">
      <img class="avatar" id="avatar" alt="">
    </a>

    <div class="tile tile-head">
      <span class="eyebrow">proof of work</span>
      <h1 class="pname" id="name">{username}</h1>
      <p class="pbio" id="bio"></p>
      <p class="pmeta" id="pmeta"></p>
    </div>

    <div class="tile tile-lang">
      <span class="tile-label">top languages</span>
      <div class="langbar" id="langbar"></div>
      <div class="langlegend" id="langlegend"></div>
    </div>

    <a class="tile tile-social sc-github"   id="l-github"   target="_blank" rel="noopener"><span class="sc-go">&#8599;</span><span class="sc-name">GitHub</span></a>
    <a class="tile tile-social sc-linkedin" id="l-linkedin" target="_blank" rel="noopener"><span class="sc-go">&#8599;</span><span class="sc-name">LinkedIn</span></a>
    <a class="tile tile-social sc-twitter"  id="l-twitter"  target="_blank" rel="noopener"><span class="sc-go">&#8599;</span><span class="sc-name">Twitter</span></a>
    <a class="tile tile-social sc-email"    id="l-email"><span class="sc-go">&#8599;</span><span class="sc-name">Email</span></a>

    <div class="tile num n-prs"><span class="v" id="s-prs">—</span><span class="l">pull requests</span></div>
    <div class="tile num n-merged merged"><span class="v" id="s-merged">—</span><span class="l">merged</span></div>
    <div class="tile num n-issues"><span class="v" id="s-issues">—</span><span class="l">issues opened</span></div>
    <div class="tile num n-orgs"><span class="v" id="s-orgs">—</span><span class="l">organizations</span></div>
    <div class="tile num n-followers"><span class="v" id="s-followers">—</span><span class="l">followers</span></div>
    <div class="tile num n-following"><span class="v" id="s-following">—</span><span class="l">following</span></div>
    <div class="tile num n-repos"><span class="v" id="s-repos">—</span><span class="l">public repos</span></div>
    <div class="tile num n-stars"><span class="v" id="s-stars">—</span><span class="l">stars earned</span></div>
  </section>

  <div class="seg" id="seg" hidden>
    <button data-mode="prs" class="active">Pull Requests</button>
    <button data-mode="issues">Issues</button>
  </div>

  <div class="filters" id="filters" hidden></div>

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
  const LANG_COLORS = { Java:"#b07219", Vue:"#41b883", TypeScript:"#3178c6", JavaScript:"#f1e05a", HTML:"#e34c26", CSS:"#563d7c", Python:"#3572A5", Shell:"#89e051", "C++":"#f34b7d", C:"#555555", Go:"#00ADD8", Ruby:"#701516", Dockerfile:"#384d54", Makefile:"#427819", SCSS:"#c6538c", Kotlin:"#A97BFF" };
  const FILTERS = { prs: [["all","All"],["merged","Merged"],["open","Open"],["closed","Closed"]], issues: [["all","All"],["open","Open"],["closed","Closed"]] };
  let mode = "prs", currentFilter = "all", data = null;

  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c])); }

  function renderProfile(){
    const p = data.profile || {};
    if (p.avatar) document.getElementById("avatar").src = p.avatar;
    if (p.github) document.getElementById("avatarLink").href = p.github;
    document.getElementById("name").textContent = p.name || data.username;
    document.getElementById("bio").textContent = p.bio || "";
    document.getElementById("pmeta").textContent = [p.company, p.location].filter(Boolean).join("  ·  ");
    const soc = {
      "l-github":   p.github,
      "l-linkedin": p.linkedin,
      "l-twitter":  p.twitter ? "https://twitter.com/" + p.twitter : null,
      "l-email":    p.email ? "mailto:" + p.email : null,
    };
    Object.entries(soc).forEach(([id, href]) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (href) el.href = href; else el.style.display = "none";
    });
  }

  function renderLanguages(){
    const langs = data.languages || [];
    document.getElementById("langbar").innerHTML = langs.map(l =>
      `<span class="langseg" style="width:${l.pct}%;background:${LANG_COLORS[l.name]||'#888'}" title="${escapeHtml(l.name)} ${l.pct}%"></span>`).join("");
    document.getElementById("langlegend").innerHTML = langs.map(l =>
      `<span class="lang"><i style="background:${LANG_COLORS[l.name]||'#888'}"></i>${escapeHtml(l.name)} <b>${l.pct}%</b></span>`).join("");
  }

  function renderStats(){
    const pr = data.contributions.prs.totals, is = data.contributions.issues.totals, p = data.profile || {};
    const set = (id,v) => { const e=document.getElementById(id); if(e) e.textContent = (v==null?"—":v); };
    set("s-prs", pr.total); set("s-merged", pr.merged); set("s-issues", is.total);
    set("s-orgs", data.contributions.prs.orgs.length);
    set("s-followers", p.followers); set("s-following", p.following);
    set("s-repos", p.public_repos); set("s-stars", p.stars);
    if (data.generated_at) document.getElementById("generated").textContent = "Updated " + data.generated_at;
  }

  function renderFilters(){
    const f = document.getElementById("filters");
    f.innerHTML = FILTERS[mode].map(([k,l]) =>
      `<button data-filter="${k}"${k===currentFilter?' class="active"':''}>${l}</button>`).join("");
    f.querySelectorAll("button").forEach(btn => btn.addEventListener("click", () => {
      currentFilter = btn.dataset.filter; renderFilters(); render();
    }));
  }

  function render(){
    const src = data.contributions[mode];
    const list = document.getElementById("list");
    list.innerHTML = "";
    const orgs = src.orgs.map(org => ({ ...org, visible: org.items.filter(it => currentFilter==="all" || STATE_LABEL[it.state]===currentFilter) }))
                         .filter(org => org.visible.length > 0);
    if (orgs.length === 0){ list.innerHTML = '<div class="empty">No entries match this filter.</div>'; return; }
    const noun = mode==="prs" ? ["PR","PRs"] : ["issue","issues"];
    orgs.forEach(org => {
      const card = document.createElement("div"); card.className = "org";
      const header = document.createElement("div"); header.className = "org-header";
      const pill = mode==="prs" ? `${org.merged} merged` : `${org.closed} closed`;
      header.innerHTML = `
        <span class="chev">&#9654;</span>
        <img class="org-logo" alt="" src="https://github.com/${org.name}.png?size=64" onerror="this.style.visibility='hidden'">
        <span class="org-name">${escapeHtml(org.name)}</span>
        <span class="org-meta"><b>${org.visible.length}</b> ${org.visible.length===1?noun[0]:noun[1]}<span class="pill">${pill}</span></span>`;
      const rows = document.createElement("div"); rows.className = "prs";
      org.visible.forEach(it => {
        const row = document.createElement("div"); row.className = "pr";
        const label = STATE_LABEL[it.state] || "open";
        const date = it.merged_at || it.created_at;
        row.innerHTML = `
          <span class="pr-status ${label}">${label}</span>
          <span class="pr-title">${it.number ? `<span class="pr-num">#${it.number}</span>` : ""}<a href="${it.url}" target="_blank" rel="noopener">${escapeHtml(it.title)}</a></span>
          <span class="pr-date">${date || ""}</span>`;
        rows.appendChild(row);
      });
      header.onclick = () => card.classList.toggle("open");
      card.appendChild(header); card.appendChild(rows); list.appendChild(card);
    });
  }

  function setMode(m){
    mode = m; currentFilter = "all";
    document.querySelectorAll("#seg button").forEach(b => b.classList.toggle("active", b.dataset.mode===m));
    renderFilters(); render();
  }

  document.querySelectorAll("#seg button").forEach(btn => btn.addEventListener("click", () => setMode(btn.dataset.mode)));

  fetch("./data.json", { cache: "no-store" })
    .then(r => { if (!r.ok) throw new Error("data.json not found"); return r.json(); })
    .then(json => {
      data = json;
      document.getElementById("seg").hidden = false;
      document.getElementById("filters").hidden = false;
      renderProfile(); renderLanguages(); renderStats(); setMode("prs");
    })
    .catch(err => {
      document.getElementById("list").innerHTML = `<div class="empty">Failed to load data.json — ${escapeHtml(err.message)}</div>`;
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


# ─────────────────────────────────────────────────────────────────────────────
# THEME: NEWSPAPER — classic broadsheet, newsprint, serif, thin rules, masthead
# ─────────────────────────────────────────────────────────────────────────────
NEWS_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=PT+Serif:ital,wght@0,400;0,700;1,400&family=Oswald:wght@400;500;600&display=swap" rel="stylesheet">"""
NEWS_CSS = """    :root {
      --bg: #f4f1e9;
      --bg-2: #e9e4d6;
      --paper: #faf8f1;
      --ink: #17140f;
      --ink-soft: #46413a;
      --ink-faint: #857e70;
      --line: #cfc7b5;
      --rule: #17140f;
      --accent: #8b1a1a;
      --merged: #2f5a2f;
      --open: #8a5a12;
      --closed: #8b1a1a;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'PT Serif', Georgia, serif;
      background-image: repeating-linear-gradient(0deg, rgba(23,20,15,0.014) 0 1px, transparent 1px 3px);
    }
    .oswald { font-family: 'Oswald', sans-serif; }
    main { max-width: 900px; margin: 0 auto; padding: 40px 24px 96px; }

    .switch { display: flex; justify-content: center; gap: 22px; margin-bottom: 22px; flex-wrap: wrap; font-family: 'Oswald', sans-serif; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.14em; }
    .switch a { color: var(--ink-soft); text-decoration: none; padding-bottom: 3px; border-bottom: 2px solid transparent; transition: all 0.15s; }
    .switch a:hover { color: var(--accent); }
    .switch a.current { color: var(--ink); border-bottom-color: var(--accent); }

    .head { text-align: center; border-top: 4px double var(--rule); border-bottom: 1px solid var(--rule); padding: 16px 0 14px; margin-bottom: 4px; }
    .title { font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: clamp(2.8rem, 9vw, 5.2rem); letter-spacing: -0.01em; line-height: 0.98; margin: 0; color: var(--ink); }
    .subtitle { font-family: 'Oswald', sans-serif; text-transform: uppercase; letter-spacing: 0.18em; margin: 12px 0 0; color: var(--ink-soft); font-size: 0.76rem; }
    .subtitle b { color: var(--ink); font-weight: 600; }
    .subtitle .dot { color: var(--accent); margin: 0 8px; }
    .stats, .filters, #list { border-top: none; }
    .head + .stats { border-top: 2px solid var(--rule); margin-top: 0; }

    .stats { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px; padding: 18px 8px; margin: 0 0 26px; border-bottom: 2px solid var(--rule); }
    .stat { display: flex; flex-direction: column; gap: 2px; align-items: center; text-align: center; flex: 1; min-width: 90px; }
    .stat + .stat { border-left: 1px solid var(--line); }
    .stat .v { font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 2rem; line-height: 1; color: var(--ink); }
    .stat .l { font-family: 'Oswald', sans-serif; font-size: 0.66rem; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.14em; }
    .stat.merged .v { color: var(--merged); }
    .stat.open .v { color: var(--open); }
    .stat.closed .v { color: var(--closed); }

    .filters { display: flex; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }
    .filters button { background: transparent; color: var(--ink-soft); border: 1px solid var(--rule); padding: 7px 18px; font-family: 'Oswald', sans-serif; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; border-radius: 0; transition: all 0.15s; }
    .filters button:hover { color: var(--accent); border-color: var(--accent); }
    .filters button.active { color: var(--paper); background: var(--ink); border-color: var(--ink); }

    .org { border: 1px solid var(--rule); background: var(--paper); border-radius: 0; margin-bottom: -1px; overflow: hidden; }
    .org.open { border-color: var(--rule); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 14px 20px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg-2); }
    .chev { color: var(--accent); font-size: 0.8rem; transition: transform 0.2s; width: 14px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 30px; height: 30px; border-radius: 0; object-fit: cover; background: var(--bg-2); border: 1px solid var(--rule); filter: grayscale(1) contrast(1.05); }
    .org-name { flex: 1; font-family: 'Playfair Display', Georgia, serif; font-weight: 700; font-size: 1.3rem; color: var(--ink); }
    .org-meta { font-family: 'Oswald', sans-serif; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-soft); }
    .org-meta b { color: var(--ink); font-weight: 600; }
    .org-meta .pill { display: inline-block; padding: 2px 10px; border: 1px solid var(--merged); color: var(--merged); margin-left: 10px; font-size: 0.68rem; }

    .prs { display: none; border-top: 1px solid var(--rule); background: var(--bg); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 92px 1fr auto; gap: 16px; align-items: baseline; padding: 12px 20px 12px 50px; font-size: 0.98rem; border-bottom: 1px solid var(--line); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-family: 'Oswald', sans-serif; font-size: 0.62rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 8px; border-radius: 0; text-align: center; border: 1px solid currentColor; }
    .pr-status.merged { color: var(--merged); }
    .pr-status.open { color: var(--open); }
    .pr-status.closed { color: var(--closed); }
    .pr-title a { color: var(--ink); text-decoration: none; transition: color 0.15s; }
    .pr-title a:hover { color: var(--accent); text-decoration: underline; }
    .pr-num { font-family: 'Oswald', sans-serif; color: var(--ink-faint); margin-right: 6px; font-size: 0.82rem; }
    .pr-date { font-family: 'Oswald', sans-serif; color: var(--ink-faint); font-size: 0.74rem; letter-spacing: 0.04em; white-space: nowrap; }

    .empty { color: var(--ink-faint); padding: 16px; font-style: italic; }
    footer { margin-top: 48px; padding-top: 18px; border-top: 4px double var(--rule); color: var(--ink-faint); font-family: 'Oswald', sans-serif; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.08em; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    footer a { color: var(--ink-soft); text-decoration: none; border-bottom: 1px solid var(--line); }
    footer a:hover { color: var(--accent); border-bottom-color: var(--accent); }
    @media (max-width: 600px) { main { padding: 28px 16px 64px; } .pr { grid-template-columns: 82px 1fr; padding-left: 24px; } .pr-date { grid-column: 2; } .stat + .stat { border-left: none; } }"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: COMIC — pop-art comic book, halftone dots, bold outlines, POW! energy
# ─────────────────────────────────────────────────────────────────────────────
COMIC_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:ital,wght@0,400;0,700;1,700&display=swap" rel="stylesheet">"""
COMIC_CSS = """    :root {
      --bg: #ffe74c;
      --bg-2: #fff4bf;
      --paper: #ffffff;
      --ink: #1a1a1a;
      --ink-soft: #3a3a3a;
      --ink-faint: #6b6b6b;
      --line: #1a1a1a;
      --accent: #ff2b4e;
      --accent-2: #2b6cff;
      --merged: #17a54a;
      --open: #ff9d0a;
      --closed: #ff2b4e;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif; font-weight: 700;
      background-image: radial-gradient(circle, rgba(26,26,26,0.10) 1.6px, transparent 1.7px);
      background-size: 18px 18px; background-attachment: fixed;
    }
    .bangers { font-family: 'Bangers', cursive; }
    main { max-width: 920px; margin: 0 auto; padding: 52px 24px 96px; }

    .switch { display: flex; gap: 10px; margin-bottom: 34px; flex-wrap: wrap; }
    .switch a {
      font-family: 'Bangers', cursive; letter-spacing: 0.06em; font-size: 1.05rem;
      color: var(--ink); text-decoration: none; padding: 6px 16px; background: var(--paper);
      border: 3px solid var(--ink); border-radius: 999px; box-shadow: 3px 3px 0 var(--ink); transition: transform 0.08s;
    }
    .switch a:hover { transform: translate(-1px,-1px); color: var(--accent-2); }
    .switch a.current { background: var(--accent); color: #fff; }

    .title {
      font-family: 'Bangers', cursive; font-weight: 400; font-size: clamp(3.4rem, 11vw, 6.5rem);
      letter-spacing: 0.02em; line-height: 0.9; margin: 0 0 14px; color: var(--open);
      -webkit-text-stroke: 3px var(--ink); text-shadow: 6px 6px 0 var(--accent), 6px 6px 0 var(--ink);
      transform: rotate(-2deg);
    }
    .subtitle { font-family: 'Bangers', cursive; letter-spacing: 0.04em; margin: 0 0 32px; color: var(--ink); font-size: 1.3rem; }
    .subtitle b { color: var(--accent); }
    .subtitle .dot { color: var(--accent-2); margin: 0 8px; }

    .stats { display: flex; flex-wrap: wrap; gap: 16px; padding: 22px 24px; margin-bottom: 28px; background: var(--paper); border: 4px solid var(--ink); border-radius: 18px; box-shadow: 7px 7px 0 var(--ink); }
    .stat { display: flex; flex-direction: column; gap: 2px; align-items: center; }
    .stat .v { font-family: 'Bangers', cursive; font-size: 2.4rem; line-height: 1; color: var(--accent-2); -webkit-text-stroke: 1.5px var(--ink); }
    .stat .l { font-family: 'Bangers', cursive; letter-spacing: 0.05em; font-size: 0.92rem; color: var(--ink-faint); text-transform: uppercase; }
    .stat.merged .v { color: var(--merged); }
    .stat.open .v { color: var(--open); }
    .stat.closed .v { color: var(--accent); }

    .filters { display: flex; gap: 12px; margin-bottom: 22px; flex-wrap: wrap; }
    .filters button {
      font-family: 'Bangers', cursive; letter-spacing: 0.05em; font-size: 1.05rem; color: var(--ink);
      background: var(--paper); border: 3px solid var(--ink); padding: 6px 20px; cursor: pointer;
      border-radius: 999px; box-shadow: 3px 3px 0 var(--ink); transition: transform 0.08s;
    }
    .filters button:hover { transform: translate(-1px,-1px); color: var(--accent-2); }
    .filters button.active { background: var(--accent); color: #fff; }

    .org { border: 4px solid var(--ink); background: var(--paper); border-radius: 16px; margin-bottom: 16px; overflow: hidden; box-shadow: 6px 6px 0 var(--ink); transition: transform 0.1s; }
    .org:hover { transform: translate(-2px,-2px); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 15px 20px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg-2); }
    .chev { color: var(--accent); font-size: 1rem; transition: transform 0.2s; width: 16px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; background: var(--bg-2); border: 3px solid var(--ink); }
    .org-name { flex: 1; font-family: 'Bangers', cursive; letter-spacing: 0.03em; font-size: 1.6rem; color: var(--ink); }
    .org-meta { font-size: 0.9rem; color: var(--ink-soft); font-weight: 700; }
    .org-meta b { color: var(--accent-2); }
    .org-meta .pill { display: inline-block; padding: 2px 12px; border-radius: 999px; background: var(--merged); color: #fff; margin-left: 10px; font-size: 0.78rem; border: 2px solid var(--ink); }

    .prs { display: none; border-top: 4px solid var(--ink); background: var(--bg-2); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 96px 1fr auto; gap: 16px; align-items: baseline; padding: 12px 20px 12px 48px; font-size: 1rem; border-bottom: 2px dashed var(--ink); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-family: 'Bangers', cursive; letter-spacing: 0.04em; font-size: 0.82rem; text-transform: uppercase; padding: 3px 10px; border-radius: 999px; text-align: center; color: #fff; border: 2px solid var(--ink); }
    .pr-status.merged { background: var(--merged); }
    .pr-status.open { background: var(--open); }
    .pr-status.closed { background: var(--accent); }
    .pr-title a { color: var(--ink); text-decoration: none; }
    .pr-title a:hover { color: var(--accent-2); text-decoration: underline; }
    .pr-num { font-family: 'Bangers', cursive; color: var(--accent); margin-right: 6px; font-size: 0.95rem; }
    .pr-date { color: var(--ink-faint); font-size: 0.82rem; white-space: nowrap; font-weight: 700; }

    .empty { color: var(--ink-faint); padding: 16px; }
    footer { margin-top: 52px; padding-top: 20px; border-top: 4px solid var(--ink); color: var(--ink-soft); font-size: 0.9rem; font-weight: 700; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    footer a { color: var(--accent-2); text-decoration: none; }
    footer a:hover { color: var(--accent); text-decoration: underline; }
    @media (max-width: 600px) { main { padding: 32px 16px 64px; } .pr { grid-template-columns: 86px 1fr; padding-left: 24px; } .pr-date { grid-column: 2; } }"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME: NOTEBOOK — hand-drawn, ruled paper, handwriting, sticky notes, doodles
# ─────────────────────────────────────────────────────────────────────────────
NOTEBOOK_FONTS = """  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Patrick+Hand&display=swap" rel="stylesheet">"""
NOTEBOOK_CSS = """    :root {
      --bg: #fbfaf3;
      --bg-2: #f3f1e3;
      --paper: #fffef8;
      --ink: #2b2b3a;
      --ink-soft: #4f4f63;
      --ink-faint: #8a8a9c;
      --line: #c9d4e6;
      --accent: #d64545;
      --accent-2: #3a5bbf;
      --merged: #2f8f4e;
      --open: #d68a1e;
      --closed: #d64545;
    }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--ink); margin: 0; padding: 0; min-height: 100%; }
    body {
      font-family: 'Patrick Hand', 'Comic Sans MS', cursive; font-size: 18px;
      background-image:
        linear-gradient(90deg, transparent 62px, rgba(214,69,69,0.35) 62px, rgba(214,69,69,0.35) 64px, transparent 64px),
        repeating-linear-gradient(180deg, transparent 0 30px, var(--line) 30px 31px);
      background-attachment: fixed;
    }
    .caveat { font-family: 'Caveat', cursive; }
    main { max-width: 860px; margin: 0 auto; padding: 48px 24px 96px 84px; }

    .switch { display: flex; gap: 12px; margin-bottom: 30px; flex-wrap: wrap; }
    .switch a {
      font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.35rem;
      color: var(--ink-soft); text-decoration: none; padding: 2px 14px; background: var(--paper);
      border: 2px solid var(--ink); border-radius: 14px 10px 16px 8px / 8px 16px 10px 14px;
      box-shadow: 2px 2px 0 rgba(43,43,58,0.5); transition: transform 0.1s;
    }
    .switch a:hover { transform: rotate(-2deg); color: var(--accent-2); }
    .switch a.current { background: #fff6a8; color: var(--ink); }

    .title { font-family: 'Caveat', cursive; font-weight: 700; font-size: clamp(3.4rem, 11vw, 6rem); line-height: 0.95; margin: 0 0 6px; color: var(--ink); transform: rotate(-1.5deg); }
    .subtitle { font-family: 'Patrick Hand', cursive; margin: 0 0 34px; color: var(--ink-soft); font-size: 1.15rem; }
    .subtitle b { color: var(--accent); text-decoration: underline wavy var(--accent); }
    .subtitle .dot { color: var(--accent-2); margin: 0 6px; }

    .stats { display: flex; flex-wrap: wrap; gap: 18px; padding: 8px 0; margin-bottom: 30px; background: transparent; }
    .stat {
      display: flex; flex-direction: column; gap: 0; align-items: center; padding: 14px 20px 16px;
      background: #fff6a8; border: 1px solid rgba(43,43,58,0.4); box-shadow: 3px 4px 6px rgba(43,43,58,0.18);
      min-width: 92px;
    }
    .stat:nth-child(2) { background: #cfe8ff; transform: rotate(1.5deg); }
    .stat:nth-child(3) { background: #d8f5d8; transform: rotate(-1.5deg); }
    .stat:nth-child(4) { background: #ffd6d6; transform: rotate(1deg); }
    .stat:nth-child(5) { background: #ecd9ff; transform: rotate(-1deg); }
    .stat .v { font-family: 'Caveat', cursive; font-weight: 700; font-size: 2.3rem; line-height: 1; color: var(--ink); }
    .stat .l { font-family: 'Patrick Hand', cursive; font-size: 0.82rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.06em; }

    .filters { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
    .filters button {
      font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.3rem; color: var(--ink-soft);
      background: var(--paper); border: 2px solid var(--ink); padding: 1px 18px; cursor: pointer;
      border-radius: 14px 8px 16px 10px / 10px 16px 8px 14px; box-shadow: 2px 2px 0 rgba(43,43,58,0.5); transition: transform 0.1s;
    }
    .filters button:hover { transform: rotate(-2deg); color: var(--accent-2); }
    .filters button.active { background: #fff6a8; color: var(--ink); }

    .org { border: 2px solid var(--ink); background: var(--paper); border-radius: 16px 10px 18px 8px / 8px 18px 10px 16px; margin-bottom: 16px; overflow: hidden; box-shadow: 3px 4px 0 rgba(43,43,58,0.35); }
    .org-header { display: flex; align-items: center; gap: 14px; padding: 14px 20px; cursor: pointer; user-select: none; }
    .org-header:hover { background: var(--bg-2); }
    .chev { color: var(--accent); font-size: 0.9rem; transition: transform 0.2s; width: 16px; }
    .org.open .chev { transform: rotate(90deg); }
    .org-logo { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; background: var(--bg-2); border: 2px solid var(--ink); }
    .org-name { flex: 1; font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.7rem; color: var(--ink); }
    .org-meta { font-size: 1rem; color: var(--ink-soft); }
    .org-meta b { color: var(--accent-2); }
    .org-meta .pill { display: inline-block; padding: 1px 12px; border-radius: 999px; background: #d8f5d8; color: var(--merged); margin-left: 8px; font-size: 0.9rem; border: 1px solid var(--merged); }

    .prs { display: none; border-top: 2px dashed var(--ink); background: var(--bg); }
    .org.open .prs { display: block; }
    .pr { display: grid; grid-template-columns: 92px 1fr auto; gap: 16px; align-items: baseline; padding: 11px 20px 11px 46px; font-size: 1.05rem; border-bottom: 1px solid var(--line); }
    .pr:last-child { border-bottom: none; }
    .pr-status { font-family: 'Patrick Hand', cursive; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.03em; padding: 2px 10px; border-radius: 999px; text-align: center; border: 1.5px solid currentColor; }
    .pr-status.merged { color: var(--merged); background: #eafaea; }
    .pr-status.open { color: var(--open); background: #fdf3e0; }
    .pr-status.closed { color: var(--closed); background: #fdeaea; }
    .pr-title a { color: var(--ink); text-decoration: none; }
    .pr-title a:hover { color: var(--accent-2); text-decoration: underline wavy; }
    .pr-num { color: var(--accent); margin-right: 6px; font-size: 0.95rem; }
    .pr-date { color: var(--ink-faint); font-size: 0.92rem; white-space: nowrap; }

    .empty { color: var(--ink-faint); padding: 16px; }
    footer { margin-top: 48px; padding-top: 18px; border-top: 2px dashed var(--ink); color: var(--ink-faint); font-size: 1rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    footer a { color: var(--accent-2); text-decoration: underline; }
    footer a:hover { color: var(--accent); }
    @media (max-width: 600px) { main { padding: 32px 16px 64px 40px; } .pr { grid-template-columns: 82px 1fr; padding-left: 22px; } .pr-date { grid-column: 2; } }"""


STYLES = {
    "techno": (TECHNO_FONTS, TECHNO_CSS),
    "pixels": (PIXELS_FONTS, PIXELS_CSS),
    "modern": (MODERN_FONTS, MODERN_CSS),
    "retro":  (RETRO_FONTS,  RETRO_CSS),
    "news":   (NEWS_FONTS,   NEWS_CSS),
    "comic":  (COMIC_FONTS,  COMIC_CSS),
    "notebook": (NOTEBOOK_FONTS, NOTEBOOK_CSS),
}

# Per-theme tile tokens consumed by the shared bento CSS below. Each theme keeps
# its own character (corner style, shadow, display font) while sharing layout.
BENTO_VARS = {
    "notebook": ":root{ --display:'Caveat',cursive; --radius:16px 10px 18px 8px / 8px 18px 10px 16px; --shadow:3px 4px 0 rgba(43,43,58,0.35); --tile-border:2px solid var(--ink); --avatar-radius:50%; }",
    "comic":    ":root{ --display:'Bangers',cursive; --radius:16px; --shadow:6px 6px 0 var(--ink); --tile-border:4px solid var(--ink); --avatar-radius:50%; }",
    "retro":    ":root{ --display:'DM Serif Display',Georgia,serif; --radius:18px; --shadow:4px 4px 0 var(--ink); --tile-border:2px solid var(--ink); --avatar-radius:50%; }",
    "news":     ":root{ --display:'Playfair Display',Georgia,serif; --radius:0; --shadow:none; --tile-border:1px solid var(--rule); --avatar-radius:0; }",
}

# Shared bento layout — uses each theme's CSS variables so it adapts automatically.
BENTO_CSS = """
    /* ── bento mosaic (shared across themes) ─────────────────────────── */
    .bento { display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 140px; grid-auto-flow: row dense; gap: 14px; margin-bottom: 30px; }
    .tile { background: var(--paper); border: var(--tile-border, 1px solid var(--line)); border-radius: var(--radius, 14px); box-shadow: var(--shadow, none); padding: 18px 20px; overflow: hidden; }

    .tile-avatar { grid-column: span 2; grid-row: span 2; padding: 0; display: block; }
    .tile-avatar .avatar { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s; }
    .tile-avatar:hover .avatar { transform: scale(1.04); }

    .tile-head { grid-column: span 2; grid-row: span 2; display: flex; flex-direction: column; justify-content: center; gap: 5px; }
    .eyebrow { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.2em; color: var(--ink-faint); }
    .pname { font-family: var(--display, inherit); font-weight: 700; font-size: clamp(1.9rem, 5vw, 2.8rem); line-height: 1.02; margin: 0; color: var(--ink); }
    .pbio { margin: 4px 0 0; color: var(--ink-soft); font-size: 0.9rem; line-height: 1.45; }
    .pmeta { margin: 2px 0 0; color: var(--ink-faint); font-size: 0.82rem; }

    .tile-lang { grid-column: span 2; grid-row: span 2; display: flex; flex-direction: column; gap: 14px; justify-content: center; }
    .tile-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.16em; color: var(--ink-faint); }
    .langbar { display: flex; height: 14px; border-radius: 999px; overflow: hidden; background: var(--bg-2); border: 1px solid var(--line); }
    .langseg { height: 100%; }
    .langlegend { display: flex; flex-wrap: wrap; gap: 8px 16px; }
    .lang { font-size: 0.8rem; color: var(--ink-soft); display: inline-flex; align-items: center; gap: 6px; }
    .lang i { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
    .lang b { color: var(--ink); font-weight: 600; }

    .tile-social { display: flex; flex-direction: column; justify-content: space-between; text-decoration: none; color: var(--ink); cursor: pointer; transition: transform 0.12s, border-color 0.15s, color 0.15s; }
    .tile-social .sc-go { align-self: flex-end; color: var(--ink-faint); font-size: 1.25rem; line-height: 1; }
    .tile-social .sc-name { font-family: var(--display, inherit); font-weight: 700; font-size: 1.45rem; margin-top: auto; }
    .tile-social:hover { color: var(--accent); border-color: var(--accent); transform: translateY(-2px); }
    .tile-social:hover .sc-go { color: var(--accent); }

    .num { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
    .num .v { font-family: var(--display, inherit); font-weight: 700; font-size: 2rem; line-height: 1; color: var(--accent); }
    .num.merged .v { color: var(--merged); }
    .num .l { font-size: 0.7rem; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.06em; }

    .seg { display: inline-flex; gap: 4px; margin-bottom: 18px; padding: 4px; border: var(--tile-border, 1px solid var(--line)); border-radius: 999px; background: var(--bg-2); }
    .seg button { border: none; background: transparent; color: var(--ink-soft); font-family: inherit; font-size: 0.9rem; font-weight: 600; padding: 6px 20px; border-radius: 999px; cursor: pointer; transition: all 0.15s; }
    .seg button:hover { color: var(--accent); }
    .seg button.active { background: var(--accent); color: var(--paper); }

    @media (max-width: 760px) {
      .bento { grid-template-columns: repeat(2, 1fr); grid-auto-rows: 132px; }
      .tile-avatar, .tile-head, .tile-lang { grid-column: span 2; }
    }
    @media (max-width: 440px) { .bento { grid-auto-rows: 120px; } }"""


def build():
    os.makedirs(DOCS, exist_ok=True)
    for fname, key, label in THEMES:
        fonts, css = STYLES[key]
        css = css + "\n" + BENTO_VARS.get(key, "") + "\n" + BENTO_CSS
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
