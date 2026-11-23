"""A2: paid tickets in undersold competitions.

Three levels of information, kept strictly apart:
  ex-ante floor   - V/(max+k) vs price: uses only what is published before buying.
  ex-ante current - needs sales counts observed BEFORE close (forward data; not available historically).
  perfect hindsight - final sold count known. An UPPER BOUND on any strategy, not a strategy.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path


def load(path: Path) -> list[dict]:
    rows = []
    for r in csv.DictReader(open(path)):
        if r["cash_value_pence"]:
            rows.append({"competition": r["competition"], "end_at": r["end_at"], "price": int(r["ticket_price_pence"]),
                         "max": int(r["max_tickets"]), "sold": int(r["tickets_sold"]), "value": int(r["cash_value_pence"]),
                         "limit": int(r["ticket_limit_per_user"]) if r["ticket_limit_per_user"] else None})
    return rows


def ex_ante_floor_positive(rows: list[dict]) -> list[dict]:
    """Competitions where one paid ticket is positive EV even if every ticket sells."""
    return [r for r in rows if r["value"] / r["max"] > r["price"]]


def optimal_k(value: float, others: int, price: float, limit: int | None, available: int) -> tuple[int, float]:
    """Maximise k*V/(others+k) - k*price over integer k (concave in k)."""
    if price <= 0 or others <= 0:
        return 0, 0.0
    k_star = math.sqrt(value * others / price) - others
    best = (0, 0.0)
    for k in {max(0, math.floor(k_star)), max(0, math.ceil(k_star)), 1}:
        k = min(k, available, limit if limit else k)
        if k <= 0:
            continue
        p = k * value / (others + k) - k * price
        if p > best[1]:
            best = (k, p)
    return best


def perfect_hindsight_bound(rows: list[dict]) -> dict:
    total_profit, total_spend, comps = 0.0, 0.0, []
    for r in rows:
        k, profit = optimal_k(r["value"], r["sold"], r["price"], r["limit"], r["max"] - r["sold"])
        if k > 0 and profit > 0:
            comps.append({**r, "k": k, "profit_pence": profit})
            total_profit += profit
            total_spend += k * r["price"]
    return {"competitions": len(rows), "profitable": len(comps), "total_profit_pence": total_profit,
            "total_spend_pence": total_spend, "detail": comps}
