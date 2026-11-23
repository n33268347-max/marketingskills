"""Write observations and draw results into the append-only store."""

from __future__ import annotations

import csv
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .db.database import ensure_competition, insert, transaction
from .parsers.generic import ExtractedCompetition

log = logging.getLogger(__name__)

DRAW_CSV_COLUMNS = [
    "platform_slug", "external_ref", "competition_name", "drawn_at", "prize_rank",
    "winning_ticket_number", "ticket_range_min", "ticket_range_max", "tickets_sold_at_draw",
    "selection_method", "independent_rng", "rng_name", "evidence_url",
]


def record_observation(conn, platform_slug: str, external_ref: str, source_url: str,
                       ec: ExtractedCompetition, snapshot_id: int | None = None, **extra) -> int:
    with transaction(conn):
        cid = ensure_competition(conn, platform_slug, external_ref, ec.name or external_ref)
        return insert(conn, "competition_observations", {
            "competition_id": cid,
            "observed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "snapshot_id": snapshot_id,
            "source_url": source_url,
            "advertised_value_pence": ec.advertised_value_pence,
            "cash_alternative_pence": ec.cash_alternative_pence,
            "ticket_price_pence": ec.ticket_price_pence,
            "max_tickets": ec.max_tickets,
            "tickets_sold": ec.tickets_sold,
            "tickets_sold_basis": ec.tickets_sold_basis or ("not_disclosed" if ec.tickets_sold is None else None),
            **extra,
        })


def _opt_int(v: str | None) -> int | None:
    v = (v or "").strip().replace(",", "")
    return int(v) if v else None


def import_draws_csv(conn: sqlite3.Connection, path: str | Path) -> tuple[int, list[str]]:
    """Import manually transcribed draw results. Each row MUST cite evidence_url.

    Rows that already exist (same competition, rank, ticket, evidence) are skipped,
    so re-importing a file is safe. Returns (inserted, errors).
    """
    inserted, errors = 0, []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = set(DRAW_CSV_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            return 0, [f"missing columns: {sorted(missing)}"]
        for i, row in enumerate(reader, start=2):
            try:
                if not (row["evidence_url"] or "").startswith("http"):
                    raise ValueError("evidence_url is required")
                if conn.execute("SELECT 1 FROM platforms WHERE slug=?", (row["platform_slug"],)).fetchone() is None:
                    raise ValueError(f"unknown platform {row['platform_slug']!r}")
                with transaction(conn):
                    cid = ensure_competition(conn, row["platform_slug"], row["external_ref"], row["competition_name"])
                    rank = _opt_int(row["prize_rank"]) or 1
                    ticket = _opt_int(row["winning_ticket_number"])
                    dup = conn.execute(
                        """SELECT 1 FROM draw_results WHERE competition_id=? AND prize_rank=?
                           AND IFNULL(winning_ticket_number,-1)=IFNULL(?,-1) AND evidence_url=?""",
                        (cid, rank, ticket, row["evidence_url"]),
                    ).fetchone()
                    if dup:
                        continue
                    insert(conn, "draw_results", {
                        "competition_id": cid,
                        "drawn_at": row["drawn_at"] or None,
                        "prize_rank": rank,
                        "winning_ticket_number": ticket,
                        "ticket_range_min": _opt_int(row["ticket_range_min"]),
                        "ticket_range_max": _opt_int(row["ticket_range_max"]),
                        "tickets_sold_at_draw": _opt_int(row["tickets_sold_at_draw"]),
                        "selection_method": row["selection_method"] or None,
                        "independent_rng": (row["independent_rng"] or "unknown").lower(),
                        "rng_name": row["rng_name"] or None,
                        "evidence_url": row["evidence_url"],
                    })
                    inserted += 1
            except Exception as exc:  # report and continue: one bad row must not stop the file
                errors.append(f"line {i}: {exc}")
    log.info("draw import: %d inserted, %d errors", inserted, len(errors))
    return inserted, errors
