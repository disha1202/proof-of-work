# Proof of Work

A curated view of my open-source pull requests, rendered in four themes:
**techno**, **pixels**, **modern**, and **retro**.

Live: `https://disha1202.github.io/proof-of-work/`

## How it works

- `fetch_data.py` queries the GitHub API for all PRs authored by the user
  (across all time, excluding the user's own repos) and writes `docs/data.json`.
- `docs/index*.html` are standalone themed pages that fetch `data.json` and
  render stats, per-org cards, and filterable PR rows. The markup and JavaScript
  are identical across themes — only the styling differs.
- `build_site.py` generates those four HTML files from a single source of truth
  (shared body + JS, per-theme CSS). Run it after editing themes.
- A GitHub Actions workflow refreshes `data.json` daily.

## Themes

| File                     | Theme  | Style                         |
|--------------------------|--------|-------------------------------|
| `docs/index.html`        | techno | neon cyberpunk, dark, glow    |
| `docs/index-pixels.html` | pixels | 8-bit retro game, pixel font  |
| `docs/index-modern.html` | modern | clean, light, minimal         |
| `docs/index-retro.html`  | retro  | 70s vintage, warm, groovy     |

## Local development

```bash
# regenerate the four themed pages after editing build_site.py
python3 build_site.py

# refresh contribution data (optional: export GITHUB_TOKEN for higher rate limits)
GITHUB_USER=disha1202 python3 fetch_data.py

# preview
python3 -m http.server -d docs 8000   # open http://localhost:8000
```

## Deploying to GitHub Pages

1. Create a repo named `proof-of-work` and push this project.
2. In **Settings → Pages**, set the source to the `main` branch, `/docs` folder.
3. The site is served at `https://<username>.github.io/proof-of-work/`.
