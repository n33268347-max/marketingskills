"""Freeze the V1 research results as version-controlled CSVs plus a SHA-256 manifest.

The SQLite database and raw page archive are gitignored (raw pages can hold
winners' names), so without this the V1 evidence exists only on one machine.
Frozen files hold no personal data and must never be edited: later phases
read them and write their own outputs elsewhere.
"""
import csv, hashlib, json, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/frozen/v1"
QUERIES = {
    "draw_results.csv": """SELECT c.platform_slug, c.external_ref AS competition, d.external_result_id, d.drawn_at, d.draw_type,
        d.winning_ticket_number, d.tickets_sold_at_draw, d.rng_published_seed, d.rng_unix_time, d.rng_index, d.rng_entries,
        d.evidence_url, d.snapshot_id FROM current_draw_results d JOIN competitions c ON c.id=d.competition_id ORDER BY d.drawn_at, d.id""",
    "competition_observations.csv": """SELECT c.platform_slug, c.external_ref AS competition, o.id AS observation_id, o.supersedes_id, o.observed_at,
        o.ticket_price_pence, o.max_tickets, o.tickets_sold, o.tickets_sold_basis, o.advertised_value_pence, o.cash_alternative_pence,
        o.number_of_prizes, o.max_entries_per_person, o.closes_at, o.source_url, o.snapshot_id
        FROM competition_observations o JOIN competitions c ON c.id=o.competition_id ORDER BY o.id""",
    "claims.csv": """SELECT id, platform_slug, topic, value, evidence_level, source_kind, source_url, source_quote, accessed_on,
        snapshot_sha256, supersedes_id, statement FROM claims ORDER BY id""",
    "hypothesis_runs.csv": "SELECT * FROM hypothesis_runs ORDER BY id",
    "snapshots_index.csv": "SELECT id, url, fetched_at, http_status, outcome, robots_allowed, content_sha256, note FROM snapshots ORDER BY id",
}

def main():
    if (OUT / "MANIFEST.json").exists() and "--force" not in sys.argv:
        sys.exit("V1 is already frozen; refusing to overwrite (frozen research is immutable).")
    OUT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(ROOT / "data/db/raffle_edge.sqlite")
    files = {}
    for name, q in QUERIES.items():
        cur = conn.execute(q)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(OUT / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(cols); w.writerows(rows)
        files[name] = {"rows": len(rows), "sha256": hashlib.sha256((OUT / name).read_bytes()).hexdigest()}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    manifest = {"frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "code_commit": commit,
                "note": "V1 baseline. Immutable. Contains no personal data (winner names were never stored).", "files": files}
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
