#!/usr/bin/env python3
"""Fetch a user's open-source pull requests and write docs/data.json.

Includes ALL external contributions across all time (no date window).
PRs to the user's own repositories are excluded (proof of work = contributions
to other people's projects). Set INCLUDE_OWN=1 to include them too.

Env:
  GITHUB_USER   GitHub login to fetch (default: disha1202)
  GITHUB_TOKEN  optional PAT — raises the API rate limit (recommended in CI)
  INCLUDE_OWN   set to 1 to also include PRs to the user's own repos
"""
import json, os, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime, timezone

USER = os.getenv("GITHUB_USER", "disha1202")
TOKEN = os.getenv("GITHUB_TOKEN")
INCLUDE_OWN = os.getenv("INCLUDE_OWN") == "1"
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


def fetch_all():
    items, page = [], 1
    while True:
        d = api(f"https://api.github.com/search/issues?q=author:{USER}+type:pr&per_page=100&page={page}")
        batch = d.get("items", [])
        items.extend(batch)
        total = d.get("total_count", 0)
        print(f"page {page}: {len(batch)} (total so far {len(items)} / {total})")
        if len(batch) < 100 or len(items) >= total:
            break
        page += 1
        time.sleep(2)
    return items


def build(items):
    prs_by_org = defaultdict(list)
    for it in items:
        org = it["repository_url"].split("/repos/")[1].split("/")[0]
        if org == USER and not INCLUDE_OWN:
            continue
        merged_at = (it.get("pull_request") or {}).get("merged_at")
        if merged_at:
            state, mdate = "Merged", merged_at[:10]
        else:
            state, mdate = it["state"].capitalize(), None
        prs_by_org[org].append({
            "number": it["number"],
            "title": it["title"],
            "url": it["html_url"],
            "state": state,
            "created_at": it["created_at"][:10],
            "merged_at": mdate,
            "repo": it["repository_url"].split("/repos/")[1].split("/")[1],
        })

    def merged_ct(prs):
        return sum(1 for p in prs if p["state"] == "Merged")

    ordered = sorted(prs_by_org.keys(),
                     key=lambda o: (merged_ct(prs_by_org[o]), len(prs_by_org[o])),
                     reverse=True)

    site_orgs = []
    for org in ordered:
        prs = sorted(prs_by_org[org], key=lambda x: x["created_at"], reverse=True)
        site_orgs.append({"name": org, "merged": merged_ct(prs), "prs": prs})

    total = sum(len(o["prs"]) for o in site_orgs)
    tm = sum(1 for o in site_orgs for p in o["prs"] if p["state"] == "Merged")
    to = sum(1 for o in site_orgs for p in o["prs"] if p["state"] == "Open")
    tc = sum(1 for o in site_orgs for p in o["prs"] if p["state"] == "Closed")

    return {
        "username": USER,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "totals": {"prs": total, "merged": tm, "open": to, "closed": tc},
        "orgs": site_orgs,
    }


def main():
    print(f"Fetching PRs for: {USER}  (include_own={INCLUDE_OWN})")
    data = build(fetch_all())
    out = os.path.join(HERE, "docs", "data.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    t = data["totals"]
    print(f"\nWrote {out}")
    print(f"{t['prs']} PRs | {t['merged']} merged, {t['open']} open, {t['closed']} closed | {len(data['orgs'])} orgs")
    for o in data["orgs"]:
        print(f"  {o['name']}: {len(o['prs'])} ({o['merged']} merged)")


if __name__ == "__main__":
    main()
