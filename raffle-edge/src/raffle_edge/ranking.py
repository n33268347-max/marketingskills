"""Transparent platform ranking rubric.

Two scores are produced per platform:

* **confirmed**   - computed ONLY from A_CONFIRMED claims (direct primary read).
* **provisional** - also counts P_PROVISIONAL claims (search snippet / third
  party). Useful for prioritising verification work, never for conclusions.

Unknowns score zero and are listed as gaps, so a platform is never rewarded for
what we have not established.
The weights are explicit and documented here; change them in one place.

Why these features: the statistical work in Phases 4-5 needs, per draw, the
winning ticket number AND the valid ticket range (max tickets or tickets sold).
Without both, a uniformity test is impossible. Transparency features capture
whether the draw mechanism can be independently understood.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

# feature -> (topic, value that earns the points, points)
ACCESSIBILITY_RUBRIC: dict[str, tuple[str, str, int]] = {
    "public results page": ("results_page", "yes", 30),
    "results include winning ticket number": ("results_show_ticket_number", "yes", 25),
    "tickets sold disclosed": ("discloses_tickets_sold", "yes", 20),
    "max tickets disclosed": ("discloses_max_tickets", "yes", 15),
    "robots.txt permits results pages": ("robots_results_allowed", "yes", 10),
}

TRANSPARENCY_RUBRIC: dict[str, tuple[str, str, int]] = {
    "winner selection method published": ("winner_selection", "*", 25),
    "named independent random source": ("independent_rng", "yes", 25),
    "public live/recorded draw": ("live_draw", "yes", 20),
    "ticket allocation method published": ("ticket_allocation", "*", 15),
    "DCMS code of practice signatory": ("code_of_practice", "yes", 15),
}

RESEARCH_POTENTIAL_WEIGHTS = {"accessibility": 0.6, "transparency": 0.4}


@dataclass
class PlatformScore:
    slug: str
    name: str
    basis: str = "confirmed"
    accessibility: int = 0
    transparency: int = 0
    research_potential: float = 0.0
    evidence_coverage: float = 0.0  # share of rubric topics with a claim at this basis
    earned: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)  # unknown / unverified
    negatives: list[str] = field(default_factory=list)  # confirmed "no"


BASIS_LEVELS = {
    "confirmed": ("A_CONFIRMED",),
    "provisional": ("A_CONFIRMED", "P_PROVISIONAL"),
}


def _claimed_values(conn: sqlite3.Connection, slug: str, basis: str) -> dict[str, set[str]]:
    levels = BASIS_LEVELS[basis]
    out: dict[str, set[str]] = {}
    q = (
        "SELECT topic, value FROM current_claims WHERE platform_slug=? AND evidence_level IN (%s)"
        % ",".join("?" for _ in levels)
    )
    by_level: dict[str, dict[str, set[str]]] = {}
    for r in conn.execute(q.replace("SELECT topic, value", "SELECT topic, value, evidence_level"), (slug, *levels)):
        by_level.setdefault(r["topic"], {}).setdefault(r["evidence_level"], set()).add((r["value"] or "").strip().lower())
    for topic, lv in by_level.items():
        # A confirmed claim overrides any provisional claim on the same topic.
        out[topic] = lv.get("A_CONFIRMED") or lv.get("P_PROVISIONAL", set())
    return out


def _apply(rubric, confirmed, score: PlatformScore) -> tuple[int, int]:
    pts, covered = 0, 0
    for label, (topic, wanted, weight) in rubric.items():
        values = confirmed.get(topic)
        if not values:
            score.gaps.append(label)
            continue
        covered += 1
        hit = any(v and v not in ("no", "unknown") for v in values) if wanted == "*" else wanted in values
        if hit:
            pts += weight
            score.earned.append(label)
        else:
            score.negatives.append(label)
    return pts, covered


def score_platform(conn: sqlite3.Connection, slug: str, basis: str = "confirmed") -> PlatformScore:
    if basis not in BASIS_LEVELS:
        raise ValueError(basis)
    row = conn.execute("SELECT name FROM platforms WHERE slug=?", (slug,)).fetchone()
    if row is None:
        raise KeyError(slug)
    s = PlatformScore(slug=slug, name=row["name"], basis=basis)
    confirmed = _claimed_values(conn, slug, basis)
    s.accessibility, c1 = _apply(ACCESSIBILITY_RUBRIC, confirmed, s)
    s.transparency, c2 = _apply(TRANSPARENCY_RUBRIC, confirmed, s)
    w = RESEARCH_POTENTIAL_WEIGHTS
    s.research_potential = round(w["accessibility"] * s.accessibility + w["transparency"] * s.transparency, 1)
    s.evidence_coverage = round((c1 + c2) / (len(ACCESSIBILITY_RUBRIC) + len(TRANSPARENCY_RUBRIC)), 2)
    return s


def rank_all(conn: sqlite3.Connection, basis: str = "confirmed") -> list[PlatformScore]:
    slugs = [r["slug"] for r in conn.execute("SELECT slug FROM platforms ORDER BY slug")]
    scores = [score_platform(conn, s, basis) for s in slugs]
    return sorted(scores, key=lambda x: (-x.research_potential, -x.evidence_coverage, x.slug))
