"""Markdown reports generated from the database (never hand-edited)."""

from __future__ import annotations

import sqlite3
from datetime import date

from .ranking import ACCESSIBILITY_RUBRIC, TRANSPARENCY_RUBRIC, rank_all

LEVEL_LABEL = {
    "A_CONFIRMED": "A · confirmed",
    "P_PROVISIONAL": "P · provisional",
    "B_OBSERVATION": "B · observation",
    "C_HYPOTHESIS": "C · hypothesis",
    "UNKNOWN": "unknown",
}


def _esc(s: str | None) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def ranking_report(conn: sqlite3.Connection) -> str:
    conf = {s.slug: s for s in rank_all(conn, "confirmed")}
    prov = rank_all(conn, "provisional")
    counts = dict(conn.execute("SELECT evidence_level, COUNT(*) FROM current_claims GROUP BY evidence_level").fetchall())
    lines = [
        "# Platform research ranking",
        "",
        f"_Generated {date.today().isoformat()} by `raffle-edge report`. Do not edit by hand._",
        "",
        "Claim counts by evidence level: " + ", ".join(f"{LEVEL_LABEL.get(k, k)}: {v}" for k, v in sorted(counts.items())),
        "",
        "**Read this first.** The *confirmed* columns use only claims read directly from a primary source. "
        "The *provisional* columns also count search-snippet and third-party claims; they decide what to verify "
        "next and are not findings.",
        "",
        "| # | Platform | Provisional research potential | Prov. accessibility | Prov. transparency | Prov. coverage | Confirmed research potential |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, s in enumerate(prov, 1):
        c = conf[s.slug]
        lines.append(
            f"| {i} | {s.name} | {s.research_potential} | {s.accessibility} | {s.transparency} | "
            f"{int(s.evidence_coverage * 100)}% | {c.research_potential} |"
        )
    lines += ["", "## Rubric", "", "Accessibility (0–100):", ""]
    lines += [f"- {k}: {w} pts (topic `{t}` = `{v}`)" for k, (t, v, w) in ACCESSIBILITY_RUBRIC.items()]
    lines += ["", "Transparency (0–100):", ""]
    lines += [f"- {k}: {w} pts (topic `{t}` {'documented' if v == '*' else '= `' + v + '`'})" for k, (t, v, w) in TRANSPARENCY_RUBRIC.items()]
    lines += ["", "Research potential = 0.6 × accessibility + 0.4 × transparency.", "", "## Per-platform gaps (provisional basis)", ""]
    for s in prov:
        lines.append(f"- **{s.name}**: earned {', '.join(s.earned) or 'nothing'}; "
                     f"gaps: {', '.join(s.gaps) or 'none'}; negatives: {', '.join(s.negatives) or 'none'}")
    return "\n".join(lines) + "\n"


def dossier(conn: sqlite3.Connection, slug: str) -> str:
    p = conn.execute("SELECT * FROM platforms WHERE slug=?", (slug,)).fetchone()
    if p is None:
        raise KeyError(slug)
    lines = [f"## {p['name']}", "", f"Base URL: {p['base_url']}", "",
             "| Topic | Value | Statement | Evidence | Source |", "|---|---|---|---|---|"]
    for c in conn.execute("SELECT * FROM current_claims WHERE platform_slug=? ORDER BY topic, id", (slug,)):
        src = f"[{c['source_kind']}]({c['source_url']})" if c["source_url"] else "—"
        lines.append(f"| {c['topic']} | {_esc(c['value'])} | {_esc(c['statement'])} | {LEVEL_LABEL[c['evidence_level']]} | {src} |")
    probes = conn.execute("SELECT * FROM probes WHERE platform_slug=? ORDER BY id DESC LIMIT 8", (slug,)).fetchall()
    if probes:
        lines += ["", "Latest probes:", ""]
        lines += [f"- {r['probed_at']} {r['target']}: {r['outcome']} ({r['http_status']}) {r['note'] or ''}" for r in probes]
    return "\n".join(lines) + "\n"


def dossiers_report(conn: sqlite3.Connection) -> str:
    slugs = [r["slug"] for r in conn.execute("SELECT slug FROM platforms ORDER BY name")]
    head = ["# Platform dossiers", "", f"_Generated {date.today().isoformat()} from the claims table. Do not edit by hand._", ""]
    return "\n".join(head) + "\n".join(dossier(conn, s) for s in slugs)
