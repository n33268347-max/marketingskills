# Raffle Edge: Research & Development Plan

_Version 0.2 · 2026-11-23 · Status: Phase 1 and 1b complete (155 claims directly confirmed; see PHASE1_REPORT.md)_

## 1. Objective and prior expectations

**Objective:** find out whether any UK online prize competition gives a *legitimate, measurable* edge, and if so where. Then judge whether the research could support a business.

The plan states the starting prior up front, so it can be tested rather than quietly assumed:

- **Draw randomness.** A competently built draw has no exploitable pattern. Examples are a live ball machine, `random_int`, PromoVeritas or a GLI-certified engine. **The default expectation is a null result** for every "pattern in winning numbers" test. A null result is a valid finding and will be published as one.
- **Value.** The most plausible real edge is *mathematical value*, not prediction. Several operators reportedly draw "regardless of tickets sold". When such a competition closes undersold, a ticket's expected value can exceed its price. That needs no RNG weakness, only accurate sold/total counts and prize values.
- **Implementation defects.** If a draw has a defect, it is most likely an engineering bug rather than a predictable RNG. Examples:
  - off-by-one ranges, where ticket 1 or the maximum ticket can never win
  - modulo bias
  - drawing from the full range when only sold tickets should be eligible
  - instant-win allocation leaks

  These show up as distributional anomalies across many draws. Any such finding goes to **responsible disclosure**, not exploitation (see `COMPLIANCE.md`).

## 2. Hypothesis register

Every hypothesis is pre-registered here before data is examined. Failed hypotheses are kept and marked, never deleted.

| ID | Hypothesis | Type | Data needed | Test | Status |
|---|---|---|---|---|---|
| H1 | Some competitions that draw regardless of sell-out close with EV per ticket > price | Value | prize value, ticket price, **final tickets sold**, max tickets | Exact EV per competition; share with EV > price; CI by bootstrap over competitions | Open, needs Phase 2 data |
| H2 | Instant-win competitions with publicly listed remaining winning numbers have time-varying EV that sometimes exceeds the price | Value | remaining prize list, tickets remaining, over time | EV trajectory; prevalence of EV > price | Open |
| H3 | Winning ticket positions are uniform on the eligible range (null) | Integrity | winning number, range, **allocation method** | χ² on normalised positions, KS, runs test, endpoint test | Open, expected to hold |
| H4 | Endpoint tickets (min/max) win at the expected 1/N rate | Integrity (off-by-one) | as H3 | Binomial test pooled across draws | Open |
| H5 | Draw-to-draw winning positions are independent | Integrity | ordered series per platform | Lag-k autocorrelation, Ljung–Box, permutation test | Open |
| H6 | The free postal route has higher EV per £ than paid entry on low-price competitions | Value | stamp cost, entries per postcard, ticket price | Arithmetic | Open; legal to report, never automated |
| H7 | Advertised prize values exceed independently verified market values | Value accuracy | advertised value, cash alternative, market comparables | Paired ratio with CI | Open |
| H8 | 7days' published seed/index/entry count reproduce each past automated draw (Mersenne Twister, time seed, per operator) | Integrity / audit | published seed, index, entries, winning ticket | Exact reproduction rate; any mismatch → disclosure | Open. Past draws only; no prediction. |

## 3. Research targets: the first ten platforms

Selection criteria: scale or prominence, a raffle-style numbered-ticket format, and public information about draws.

Ranked on the **confirmed** basis after Phase 1b. Exact scores are in `docs/generated/PLATFORM_RANKING.md`.

| Rank | Platform | Why it matters | Automated collection |
|---|---|---|---|
| 1 | 7days Performance | Winning ticket, seed, index, entries and sold/total published per draw. Random allocation. Draws regardless of sell-out. | No prohibition found |
| 2 | Elite Competitions | Winning ticket numbers; GLI-certified allocation RNG; physical ball machine; redraw on unsold | No prohibition found (excessive-traffic clause; ClaudeBot blocked, Claude-User not) |
| 3 | Dream Car Giveaways | `random_int` or live presenter; max entries and % sold; Code signatory | No prohibition found |
| 4 | Rev Comps | Entry lists with total/sold/remaining: best H1 data | No prohibition found (Crawl-delay 60 s) |
| 5 | Lucky Day | Winning numbers back to Oct 2023; not a Code signatory | No prohibition found |
| 6 | Click Competitions | Good data, but **terms prohibit AI/scraping** | **Manual only** |
| 7 | Omaze UK | Market leader; entry codes only, no counts | No prohibition found |
| 8 | BOTB | Spot-the-ball; **terms prohibit AI/scraping** | **Manual only** |
| 9 | Raffle House | JS-rendered; robots disallows /winners | Results disallowed |
| 10 | Raffall | JS-rendered; CAPTCHA on help centre; removed from the Code list | Not readable |

