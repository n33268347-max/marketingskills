# Raffle Edge

Evidence-first research tooling for UK online prize competitions. The question it asks: is there a legitimate, measurable statistical or value advantage anywhere? A null answer is an acceptable result.

**Status:** Phases 1–1b complete; Phase 2–5 modules built and running on 7days Performance. See [docs/PHASE1_REPORT.md](docs/PHASE1_REPORT.md) and [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md).

## Quick start

```bash
cd raffle-edge
pip install -e '.[dev]'            # or: export PYTHONPATH=src
python -m pytest -q                # full test suite
raffle-edge load-registry          # validate seed, append new claims to data/db/raffle_edge.sqlite
raffle-edge rank --basis confirmed # ranking from directly confirmed claims only
raffle-edge report                 # writes docs/generated/*.md
raffle-edge probe --all            # robots-respecting probe (needs network access to the platforms)
raffle-edge extract page.html      # parse a saved page; --store to record an observation
raffle-edge import-draws data/templates/draw_results_template.csv
raffle-edge fetch URL --text-dir out/      # archive any page politely (blocklist + robots enforced)
raffle-edge merge-verified claims.json     # quote-check claims against archived pages
raffle-edge collect 7days-performance      # public draw-results feed (names dropped)
raffle-edge collect 7days-performance --details-sample 200   # value inputs, random sample
raffle-edge analyze 7days-performance --record               # H8 audit, H3-H5 tests, walk-forward, H1
```

## Principles

- **Evidence levels on every claim.** `A_CONFIRMED` (a direct primary read) is the only level that counts as a fact. The database enforces this.
- **Immutable history.** The tables are append-only. Corrections supersede earlier rows; they never overwrite them.
- **Compliance by construction.**
  - robots.txt is obeyed, and an unreadable robots.txt counts as disallow.
  - Any CAPTCHA or bot challenge stops collection from that host.
  - No logins, no entries, no personal data.

  See [docs/COMPLIANCE.md](docs/COMPLIANCE.md).
- **No guessing.** A parser leaves a field empty rather than infer a value. Unknown is stored as NULL, never 0.

## Layout

See plan §8.
