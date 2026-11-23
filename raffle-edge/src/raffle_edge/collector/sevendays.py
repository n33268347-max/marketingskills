"""7days Performance collector: public draw-results feed -> append-only store.

Source: the JSON feed the public /draw-results page itself loads
(GET https://7daysperformance.co.uk/api/v3/draw-result?page=N&size=100).
robots.txt: none (site serves HTML at /robots.txt). Terms reviewed 2026-11-23:
no prohibition on automated access found. No authentication is used.

Personal data: the feed includes winners' full names. They are dropped here,
before anything is written to the database. The raw snapshot (gitignored,
local audit copy) still contains them and must never be published.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass

from ..db.database import ensure_competition, ensure_platform, insert, transaction
from .fetcher import PoliteFetcher

log = logging.getLogger(__name__)

PLATFORM = "7days-performance"
BASE = "https://7daysperformance.co.uk"
FEED = BASE + "/api/v3/draw-result?page={page}&size={size}"


@dataclass
class SevenDaysResult:
    result_id: str
    raffle_id: str
    raffle_slug: str
    title: str
    end_at: str | None
    result_at: str | None
    is_instant_win: bool
    winning_ticket: int | None
    draw_type: str
    rng_seed: str | None = None
    rng_unix_time: str | None = None
    rng_index: int | None = None
    rng_entries: int | None = None


def _to_int(v) -> int | None:
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def parse_page(payload: dict) -> tuple[list[SevenDaysResult], dict]:
    """Parse one feed page. Winner names are never read into the result."""
    out: list[SevenDaysResult] = []
    for item in payload.get("data", []):
        raffle = item.get("raffle") or {}
        winner = item.get("winner") or {}
        rng = item.get("random_draw_result_winner") or None
        is_iw = bool(raffle.get("is_instant_win"))
        draw_type = "instant_win" if is_iw else ("automated" if rng else "live_or_unspecified")
        r = SevenDaysResult(
            result_id=str(item["id"]),
            raffle_id=str(raffle.get("id")),
            raffle_slug=str(raffle.get("slug")),
            title=str(raffle.get("title") or raffle.get("slug")),
            end_at=raffle.get("end_at"),
            result_at=raffle.get("result_at"),
            is_instant_win=is_iw,
            winning_ticket=_to_int(winner.get("ticket_number") if winner else None),
            draw_type=draw_type,
        )
        if rng:
            r.rng_seed = rng.get("rng_seed")
            r.rng_unix_time = rng.get("unix_time")
            r.rng_index = _to_int(rng.get("winning_index"))
            r.rng_entries = _to_int(rng.get("entries_number"))
            if r.winning_ticket is None:
                r.winning_ticket = _to_int(rng.get("winning_raffle_number"))
        out.append(r)
    return out, payload.get("pagination") or {}


def store(conn: sqlite3.Connection, results: list[SevenDaysResult], snapshot_id: int | None) -> int:
    added = 0
    with transaction(conn):
        ensure_platform(conn, PLATFORM, "7days Performance", BASE)
        for r in results:
            cid = ensure_competition(conn, PLATFORM, r.raffle_slug, r.title)
            if conn.execute(
                "SELECT 1 FROM draw_results WHERE competition_id=? AND external_result_id=?", (cid, r.result_id)
            ).fetchone():
                continue
            insert(conn, "draw_results", {
                "competition_id": cid,
                "drawn_at": r.result_at or r.end_at,
                "winning_ticket_number": r.winning_ticket,
                "tickets_sold_at_draw": r.rng_entries,
                "selection_method": {"automated": "Mersenne Twister (PHP mt_rand) over sold-ticket list",
                                     "instant_win": "pre-allocated instant win"}.get(r.draw_type),
                "independent_rng": "unknown",
                "rng_name": "mt_rand" if r.draw_type == "automated" else None,
                "evidence_url": f"{BASE}/draw-result/{r.raffle_slug}",
                "snapshot_id": snapshot_id,
                "external_result_id": r.result_id,
                "draw_type": r.draw_type,
                "rng_published_seed": r.rng_seed,
                "rng_unix_time": r.rng_unix_time,
                "rng_index": r.rng_index,
                "rng_entries": r.rng_entries,
            })
            added += 1
    return added


def collect(conn: sqlite3.Connection, fetcher: PoliteFetcher, size: int = 100, max_pages: int | None = None) -> dict:
    page, last, added, seen, errors = 1, None, 0, 0, []
    while True:
        res = fetcher.fetch(FEED.format(page=page, size=size))
        if not res.ok:
            errors.append(f"page {page}: {res.outcome} {res.note or ''}")
            break
        try:
            results, pag = parse_page(json.loads(res.text()))
        except (json.JSONDecodeError, KeyError) as exc:
            errors.append(f"page {page}: parse error {exc}")
            break
        seen += len(results)
        added += store(conn, results, res.snapshot_id)
        last = pag.get("last") or last
        log.info("7days page %s/%s: %d results", page, last, len(results))
        if not pag.get("next") or (max_pages and page >= max_pages):
            break
        page += 1
    return {"pages": page, "last": last, "seen": seen, "added": added, "errors": errors}


DETAIL = BASE + "/api/v2/raffle-draw/{slug}/GBP?include_finished=true"


def _pence(v) -> int | None:
    try:
        from decimal import Decimal

        return int((Decimal(str(v)) * 100).to_integral_value())
    except Exception:
        return None


def parse_detail(d: dict) -> dict:
    """Value inputs from a competition record. Names are never read."""
    offers = d.get("offers") or []
    single = next((o for o in offers if o.get("tickets_quantity") == 1), None)
    count = d.get("prize_count") or 1
    end_prizes = d.get("end_prizes") or []
    cash_total = (sum(_pence(p.get("cashAlternative")) or 0 for p in end_prizes) if end_prizes
                  else ((_pence(d.get("cash_alternative")) or 0) * count if d.get("cash_alternative") is not None else None))
    advertised = _pence(d.get("prize_value"))
    return {
        "ticket_price_pence": _pence(single["price"]) if single else None,
        "max_tickets": d.get("max_entries"),
        "tickets_sold": d.get("current_entries"),
        "advertised_value_pence": advertised * count if advertised is not None else None,
        "cash_alternative_pence": cash_total or None,
        "number_of_prizes": count,
        "max_entries_per_person": d.get("ticket_limit_per_user"),
        "closes_at": d.get("end_at"),
        "is_cash_prize": bool(d.get("is_cash")),
    }


def collect_details(conn: sqlite3.Connection, fetcher: PoliteFetcher, slugs: list[str]) -> dict:
    from ..db.database import insert as _insert

    done, errors = 0, []
    for slug in slugs:
        url = DETAIL.format(slug=slug)
        res = fetcher.fetch(url)
        if not res.ok:
            errors.append(f"{slug}: {res.outcome}")
            continue
        try:
            v = parse_detail(json.loads(res.text()))
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"{slug}: parse {exc}")
            continue
        if v["tickets_sold"] is not None and v["max_tickets"] is not None and v["tickets_sold"] > v["max_tickets"]:
            errors.append(f"{slug}: sold > max, skipped")
            continue
        is_cash = v.pop("is_cash_prize")
        with transaction(conn):
            cid = ensure_competition(conn, PLATFORM, slug, slug)
            _insert(conn, "competition_observations", {
                "competition_id": cid,
                "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "snapshot_id": res.snapshot_id,
                "source_url": f"{BASE}/competition/{slug}",
                "tickets_sold_basis": "disclosed_count" if v["tickets_sold"] is not None else "not_disclosed",
                "winner_selection_method": None,
                "prize_description": "cash prize" if is_cash else None,
                **v,
            })
        done += 1
    return {"requested": len(slugs), "stored": done, "errors": errors}
