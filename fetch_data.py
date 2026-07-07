#!/usr/bin/env python3
"""Fetch a user's GitHub profile, contributions, and stats -> docs/data.json.

Collects (all across time, external repos only):
  - profile: name, avatar, bio, company, location, socials, follower/repo/star counts
  - languages: byte-weighted breakdown across the user's own repos
  - contributions.prs / contributions.issues: grouped by org, with totals

Env:
  GITHUB_USER    GitHub login to fetch (default: disha1202)
  GITHUB_TOKEN   optional PAT — raises the API rate limit (recommended in CI)
  PROFILE_EMAIL  email to display (GitHub email is usually private)
  LINKEDIN_URL   LinkedIn profile URL to display (not available via GitHub API)
  INCLUDE_OWN    set to 1 to also include contributions to the user's own repos
"""
import json, os, time, urllib.request, urllib.error
from collections import defaultdict, Counter
from datetime import datetime, timezone

USER = os.getenv("GITHUB_USER", "disha1202")
TOKEN = os.getenv("GITHUB_TOKEN")
INCLUDE_OWN = os.getenv("INCLUDE_OWN") == "1"
EMAIL = os.getenv("PROFILE_EMAIL", "dishatalreja1202@gmail.com")
LINKEDIN = os.getenv("LINKEDIN_URL", "https://www.linkedin.com/in/dishatalreja/")
HERE = os.path.dirname(os.path.abspath(__file__))


def api(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "pow-fetch"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 5:
                wait = 20 * (attempt + 1)
                print(f"  rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise


def search_all(kind):
    """kind: 'pr' or 'issue' — returns all matching items authored by USER."""
    items, page = [], 1
    while True:
        d = api(f"https://api.github.com/search/issues?q=author:{USER}+type:{kind}&per_page=100&page={page}")
        batch = d.get("items", [])
        items.extend(batch)
        total = d.get("total_count", 0)
        print(f"  {kind}s page {page}: {len(batch)} (total {len(items)}/{total})")
        if len(batch) < 100 or len(items) >= total:
            break
        page += 1
        time.sleep(2)
    return items


def group(items, is_pr):
    by_org = defaultdict(list)
    for it in items:
        org = it["repository_url"].split("/repos/")[1].split("/")[0]
        if org == USER and not INCLUDE_OWN:
            continue
        merged_at = (it.get("pull_request") or {}).get("merged_at") if is_pr else None
        if merged_at:
            state, date = "Merged", merged_at[:10]
        else:
            state, date = it["state"].capitalize(), (it.get("closed_at") or it["created_at"])[:10]
        by_org[org].append({
            "number": it["number"],
            "title": it["title"],
            "url": it["html_url"],
            "state": state,
            "created_at": it["created_at"][:10],
            "merged_at": merged_at[:10] if merged_at else None,
            "repo": it["repository_url"].split("/repos/")[1].split("/")[1],
        })

    def cnt(items, s):
        return sum(1 for p in items if p["state"] == s)

    ordered = sorted(by_org.keys(),
                     key=lambda o: (cnt(by_org[o], "Merged"), len(by_org[o])),
                     reverse=True)
    orgs = []
    for org in ordered:
        its = sorted(by_org[org], key=lambda x: x["created_at"], reverse=True)
        orgs.append({
            "name": org,
            "merged": cnt(its, "Merged"),
            "closed": cnt(its, "Closed"),
            "items": its,
        })
    all_items = [p for o in orgs for p in o["items"]]
    totals = {
        "total": len(all_items),
        "merged": sum(1 for p in all_items if p["state"] == "Merged"),
        "open": sum(1 for p in all_items if p["state"] == "Open"),
        "closed": sum(1 for p in all_items if p["state"] == "Closed"),
    }
    return {"totals": totals, "orgs": orgs}


def languages_and_stats():
    repos, page = [], 1
    while True:
        d = api(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
        if not d:
            break
        repos.extend(d)
        if len(d) < 100:
            break
        page += 1
    owned = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in owned)
    byt = Counter()
    for r in owned:
        try:
            for lang, b in api(r["languages_url"]).items():
                byt[lang] += b
        except Exception:
            pass
    total = sum(byt.values()) or 1
    langs = [{"name": l, "pct": round(100 * b / total, 1)} for l, b in byt.most_common(6)]
    return langs, stars


def main():
    print(f"Fetching for {USER} (include_own={INCLUDE_OWN})")
    p = api(f"https://api.github.com/users/{USER}")
    print("  profile ok")
    langs, stars = languages_and_stats()
    print(f"  languages: {[l['name'] for l in langs]}  stars={stars}")
    prs = group(search_all("pr"), is_pr=True)
    issues = group(search_all("issue"), is_pr=False)

    data = {
        "username": USER,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "profile": {
            "name": p.get("name") or USER,
            "login": USER,
            "avatar": p.get("avatar_url"),
            "bio": p.get("bio"),
            "company": p.get("company"),
            "location": p.get("location"),
            "followers": p.get("followers"),
            "following": p.get("following"),
            "public_repos": p.get("public_repos"),
            "stars": stars,
            "github": f"https://github.com/{USER}",
            "twitter": p.get("twitter_username"),
            "email": EMAIL,
            "linkedin": LINKEDIN,
            "blog": p.get("blog") or None,
        },
        "languages": langs,
        "contributions": {"prs": prs, "issues": issues},
    }
    out = os.path.join(HERE, "docs", "data.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {out}")
    print(f"  PRs: {prs['totals']}  ({len(prs['orgs'])} orgs)")
    print(f"  Issues: {issues['totals']}  ({len(issues['orgs'])} orgs)")


if __name__ == "__main__":
    main()