The machine-generated version with exact rubric points is in `docs/generated/PLATFORM_RANKING.md`.

Phase 1 rested on search snippets. Phase 1b replaced most of them with direct, quote-checked reads.

### What each platform can support

| Analysis | Needs | Candidate platforms |
|---|---|---|
| H3/H4/H5 integrity tests | winning number + eligible range + allocation method | 7days, Click, DCG, Elite, Lucky Day (range missing) |
| H1 undersold EV | final sold count + max + price + value | Rev Comps, 7days, DCG (entry lists) |
| H2 instant-win EV | visible remaining winning numbers | DCG, 7days |
| Value comparison only | price + prize | All, including Omaze and BOTB |

## 4. Evidence standard

| Level | Meaning | Requirement | Counts toward |
|---|---|---|---|
| `A_CONFIRMED` | Fact read directly from the primary source | Source URL, access date, archived snapshot, `source_kind` = `primary_direct` or `regulator` | Confirmed score, findings |
| `P_PROVISIONAL` | Reported but not read verbatim (search snippet, third party) | Source URL | Provisional score only (prioritisation) |
| `B_OBSERVATION` | Statistical observation from our own analysis | `analysis_ref` to a reproducible run | Findings, with full stats block |
| `C_HYPOTHESIS` | Needs investigation | None | Nothing |
| `UNKNOWN` | Explicit gap | None | Listed as a gap |

The database enforces these rules with `CHECK` constraints, not just convention.

## 5. Statistical methodology (Phases 4–5)

### 5.1 The null depends on ticket allocation

| Allocation | Eligible winning set under H0 | Normalised position |
|---|---|---|
| Sequential (1..sold) | Uniform on 1..sold | u = (n − 1 + 0.5) / sold |
| Random from 1..max, only sold eligible | Uniform on the *sold* numbers. These are a random subset of 1..max, so marginally uniform on 1..max. | u = (n − 1 + 0.5) / max |
| Player-chosen numbers | **Not** uniform on the range. People favour some numbers. | Do not test positions; test only "drawn among sold" |

**Confirmed in Phase 1b:** Elite, 7days (live and auto), Click auto and Rev Comps auto draw only from sold tickets; Elite and 7days redraw if an unsold number comes up. For these platforms the H0 for H3 is "uniform over the sold set".

Getting this wrong manufactures fake anomalies. Allocation must therefore be `A_CONFIRMED` before running H3 on a platform.

### 5.2 Tests

- **Uniformity:**
  - χ² on deciles of u (pooled across draws with different ranges)
  - Kolmogorov–Smirnov on u
  - Anderson–Darling as a tail-sensitive check
- **Endpoints (off-by-one):** a binomial test that the count of n = min or n = max equals Σ 1/N_i.
- **Independence:** Wald–Wolfowitz runs test above/below the median; lag-1..k autocorrelation; Ljung–Box.
- **Calibration of every test:** Monte Carlo, simulating 10,000 datasets under H0 with the *same* ranges and sample sizes. The observed statistic is then compared to the simulated distribution. This removes reliance on asymptotic approximations.
- **Permutation tests** for any platform-vs-platform or before/after comparison.
- **Multiple testing:** Benjamini–Hochberg FDR at q = 0.05 across the whole family of tests in a run. Holm–Bonferroni where a strict family-wise claim is made.
- **Effect sizes:** Cohen's w for χ², KS D, and the proportion difference with Wilson 95% CI for endpoints.

### 5.3 Power: how much data is needed

These are approximations from Cohen's χ² power tables (df = 9, α = 0.05, power = 0.8):

| Effect size w | Draws needed |
|---|---|
| 0.3 (large) | ~175 |
| 0.2 (medium-small) | ~400 |
| 0.1 (small) | ~1,600 |

Endpoint bias on a range of 10,000 tickets is almost undetectable without enormous samples: expected hits are about 1 in 5,000 draws. Pooling small-range draws, such as instant-win or low-cap competitions, is the only realistic route.

The real Phase 4 power calculation will be done by simulation for each platform's actual mix of ranges.

### 5.4 Validation and backtesting rules (Phase 5)

