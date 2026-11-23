"""Generates docs/generated/ANALYSIS_7DAYS.md from the database."""

from __future__ import annotations

import sqlite3
from datetime import date

import numpy as np

from ..audit.h8_sevendays import SEED_RULE, run as run_h8
from .uniformity import run_all


def _fmt_p(p: float) -> str:
    return f"{p:.4f}" if p >= 1e-4 else f"{p:.1e}"


def build(conn: sqlite3.Connection, sims: int = 2000) -> str:
    counts = conn.execute(
        """SELECT d.draw_type, COUNT(*) FROM current_draw_results d JOIN competitions c ON c.id=d.competition_id
           WHERE c.platform_slug='7days-performance' GROUP BY d.draw_type"""
    ).fetchall()
    span = conn.execute(
        """SELECT MIN(drawn_at), MAX(drawn_at) FROM current_draw_results d JOIN competitions c ON c.id=d.competition_id
           WHERE c.platform_slug='7days-performance'"""
    ).fetchone()
    lines = [
        "# 7days Performance: draw audit and integrity tests",
        "",
        f"_Generated {date.today().isoformat()} by `raffle-edge analyze 7days-performance`. Do not edit by hand._",
        "",
        "Source: the public draw-results feed. Winner names are dropped at ingest.",
        f"Results span {span[0]} → {span[1]}. By type: " + ", ".join(f"{t}: {n}" for t, n in counts) + ".",
        "",
        "## H8: reproducing published automated draws",
        "",
        f"Rule tested (from the operator's own description): `{SEED_RULE}`.",
        "It is checked against the published `unix_time`, `winning_index` and `entries_number`, and is applied to past, published draws only.",
        "",
    ]
    h8 = run_h8(conn)
    lines += [
        f"- Automated draws checked: **{h8.checked}**",
        f"- Reproduced exactly: **{h8.reproduced}** ({h8.rate:.1%})" if h8.checked else "- (none)",
        f"- Last draw that reproduces: {h8.last_reproducing}",
        f"- First draw that does not reproduce: {h8.first_nonreproducing}",
        "",
        "| Month | Checked | Reproduced | Rate |",
        "|---|---|---|---|",
    ]
    lines += [f"| {m} | {c} | {r} | {r / c:.0%} |" for m, (c, r) in h8.by_month.items()]
    lines += [
        "",
        "By chance alone, a wrong rule reproduces a draw with probability 1/entries, which is about 0 for these sizes. Any non-trivial reproduction rate therefore confirms the rule for those draws. Where draws stop reproducing, either the seed derivation changed or something else feeds the seed (for example the published `rng_seed` hash). This needs an explanation from the operator before any conclusion is drawn.",
        "",
        "## H3–H5: is the winning position uniform over the entry list?",
        "",
        "Under H0, `winning_index` is uniform on 1..`entries_number` (the operator draws a line of the sold-ticket list).",
        "",
    ]
    rows = conn.execute(
        """SELECT d.rng_index, d.rng_entries FROM current_draw_results d JOIN competitions c ON c.id=d.competition_id
           WHERE c.platform_slug='7days-performance' AND d.draw_type='automated'
             AND d.rng_index IS NOT NULL AND d.rng_entries > 0 ORDER BY d.drawn_at"""
    ).fetchall()
    if len(rows) < 30:
        lines.append(f"Insufficient data ({len(rows)} draws).")
        return "\n".join(lines) + "\n"
    pos = np.array([r[0] for r in rows])
    ns = np.array([r[1] for r in rows])
    lines += [
        f"n = {len(rows)} automated draws; entries per draw: median {int(np.median(ns))}, min {ns.min()}, max {ns.max()}.",
        "",
        "| Hypothesis | Test | n | Statistic | p | BH-adjusted p | Effect | 95% interval | Significant after correction |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    findings = run_all(pos, ns, sims=sims)
    for f in findings:
        eff = f"{f.effect_label} = {f.effect_size:.3f}" if f.effect_size is not None else "—"
        ci = f"[{f.ci95[0]:.3f}, {f.ci95[1]:.3f}]" if f.ci95 else "—"
        lines.append(f"| {f.hypothesis} | {f.test} | {f.n} | {f.statistic:.4g} | {_fmt_p(f.p_value)} | "
                     f"{_fmt_p(f.p_adjusted)} | {eff} | {ci} | {'**yes**' if f.significant_after_correction else 'no'} |")
    lim = sorted({l for f in findings for l in f.limitations})
    lines += ["", "Limitations:", ""] + [f"- {l}" for l in lim] + [
        "- These tests check the draw step only (index within the list). They cannot check how ticket numbers were allocated, or whether the published list is complete.",
        "- **Independent validation:** not yet done. A significant result must be re-tested on draws collected after this report (a hold-out) before it counts as a finding.",
        "- A historical pattern is not evidence of future predictability.",
    ]
    return "\n".join(lines) + "\n"
