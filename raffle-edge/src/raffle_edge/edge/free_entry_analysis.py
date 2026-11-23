"""A3: free postal entry route as a source of expected value.

Mechanics (7days, confirmed from its terms and competition records):
  * a postcard earns `tickets_per_postcard` tickets (observed: ceil(91p / price), min 1);
  * postal tickets join the same draw as paid tickets;
  * multiple postcards are allowed up to the per-person entry limit, each posted separately.

Ex-ante floor: the final number of tickets in the draw is at most max_tickets,
so EV per postcard >= t * V / (max_tickets + t) - cost. That floor uses only
information published BEFORE entry, so it involves no hindsight.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .monte_carlo import Entry, simulate

STAMP_2ND_CLASS_PENCE = 91  # Royal Mail from 7 Apr 2026 (press reports; Lucky Day terms use the same 91p figure)


@dataclass
class Costs:
    stamp_pence: float = STAMP_2ND_CLASS_PENCE
    postcard_pence: float = 15.0      # ASSUMPTION: plain postcard bought in packs; not sourced
    minutes_per_card: float = 3.0     # ASSUMPTION: write, address, post
    hourly_value_pence: float = 0.0   # time valued at zero by default; set e.g. 1271 for £12.71/h

    @property
    def per_card(self) -> float:
        return self.stamp_pence + self.postcard_pence + self.minutes_per_card / 60 * self.hourly_value_pence


@dataclass
class Comp:
    competition: str
    end_at: str
    price: int
    max_tickets: int
    sold: int
    t: int
    value: int
    limit: int | None

    def ev_floor_card(self) -> float:       # ex-ante: assumes the draw fills to max
        return self.t * self.value / (self.max_tickets + self.t)

    def ev_realised_card(self) -> float:    # ex-post: final sold count (others) + this card
        others = min(self.sold, self.max_tickets - self.t)
        return self.t * self.value / (others + self.t)


def load(path: Path) -> list[Comp]:
    out = []
    for r in csv.DictReader(open(path)):
        if not r["cash_value_pence"] or not r["tickets_per_postcard"]:
            continue
        out.append(Comp(r["competition"], r["end_at"], int(r["ticket_price_pence"]), int(r["max_tickets"]), int(r["tickets_sold"]),
                        int(r["tickets_per_postcard"]), int(r["cash_value_pence"]),
                        int(r["ticket_limit_per_user"]) if r["ticket_limit_per_user"] else None))
    return sorted(out, key=lambda c: c.end_at)


def rule_selected(comps: list[Comp], costs: Costs, margin: float = 1.0) -> list[Comp]:
    """Pre-registered rule: post a card only if the EX-ANTE floor EV exceeds cost x margin."""
    return [c for c in comps if c.ev_floor_card() > costs.per_card * margin]


def validate_time_split(comps: list[Comp], costs: Costs, split_at: str) -> dict:
    """The rule has no fitted parameters; the split checks it holds in a later period too."""
    res = {}
    for name, part in (("train", [c for c in comps if c.end_at < split_at]), ("test", [c for c in comps if c.end_at >= split_at])):
        sel = rule_selected(part, costs)
        res[name] = {
            "competitions": len(part), "selected": len(sel),
            "mean_ev_floor_per_card_p": (sum(c.ev_floor_card() for c in sel) / len(sel)) if sel else None,
            "mean_ev_realised_per_card_p": (sum(c.ev_realised_card() for c in sel) / len(sel)) if sel else None,
            "share_realised_above_cost": (sum(c.ev_realised_card() > costs.per_card for c in sel) / len(sel)) if sel else None,
        }
    return res


def budget_portfolio(comps: list[Comp], costs: Costs, budget_pence: float, cards_per_comp: int = 1) -> list[Entry]:
    """Spread a budget over the selected competitions, best ex-ante floor first, ignoring hindsight."""
    entries: list[Entry] = []
    spent = 0.0
    for c in sorted(rule_selected(comps, costs), key=lambda c: -c.ev_floor_card() / costs.per_card):
        cap = cards_per_comp if c.limit is None else min(cards_per_comp, max(1, c.limit // c.t))
        for _ in range(cap):
            if spent + costs.per_card > budget_pence:
                return entries
            # realised odds: one card's t tickets among final sold + t
            others = min(c.sold, c.max_tickets - c.t)
            entries.append(Entry(p_win=c.t / (others + c.t), prize_pence=c.value, cost_pence=costs.per_card))
            spent += costs.per_card
    return entries


def simulate_budget(comps, costs, budget_pence, cards_per_comp=1, sims=200_000):
    return simulate(budget_portfolio(comps, costs, budget_pence, cards_per_comp), sims=sims)
