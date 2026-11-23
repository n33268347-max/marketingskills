"""Independent draw-verification prototype (V2 Stream D).

Classifies each published draw into exactly one status:

  VERIFIED                       documented method reproduces the winning position from published
                                 inputs AND a published entry list maps that position to the winning ticket
  REPRODUCIBLE                   documented method reproduces the winning position from published inputs;
                                 position -> ticket mapping not checkable (entry list not published)
  NOT_INDEPENDENTLY_REPRODUCIBLE every input the documented method needs is published, but it does not
                                 reproduce the result. This is NOT evidence of manipulation.
  INSUFFICIENT_INFORMATION       inputs needed to recompute the draw are not published (e.g. live draws)
  INCONSISTENT_EVIDENCE          published fields contradict each other (e.g. index outside 1..entries)

Only past, published draws are processed. Nothing here predicts future draws.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

from ..audit.h8_sevendays import seed_from_unix_time
from ..audit.php_mt import mt_rand_once

STATUSES = ("VERIFIED", "REPRODUCIBLE", "NOT_INDEPENDENTLY_REPRODUCIBLE", "INSUFFICIENT_INFORMATION", "INCONSISTENT_EVIDENCE")


@dataclass
class DrawRecord:
    operator: str
    draw_id: str
    competition: str
    drawn_at: str
    draw_type: str
    published_seed: str | None
    unix_time: str | None
    index: int | None
    entries: int | None
    winning_ticket: int | None
    max_tickets: int | None = None
    entry_list: list[int] | None = None  # ticket numbers in published order, if published


@dataclass
class Method:
    name: str
    description: str
    applies: Callable[[DrawRecord], bool]
    recompute: Callable[[DrawRecord], int]
    source: str


@dataclass
class Verdict:
    record: DrawRecord
    status: str
    method: str | None
    checks: list[str] = field(default_factory=list)


def consistency_problems(r: DrawRecord) -> list[str]:
    p = []
    if r.index is not None and r.entries is not None and not (1 <= r.index <= r.entries):
        p.append(f"index {r.index} outside 1..{r.entries}")
    if r.winning_ticket is not None and r.max_tickets is not None and not (1 <= r.winning_ticket <= r.max_tickets):
        p.append(f"winning ticket {r.winning_ticket} outside 1..{r.max_tickets}")
    if r.entries is not None and r.max_tickets is not None and r.entries > r.max_tickets:
        p.append(f"entries {r.entries} exceed max tickets {r.max_tickets}")
    if r.entry_list is not None and r.entries is not None and len(r.entry_list) != r.entries:
        p.append("entry list length differs from published entry count")
    return p


def verify(records: list[DrawRecord], methods: list[Method]) -> list[Verdict]:
    out = []
    for r in records:
        problems = consistency_problems(r)
        if problems:
            out.append(Verdict(r, "INCONSISTENT_EVIDENCE", None, problems)); continue
        if r.draw_type != "automated" or r.index is None or not r.entries:
            out.append(Verdict(r, "INSUFFICIENT_INFORMATION", None, ["no published RNG inputs (live, instant-win or missing fields)"])); continue
        m = next((m for m in methods if m.applies(r)), None)
        if m is None:
            out.append(Verdict(r, "NOT_INDEPENDENTLY_REPRODUCIBLE", None,
                               ["inputs published, but no documented method matches this seed format"])); continue
        if m.recompute(r) != r.index:
            out.append(Verdict(r, "NOT_INDEPENDENTLY_REPRODUCIBLE", m.name, ["documented method does not reproduce the published index"])); continue
        if r.entry_list is not None:
            ok = r.entry_list[r.index - 1] == r.winning_ticket
            out.append(Verdict(r, "VERIFIED" if ok else "INCONSISTENT_EVIDENCE", m.name,
                               [] if ok else ["index reproduces but entry list maps it to a different ticket"]))
        else:
            out.append(Verdict(r, "REPRODUCIBLE", m.name, ["entry list not published: position->ticket mapping unchecked"]))
    return out


SEVENDAYS_V1 = Method(
    name="7days-v1 mt_srand(ms)",
    description="mt_srand(seed); mt_rand(1, entries) where the published seed equals the draw timestamp in milliseconds",
    applies=lambda r: bool(r.published_seed and r.unix_time and r.published_seed.isdigit()
                           and len(r.published_seed) == 13 and int(r.published_seed) == seed_from_unix_time(r.unix_time)),
    recompute=lambda r: mt_rand_once(int(r.published_seed), 1, r.entries),
    source="7days 'Draws Explained' page (archived 2026-11-23), operator's published example reproduced",
)


def load_7days(frozen_draws: Path, processed: Path | None = None) -> list[DrawRecord]:
    maxes = {}
    if processed and processed.exists():
        maxes = {r["competition"]: int(r["max_tickets"]) for r in csv.DictReader(open(processed))}
    out = []
    for d in csv.DictReader(open(frozen_draws)):
        if d["platform_slug"] != "7days-performance":
            continue
        toi = lambda v: int(v) if v not in ("", None) else None
        out.append(DrawRecord("7days Performance", d["external_result_id"], d["competition"], d["drawn_at"], d["draw_type"],
                              d["rng_published_seed"] or None, d["rng_unix_time"] or None, toi(d["rng_index"]), toi(d["rng_entries"]),
                              toi(d["winning_ticket_number"]), maxes.get(d["competition"])))
    return out


def audit_report(verdicts: list[Verdict], operator: str, methods: list[Method]) -> str:
    by = Counter(v.status for v in verdicts)
    months = defaultdict(Counter)
    for v in verdicts:
        months[(v.record.drawn_at or "")[:7]][v.status] += 1
    L = [f"# Independent draw verification report (PROTOTYPE): {operator}", "",
         f"_Generated {date.today().isoformat()} by RAFFLE EDGE `draw_verification.py`. Prototype; not a certificate._", "",
         "## Scope", "", f"- Published draw results examined: **{len(verdicts)}**",
         f"- Period: {min(v.record.drawn_at for v in verdicts)} to {max(v.record.drawn_at for v in verdicts)}",
         "- Inputs: only information the operator published (draw-results feed, competition pages, method description).",
         "- Not examined: the operator's systems, entry lists, payment records, or any personal data.", "",
         "## Methods applied", ""]
    L += [f"- **{m.name}**: {m.description}. Source: {m.source}." for m in methods]
    L += ["", "## Result by status", "", "| Status | Draws | Meaning |", "|---|---|---|"]
    meaning = {
        "VERIFIED": "Recomputed and matched to the winning ticket via a published entry list",
        "REPRODUCIBLE": "Winning position recomputed exactly from published inputs",
        "NOT_INDEPENDENTLY_REPRODUCIBLE": "Inputs published, but the documented method does not reproduce the result. Not evidence of wrongdoing.",
        "INSUFFICIENT_INFORMATION": "Inputs needed to recompute the draw were not published (live draws, instant wins)",
        "INCONSISTENT_EVIDENCE": "Published fields contradict each other",
    }
    L += [f"| {s} | {by.get(s, 0)} | {meaning[s]} |" for s in STATUSES]
    L += ["", "## By month", "", "| Month | " + " | ".join(STATUSES) + " |", "|---|" + "---|" * len(STATUSES)]
    for m in sorted(months):
        L.append(f"| {m} | " + " | ".join(str(months[m].get(s, 0)) for s in STATUSES) + " |")
    inc = [v for v in verdicts if v.status == "INCONSISTENT_EVIDENCE"]
    L += ["", "## Consistency checks", "",
          "- Checked: index within 1..entries; winning ticket within 1..max tickets; entries ≤ max tickets; entry-list length.",
          f"- Records with inconsistencies: **{len(inc)}**."]
    L += [f"  - {v.record.draw_id} ({v.record.drawn_at}): {'; '.join(v.checks)}" for v in inc[:20]]
    return "\n".join(L) + "\n"
