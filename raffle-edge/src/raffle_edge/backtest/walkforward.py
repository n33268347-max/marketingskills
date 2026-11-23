"""Phase 5: walk-forward tests of "pattern" hypotheses against a random baseline.

Rules enforced here:
  * Chronological split only. The pattern is CHOSEN on the training window
    and SCORED on the later test window. No test-window data is visible
    when choosing.
  * Baseline = random entry, i.e. the hit rate a pattern-free ticket gets.
  * Every run is written to the append-only `hypothesis_runs` ledger,
    including failures.

Pattern tested (H3-strategy): "the decile of the entry list that won most
often in training will win more often than 10% in testing." If draws are
fair, the test hit rate should be ~10% and the hypothesis should fail.

Note on actionability: at operators that allocate ticket numbers randomly
(e.g. 7days), an entrant cannot choose a list position at all, so even a
'supported' result here would not be a usable strategy.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import numpy as np
from scipy import stats

from .. import __version__
from ..db.database import insert, transaction


@dataclass
class WalkForwardResult:
    split_at: str
    n_train: int
    n_test: int
    chosen_decile: int
    train_rate: float
    test_rate: float
    baseline: float
    p_value: float
    ci: tuple[float, float]
    outcome: str


def decile_strategy(dates: list[str], pos: np.ndarray, n: np.ndarray, split_at: str, alpha: float = 0.05) -> WalkForwardResult:
    dates_arr = np.array(dates)
    train, test = dates_arr < split_at, dates_arr >= split_at
    if train.sum() < 50 or test.sum() < 50:
        raise ValueError("need >= 50 draws in each window")
    dec = np.minimum(((pos - 1) * 10) // n, 9)  # decile of the position within 1..N
    counts = np.bincount(dec[train], minlength=10)
    chosen = int(np.argmax(counts))
    train_rate = counts[chosen] / train.sum()
    hits = int(np.sum(dec[test] == chosen))
    m = int(test.sum())
    # Exact baseline per draw: share of positions 1..N falling in the chosen decile.
    lo_edge = np.ceil(chosen * n[test] / 10).astype(int) + 1
    hi_edge = np.ceil((chosen + 1) * n[test] / 10).astype(int)
    base = float(np.mean((np.minimum(hi_edge, n[test]) - lo_edge + 1) / n[test]))
    p = float(stats.binomtest(hits, m, base, alternative="greater").pvalue)
    ci = stats.binomtest(hits, m).proportion_ci(0.95)
    outcome = "supported" if p < alpha and ci.low > base else "not_supported"
    return WalkForwardResult(split_at, int(train.sum()), m, chosen, float(train_rate), hits / m, base, p,
                             (float(ci.low), float(ci.high)), outcome)


def record(conn: sqlite3.Connection, r: WalkForwardResult, platform: str, dataset: str) -> int:
    with transaction(conn):
        return insert(conn, "hypothesis_runs", {
            "hypothesis_id": "H3-strategy", "platform_slug": platform,
            "method": "walk-forward: pick most frequent winning decile in train, score hit rate in test; one-sided binomial vs exact baseline",
            "train_period": f"< {r.split_at}", "test_period": f">= {r.split_at}", "n_train": r.n_train, "n_test": r.n_test,
            "metric": f"hit rate of decile {r.chosen_decile}", "train_value": r.train_rate, "test_value": r.test_rate,
            "baseline_value": r.baseline, "p_value": r.p_value, "ci_low": r.ci[0], "ci_high": r.ci[1],
            "outcome": r.outcome, "code_version": __version__, "notes": dataset,
        })
