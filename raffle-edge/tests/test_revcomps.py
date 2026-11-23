"""SYNTHETIC HTML shaped like the public pages; no real data."""
from raffle_edge.collector.revcomps import cash_value, parse_current, parse_entry_lists

CUR = """<div><p>£4.50</p><p>£3.97</p><p>24999 TKTS</p><p>WIN THU 26TH NOV @ 11PM</p><p>11% Sold</p>
<p>2023 TEST CAR + £2,000 OR £45,000</p><p>Enter Now</p>
<p>FREE</p><p>9999999 TKTS</p><p>WIN FRI</p><p>1% Sold</p><p>FREE DRAW: £25,000 CASH GIVEAWAY</p></div>"""
LISTS = """<div><p>TEST BIKE</p><p>Draw: MON 16TH NOV</p><p>Total:</p><p>1999</p><p>Sold:</p><p>944</p><p>Remaining:</p><p>1055</p></div>"""


def test_cash_value_rules():
    assert cash_value("2023 X + £5,000 OR £80,000") == (8000000, "cash_alternative_in_title")
    assert cash_value("£10,000 CASH - LOW ODDS") == (1000000, "cash_prize")
    assert cash_value("2019 ABARTH 595C + £1,000") == (None, None)  # car value unknown: no guessing


def test_parse_current_and_discount():
    a, b = parse_current(CUR)
    assert (a.price_pence, a.was_price_pence, a.max_tickets, a.sold_pct, a.cash_value_pence) == (397, 450, 24999, 11.0, 4500000)
    assert b.price_pence == 0 and b.max_tickets == 9999999


def test_parse_entry_lists():
    (e,) = parse_entry_lists(LISTS)
    assert (e.total, e.sold, e.remaining) == (1999, 944, 1055)
