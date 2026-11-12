import json, os, urllib.request, datetime

URL = "https://api.github.com/search/repositories?q=stars:%3E10000&sort=stars&order=desc&per_page=30"
tw = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime.now(tw)
today = now.strftime("%Y-%m-%d")

req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "top30-bot"})
if os.getenv("GITHUB_TOKEN"):
    req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
repos = json.load(urllib.request.urlopen(req))["items"]

old = {}
if os.path.exists("data.json"):
    old = json.load(open("data.json", encoding="utf-8"))

# baseline = 昨天(或更早一天)的排名快照；同一天重跑則沿用
if old.get("date") == today:
    baseline, bdate = old.get("baseline", {}), old.get("baseline_date")
else:
    baseline = {i["name"]: {"rank": i["rank"], "stars": i["stars"]} for i in old.get("items", [])}
    bdate = old.get("date")

items = []
for n, r in enumerate(repos, 1):
    b = baseline.get(r["full_name"])
    items.append({
        "rank": n, "name": r["full_name"], "url": r["html_url"],
        "avatar": r["owner"]["avatar_url"], "desc": r.get("description") or "",
        "lang": r.get("language") or "", "stars": r["stargazers_count"],
        "change": (b["rank"] - n) if b else None,
        "star_delta": (r["stargazers_count"] - b["stars"]) if b else None,
        "is_new": b is None and bool(baseline),
    })

json.dump({"date": today, "updated": now.isoformat(timespec="minutes"),
           "baseline_date": bdate, "baseline": baseline, "items": items},
          open("data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("updated", today)
