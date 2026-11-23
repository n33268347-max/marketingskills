# Independent draw verification report (PROTOTYPE): 7days Performance

_Generated 2026-11-23 by RAFFLE EDGE `draw_verification.py`. Prototype; not a certificate._

## Scope

- Published draw results examined: **1650**
- Period: 2010-01-01T00:00:00+00:00 to 2026-11-22T22:00:00+00:00
- Inputs: only information the operator published (draw-results feed, competition pages, method description).
- Not examined: the operator's systems, entry lists, payment records, or any personal data.

## Methods applied

- **7days-v1 mt_srand(ms)**: mt_srand(seed); mt_rand(1, entries) where the published seed equals the draw timestamp in milliseconds. Source: 7days 'Draws Explained' page (archived 2026-11-23), operator's published example reproduced.

## Result by status

| Status | Draws | Meaning |
|---|---|---|
| VERIFIED | 0 | Recomputed and matched to the winning ticket via a published entry list |
| REPRODUCIBLE | 302 | Winning position recomputed exactly from published inputs |
| NOT_INDEPENDENTLY_REPRODUCIBLE | 464 | Inputs published, but the documented method does not reproduce the result. Not evidence of wrongdoing. |
| INSUFFICIENT_INFORMATION | 884 | Inputs needed to recompute the draw were not published (live draws, instant wins) |
| INCONSISTENT_EVIDENCE | 0 | Published fields contradict each other |

## By month

| Month | VERIFIED | REPRODUCIBLE | NOT_INDEPENDENTLY_REPRODUCIBLE | INSUFFICIENT_INFORMATION | INCONSISTENT_EVIDENCE |
|---|---|---|---|---|---|
| 2010-01 | 0 | 0 | 0 | 6 | 0 |
| 2026-05 | 0 | 41 | 0 | 39 | 0 |
| 2026-06 | 0 | 119 | 0 | 128 | 0 |
| 2026-07 | 0 | 130 | 0 | 138 | 0 |
| 2026-08 | 0 | 12 | 113 | 144 | 0 |
| 2026-09 | 0 | 0 | 128 | 145 | 0 |
| 2026-10 | 0 | 0 | 120 | 162 | 0 |
| 2026-11 | 0 | 0 | 103 | 122 | 0 |

## Consistency checks

- Checked: index within 1..entries; winning ticket within 1..max tickets; entries ≤ max tickets; entry-list length.
- Records with inconsistencies: **0**.

## Interpretation

- **May to 3 August 2026: 302 of 302 automated draws are REPRODUCIBLE.** The winning position recomputes exactly from published data, using the method the operator documents.
  - These draws cannot be VERIFIED end to end. The entry list that maps a position to a ticket number was not available to this audit (it may contain names).
  - Supplying a names-free entry list, or its hash, would close that gap.
- **From 5 August 2026: 464 automated draws are NOT INDEPENDENTLY REPRODUCIBLE.** The published seed format changed twice:
  - 5 Aug – 20 Oct: integers of varying length.
  - From 21 Oct: 64-character hex.
- **Alternatives tested on those draws** (all re-computations of past published draws):
  - PHP `mt_rand` seeded with the published value, at both range offsets.
  - PHP 8.2 `Xoshiro256StarStar` seeded with the 32-byte hex value or with the integer value.
  - The first 50 outputs of each of those generators.
- **Result of those tests:** none reproduces the draws systematically. Hit rates match chance.
  - **Minor anomaly:** 3 of the 149 hex-seed draws match `Xoshiro256StarStar(hex) → getInt(0, N−1)` at the first output. About 0.12 would be expected by chance, so p ≈ 0.0002 before correction and about 0.01 after correcting for roughly 50 variants tried.
  - This is not a method that explains the draws. It is recorded as **inconclusive** and is a question for the operator.
- **No published fields contradict each other** across 1,650 results (0 INCONSISTENT_EVIDENCE).
- **Not being able to reproduce a draw is not evidence of manipulation.** The likeliest explanation is an undocumented change of method or seed derivation, for example a move to a cryptographically secure generator. The public description was not updated to match.

## What an operator would need to publish for full independent verification

This can be done without exposing internal systems or personal data. A reference implementation is in `src/raffle_edge/edge/verifiable_draw_spec.py`, with tests in `tests/test_draw_verification.py`.

| Step | When | Published | Purpose |
|---|---|---|---|
| 1 | Before sales close | `SHA256(server_seed)` (commitment) | Fixes the seed before the entries are known |
| 2 | At close | Ordered list of sold ticket numbers (numbers only), and its SHA-256 | Fixes the eligible set; no names |
| 3 | Draw | `index = HMAC-SHA256(server_seed, draw_id ‖ entry_hash)` with rejection sampling | Unbiased, deterministic draw |
| 4 | After the draw | `server_seed` revealed | Anyone can recompute steps 1–3 |

Properties:
- The operator cannot change the seed after seeing the entries, because the commitment is published first.
- Players cannot predict the result, because the seed stays secret until after close.
- Any change to the entry list is detectable.
- No personal data is published.
- The tests show tampering being detected: a forged winner, a swapped seed and an added ticket.

This maps directly onto DCMS Code clause 2.2: "a computer process that produces verifiably random and auditable results".

## Limitations

- **Scope:** one operator, using public data only. No access to systems or entry lists.
- **Not a certificate:** RAFFLE EDGE is not an accredited test house. Accreditation and liability terms need legal advice before any commercial use (see `LEGAL_RESEARCH_REGISTER.md`).
- **Draws without RNG inputs are not covered:** live draws and instant wins publish no RNG inputs, so they are outside this method.
