"""Monte Carlo simulation of what a real entrant would experience.

Positive expected value is not the same as a likely profit: prize draws have
tiny win probabilities, so a small budget usually loses everything even when
each entry has positive EV. This module quantifies that.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Entry:
    p_win: float        # probability this entry (or bundle of tickets) wins
    prize_pence: float  # value if it wins (cash basis)
    cost_pence: float   # money cost of this entry


@dataclass
class PortfolioOutcome:
    n_entries: int
    total_cost_pence: float
    expected_return_pence: float
    expected_profit_pence: float
    p_any_win: float
    p_profit: float
    profit_quantiles_pence: dict
    sims: int


def simulate(entries: list[Entry], sims: int = 200_000, seed: int = 20261123) -> PortfolioOutcome:
    rng = np.random.default_rng(seed)
    p = np.array([e.p_win for e in entries])
    v = np.array([e.prize_pence for e in entries])
    cost = float(sum(e.cost_pence for e in entries))
    wins = np.zeros(sims)
    any_win = np.zeros(sims, dtype=bool)
    for start in range(0, len(entries), 256):  # chunked to bound memory
        hit = rng.random((sims, len(p[start:start + 256]))) < p[start:start + 256]
        wins += hit @ v[start:start + 256]
        any_win |= hit.any(axis=1)
    profit = wins - cost
    qs = {q: float(np.quantile(profit, q)) for q in (0.05, 0.5, 0.95, 0.99)}
    exp_ret = float((p * v).sum())
    return PortfolioOutcome(len(entries), cost, exp_ret, exp_ret - cost, float(any_win.mean()),
                            float((profit > 0).mean()), qs, sims)
