import numpy as np

from raffle_edge.analysis.uniformity import benjamini_hochberg, run_all


def test_fair_draws_rarely_flag():
    # Calibration: under H0, the share of runs with any BH-significant test should be ~<= alpha.
    rng = np.random.default_rng(1)
    flagged = 0
    for i in range(40):
        ns = rng.integers(50, 5000, size=300)
        pos = rng.integers(1, ns + 1)
        if any(f.significant_after_correction for f in run_all(pos, ns, seed=i, sims=300)):
            flagged += 1
    assert flagged <= 6  # 40 runs at FDR 5%: expect ~2; allow sampling slack


def test_off_by_one_bias_is_detected():
    # Implementation bug: the top position can never win and position 1 wins twice as often.
    rng = np.random.default_rng(2)
    ns = np.full(3000, 20)
    pos = rng.integers(0, 20, size=3000)  # 0..19 instead of 1..20
    pos[pos == 0] = 1
    f = {x.hypothesis: x for x in run_all(pos, ns, sims=500)}
    assert f["H4 endpoint (max)"].significant_after_correction
    assert f["H4 endpoint (max)"].statistic == 0


def test_sequential_drift_is_detected():
    ns = np.full(400, 1000)
    pos = (np.arange(400) * 2.5 % 1000 + 1).astype(int)  # strongly autocorrelated
    res = run_all(pos, ns, sims=300)
    assert any(f.hypothesis.startswith("H5") and f.significant_after_correction for f in res)


def test_bh_matches_textbook():
    assert np.allclose(benjamini_hochberg([0.01, 0.04, 0.03, 0.2]), [0.04, 0.16 / 3, 0.16 / 3, 0.2])
