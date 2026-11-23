"""Rev Comps: parse the server-rendered current-competitions and past entry-list pages.

Only public, server-rendered HTML is used (fetched through PoliteFetcher with
the site's 60 s Crawl-delay). The paginated archive is loaded by a third-party
API; that API is NOT used. Prize cash values are taken only where the title
states a cash alternative ("... OR £80,000") or the prize is cash itself.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from bs4 import BeautifulSoup

_MONEY = r"£\s?([\d,]+(?:\.\d{2})?)"


def _p(s: str) -> int:
    return int(round(float(s.replace(",", "")) * 100))


@dataclass
class RevCurrent:
    title: str
    price_pence: int
    was_price_pence: int | None
    max_tickets: int
    sold_pct: float | None
    draw_text: str
    cash_value_pence: int | None
    cash_basis: str | None


def cash_value(title: str) -> tuple[int | None, str | None]:
    m = re.search(r"\bOR\s+" + _MONEY, title, re.I)
    if m:
        return _p(m.group(1)), "cash_alternative_in_title"
    m = re.fullmatch(r".*?" + _MONEY + r"\s+(?:TAX[- ]FREE\s+)?CASH\b.*", title, re.I)
    if m and not re.search(r"\+\s*" + _MONEY + r"\s+(?:TAX[- ]FREE\s+)?CASH", title, re.I):
        return _p(m.group(1)), "cash_prize"
    return None, None


def parse_current(html: str) -> list[RevCurrent]:
    text = BeautifulSoup(html, "lxml").get_text("\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    out, i = [], 0
    while i < len(lines):
        if re.fullmatch(r"\d[\d,]* TKTS", lines[i]):
            prices = []
            j = i - 1
            while j >= 0 and re.fullmatch(r"£[\d,.]+|FREE", lines[j]):
                prices.insert(0, lines[j]); j -= 1
            draw = lines[i + 1] if i + 1 < len(lines) else ""
            pct = re.fullmatch(r"(\d+)% Sold", lines[i + 2]) if i + 2 < len(lines) else None
            title = lines[i + 3] if pct and i + 3 < len(lines) else ""
            if prices and title:
                cur = prices[-1]
                price = 0 if cur == "FREE" else _p(cur.strip("£"))
                was = _p(prices[0].strip("£")) if len(prices) > 1 and prices[0] != "FREE" else None
                cv, basis = cash_value(title)
                out.append(RevCurrent(title, price, was, int(lines[i].split()[0].replace(",", "")),
                                      float(pct.group(1)) if pct else None, draw, cv, basis))
            i += 4
        else:
            i += 1
    return out


@dataclass
class RevEntryList:
    title: str
    draw_date_text: str
    total: int
    sold: int
    remaining: int
    cash_value_pence: int | None


def parse_entry_lists(html: str) -> list[RevEntryList]:
    text = BeautifulSoup(html, "lxml").get_text("\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    out = []
    for i, l in enumerate(lines):
        if l.startswith("Draw:") and i >= 1 and i + 6 < len(lines) and lines[i + 1] == "Total:" and lines[i + 3] == "Sold:":
            cv, _ = cash_value(lines[i - 1])
            out.append(RevEntryList(lines[i - 1], l[5:].strip(), int(lines[i + 2]), int(lines[i + 4]), int(lines[i + 6]), cv))
    return out


PLATFORM = "rev-comps"
BASE = "https://www.revcomps.com"
PAGES = {"current": BASE + "/current-competitions", "live_lists": BASE + "/past-entry-lists",
         "auto_lists": BASE + "/past-autodraw-entry-lists"}


def _ref(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:120]


def collect(conn, fetcher) -> dict:
    """One forward observation: current competitions (pre-close % sold) and final entry lists."""
    from ..db.database import ensure_competition, ensure_platform, insert, transaction

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = {"observed_at": now, "current": 0, "final": 0, "errors": []}
    for kind, url in PAGES.items():
        res = fetcher.fetch(url)
        if not res.ok:
            summary["errors"].append(f"{kind}: {res.outcome}")
            continue
        html = res.text()
        with transaction(conn):
            ensure_platform(conn, PLATFORM, "Rev Comps", BASE)
            if kind == "current":
                for c in parse_current(html):
                    cid = ensure_competition(conn, PLATFORM, _ref(c.title), c.title)
                    insert(conn, "competition_observations", {
                        "competition_id": cid, "observed_at": now, "snapshot_id": res.snapshot_id, "source_url": url,
                        "prize_description": c.draw_text, "ticket_price_pence": c.price_pence, "max_tickets": c.max_tickets,
                        "tickets_sold": round(c.sold_pct / 100 * c.max_tickets) if c.sold_pct is not None else None,
                        "tickets_sold_basis": "derived_from_percentage" if c.sold_pct is not None else "not_disclosed",
                        "cash_alternative_pence": c.cash_value_pence,
                        "verified_value_source": c.cash_basis,
                    })
                    summary["current"] += 1
            else:
                for e in parse_entry_lists(html):
                    cid = ensure_competition(conn, PLATFORM, _ref(e.title), e.title)
                    if conn.execute("""SELECT 1 FROM competition_observations WHERE competition_id=? AND tickets_sold=?
                                       AND tickets_sold_basis='disclosed_count'""", (cid, e.sold)).fetchone():
                        continue
                    insert(conn, "competition_observations", {
                        "competition_id": cid, "observed_at": now, "snapshot_id": res.snapshot_id, "source_url": url,
                        "prize_description": f"entry list ({kind}); draw {e.draw_date_text}", "max_tickets": e.total,
                        "tickets_sold": e.sold, "tickets_sold_basis": "disclosed_count", "cash_alternative_pence": e.cash_value_pence,
                    })
                    summary["final"] += 1
    return summary
