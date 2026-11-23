"""Build the V2 processed competition dataset for 7days from frozen observations
plus the archived competition records (original data untouched).

Output: data/processed/v2/7days_competitions.csv (no personal data).
"""
import csv, hashlib, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data/frozen/v1/competition_observations.csv"
OUT = ROOT / "data/processed/v2/7days_competitions.csv"

obs = list(csv.DictReader(open(FROZEN)))
sup = {o["supersedes_id"] for o in obs if o["supersedes_id"]}
cur = [o for o in obs if o["observation_id"] not in sup and o["platform_slug"] == "7days-performance"]
conn = sqlite3.connect(ROOT / "data/db/raffle_edge.sqlite")
snap = {r[0]: (r[1], r[2]) for r in conn.execute("SELECT id, content_path, content_sha256 FROM snapshots")}
cols = ["competition", "start_at", "end_at", "draw_method", "ticket_price_pence", "max_tickets", "tickets_sold",
        "ticket_limit_per_user", "tickets_per_postcard", "advertised_value_pence", "cash_value_pence", "number_of_prizes",
        "prize_title", "is_cash_prize_title", "snapshot_sha256"]
rows = []
for o in cur:
    path, sha = snap[int(o["snapshot_id"])]
    d = json.loads((ROOT / "data/raw" / path).read_text(encoding="utf-8"))
    titles = [str(p.get("title") or "") for p in (d.get("end_prizes") or [])]
    rows.append({
        "competition": o["competition"], "start_at": d.get("start_at"), "end_at": d.get("end_at"), "draw_method": d.get("draw_method"),
        "ticket_price_pence": o["ticket_price_pence"], "max_tickets": o["max_tickets"], "tickets_sold": o["tickets_sold"],
        "ticket_limit_per_user": d.get("ticket_limit_per_user"), "tickets_per_postcard": d.get("tickets_added_per_postcard_entry"),
        "advertised_value_pence": o["advertised_value_pence"], "cash_value_pence": o["cash_alternative_pence"],
        "number_of_prizes": o["number_of_prizes"], "prize_title": " | ".join(titles)[:200],
        "is_cash_prize_title": int(bool(titles) and all(re.search(r"cash", t, re.I) for t in titles)), "snapshot_sha256": sha,
    })
rows.sort(key=lambda r: r["end_at"] or "")
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} rows -> {OUT}  sha256={hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]}")
