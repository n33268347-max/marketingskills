"""H8: can 7days' PUBLISHED automated draws be reproduced from PUBLISHED data?

Operator's own description (archived 2026-11-23): automated draws call PHP
mt_srand(seed) then mt_rand(1, N) to pick a line in the list of sold tickets
sorted by issue time; "The seed: This is calculated from the current time".

This module only re-computes results that have already been published, from
values published alongside them. It never estimates seeds for, or outcomes of,
draws that have not happened.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field

from .php_mt import mt_rand_once

SEED_RULE = "seed = int(round(unix_time * 1000)); index = mt_rand(1, entries)"


def seed_from_unix_time(unix_time: str) -> int:
    whole, _, frac = unix_time.strip().partition(".")
    frac = (frac + "000")[:3]
    return int(whole) * 1000 + int(frac)


@dataclass
class H8Result:
    rule: str = SEED_RULE
    checked: int = 0
    reproduced: int = 0
    by_month: dict = field(default_factory=dict)  # 'YYYY-MM' -> [checked, reproduced]
    first_nonreproducing: str | None = None
    last_reproducing: str | None = None

    @property
    def rate(self) -> float:
        return self.reproduced / self.checked if self.checked else float("nan")


def run(conn: sqlite3.Connection, platform_slug: str = "7days-performance") -> H8Result:
    rows = conn.execute(
        """SELECT d.drawn_at, d.rng_unix_time, d.rng_index, d.rng_entries
           FROM current_draw_results d JOIN competitions c ON c.id = d.competition_id
           WHERE c.platform_slug = ? AND d.draw_type = 'automated'
             AND d.rng_unix_time IS NOT NULL AND d.rng_index IS NOT NULL AND d.rng_entries > 0
           ORDER BY d.drawn_at""",
        (platform_slug,),
    ).fetchall()
    res = H8Result()
    months: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        ok = mt_rand_once(seed_from_unix_time(r["rng_unix_time"]), 1, r["rng_entries"]) == r["rng_index"]
        m = (r["drawn_at"] or "")[:7]
        months[m][0] += 1
        months[m][1] += int(ok)
        res.checked += 1
        res.reproduced += int(ok)
        if ok:
            res.last_reproducing = r["drawn_at"]
        elif res.first_nonreproducing is None:
            res.first_nonreproducing = r["drawn_at"]
    res.by_month = dict(sorted(months.items()))
    return res
