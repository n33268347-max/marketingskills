"""Generic, conservative extractor for public competition pages.

It only returns a field when it finds explicit evidence, and records where each
value came from (`provenance`). It never guesses: an absent field stays None.

Platform-specific parsers (Phase 2) should subclass or wrap this once real,
robots-permitted page snapshots have been archived for each platform.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup

_NUM = r"(\d{1,3}(?:,\d{3})+|\d+)"


def _int(s: str) -> int:
    return int(s.replace(",", ""))


def _pence(s: str) -> int | None:
    try:
        return int((Decimal(s.replace(",", "").replace("£", "").strip()) * 100).to_integral_value())
    except (InvalidOperation, ValueError):
        return None


@dataclass
class ExtractedCompetition:
    name: str | None = None
    ticket_price_pence: int | None = None
    max_tickets: int | None = None
    tickets_sold: int | None = None
    tickets_remaining: int | None = None
    tickets_sold_basis: str | None = None
    advertised_value_pence: int | None = None
    cash_alternative_pence: int | None = None
    winning_ticket_number: int | None = None
    provenance: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def _jsonld_blocks(soup: BeautifulSoup) -> list[dict]:
    out: list[dict] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        out.extend(i for i in items if isinstance(i, dict))
    return out


def extract(html: str) -> ExtractedCompetition:
    soup = BeautifulSoup(html, "lxml")
    ec = ExtractedCompetition()

    # 1. Structured data (schema.org Product / Offer) - most reliable.
    for block in _jsonld_blocks(soup):
        types = block.get("@type")
        types = types if isinstance(types, list) else [types]
        if "Product" in types:
            if block.get("name") and ec.name is None:
                ec.name = str(block["name"]).strip()
                ec.provenance["name"] = "json-ld Product.name"
            offers = block.get("offers")
            offers = offers[0] if isinstance(offers, list) and offers else offers
            if isinstance(offers, dict) and offers.get("price") is not None and offers.get("priceCurrency", "GBP") == "GBP":
                p = _pence(str(offers["price"]))
                if p is not None:
                    ec.ticket_price_pence = p
                    ec.provenance["ticket_price_pence"] = "json-ld Offer.price"

    if ec.name is None:
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            ec.name = h1.get_text(" ", strip=True)
            ec.provenance["name"] = "h1"

    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

    # 2. Ticket counts. Formats seen in UK competition sites: "1,265 / 1,999",
    #    "1,265 sold", "734 remaining", "Max 1,999 tickets".
    m = re.search(rf"{_NUM}\s*/\s*{_NUM}\s*(?:tickets|entries|sold)?", text, re.I)
    if m and re.search(r"sold|tickets|entries", text[max(0, m.start() - 40): m.end() + 20], re.I):
        sold, total = _int(m.group(1)), _int(m.group(2))
        if sold <= total:
            ec.tickets_sold, ec.max_tickets = sold, total
            ec.tickets_sold_basis = "disclosed_count"
            ec.provenance["tickets_sold"] = ec.provenance["max_tickets"] = f"text '{m.group(0)}'"
    if ec.max_tickets is None:
        m = re.search(rf"(?:max(?:imum)?|only|total(?: of)?)\s*{_NUM}\s*(?:tickets|entries)", text, re.I)
        if m:
            ec.max_tickets = _int(m.group(1))
            ec.provenance["max_tickets"] = f"text '{m.group(0)}'"
    m = re.search(rf"{_NUM}\s*(?:tickets|entries)?\s*(?:remaining|left)", text, re.I)
    if m:
        ec.tickets_remaining = _int(m.group(1))
        ec.provenance["tickets_remaining"] = f"text '{m.group(0)}'"
        if ec.tickets_sold is None and ec.max_tickets is not None and ec.tickets_remaining <= ec.max_tickets:
            ec.tickets_sold = ec.max_tickets - ec.tickets_remaining
            ec.tickets_sold_basis = "derived_from_remaining"
            ec.provenance["tickets_sold"] = "max_tickets - tickets_remaining"
    if ec.tickets_sold is None and ec.max_tickets is not None:
        m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%\s*sold", text, re.I)
        if m:
            pct = Decimal(m.group(1))
            ec.tickets_sold = int((pct / 100 * ec.max_tickets).to_integral_value())
            ec.tickets_sold_basis = "derived_from_percentage"
            ec.provenance["tickets_sold"] = f"text '{m.group(0)}' x max_tickets (rounded; approximate)"
            ec.warnings.append("tickets_sold derived from a rounded percentage; precision limited")

    # 3. Ticket price if no structured data.
    if ec.ticket_price_pence is None:
        m = re.search(r"(?:ticket price|price per (?:ticket|entry)|per ticket)[:\s]*£\s?(\d+(?:\.\d{1,2})?)", text, re.I) or re.search(
            r"£\s?(\d+(?:\.\d{1,2})?)\s*(?:per|a)\s*(?:ticket|entry)", text, re.I
        )
        if m:
            ec.ticket_price_pence = _pence(m.group(1))
            ec.provenance["ticket_price_pence"] = f"text '{m.group(0)}'"
        else:
            m = re.search(r"(\d{1,2})p\s*(?:per|a)?\s*(?:ticket|entry)", text, re.I)
            if m:
                ec.ticket_price_pence = int(m.group(1))
                ec.provenance["ticket_price_pence"] = f"text '{m.group(0)}'"

    # 4. Prize value and cash alternative (advertised, NOT verified).
    m = re.search(r"(?:worth|rrp|value[d]?(?: at)?)[:\s]*£\s?([\d,]+(?:\.\d{2})?)", text, re.I)
    if m:
        ec.advertised_value_pence = _pence(m.group(1))
        ec.provenance["advertised_value_pence"] = f"text '{m.group(0)}' (advertised, unverified)"
    m = re.search(r"(?:or|cash alternative(?: of)?)\s*£\s?([\d,]+(?:\.\d{2})?)\s*(?:cash|tax[- ]free)?", text, re.I)
    if m and "cash" in m.group(0).lower():
        ec.cash_alternative_pence = _pence(m.group(1))
        ec.provenance["cash_alternative_pence"] = f"text '{m.group(0)}'"

    # 5. Winning ticket number on result pages.
    m = re.search(rf"winning (?:ticket|number|ticket number)[:#\s]*#?\s*{_NUM}", text, re.I)
    if m:
        ec.winning_ticket_number = _int(m.group(1))
        ec.provenance["winning_ticket_number"] = f"text '{m.group(0)}'"

    if ec.tickets_sold is not None and ec.max_tickets is not None and ec.tickets_sold > ec.max_tickets:
        ec.warnings.append("tickets_sold > max_tickets; discarding both")
        ec.tickets_sold = ec.max_tickets = None
    return ec
