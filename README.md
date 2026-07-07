# Proof of Work

A personal open-source dashboard rendered as a **bento grid**, in four themes:
**notebook**, **comic**, **retro**, and **newspaper**.

Live: `https://disha1202.github.io/proof-of-work/`

## What it shows

- **Profile tile** — avatar, name, bio, company/location, and links (GitHub, LinkedIn, Twitter, email).
- **Top languages** — byte-weighted breakdown across your repos (Java, Vue, TypeScript, …).
- **Stat tiles** — pull requests, merged, issues opened, organizations, followers, following, public repos, stars.
- **Contributions** — a `Pull Requests` / `Issues` toggle; each groups entries by organization with
  All / Merged / Open / Closed filters (issues use All / Open / Closed).

## How it works

- `fetch_data.py` queries the GitHub API for your profile, all authored PRs and issues
  (across all time, excluding your own repos), and language stats, then writes `docs/data.json`.
- `docs/index*.html` are standalone themed pages that fetch `data.json` and render the bento.
  Markup and JavaScript are shared (generated from one source); only styling differs per theme.
- `build_site.py` generates the four HTML files: shared body + JS, per-theme CSS, plus a shared
  bento layout parametrized by each theme's CSS variables. Run it after editing themes.
- A GitHub Actions workflow refreshes `data.json` daily.

## Themes

| File | Theme | Look |
|------|-------|------|
| `docs/index.html` | **notebook** (default) | ruled paper, handwriting, sticky-note tiles |
| `docs/index-comic.html` | **comic** | pop-art halftone, bold outlines, POW! energy |
| `docs/index-retro.html` | **retro** | 70s vintage, warm, groovy serif |
| `docs/index-news.html` | **newspaper** | broadsheet serif, thin rules, square avatar |

Theme CSS for the retired techno/pixels/modern themes is retained (unused) in `build_site.py`;
re-add any by adding a row to the `THEMES` list.

## Local development

```bash
# regenerate the themed pages after editing build_site.py
python3 build_site.py

# refresh data (GITHUB_TOKEN raises the API rate limit; LINKEDIN_URL / PROFILE_EMAIL are configurable)
GITHUB_USER=disha1202 python3 fetch_data.py

# preview — must be served over HTTP (browsers block fetch() on file://)
python3 -m http.server -d docs 8000   # open http://localhost:8000
```

## Deploying to GitHub Pages

1. Create a repo named `proof-of-work` and push this project.
2. In **Settings → Pages**, set the source to the `main` branch, `/docs` folder.
3. The site is served at `https://<username>.github.io/proof-of-work/`.
