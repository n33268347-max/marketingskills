# Experiment log: RAFFLE EDGE V2

All runs on 2026-11-23. Code: the `raffle-edge` package at the commit that adds this file. The frozen inputs are listed in `data/frozen/v1/MANIFEST.json` with their SHA-256 hashes. Monte Carlo and sampling seed: 20261123 unless stated.

| # | Experiment | Inputs | Parameters | Result | Outcome |
|---|---|---|---|---|---|
| X1 | Freeze V1 baseline | SQLite DB | `scripts/freeze_v1.py` | 5 CSVs, 2,561 rows, SHA-256 manifest; no personal data (scan for redacted names: 0) | Done |
| X2 | Independent baseline re-check | Frozen CSVs | NumPy MT19937; SciPy KS; plain-CSV EV maths | 1,650 / 766 / 302 of 302 / 1 of 464 / 3 of 200 / max +5.34p all reproduce. Return per £: median 0.545, mean 0.573, revenue-weighted 0.586 | Baseline confirmed (one clarification: V1's "55p" was the median) |
| X3 | Processed dataset | Frozen observations + archived records | `scripts/build_processed_v2.py` | 200 rows with postal tickets per card, per-person limit, prize titles | Done |
| X4 | A3 postal floor rule | X3 | Cost per card 106p (91p stamp + 15p card); rule: floor EV > cost | 16 of 200 qualify. Train 7 of 103, test 9 of 97. Test realised EV/cost 2.98 (bootstrap CI 1.71–5.38) | E05 SUPPORTED |
| X5 | A3 with time valued | X3 | Cost 170p (time at £12.71/h, 3 min/card) | 3 of 200 qualify | Edge shrinks sharply once time is valued |
| X6 | A3 portfolio simulation | X3 | 100,000–200,000 sims; budgets £50/£100; up to 5/20/60 cards per competition | £100: E[profit] +£158 to +£342, P(any win) 9–12%, median outcome −£85 to −£100 | High variance |
| X7 | A3 cards needed | X3 | Mean P(win)/card 0.157% | 442 cards for a 50% chance of at least one win; 1,468 for 90% | Practical constraint |
| X8 | A2 ex-ante paid floor | X3 | V/(max+1) > price | 0 of 200 | E03 REJECTED |
| X9 | A2 perfect-hindsight bound | X3 | Optimal k per competition | 3 of 200; total £4.89 profit on £100.03 spend | E04 NOT PRACTICALLY EXPLOITABLE |
| X10 | A1 drivers of value | X3 | OLS, HC3 errors | Cash prize +0.242 log-return (CI 0.211–0.272); payout if sold out 41–50p per £; R² 0.77 (fill rate partly mechanical) | E07 SUPPORTED (lower loss, not profit) |
| X11 | A4 ticket numbers | Frozen draws + X3 | KS on (ticket − 0.5)/max | n=200, D=0.038, p=0.93 | E06 REJECTED |
| X12 | A5 bundles (7days) | Archived records | Count offers | 200 of 200 single price | E08 REJECTED |
| X13 | Rev Comps pages | 4 pages (60 s crawl delay) | Server-rendered HTML only | 21 current competitions with % sold; 16 final entry lists. The API-loaded archive (11,051 lists) was **not** used. prev.revcomps.com does not resolve. | Forward test started (E09) |
| X14 | Draw verification: new seed formats | Frozen draws | PHP mt_rand (seed = published value); PHP 8.2 Xoshiro256** (hex and int seeds), offsets 0 and 1; first 50 outputs | No systematic reproduction. 3 of 149 hex draws match Xoshiro getInt(0,N−1) at output 1 (chance 0.12; p≈0.0002 raw, ≈0.01 after ~50 variants) | Inconclusive; ask the operator; investigation stopped |
| X15 | Draw verification prototype | Frozen draws | 5-status classifier | 302 reproducible, 464 not independently reproducible, 884 insufficient information, 0 inconsistent | Prototype works |
| X16 | Verifiable-draw protocol | Synthetic | Commit-reveal + HMAC rejection sampling | Detects forged winner, swapped seed and added ticket; index uniform over 5,000 runs | Reference implementation |
| X17 | Legal quote re-check | 76 legal quotes | `verify.check_claims` | 76 of 76 found verbatim in archived pages | Done |
| X18 | Platform claims merge | 69 claims | Quote check + personal-data guard | 69 of 69 accepted | Done |

## Failed or abandoned lines, recorded deliberately

- **Rev Comps full history (11,051 auto-draw lists):** abandoned. The data is behind a third-party API (api.optimize.io), and bulk extraction raises database-right and terms concerns. Permitted alternative: ask the operator, which needs your approval.
- **Aspire terms:** unreadable. The page is rendered client-side from Aspire's backend, and the backend was not queried. Automated access is paused until a person reads the terms.
- **"The Competition Guys":** no UK operator found under that exact name. Not substituted.
- **Reverse-engineering 7days' post-August seed:** stopped after the documented and standard PHP engines failed. Going further would mean guessing at an undocumented, possibly cryptographic system, which is out of scope.
