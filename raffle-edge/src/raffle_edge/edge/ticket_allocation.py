"""A4: ticket-number mechanics.

Mathematical point: when the winner is drawn uniformly from the SOLD tickets,
every sold ticket has probability 1/sold whatever its number. Choosing or
receiving a particular number cannot change the odds. The only empirical
question is whether the operator's process matches that description.

Empirical check (7days): with random allocation from 1..max, the winning
ticket NUMBER should be uniform on 1..max.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy import stats


def winning_number_uniformity(frozen_draws: Path, processed: Path) -> dict:
    maxes = {r["competition"]: int(r["max_tickets"]) for r in csv.DictReader(open(processed))}
    pairs = []
    for d in csv.DictReader(open(frozen_draws)):
        if d["competition"] in maxes and d["draw_type"] == "automated" and d["winning_ticket_number"]:
            pairs.append((int(d["winning_ticket_number"]), maxes[d["competition"]]))
    w = np.array([p[0] for p in pairs]); m = np.array([p[1] for p in pairs])
    ok = (w >= 1) & (w <= m)
    u = (w[ok] - 0.5) / m[ok]
    ks = stats.kstest(u, "uniform")
    return {"n": int(ok.sum()), "out_of_range": int((~ok).sum()), "ks_D": float(ks.statistic), "ks_p": float(ks.pvalue),
            "deciles": np.histogram(u, bins=10, range=(0, 1))[0].tolist()}
