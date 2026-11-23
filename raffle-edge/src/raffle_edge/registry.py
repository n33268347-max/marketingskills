"""Platform registry: evidence-labelled claims about each competition platform.

The seed file (data/seed/platforms.json) is hand-curated from public sources.
Every claim carries an evidence level. A_CONFIRMED claims (direct read of the
primary source, with URL and access date) drive the *confirmed* score;
P_PROVISIONAL claims (search-snippet or third-party) only feed the clearly
labelled *provisional* score and are queued for direct verification.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .db.database import ensure_platform, insert, transaction

log = logging.getLogger(__name__)

EVIDENCE_LEVELS = ("A_CONFIRMED", "P_PROVISIONAL", "B_OBSERVATION", "C_HYPOTHESIS", "UNKNOWN")
SOURCE_KINDS = ("primary_direct", "primary_search_snippet", "third_party", "regulator", "none")

# Controlled vocabulary for claim topics. Free-text topics are rejected so the
# ranking rubric can rely on them.
TOPICS: dict[str, str] = {
    "operator": "Operating company and registration details",
    "formats": "Competition formats offered",
    "ticket_price_range": "Typical ticket prices",
    "ticket_allocation": "How ticket numbers are assigned (random_assigned / player_chosen / sequential)",
    "winner_selection": "How the winner is selected, as published",
    "independent_rng": "Whether a named third-party random source / adjudicator is used (yes/no)",
    "live_draw": "Whether draws are streamed or recorded publicly (yes/no)",
    "results_page": "Whether a public historical results/winners page exists (yes/no)",
    "results_show_ticket_number": "Whether published results include the winning ticket number (yes/no)",
    "discloses_max_tickets": "Whether the maximum number of tickets is published per competition (yes/no)",
    "discloses_tickets_sold": "Whether tickets sold / entries are published (yes/no)",
    "instant_wins": "Instant-win mechanism details",
    "free_entry_route": "Free postal entry route (yes/no)",
    "robots_results_allowed": "Whether robots.txt permits fetching the results pages (yes/no)",
    "code_of_practice": "Signatory to the DCMS prize competitions voluntary code (yes/no)",
    "regulatory_history": "ASA rulings, press investigations, enforcement",
    "terms_url": "Location of published terms and conditions",
    "notes": "Other research notes",
}


class RegistryError(ValueError):
    pass


@dataclass
class Claim:
    topic: str
    statement: str
    evidence_level: str
    value: str | None = None
    source_url: str | None = None
    source_kind: str | None = None
    source_quote: str | None = None
    accessed_on: str | None = None
    analysis_ref: str | None = None

    def validate(self, platform: str) -> None:
        where = f"{platform}/{self.topic}"
        if self.topic not in TOPICS:
            raise RegistryError(f"{where}: unknown topic (allowed: {', '.join(TOPICS)})")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise RegistryError(f"{where}: bad evidence_level {self.evidence_level!r}")
        if not self.statement.strip():
            raise RegistryError(f"{where}: empty statement")
        if self.evidence_level == "A_CONFIRMED" and not (self.source_url and self.accessed_on):
            raise RegistryError(f"{where}: A_CONFIRMED claims need source_url and accessed_on")
        if self.source_kind is not None and self.source_kind not in SOURCE_KINDS:
            raise RegistryError(f"{where}: bad source_kind {self.source_kind!r}")
        if self.evidence_level == "A_CONFIRMED" and self.source_kind not in ("primary_direct", "regulator"):
            raise RegistryError(f"{where}: A_CONFIRMED requires a direct primary or regulator source")
        if self.evidence_level == "P_PROVISIONAL" and not self.source_url:
            raise RegistryError(f"{where}: P_PROVISIONAL claims need source_url")
        if self.evidence_level == "B_OBSERVATION" and not self.analysis_ref:
            raise RegistryError(f"{where}: B_OBSERVATION claims need analysis_ref")


@dataclass
class Platform:
    slug: str
    name: str
    base_url: str
    results_url: str | None = None
    terms_url: str | None = None
    claims: list[Claim] = field(default_factory=list)


def load_seed(path: str | Path) -> tuple[dict[str, Any], list[Platform]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    platforms: list[Platform] = []
    seen: set[str] = set()
    for p in data["platforms"]:
        if p["slug"] in seen:
            raise RegistryError(f"duplicate platform slug {p['slug']}")
        seen.add(p["slug"])
        claims = [Claim(**c) for c in p.get("claims", [])]
        for c in claims:
            c.validate(p["slug"])
        platforms.append(
            Platform(
                slug=p["slug"],
                name=p["name"],
                base_url=p["base_url"],
                results_url=p.get("results_url"),
                terms_url=p.get("terms_url"),
                claims=claims,
            )
        )
    return meta, platforms


def sync_to_db(conn: sqlite3.Connection, platforms: list[Platform], recorded_by: str = "seed") -> int:
    """Append claims that are not already present. Returns number of new claims.

    Existing claims are never modified. If the seed changes a statement, the new
    version is appended and marked as superseding the previous current claim on
    the same (platform, topic, source_url).
    """
    added = 0
    with transaction(conn):
        for p in platforms:
            ensure_platform(conn, p.slug, p.name, p.base_url)
            for c in p.claims:
                exists = conn.execute(
                    """SELECT 1 FROM claims WHERE platform_slug=? AND topic=? AND statement=?
                       AND evidence_level=? AND IFNULL(value,'')=IFNULL(?, '')
                       AND IFNULL(source_url,'')=IFNULL(?, '')""",
                    (p.slug, c.topic, c.statement, c.evidence_level, c.value, c.source_url),
                ).fetchone()
                if exists:
                    continue
                prev = conn.execute(
                    """SELECT id FROM current_claims WHERE platform_slug=? AND topic=?
                       AND IFNULL(source_url,'')=IFNULL(?, '') ORDER BY id DESC LIMIT 1""",
                    (p.slug, c.topic, c.source_url),
                ).fetchone()
                insert(
                    conn,
                    "claims",
                    {
                        "platform_slug": p.slug,
                        "topic": c.topic,
                        "statement": c.statement,
                        "evidence_level": c.evidence_level,
                        "value": c.value,
                        "source_url": c.source_url,
                        "source_kind": c.source_kind,
                        "source_quote": c.source_quote,
                        "accessed_on": c.accessed_on,
                        "analysis_ref": c.analysis_ref,
                        "recorded_by": recorded_by,
                        "supersedes_id": prev["id"] if prev else None,
                    },
                )
                added += 1
    log.info("registry sync: %d new claims", added)
    return added


def current_claims(conn: sqlite3.Connection, platform_slug: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM current_claims WHERE platform_slug=? ORDER BY topic, id", (platform_slug,)
    ).fetchall()
