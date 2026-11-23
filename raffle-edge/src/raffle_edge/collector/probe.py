"""Accessibility probe: what can be read from a platform, politely and legally."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone

from ..db.database import insert, transaction
from ..registry import Platform
from .fetcher import PoliteFetcher

log = logging.getLogger(__name__)


def probe_platform(conn: sqlite3.Connection, fetcher: PoliteFetcher, platform: Platform) -> list[dict]:
    targets = [("homepage", platform.base_url.rstrip("/") + "/")]
    if platform.results_url:
        targets.append(("results", platform.results_url))
    if platform.terms_url:
        targets.append(("terms", platform.terms_url))

    rows: list[dict] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rp = fetcher.robots_for(platform.base_url)
    rows.append({
        "platform_slug": platform.slug, "probed_at": now, "target": "robots",
        "url": platform.base_url.rstrip("/") + "/robots.txt",
        "outcome": "ok" if rp is not None else "unavailable",
        "robots_allowed": None, "http_status": None, "snapshot_id": None,
        "note": None if rp is not None else "robots.txt unreachable or challenged: all paths treated as disallowed",
    })
    for target, url in targets:
        res = fetcher.fetch(url)
        rows.append({
            "platform_slug": platform.slug, "probed_at": now, "target": target, "url": url,
            "outcome": res.outcome, "http_status": res.status,
            "robots_allowed": 0 if res.outcome == "blocked_by_robots" else (1 if rp is not None else 0),
            "snapshot_id": res.snapshot_id, "note": res.note,
        })
    with transaction(conn):
        for r in rows:
            insert(conn, "probes", r)
    return rows
