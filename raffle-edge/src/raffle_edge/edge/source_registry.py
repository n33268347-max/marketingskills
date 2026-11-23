"""Builds a single source register (CSV) from every evidence store.

Columns: source_name, url, date_accessed, quote, finding, evidence_class, snapshot_sha256, origin.
Classes (V2 scale): A primary source read directly; B reliable secondary; C statistical
inference; D hypothesis; E unknown.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

LEVEL = {"A_CONFIRMED": "A", "P_PROVISIONAL": "B", "B_OBSERVATION": "C", "C_HYPOTHESIS": "D", "UNKNOWN": "E"}


def build(db: Path, legal_json: Path, out: Path) -> int:
    rows = []
    conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
    for c in conn.execute("SELECT * FROM current_claims ORDER BY id"):
        rows.append({"source_name": f"{c['platform_slug']} / {c['topic']}", "url": c["source_url"] or "",
                     "date_accessed": c["accessed_on"] or "", "quote": c["source_quote"] or "", "finding": c["statement"],
                     "evidence_class": LEVEL.get(c["evidence_level"], "E"), "snapshot_sha256": c["snapshot_sha256"] or "",
                     "origin": "platform claims"})
    if legal_json.exists():
        for s in json.loads(legal_json.read_text()):
            rows.append({"source_name": s["source_name"], "url": s["url"], "date_accessed": s["accessed_on"], "quote": s["quote"],
                         "finding": s["finding"], "evidence_class": s["evidence_class"], "snapshot_sha256": s.get("snapshot_sha256", ""),
                         "origin": "legal register"})
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return len(rows)
