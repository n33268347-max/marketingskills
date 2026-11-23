# Phases 2–7 report: first results on 7days Performance

_2026-11-23. Generated figures: `docs/generated/ANALYSIS_7DAYS.md`. Hypothesis ledger: the `hypothesis_runs` table._

## 1. What was completed

| Phase | Built | Evidence |
|---|---|---|
| 2: historical database | 7days collector for the public draw-results feed. Winner names are dropped before storage. RNG audit columns were added to `draw_results` (additive migration). Value inputs come from per-competition records. | 1,650 results (766 automated, 704 instant win, 180 live/other), May–Nov 2026. 200 randomly sampled competitions with full value inputs. |
| 3: value calculator | `calculator/value.py`. It computes EV, P(win), hypergeometric multi-prize odds, break-even, sensitivity and instant-win EV. It keeps advertised, cash-alternative and verified values separate, and makes the draw base (sold or max) explicit. | 9 hand-worked test cases |
| 4: statistical engine | `analysis/uniformity.py`: randomized PIT, Monte Carlo χ², KS, separate min/max endpoint tests, runs test, permutation autocorrelation, Benjamini–Hochberg | Calibration test on fair draws; detects an injected off-by-one bug and injected autocorrelation |
| 5: backtesting | `backtest/walkforward.py`: chronological split, exact random baseline, append-only `hypothesis_runs` ledger | Fair data fails out of sample; real injected bias survives |
| 6: dashboard | A Data dashboard artifact fed by `scripts/export_dashboard.py` (JSON with its code embedded) | Five datasets, no personal data |
| 7: commercial | Desk research on three models (`docs/PHASE7_COMMERCIAL.md`) | Snippet-sourced; needs primary checks and interviews |

**Tests: 68 pass.**

## 2. Findings

### H8: can published automated draws be reproduced? (A: confirmed method; B: observation)

**Method.** 7days' own page says automated draws run `mt_srand(seed)` and then `mt_rand(1, entries)`, and pick the winning line of the sold-ticket list. We ported PHP's `mt_rand` and checked the port against the operator's published example: `mt_srand(1234560987123); mt_rand(1,100)` returns 55.

| Period | Published seed | Draws | Reproduced |
|---|---|---|---|
| May – 3 Aug 2026 | 13-digit millisecond timestamp | 302 | **302 (100%)** |
| 5 Aug – 20 Oct 2026 | integers of varying length | 315 | 0 |
| 21 Oct 2026 – now | 64-character hex | 149 | 0 |

- A wrong rule would match by chance only about 0.38 times across the 464 later draws. 1 matched.
- **Interpretation.** Before 4 August, every automated draw is independently verifiable, which is a strong transparency result. After that date the published verification method no longer matches the published data.
- **What this does not show.** It is no evidence of wrongdoing, and it gives entrants no edge: tickets are randomly allocated and the sold list is fixed at close.
- **Next step.** Ask the operator (draft in `docs/disclosure/7DAYS_ENQUIRY_DRAFT.md`, not sent).
- **Deliberately not done.** No attempt to reverse-engineer the new seed. If it comes from a cryptographic RNG, predicting it is out of scope by design.

### H3–H5: are winning positions uniform and independent? (B: statistical observation)

The data is 766 automated draws. Entries per draw range from 187 to 2,538,131, with a median of 2,864.

| Test | p | BH-adjusted p | Effect |
|---|---|---|---|
| χ² (10 bins, Monte Carlo) | 0.20 | 0.47 | Cohen's w = 0.126 |
| Kolmogorov–Smirnov | 0.12 | 0.47 | D = 0.043 |
| Endpoint, min position | 1.00 | 1.00 | 0 hits vs 0.59 expected |
| Endpoint, max position | 1.00 | 1.00 | 0 hits vs 0.59 expected |
| Runs test | 0.57 | 0.85 | z = −0.57 |
| Lag-1 autocorrelation | 0.23 | 0.47 | r = 0.042 |

**No deviation was detected.** The endpoint tests have almost no power at these entry counts. Chi-square power at n = 766 is adequate only for effects of roughly w ≥ 0.15.

**Walk-forward test.** The "hot decile" from training (decile 5, 12.5% in training) hit 12.3% in the test window (n = 351, 95% CI 9.0–16.1%, p = 0.098). **Not supported.** It would not be actionable anyway, because entrants cannot choose list positions.

### H1: do undersold draws ever pay? (B: statistical observation, ex-post)

The sample is 200 randomly chosen finished automated-draw competitions (seed 20261123). Each is valued as one extra ticket bought at close.

| Value basis | EV > 0 | 95% CI | Mean EV per ticket |
|---|---|---|---|
| Cash alternative (conservative) | **3 / 200 (1.5%)** | 0.5%–4.3% | −38.2p |
| Advertised value (operator's figure) | 11 / 200 (5.5%) | 3.1%–9.6% | −24.4p |

- The three positive cases were tiny: +5.3p, +1.1p and +0.04p per ticket.
- At cash value, the median return was **55p per £1** spent.
- Fill rate: median 80%, lower quartile 67%, sold out 44/200.
- **Interpretation.** The structural condition for H1 exists: draws go ahead regardless of sales. In practice, competitions almost never close undersold enough to give a ticket positive value at cash value, and when they do, the edge is pennies. This is an ex-post upper bound, because a buyer cannot know the final count. **H1 is not supported as a source of advantage.**

### Overall answer so far

No measurable entrant advantage was found at 7days Performance:
- Draws look fair.
- Pattern strategies fail out of sample, and the ticket system makes them impossible to act on anyway.
- Undersold positive-value draws are rare and worth pennies.

The one substantive finding is about **auditability**: a fully verifiable draw process silently stopped being verifiable.

## 3. Missing information

- The operator's explanation of the August and October seed changes.
- H1 forward test: observations of **open** competitions shortly before close. The public list endpoint (`api/v2/raffle-draws/`) has not been examined yet.
- Other platforms: Rev Comps (entry lists, Crawl-delay 60 s), Elite and Lucky Day (winning numbers), DCG (closed competition pages). BOTB and Click are manual-only.
- Independent prize valuation (H7): we rely on the operator's cash alternative.
- Phase 7: primary-source checks of the snippet figures, and customer interviews.

## 4. Assumptions

- The operator's published `entries_number` equals the sold-ticket list used for the draw.
- The cash alternative is an achievable value for the prize. For cash prizes, the prize title ("£250 Tax Free Cash") is taken as evidence that the prize is cash, because the feed's `is_cash` flag is unreliable.
- The 200-competition sample represents automated-draw competitions. Live-draw and instant-win formats are not covered.
- `latest_observations` reflects final counts for finished competitions. They were observed after close.

## 5. Recommendation

1. **Send the 7days enquiry** (your decision; draft ready).
2. **Treat Model 3 as the business direction to test** (draw-integrity auditing for operators against DCMS Code clause 2.2). The project's real demonstrated capability is reproducing and statistically auditing published draws, not finding an entrant edge. Run the interview plan in `docs/PHASE7_COMMERCIAL.md` before building anything paid.
3. **Keep H1 open only as a forward test** on one more platform with published sold counts (Rev Comps), so the negative result is not specific to one operator.
4. **Commercial use of collected data needs legal advice** on database right and on each operator's terms.
