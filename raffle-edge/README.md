# Raffle Edge

Evidence-first research tooling for UK online prize competitions. The question it asks: is there a legitimate, measurable statistical or value advantage anywhere? A null answer is an acceptable result.

**Status:** Phase 1 prototype. See [docs/PHASE1_REPORT.md](docs/PHASE1_REPORT.md) and [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md).

## Quick start

```bash
cd raffle-edge
pip install -e '.[dev]'            # or: export PYTHONPATH=src
python -m pytest -q                # 27 tests
raffle-edge load-registry          # validate seed, append new claims to data/db/raffle_edge.sqlite
raffle-edge rank                   # provisional ranking (use --basis confirmed for strict)
raffle-edge report                 # writes docs/generated/*.md
raffle-edge probe --all            # robots-respecting probe (needs network access to the platforms)
raffle-edge extract page.html      # parse a saved page; --store to record an observation
raffle-edge import-draws data/templates/draw_results_template.csv
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
