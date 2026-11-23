# Phase 1 report: platform research and prototype

_2026-11-23_

## 1. What was completed

| Item | State |
|---|---|
| R&D plan with pre-registered hypotheses H1–H7 | `docs/RESEARCH_PLAN.md` |
| First ten platforms identified and provisionally ranked | `docs/generated/PLATFORM_RANKING.md` |
| Per-platform dossiers (115 evidence-labelled claims) | `docs/generated/PLATFORM_DOSSIERS.md`, source in `scripts/build_seed.py` |
| Evidence model (A / P / B / C / UNKNOWN), enforced by DB constraints | `src/raffle_edge/db/schema.sql` |
| Immutable SQLite store (append-only triggers, supersede-not-overwrite) | same |
| Compliance-first fetcher | `collector/fetcher.py` |
| Accessibility probe | `collector/probe.py` |
| Conservative page extractor (records the provenance of each field, never guesses) | `parsers/generic.py` |
| Manual draw-result CSV import (evidence URL required, safe to re-run) | `ingest.py`, `data/templates/` |
| CLI and generated reports | `cli.py`, `reporting.py` |
| Compliance and disclosure policy | `docs/COMPLIANCE.md` |

The fetcher:
- obeys robots.txt, and treats an unreadable robots.txt as disallow
- enforces a per-host delay
- stops on any CAPTCHA or bot challenge
- archives every response by its SHA-256 hash

## 2. Evidence and test results

```
$ python -m pytest -q
27 passed
```

The tests cover:
- **Immutability:** UPDATE and DELETE are rejected; corrections go through superseding rows.
- **Range checks:** a winning number must fall inside its ticket range, and tickets sold cannot exceed the maximum.
- **Evidence rules:** an `A_CONFIRMED` claim is rejected unless it comes from a direct read.
- **Registry:** seed validation and idempotent sync.
- **Rubric:** points, gaps and negatives, and hypotheses never score.
- **Fetcher:**
  - obeys robots.txt
  - fails closed when robots.txt is unreachable
  - stops on a bot challenge
  - enforces the rate limit
  - archives snapshots
- **Parser:** extracts from structured data and from text, derives counts from percentages with a warning, and returns nothing when the page gives nothing.
- **CSV import:** validates rows and is safe to re-run.

**Live probe (real run):** `raffle-edge probe 7days-performance elite-competitions`. The sandbox's network proxy refused robots.txt, so the fetcher marked every path as disallowed and fetched nothing. This is the intended fail-closed behaviour. It also means **no platform page has been read directly by this project yet.**

## 3. Findings, labelled

**A. Confirmed facts:** none at the `A_CONFIRMED` standard yet. Direct reads were blocked.

**P. Provisional (search snippets or third parties; verify before use):**
- **7days Performance:**
  - Reportedly publishes winning ticket, draw time and sold/total for each draw.
  - Allocates ticket numbers at random.
  - Claims GLI certification.
- **Dream Car Giveaways:**
  - Two different winner-selection methods are described: PHP `random_int` for automated draws, and the Google RNG on Facebook Live. This needs clarifying; they may cover different eras or draw types.
  - Instant-win winning numbers are reportedly visible on the competition page. That would make the remaining instant-win expected value observable from public data (H2).
- **Rev Comps:** a past-entry-lists archive with total, sold and remaining tickets is the best candidate dataset for H1 (undersold competitions that still draw).
- **Several operators:** state that the draw goes ahead "regardless of tickets sold" (7days, Rev Comps, Elite, DCG). This is the structural condition for H1.
- **BOTB:** the main game is a judged spot-the-ball contest, so there is no winning ticket number and integrity tests on numbers do not apply.
- **Omaze:** uses entry codes with millions of entries and no public counts, so it supports value comparison only.

**C. Hypotheses:** H1–H7 in the plan. A reviewer's allegation of a time-seeded Mersenne Twister at one operator is logged as an unverified hypothesis only.

## 4. Missing information

- **Direct reads of every operator page and robots.txt.** This is blocked until the 10 hosts are added to the environment's network allowlist, or the work runs on a normal machine.
- **GOV.UK Code text and signatory list.** Not loaded.
- **Results archives:** how far back each one goes, and whether winning numbers come with a ticket range.
- **Ticket allocation method:** unknown for Elite, Rev Comps, Lucky Day and DCG. This blocks H3 for them; see plan §5.1.
- **Unsold winning numbers:** whether a draw can land on an unsold number, and what happens if it does. This determines N_eff in the calculator.
- **Terms of use per platform** regarding automated access.

## 5. Assumptions

- Search snippets reflect the operators' pages around Nov 2026. They may be stale or paraphrased.
- The ten platforms are representative of the UK numbered-ticket market. Omaze and BOTB are included for scale even though their formats limit the integrity tests.
- The rubric weights (accessibility 60%, transparency 40%) reflect what the statistical work needs. They are a judgement call and are kept in one place (`ranking.py`).

## 6. Recommended next step

**Phase 1b (short):** run the prototype from a network that can reach the platforms.

1. Run `raffle-edge probe --all`.
2. Read terms of use and robots.txt for the top 6.
3. Promote verified claims to `A_CONFIRMED`, with snapshots.
4. Load the GOV.UK Code and signatory list.

**Then Phase 2:** build parsers for 7days and Rev Comps first.
- 7days has the richest per-draw fields.
- Rev Comps' entry lists feed H1.

Bring the Phase 3 value calculator forward alongside Phase 2. H1 is the most plausible genuine edge, and it needs no pattern-finding at all.
