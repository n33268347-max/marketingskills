"""Builds PLATFORM_RESEARCH_MATRIX.csv from the claims database.

Each cell is the best available claim for that topic: A_CONFIRMED first, then
P_PROVISIONAL. The evidence class is shown alongside using the V2 scale:
A = primary source read directly; B = reliable secondary; C = statistical
inference; D = hypothesis; E = unknown.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

TOPICS = [
    ("operator", "Company identity"), ("terms_url", "Terms"), ("winner_selection", "Draw mechanism"),
    ("independent_rng", "Independent RNG / party"), ("live_draw", "Live draw"), ("ticket_allocation", "Ticket allocation"),
    ("discloses_max_tickets", "Max tickets disclosed"), ("discloses_tickets_sold", "Sales disclosed"),
    ("results_page", "Winners published"), ("results_show_ticket_number", "Winning ticket number shown"),
    ("free_entry_route", "Free postal route"), ("instant_wins", "Instant wins"), ("code_of_practice", "DCMS code signatory"),
    ("regulatory_history", "Regulatory history"),
]
NOTE_KEYS = {"refund_policy": "Refund policy", "bundle_discount": "Bundle discounts", "postal_entries_per_card": "Postal entries per card",
             "unsold_number_handling": "Unsold-number handling", "acceptable_use": "Acceptable-use clause"}
LEVEL_TO_CLASS = {"A_CONFIRMED": "A", "P_PROVISIONAL": "B", "B_OBSERVATION": "C", "C_HYPOTHESIS": "D", "UNKNOWN": "E"}


def _best(rows):
    for lvl in ("A_CONFIRMED", "P_PROVISIONAL", "C_HYPOTHESIS"):
        sel = [r for r in rows if r["evidence_level"] == lvl]
        if sel:
            r = sel[-1]
            txt = (r["value"] + ": " if r["value"] else "") + r["statement"]
            return txt[:220], LEVEL_TO_CLASS[lvl], r["source_url"] or ""
    return "unknown", "E", ""


def build(conn: sqlite3.Connection, blocklist: dict, verification: dict, out: Path, terms_unread: set[str] = frozenset()) -> int:
    conn.row_factory = sqlite3.Row
    cols = ["platform"]
    for _, label in TOPICS + [(k, v) for k, v in NOTE_KEYS.items()]:
        cols += [label, f"{label} [class]", f"{label} [source]"]
    cols += ["Automated collection", "Independent draw verification (this project)"]
    plats = conn.execute("SELECT slug, name, base_url FROM platforms ORDER BY name").fetchall()
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for p in plats:
            claims = conn.execute("SELECT * FROM current_claims WHERE platform_slug=? ORDER BY id", (p["slug"],)).fetchall()
            row = [p["name"]]
            for topic, _ in TOPICS:
                row += list(_best([c for c in claims if c["topic"] == topic]))
            for key in NOTE_KEYS:
                row += list(_best([c for c in claims if c["topic"] == "notes" and (c["value"] or "").startswith(key)]))
            host = "/".join(p["base_url"].split("/")[:3])
            reason = blocklist.get(host, "")
            row.append("Manual only: " + reason[:120] if reason.startswith(("BOTB", "Click", "Same")) else
                       ("Paused: terms unread" if reason.startswith("PENDING") else
                        "Terms unread (JS-rendered): not assessed" if p["slug"] in terms_unread else
                        "No prohibition found in terms read; robots.txt obeyed"))
            row.append(verification.get(p["slug"], "Not assessed"))
            w.writerow(row)
    return len(plats)
