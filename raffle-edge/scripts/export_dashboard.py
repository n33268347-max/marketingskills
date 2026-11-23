"""Export dashboard datasets (JSON {rows, meta}) from the research database.

Usage: PYTHONPATH=src python scripts/export_dashboard.py OUT_DIR
Contains no personal data: winner names are never stored in the database.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from raffle_edge.analysis.h1_value import load as load_h1
from raffle_edge.analysis.uniformity import run_all
from raffle_edge.audit.h8_sevendays import SEED_RULE, run as run_h8
from raffle_edge.db.database import connect
from raffle_edge.ranking import rank_all

ROOT = Path(__file__).resolve().parents[1]
CODE = Path(__file__).read_text(encoding="utf-8")
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write(out: Path, name: str, rows: list[dict], extra_meta: list[dict]) -> None:
    meta = [{"label": "export_dashboard.py", "value": CODE, "type": "code", "lang": "python"},
            {"label": "Input", "value": "raffle-edge research database (data/db/raffle_edge.sqlite)"},
            {"label": "Exported", "value": NOW}] + extra_meta
    (out / f"{name}.json").write_text(json.dumps({"rows": rows, "meta": meta}, indent=1, ensure_ascii=False), encoding="utf-8")


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    conn = connect(ROOT / "data/db/raffle_edge.sqlite")
    blocked = json.loads((ROOT / "data/seed/collection_blocklist.json").read_text())["hosts"]

    # 1. Platform ranking (confirmed basis)
    rows = []
    for s in rank_all(conn, "confirmed"):
        base = conn.execute("SELECT base_url FROM platforms WHERE slug=?", (s.slug,)).fetchone()[0]
        host = "/".join(base.split("/")[:3])
        code = conn.execute("""SELECT value FROM current_claims WHERE platform_slug=? AND topic='code_of_practice'
                               AND evidence_level='A_CONFIRMED' ORDER BY id DESC LIMIT 1""", (s.slug,)).fetchone()
        n_conf = conn.execute("SELECT COUNT(*) FROM current_claims WHERE platform_slug=? AND evidence_level='A_CONFIRMED'",
                              (s.slug,)).fetchone()[0]
        rows.append({"platform": s.name, "slug": s.slug, "research_potential": s.research_potential,
                     "accessibility": s.accessibility, "transparency": s.transparency,
                     "evidence_coverage": round(s.evidence_coverage * 100), "confirmed_claims": n_conf,
                     "code_signatory": (code[0] if code else "unknown"),
                     "collection": "Manual only (terms)" if host in blocked else "Permitted"})
    write(out, "platforms", rows, [{"label": "Basis", "value": "Only A_CONFIRMED claims (direct reads, quote-checked)."}])

    # 2. H8 by month
    h8 = run_h8(conn)
    write(out, "h8_months", [{"month": m, "checked": c, "reproduced": r, "not_reproduced": c - r}
                             for m, (c, r) in h8.by_month.items()],
          [{"label": "Rule", "value": SEED_RULE}])

    # 3. Integrity tests
    q = conn.execute("""SELECT d.rng_index, d.rng_entries FROM current_draw_results d JOIN competitions c ON c.id=d.competition_id
                        WHERE c.platform_slug='7days-performance' AND d.draw_type='automated'
                          AND d.rng_index IS NOT NULL AND d.rng_entries > 0 ORDER BY d.drawn_at""").fetchall()
    fs = run_all(np.array([r[0] for r in q]), np.array([r[1] for r in q]), sims=2000)
    write(out, "integrity_tests", [{"test": f"{f.hypothesis}: {f.test}", "hypothesis": f.hypothesis, "n": f.n,
                                    "p_value": round(f.p_value, 4), "p_adjusted": round(f.p_adjusted, 4),
                                    "effect": None if f.effect_size is None else round(f.effect_size, 4),
                                    "effect_label": f.effect_label,
                                    "significant": "yes" if f.significant_after_correction else "no"} for f in fs],
          [{"label": "Correction", "value": "Benjamini–Hochberg across this family, alpha 0.05; Monte Carlo seed 20261123"}])

    # 4. H1 competitions
    vals = load_h1(conn)
    write(out, "h1_competitions", [{"competition": v.slug, "price_p": v.price, "sold": v.sold, "max_tickets": v.max_tickets,
                                    "fill_pct": round(v.fill * 100, 1),
                                    "cash_value_gbp": None if v.cash is None else round(v.cash / 100, 2),
                                    "ev_cash_p": None if v.ev_cash is None else round(v.ev_cash, 2),
                                    "ev_advertised_p": None if v.ev_adv is None else round(v.ev_adv, 2),
                                    "break_even_sold": None if v.break_even_sold_cash is None else round(v.break_even_sold_cash)}
                                   for v in vals],
          [{"label": "Method", "value": "EV of one extra ticket at close = value/(sold+1) - price; draw base = sold tickets."},
           {"label": "Sample", "value": "Random sample (seed 20261123) of finished 7days automated-draw competitions."}])

    # 5. Hypothesis register (status written by hand in the plan; ledger runs appended)
    runs = conn.execute("SELECT hypothesis_id, run_at, outcome, test_value, baseline_value, p_value, n_test FROM hypothesis_runs ORDER BY id").fetchall()
    write(out, "ledger", [dict(zip(["hypothesis", "run_at", "outcome", "test_value", "baseline", "p_value", "n_test"], r)) for r in runs],
          [{"label": "Note", "value": "Every run is kept, including failures."}])
    print("exported to", out)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
