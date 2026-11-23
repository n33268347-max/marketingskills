"""Reference implementation of a proposed publishable, verifiable draw protocol.

Goal: let anyone verify a draw WITHOUT the operator exposing internal systems or
personal data. Protocol (commit-reveal):

  1. Before sales close: publish  commitment = SHA256(server_seed)          (seed kept secret)
  2. At close: publish the ordered list of SOLD ticket numbers (numbers only, no names)
     and entry_hash = SHA256("\n".join(ticket numbers in issue order))
  3. Draw: index = unbiased_index(HMAC-SHA256(server_seed, draw_id | entry_hash), N)
  4. After the draw: reveal server_seed.

Anyone can then check: SHA256(server_seed) == commitment (seed fixed before close),
entry_hash matches the published list, and the index -> winning ticket.
The operator cannot choose the seed after seeing the entries; players cannot
predict the result because the seed is secret until after close.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


def commitment(server_seed: bytes) -> str:
    return hashlib.sha256(server_seed).hexdigest()


def entry_hash(tickets: list[int]) -> str:
    return hashlib.sha256("\n".join(str(t) for t in tickets).encode()).hexdigest()


def unbiased_index(server_seed: bytes, draw_id: str, ehash: str, n: int) -> int:
    """1-based index in 1..n, rejection sampling over successive HMAC blocks (no modulo bias)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    limit = (2**256 // n) * n
    counter = 0
    while True:
        mac = hmac.new(server_seed, f"{draw_id}|{ehash}|{counter}".encode(), hashlib.sha256).digest()
        x = int.from_bytes(mac, "big")
        if x < limit:
            return x % n + 1
        counter += 1


@dataclass
class PublishedDraw:
    draw_id: str
    commitment: str
    tickets: list[int]
    entry_hash: str
    revealed_seed_hex: str
    winning_index: int
    winning_ticket: int


def run_draw(server_seed: bytes, draw_id: str, tickets: list[int]) -> PublishedDraw:
    eh = entry_hash(tickets)
    i = unbiased_index(server_seed, draw_id, eh, len(tickets))
    return PublishedDraw(draw_id, commitment(server_seed), tickets, eh, server_seed.hex(), i, tickets[i - 1])


def verify_published(d: PublishedDraw) -> list[str]:
    """Return a list of failures (empty = verified)."""
    seed = bytes.fromhex(d.revealed_seed_hex)
    fails = []
    if commitment(seed) != d.commitment:
        fails.append("revealed seed does not match pre-close commitment")
    if entry_hash(d.tickets) != d.entry_hash:
        fails.append("entry list does not match published entry hash")
    if len(set(d.tickets)) != len(d.tickets):
        fails.append("duplicate ticket numbers in entry list")
    i = unbiased_index(seed, d.draw_id, d.entry_hash, len(d.tickets))
    if i != d.winning_index:
        fails.append("recomputed index differs from published index")
    elif d.tickets[i - 1] != d.winning_ticket:
        fails.append("published winning ticket is not at the recomputed index")
    return fails
