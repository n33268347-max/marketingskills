"""H1: do competitions that draw regardless of sell-out sometimes close with
a positive expected value for a marginal ticket?

Ex-post analysis on FINISHED competitions using final sold counts. For each
competition: EV of one extra ticket bought at close = V/(sold+1) - price,
where V is total prize value on a stated basis. (The winner is drawn from the
sold list for 7days automated draws, so the draw base is 'sold'.)

This is an upper bound on what a real buyer could achieve: a buyer does not
know the final count when buying, and the operator's value figures are
self-reported. A strategy only counts if it survives a forward test on
observations taken BEFORE close (Phase 5).
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass

from ..calculator.value import DrawCompetition, Prize, evaluate


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


@dataclass
class CompValue:
    slug: str
    price: int
    max_tickets: int
    sold: int
    cash: int | None
    advertised: int | None
    ev_cash: float | None
    ev_adv: float | None
    fill: float
    break_even_sold_cash: float | None


def load(conn: sqlite3.Connection, platform: str = "7days-performance") -> list[CompValue]:
    rows = conn.execute(
        """SELECT c.external_ref slug, o.* FROM latest_observations o JOIN competitions c ON c.id=o.competition_id
           WHERE c.platform_slug=? AND o.ticket_price_pence > 0 AND o.max_tickets IS NOT NULL
             AND o.tickets_sold IS NOT NULL AND o.tickets_sold > 0""",
        (platform,),
    ).fetchall()
    out = []
    for r in rows:
        k_sold_others = r["tickets_sold"]  # buyer's extra ticket on top of final sales
        if k_sold_others + 1 > r["max_tickets"]:
            k_sold_others = r["max_tickets"] - 1  # sold out: no extra ticket available; treat as last ticket
        prize = Prize(advertised_pence=r["advertised_value_pence"], cash_alternative_pence=r["cash_alternative_pence"])
        comp = DrawCompetition(r["ticket_price_pence"], r["max_tickets"], (prize,), "sold", r["max_entries_per_person"])
        ev_cash = evaluate(comp, 1, k_sold_others, "cash_alternative").expected_value_pence if r["cash_alternative_pence"] else None
        ev_adv = evaluate(comp, 1, k_sold_others, "advertised").expected_value_pence if r["advertised_value_pence"] else None
        out.append(CompValue(r["slug"], r["ticket_price_pence"], r["max_tickets"], r["tickets_sold"],
                             r["cash_alternative_pence"], r["advertised_value_pence"], ev_cash, ev_adv,
                             r["tickets_sold"] / r["max_tickets"],
                             (r["cash_alternative_pence"] / r["ticket_price_pence"]) if r["cash_alternative_pence"] else None))
    return out


def summary_markdown(vals: list[CompValue], sample_note: str) -> str:
    lines = ["## H1: positive-EV undersold draws (ex-post)", "", sample_note, ""]
    if not vals:
        return "\n".join(lines + ["No competitions with complete value inputs yet."]) + "\n"
    n = len(vals)
    for basis, attr in (("cash alternative", "ev_cash"), ("advertised value", "ev_adv")):
        xs = [getattr(v, attr) for v in vals if getattr(v, attr) is not None]
        pos = sum(1 for x in xs if x > 0)
        lo, hi = wilson(pos, len(xs))
        mean_ev = sum(xs) / len(xs) if xs else float("nan")
        lines.append(f"- **{basis}**: {pos}/{len(xs)} competitions had EV > 0 for a marginal ticket at close "
                     f"({pos / len(xs):.1%}, Wilson 95% CI {lo:.1%}–{hi:.1%}). Mean EV per ticket {mean_ev:.1f}p.")
    fills = sorted(v.fill for v in vals)
    lines += [
        f"- Fill rate (sold / max): median {fills[n // 2]:.0%}, lower quartile {fills[n // 4]:.0%}, "
        f"sold out {sum(1 for f in fills if f >= 0.9999)}/{n}.",
        f"- Return per £ (cash basis), median: "
        f"{sorted((v.ev_cash + v.price) / v.price for v in vals if v.ev_cash is not None)[n // 2] if any(v.ev_cash is not None for v in vals) else float('nan'):.2f}.",
        "",
        "Positive-EV competitions (cash basis), largest first:",
        "",
        "| Competition | Price | Sold / max | Cash value | Break-even sold | EV per ticket |",
        "|---|---|---|---|---|---|",
    ]
    posv = sorted((v for v in vals if v.ev_cash and v.ev_cash > 0), key=lambda v: -v.ev_cash)[:15]
    for v in posv:
        lines.append(f"| {v.slug} | {v.price}p | {v.sold:,} / {v.max_tickets:,} | £{v.cash / 100:,.0f} | "
                     f"{v.break_even_sold_cash:,.0f} | +{v.ev_cash:.1f}p |")
    if not posv:
        lines.append("| — | | | | | |")
    lines += [
        "",
        "Limitations:",
        "",
        "- Ex-post: uses FINAL sold counts, which a buyer does not know. This is an upper bound on achievable value.",
        "- Values are the operator's own figures; cash alternative is the conservative basis. Advertised values are not independently verified.",
        "- One extra ticket only; buying k tickets lowers per-ticket EV because N grows with k.",
        "- Excludes the free postal route, payment fees and the per-person ticket limit.",
        "- Sample of finished automated-draw competitions; live-draw and instant-win formats are not included.",
        "- **Not yet validated out of sample.** A strategy must be forward-tested on observations taken before close.",
    ]
    return "\n".join(lines) + "\n"
