"""Collector parsing on a SYNTHETIC payload shaped like the public feed."""
from raffle_edge.collector.sevendays import parse_page, store

PAYLOAD = {
    "data": [
        {"id": 1, "raffle": {"id": 10, "slug": "win-a-thing", "title": "Win A Thing", "end_at": "2026-11-01T20:00:00+00:00",
                             "result_at": "2026-11-01T20:15:00+00:00", "is_instant_win": False},
         "winner": {"full_name": "Synthetic Person", "ticket_number": "42"},
         "random_draw_result_winner": {"unix_time": "1779570130.513", "rng_seed": "ab" * 32,
                                       "winning_index": 7, "entries_number": 100, "winning_raffle_number": "42"}},
        {"id": 2, "raffle": {"id": 11, "slug": "instant-thing", "title": "Instant", "is_instant_win": True},
         "winner": {"full_name": "Another Person", "ticket_number": "5"}},
    ],
    "pagination": {"next": None, "last": 1},
}


def test_parse_drops_names_and_keeps_rng_fields():
    results, pag = parse_page(PAYLOAD)
    assert pag["last"] == 1
    a, b = results
    assert a.draw_type == "automated" and a.rng_index == 7 and a.rng_entries == 100 and a.winning_ticket == 42
    assert b.draw_type == "instant_win" and b.rng_index is None
    assert "Person" not in repr(results)


def test_store_is_idempotent_and_has_no_names(conn):
    results, _ = parse_page(PAYLOAD)
    assert store(conn, results, None) == 2
    assert store(conn, results, None) == 0
    dump = "\n".join(str(tuple(r)) for r in conn.execute("SELECT * FROM draw_results"))
    assert "Person" not in dump


def test_parse_detail_value_inputs():
    from raffle_edge.collector.sevendays import parse_detail
    d = {"prize_value": 270, "is_cash": False, "cash_alternative": 200, "prize_count": 1,
         "end_prizes": [{"cashAlternative": "200.00"}], "offers": [{"price": 0.39, "tickets_quantity": 1}],
         "max_entries": 1299, "current_entries": 1278, "ticket_limit_per_user": 130, "end_at": "2026-11-22T21:45:00+00:00",
         "winner": {"full_name": "Synthetic Person", "ticket_number": "6"}}
    v = parse_detail(d)
    assert v["ticket_price_pence"] == 39 and v["cash_alternative_pence"] == 20000 and v["advertised_value_pence"] == 27000
    assert v["max_tickets"] == 1299 and v["tickets_sold"] == 1278
    assert "Person" not in repr(v)


def test_cash_prize_value_is_its_cash_value():
    from raffle_edge.collector.sevendays import parse_detail
    v = parse_detail({"prize_value": 1000, "is_cash": True, "cash_alternative": None, "prize_count": 1,
                      "end_prizes": [], "offers": [{"price": 0.02, "tickets_quantity": 1}],
                      "max_entries": 94999, "current_entries": 94999})
    assert v["cash_alternative_pence"] == 100000 and v["advertised_value_pence"] == 100000