- **Splits:** chronological only. Train on draws before date T, test after T. Use rolling-origin evaluation.
- **No future leakage:** each backtest step uses only data with `recorded_at` before the decision time. The append-only database makes this auditable.
- **Baseline:** random-entry strategy, same budget, same competitions.
- **Costs:** include ticket price, the payment fee if any, and tax-free prize values at *verified* value, not advertised.
- **Success criteria:** a strategy is "potentially useful" only if:
  - it beats the baseline out of sample with BH-adjusted p < 0.05,
  - the 95% CI of the return difference excludes 0, and
  - it is replicated on a second, later hold-out window.

  Everything else is recorded as a failed hypothesis.

## 6. Value calculator specification (Phase 3)

For a single-prize draw where *you* buy k tickets:

- **N_eff (the draw base):**
  - final tickets sold, if the draw is among sold tickets only
  - max tickets, if unsold numbers can "win" and roll the prize back to the operator. That rule must be confirmed per platform.
- **P(win):** k / N_eff
- **EV:** P(win) × V − k × price
  - V is the verified value, or the cash alternative where one is offered. Report both.
- **Expected return per £:** P(win) × V / (k × price)
- **Break-even sold count:** N* = V / price. If sold < N*, EV > 0.
- **Multi-prize and instant win:** sum over the prizes still available. Use hypergeometric probabilities when buying several tickets, because draws are without replacement.
- **Sensitivity:** report EV across a range of final sold counts. This matters because sold counts at purchase time are not final.

Always show advertised V, cash alternative and verified V separately. Never mix *tickets remaining*, *tickets sold* and *max tickets*.

## 7. Phase plan

| Phase | Deliverable | Exit criteria |
|---|---|---|
| 1 ✅ prototype | Registry of 10 platforms, evidence model, polite collector, immutable DB, ranking, tests | Done, except direct verification (blocked; see Phase 1 report) |
| 1b | Direct verification of top-6 claims; robots.txt review; GOV.UK Code text and signatory list | ≥ 80% of rubric topics `A_CONFIRMED` for the top 6 |
| 2 | Platform-specific parsers for permitted results pages; scheduled collection; manual CSV import path | ≥ 300 draws with range and allocation known, for ≥ 2 platforms |
| 3 | Value calculator (§6) with tests against hand-worked examples | Exact agreement on 20 worked cases |
| 4 | Statistical engine (§5.2) with Monte Carlo calibration and BH correction | Simulated-null false positive rate ≈ α; power curves produced |
| 5 | Backtester (§5.4) | Leakage tests pass; baseline reproduces |
| 6 | Dashboard (FastAPI + React) | Shows ratings, data quality, "insufficient data" flags |
| 7 | Commercial investigation | Customer interviews (≥ 15) before any paid build |

## 8. Architecture

```
raffle-edge/
├── data/seed/platforms.json      # curated, evidence-labelled registry (built by scripts/build_seed.py)
├── data/templates/               # CSV templates for manual transcription
├── data/raw/                     # content-addressed page snapshots (gitignored)
├── data/db/                      # SQLite DB (gitignored; Postgres later if needed)
├── src/raffle_edge/
│   ├── db/            schema.sql (append-only triggers), database.py
│   ├── registry.py    claims + validation
│   ├── ranking.py     transparent rubric
│   ├── collector/     fetcher.py (robots, rate limit, challenge stop), probe.py
│   ├── parsers/       generic.py (no-guess extractor); per-platform parsers in Phase 2
│   ├── ingest.py      observations + draw CSV import
│   ├── reporting.py   generated Markdown
│   └── cli.py
├── tests/             pytest; synthetic fixtures only
└── docs/
```

Planned modules:

| Phase | Module | Built with |
|---|---|---|
| 3 | `calculator/` | Python, standard library |
| 4 | `analysis/` | NumPy, SciPy, statsmodels |
| 5 | `backtest/` | |
| 6 | `api/` | FastAPI |
| 6 | `dashboard/` | Next.js |

## 9. Key risks

| Risk | Mitigation |
|---|---|
| Data access blocked or prohibited by site terms | Robots and terms review per platform; manual transcription; ask operators for data |
| Database right (CRDR 1997) on extracting a substantial part of results | Legal review before any commercial use of collected data |
| False discovery | Pre-registration, Monte Carlo nulls, FDR, out-of-sample replication |
| Undersold-EV edge is real but tiny or short-lived | Report the prevalence honestly; it may still have consumer-information value |
| Being read as a "tips" or gambling-promotion service | Research framing, no guaranteed outcomes, responsible-gambling messaging |
