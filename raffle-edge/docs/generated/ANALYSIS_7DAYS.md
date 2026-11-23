# 7days Performance: draw audit and integrity tests

_Generated 2026-11-23 by `raffle-edge analyze 7days-performance`. Do not edit by hand._

Source: the public draw-results feed. Winner names are dropped at ingest.
Results span 2010-01-01T00:00:00+00:00 → 2026-11-22T22:00:00+00:00. By type: automated: 766, instant_win: 704, live_or_unspecified: 180.

## H8: reproducing published automated draws

Rule tested (from the operator's own description): `seed = int(round(unix_time * 1000)); index = mt_rand(1, entries)`.
It is checked against the published `unix_time`, `winning_index` and `entries_number`, and is applied to past, published draws only.

- Automated draws checked: **766**
- Reproduced exactly: **303** (39.6%)
- Last draw that reproduces: 2026-10-07T22:00:00+01:00
- First draw that does not reproduce: 2026-08-05T22:00:00+01:00

| Month | Checked | Reproduced | Rate |
|---|---|---|---|
| 2026-05 | 41 | 41 | 100% |
| 2026-06 | 119 | 119 | 100% |
| 2026-07 | 130 | 130 | 100% |
| 2026-08 | 125 | 12 | 10% |
| 2026-09 | 128 | 0 | 0% |
| 2026-10 | 120 | 1 | 1% |
| 2026-11 | 103 | 0 | 0% |

By chance alone, a wrong rule reproduces a draw with probability 1/entries, which is about 0 for these sizes. Any non-trivial reproduction rate therefore confirms the rule for those draws. Where draws stop reproducing, either the seed derivation changed or something else feeds the seed (for example the published `rng_seed` hash). This needs an explanation from the operator before any conclusion is drawn.

## H3–H5: is the winning position uniform over the entry list?

Under H0, `winning_index` is uniform on 1..`entries_number` (the operator draws a line of the sold-ticket list).

n = 766 automated draws; entries per draw: median 2864, min 187, max 2538131.

| Hypothesis | Test | n | Statistic | p | BH-adjusted p | Effect | 95% interval | Significant after correction |
|---|---|---|---|---|---|---|---|---|
| H3 uniform positions | chi-square on 10 bins of randomized PIT (Monte Carlo) | 766 | 12.09 | 0.2024 | 0.4688 | Cohen's w = 0.126 | — | no |
| H3 uniform positions | Kolmogorov–Smirnov vs U(0,1) on randomized PIT | 766 | 0.04287 | 0.1164 | 0.4688 | KS D = 0.043 | — | no |
| H4 endpoint (min) | min-position hit count vs Poisson-binomial null (Monte Carlo, two-sided) | 766 | 0 | 1.0000 | 1.0000 | observed/expected ratio = 0.000 | [0.000, 6.249] | no |
| H4 endpoint (max) | max-position hit count vs Poisson-binomial null (Monte Carlo, two-sided) | 766 | 0 | 1.0000 | 1.0000 | observed/expected ratio = 0.000 | [0.000, 6.249] | no |
| H5 independence | Wald–Wolfowitz runs test (normal approx.) | 766 | 376 | 0.5691 | 0.8536 | z = -0.569 | — | no |
| H5 independence | lag-1 autocorrelation (permutation) | 766 | 0.04229 | 0.2344 | 0.4688 | autocorrelation r = 0.042 | [-0.070, 0.070] | no |

Limitations:

- CI shown is the permutation null band, not a CI for r.
- Expected hits only 0.59; very low power unless N is small. CI is for the ratio.
- Randomized PIT adds noise for small N; power is lowest when N is small.
- These tests check the draw step only (index within the list). They cannot check how ticket numbers were allocated, or whether the published list is complete.
- **Independent validation:** not yet done. A significant result must be re-tested on draws collected after this report (a hold-out) before it counts as a finding.
- A historical pattern is not evidence of future predictability.
