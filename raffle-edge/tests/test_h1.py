from raffle_edge.analysis.h1_value import load, wilson
from raffle_edge.db.database import ensure_competition, ensure_platform, insert


def test_wilson_known_value():
    lo, hi = wilson(10, 100)
    assert round(lo, 3) == 0.055 and round(hi, 3) == 0.174


def test_load_computes_marginal_ev(conn):
    ensure_platform(conn, "7days-performance", "7days", "https://x.test")
    cid = ensure_competition(conn, "7days-performance", "c1", "c1")
    # Cash £100, 39p, 199 sold of 1,000: one more ticket -> N=200, E=50p, EV=+11p.
    insert(conn, "competition_observations", {"competition_id": cid, "observed_at": "2026-11-01T00:00:00Z",
        "source_url": "https://x.test", "ticket_price_pence": 39, "max_tickets": 1000, "tickets_sold": 199,
        "cash_alternative_pence": 10000, "advertised_value_pence": 12000})
    conn.commit()
    (v,) = load(conn)
    assert round(v.ev_cash, 6) == 11 and round(v.ev_adv, 6) == 21
    assert v.break_even_sold_cash == 10000 / 39
