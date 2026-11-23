"""Break-even arithmetic for the three business models.

No demand or revenue forecast is made. Every input carries an evidence class
(A primary, B secondary, C inference, D estimate/assumption, E unknown). The
output answers only: "how many paying customers at price P are needed to cover
the costs we can evidence?" Whether those customers exist requires interviews.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    name: str
    low: float
    high: float
    evidence: str
    note: str = ""


# Annual fixed costs (GBP). Sources: docs/v2/COMMERCIAL_EVIDENCE_REGISTER.md
COMMON = [
    Item("Company formation (one-off, annualised over 1 yr)", 100, 100, "A", "Companies House fee"),
    Item("Confirmation statement", 50, 50, "A", "Companies House fee"),
    Item("Accountant", 150, 1800, "D", "quoted ranges, not a quote"),
    Item("Hosting (small Postgres + app)", 60, 180, "C/D", "$6-15/month"),
    Item("Domain, email, misc software", 50, 300, "D", "assumption"),
]
PER_MODEL = {
    "B1 draw auditing": [
        Item("Professional indemnity insurance", 130, 500, "D", "generic low-risk consultancy; audit/attestation cover UNKNOWN and likely higher (E)"),
        Item("Solicitor: engagement terms, liability, attestation wording", 550, 750, "D", "consumer-terms range used as floor; audit-specific fee UNKNOWN (E)"),
        Item("Sales time / travel / conferences", 0, 3000, "D", "assumption"),
    ],
    "B2 comparison site": [
        Item("Solicitor: s.252 'promoting' risk, CAP compliance, affiliate terms", 550, 750, "D", "floor; specialist gambling advice UNKNOWN (E)"),
        Item("Customer acquisition (SEO/paid)", 0, 12000, "E", "CAC unknown; range is a placeholder"),
        Item("Data collection & database-right clearance", 0, 2000, "E", "depends on operator permissions"),
    ],
    "B3 consumer EV intelligence": [
        Item("Solicitor: DMCC Act Sch 20 para 18 clearance", 550, 2000, "D", "banned practice risk; may be unclearable"),
        Item("Customer acquisition", 0, 12000, "E", "unknown"),
    ],
}


def fixed_costs(model: str) -> tuple[float, float]:
    items = COMMON + PER_MODEL[model]
    return sum(i.low for i in items), sum(i.high for i in items)


def break_even_customers(annual_cost: float, price_per_customer_year: float, gross_margin: float) -> float:
    return annual_cost / (price_per_customer_year * gross_margin)


def table(model: str, prices: list[float], gross_margin: float) -> list[dict]:
    lo, hi = fixed_costs(model)
    return [{"price_gbp_per_year": p, "customers_needed_low_cost": round(break_even_customers(lo, p, gross_margin), 1),
             "customers_needed_high_cost": round(break_even_customers(hi, p, gross_margin), 1)} for p in prices]
