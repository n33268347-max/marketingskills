import numpy as np
import pytest

from raffle_edge.backtest.walkforward import decile_strategy, record
from raffle_edge.db.database import ImmutableRecordError, transaction


def _dates(k):
    return [f"2026-{1 + i // 100:02d}-{1 + (i % 28):02d}" for i in range(k)]


def test_fair_draws_fail_out_of_sample():
    rng = np.random.default_rng(3)
    n = rng.integers(100, 5000, 600)
    pos = rng.integers(1, n + 1)
    r = decile_strategy(_dates(600), pos, n, "2026-04-01")
    assert r.train_rate > 0.1  # in-sample "pattern" always looks good ...
    assert r.outcome == "not_supported"  # ... and fails out of sample


def test_real_bias_survives_out_of_sample():
    rng = np.random.default_rng(4)
    n = np.full(600, 1000)
    pos = rng.integers(1, 1001, 600)
    biased = np.where(rng.random(600) < 0.3, rng.integers(1, 101, 600), pos)  # 30% extra mass in decile 0
    r = decile_strategy(_dates(600), biased, n, "2026-04-01")
    assert r.chosen_decile == 0 and r.outcome == "supported"


def test_ledger_is_append_only(conn):
    rng = np.random.default_rng(5)
    n = np.full(200, 100)
    r = decile_strategy(_dates(200), rng.integers(1, 101, 200), n, "2026-02-01")
    rid = record(conn, r, "demo", "synthetic")
    with pytest.raises(ImmutableRecordError):
        with transaction(conn):
            conn.execute("UPDATE hypothesis_runs SET outcome='supported' WHERE id=?", (rid,))
