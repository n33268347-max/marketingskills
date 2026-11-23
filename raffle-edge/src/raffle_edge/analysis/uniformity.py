"""Phase 4: integrity tests for winning positions (H3, H4, H5).

Input is a time-ordered list of (position, N): the winning position in 1..N,
where N is the size of the set the winner was drawn from under H0 (see plan
§5.1; e.g. 7days automated draws: winning_index in 1..entries_number).

Every test reports sample size, statistic, p-value (Monte Carlo calibrated
under H0 with the SAME N values), effect size, a 95% interval where
meaningful, and limitations. p-values are adjusted with Benjamini–Hochberg
across the family returned by `run_all`.

A historical pattern is not evidence of future predictability. A significant
result here is a prompt for investigation and responsible disclosure, never a
betting signal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
from scipy import stats

DEFAULT_SIMS = 2000


@dataclass
class Finding:
    hypothesis: str
    test: str
    n: int
    statistic: float
    p_value: float
    effect_size: float | None
    effect_label: str
    ci95: tuple[float, float] | None = None
    p_adjusted: float | None = None
    significant_after_correction: bool | None = None
    limitations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def _validate(pos: np.ndarray, n: np.ndarray) -> None:
    if pos.shape != n.shape or pos.ndim != 1 or len(pos) == 0:
        raise ValueError("positions and N must be equal-length 1-D, non-empty")
    if np.any(n < 1) or np.any(pos < 1) or np.any(pos > n):
        raise ValueError("each position must be within 1..N")


def randomized_pit(pos: np.ndarray, n: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Exact Uniform(0,1) under H0 for discrete uniform positions: u=(pos-1+V)/N, V~U(0,1)."""
    return (pos - 1 + rng.random(len(pos))) / n


def _simulate_positions(n: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return rng.integers(1, n + 1)


def _mc_p(observed: float, sims: np.ndarray, greater: bool = True) -> float:
    # (b + 1) / (B + 1) estimator: never returns 0.
    b = np.sum(sims >= observed) if greater else np.sum(sims <= observed)
    return float((b + 1) / (len(sims) + 1))


def chi_square_deciles(pos, n, rng, sims=DEFAULT_SIMS, bins=10) -> Finding:
    def stat(p):
        u = randomized_pit(p, n, rng)
        counts = np.histogram(u, bins=bins, range=(0, 1))[0]
        exp = len(u) / bins
        return float(((counts - exp) ** 2 / exp).sum())

    obs = stat(pos)
    null = np.array([stat(_simulate_positions(n, rng)) for _ in range(sims)])
    w = float(np.sqrt(obs / len(pos)))
    return Finding("H3 uniform positions", f"chi-square on {bins} bins of randomized PIT (Monte Carlo)", len(pos), obs,
                   _mc_p(obs, null), w, "Cohen's w",
                   limitations=["Randomized PIT adds noise for small N; power is lowest when N is small."])


def ks_uniform(pos, n, rng) -> Finding:
    u = randomized_pit(pos, n, rng)
    res = stats.kstest(u, "uniform")
    return Finding("H3 uniform positions", "Kolmogorov–Smirnov vs U(0,1) on randomized PIT", len(pos),
                   float(res.statistic), float(res.pvalue), float(res.statistic), "KS D")


def endpoint_test(pos, n, rng, which: str = "max", sims=DEFAULT_SIMS) -> Finding:
    """H4: does the lowest ('min') or highest ('max') position win at rate 1/N?

    Tested separately: a classic off-by-one bug moves wins from one end to the
    other, which a combined count would not detect.
    """
    target = np.ones_like(n) if which == "min" else n
    hits = int(np.sum(pos == target))
    expected = float(np.sum(1.0 / n))
    null = np.array([np.sum(s == target) for s in (_simulate_positions(n, rng) for _ in range(sims))])
    p_two = min(1.0, 2 * min(_mc_p(hits, null, True), _mc_p(hits, null, False)))
    lo, hi = stats.poisson.interval(0.95, hits) if hits else (0.0, 3.69)
    return Finding(f"H4 endpoint ({which})", f"{which}-position hit count vs Poisson-binomial null (Monte Carlo, two-sided)",
                   len(pos), float(hits), p_two, (hits / expected) if expected else None, "observed/expected ratio",
                   ci95=(float(lo) / expected, float(hi) / expected) if expected else None,
                   limitations=[f"Expected hits only {expected:.2f}; very low power unless N is small. CI is for the ratio."])


def runs_test(pos, n, rng) -> Finding:
    """H5: Wald–Wolfowitz runs above/below 0.5 on the PIT series in time order."""
    u = randomized_pit(pos, n, rng)
    x = u > 0.5
    n1, n2 = int(x.sum()), int((~x).sum())
    runs = 1 + int(np.sum(x[1:] != x[:-1]))
    if n1 == 0 or n2 == 0:
        return Finding("H5 independence", "runs test", len(u), float(runs), 1.0, None, "z", limitations=["degenerate"])
    mu = 2 * n1 * n2 / (n1 + n2) + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
    z = (runs - mu) / np.sqrt(var)
    return Finding("H5 independence", "Wald–Wolfowitz runs test (normal approx.)", len(u), float(runs),
                   float(2 * stats.norm.sf(abs(z))), float(z), "z")


def lag_autocorrelation(pos, n, rng, lag=1, sims=DEFAULT_SIMS) -> Finding:
    u = randomized_pit(pos, n, rng)
    if len(u) <= lag + 2:
        raise ValueError("series too short")

    def ac(v):
        a, b = v[:-lag] - v.mean(), v[lag:] - v.mean()
        return float((a * b).sum() / ((v - v.mean()) ** 2).sum())

    obs = ac(u)
    null = np.array([ac(rng.permutation(u)) for _ in range(sims)])
    return Finding("H5 independence", f"lag-{lag} autocorrelation (permutation)", len(u), obs,
                   _mc_p(abs(obs), np.abs(null)), obs, "autocorrelation r",
                   ci95=(float(np.quantile(null, 0.025)), float(np.quantile(null, 0.975))),
                   limitations=["CI shown is the permutation null band, not a CI for r."])


def benjamini_hochberg(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    prev = 1.0
    for rank, idx in reversed(list(enumerate(order, start=1))):
        prev = min(prev, pvals[idx] * m / rank)
        adj[idx] = prev
    return adj.tolist()


def run_all(positions, ns, seed: int = 20261123, sims: int = DEFAULT_SIMS, alpha: float = 0.05) -> list[Finding]:
    pos, n = np.asarray(positions, dtype=np.int64), np.asarray(ns, dtype=np.int64)
    _validate(pos, n)
    rng = np.random.default_rng(seed)
    findings = [chi_square_deciles(pos, n, rng, sims), ks_uniform(pos, n, rng),
                endpoint_test(pos, n, rng, "min", sims), endpoint_test(pos, n, rng, "max", sims),
                runs_test(pos, n, rng)]
    if len(pos) > 5:
        findings.append(lag_autocorrelation(pos, n, rng, 1, sims))
    adj = benjamini_hochberg([f.p_value for f in findings])
    for f, a in zip(findings, adj):
        f.p_adjusted = a
        f.significant_after_correction = a < alpha
        if f.n < 200:
            f.limitations.append(f"n={f.n} is small; only large deviations are detectable (plan §5.3).")
    return findings
