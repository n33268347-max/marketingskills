"""Shared validation helpers for the edge register (V2).

Complements analysis/uniformity.py (draw tests) and backtest/walkforward.py.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def bootstrap_ci(x, stat=np.mean, n_boot: int = 10_000, alpha: float = 0.05, seed: int = 20261123) -> tuple[float, float, float]:
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    boots = np.array([stat(rng.choice(x, size=len(x), replace=True)) for _ in range(n_boot)])
    return float(stat(x)), float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2))


def beta_posterior(successes: int, n: int, prior=(1.0, 1.0), cred: float = 0.95) -> dict:
    """Bayesian estimate of a proportion with a uniform Beta(1,1) prior."""
    a, b = prior[0] + successes, prior[1] + n - successes
    lo, hi = stats.beta.ppf([(1 - cred) / 2, (1 + cred) / 2], a, b)
    return {"mean": a / (a + b), "cred_low": float(lo), "cred_high": float(hi)}


def binomial_greater(k: int, n: int, p0: float) -> float:
    return float(stats.binomtest(k, n, p0, alternative="greater").pvalue)


def draws_needed_for_detectable_win(p_win_per_entry: float, prob_at_least_one: float = 0.5) -> int:
    """How many independent entries are needed for a given chance of at least one win."""
    return int(np.ceil(np.log(1 - prob_at_least_one) / np.log(1 - p_win_per_entry)))
