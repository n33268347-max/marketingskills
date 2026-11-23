"""Competition value calculator (Phase 3).

All money is integer pence on input; outputs are floats in pence unless named
otherwise. Nothing here guesses: every input that matters must be supplied, and
the caller states which prize valuation basis it is using.

Key definitions (do not mix these up):
  max_tickets              - the cap published by the operator
  tickets_sold_by_others   - tickets other people hold at draw time (NOT
                             "remaining", NOT "max")
  k                        - tickets YOU buy
  N (draw base)            - the set the winner is drawn from:
        'sold' : only sold tickets can win (operator redraws on an unsold
                 number, or draws from the sold list). N = sold_by_others + k
        'max'  : any number 1..max can be drawn and an unsold winning number
                 means nobody wins.                       N = max_tickets

For m prizes drawn without replacement, the chance that a particular prize
lands on one of your k tickets is k/N for every prize (symmetry), so expected
prize value is linear: E[prizes] = (k/N) * sum(values). The probability of
winning at least one prize is 1 - C(N-k, m) / C(N, m).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import comb
from typing import Iterable, Literal

ValueBasis = Literal["advertised", "cash_alternative", "verified"]
DrawBase = Literal["sold", "max"]


@dataclass(frozen=True)
class Prize:
    advertised_pence: int | None = None
    cash_alternative_pence: int | None = None
    verified_pence: int | None = None
    count: int = 1

    def value(self, basis: ValueBasis) -> int | None:
        return {"advertised": self.advertised_pence, "cash_alternative": self.cash_alternative_pence,
                "verified": self.verified_pence}[basis]


@dataclass(frozen=True)
class DrawCompetition:
    ticket_price_pence: int
    max_tickets: int
    prizes: tuple[Prize, ...]
    draw_base: DrawBase
    max_tickets_per_person: int | None = None

    def __post_init__(self):
        if self.ticket_price_pence < 0 or self.max_tickets <= 0:
            raise ValueError("price must be >= 0 and max_tickets > 0")
        if not self.prizes:
            raise ValueError("at least one prize is required")


@dataclass
class ValueResult:
    basis: ValueBasis
    k: int
    draw_base_size: int
    total_cost_pence: int
    p_win_any: float
    expected_prize_value_pence: float
    expected_value_pence: float          # EV = E[prizes] - cost
    expected_loss_pence: float           # max(0, -EV)
    return_per_pound: float              # E[prizes] / cost
    break_even_draw_base: float          # N at which EV = 0
    break_even_p_per_ticket: float       # price / total prize value
    notes: list[str] = field(default_factory=list)


def _total_value(prizes: Iterable[Prize], basis: ValueBasis) -> tuple[int, int, list[str]]:
    total, m, notes = 0, 0, []
    for p in prizes:
        v = p.value(basis)
        if v is None:
            raise ValueError(f"prize lacks a {basis} value; supply it or choose another basis")
        total += v * p.count
        m += p.count
    if basis == "advertised":
        notes.append("Advertised value: set by the operator, not independently verified.")
    return total, m, notes


def evaluate(comp: DrawCompetition, k: int, tickets_sold_by_others: int, basis: ValueBasis = "verified",
             fees_pence: int = 0) -> ValueResult:
    if k <= 0:
        raise ValueError("k must be >= 1")
    if comp.max_tickets_per_person is not None and k > comp.max_tickets_per_person:
        raise ValueError(f"k={k} exceeds the per-person limit {comp.max_tickets_per_person}")
    if tickets_sold_by_others < 0 or tickets_sold_by_others + k > comp.max_tickets:
        raise ValueError("sold_by_others + k must be within 0..max_tickets")

    total, m, notes = _total_value(comp.prizes, basis)
    n = tickets_sold_by_others + k if comp.draw_base == "sold" else comp.max_tickets
    if m > n:
        notes.append(f"{m} prizes but only {n} tickets in the draw base; some prizes cannot be awarded.")
    m_eff = min(m, n)
    p_any = 1.0 - comb(n - k, m_eff) / comb(n, m_eff) if m_eff else 0.0
    # Linear expected value; if prizes exceed tickets, each ticket wins at most one prize.
    e_prizes = (k / n) * total if m <= n else total * (k / m)
    cost = k * comp.ticket_price_pence + fees_pence
    ev = e_prizes - cost
    if comp.draw_base == "max":
        notes.append("Draw base is max tickets: unsold winning numbers award nothing.")
    return ValueResult(
        basis=basis, k=k, draw_base_size=n, total_cost_pence=cost, p_win_any=p_any,
        expected_prize_value_pence=e_prizes, expected_value_pence=ev, expected_loss_pence=max(0.0, -ev),
        return_per_pound=(e_prizes / cost) if cost else float("inf"),
        break_even_draw_base=(total / comp.ticket_price_pence) if comp.ticket_price_pence else float("inf"),
        break_even_p_per_ticket=(comp.ticket_price_pence / total) if total else float("inf"),
        notes=notes,
    )


def sensitivity(comp: DrawCompetition, k: int, sold_by_others_grid: Iterable[int], basis: ValueBasis = "verified",
                fees_pence: int = 0) -> list[tuple[int, float]]:
    """EV (pence) across possible final sold counts. Only meaningful for draw_base='sold'."""
    return [(s, evaluate(comp, k, s, basis, fees_pence).expected_value_pence) for s in sold_by_others_grid]


@dataclass(frozen=True)
class InstantWinState:
    """Instant-win prizes still unclaimed and tickets still unallocated.

    Assumes (per operator terms where confirmed) that winning numbers were
    pre-allocated uniformly among all numbers and that a purchased ticket
    receives a uniformly random unallocated number.
    """
    ticket_price_pence: int
    tickets_remaining: int
    remaining_prize_values_pence: tuple[int, ...]

    def expected_value(self, k: int, fees_pence: int = 0) -> dict:
        if not 0 < k <= self.tickets_remaining:
            raise ValueError("k must be in 1..tickets_remaining")
        total = sum(self.remaining_prize_values_pence)
        e = k * total / self.tickets_remaining
        cost = k * self.ticket_price_pence + fees_pence
        w = len(self.remaining_prize_values_pence)
        p_any = 1.0 - comb(self.tickets_remaining - w, k) / comb(self.tickets_remaining, k) if w else 0.0
        return {"expected_prize_value_pence": e, "cost_pence": cost, "expected_value_pence": e - cost,
                "p_win_any": p_any, "return_per_pound": e / cost if cost else float("inf")}
