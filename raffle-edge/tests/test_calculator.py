"""Hand-worked cases for the value calculator. Each expected number is derived in the comment."""
import pytest

from raffle_edge.calculator.value import DrawCompetition, InstantWinState, Prize, evaluate, sensitivity


def comp(price=100, mx=1000, prizes=(Prize(verified_pence=50_000),), base="sold", limit=None):
    return DrawCompetition(price, mx, tuple(prizes), base, limit)


def test_single_prize_sold_base():
    # 1 ticket, 499 others -> N=500. P=1/500. E[prize]=50,000/500=100p. Cost 100p. EV=0.
    r = evaluate(comp(), k=1, tickets_sold_by_others=499)
    assert r.draw_base_size == 500
    assert r.p_win_any == pytest.approx(1 / 500)
    assert r.expected_value_pence == pytest.approx(0)
    assert r.break_even_draw_base == pytest.approx(500)
    assert r.break_even_p_per_ticket == pytest.approx(100 / 50_000)


def test_undersold_draw_has_positive_ev():
    # 10 tickets, 190 others -> N=200. E=10/200*50,000=2,500p. Cost 1,000p. EV=+1,500p.
    r = evaluate(comp(), k=10, tickets_sold_by_others=190)
    assert r.expected_value_pence == pytest.approx(1500)
    assert r.return_per_pound == pytest.approx(2.5)


def test_max_base_ignores_sales():
    # Unsold numbers win nothing: N=max=1000 whatever the sales. E=5/1000*50,000=250p, cost 500p.
    r = evaluate(comp(base="max"), k=5, tickets_sold_by_others=10)
    assert r.draw_base_size == 1000 and r.expected_value_pence == pytest.approx(-250)
    assert r.expected_loss_pence == pytest.approx(250)


def test_multiple_prizes_hypergeometric():
    # N=10, k=2, m=3 prizes worth 100p each. P(at least one)=1-C(8,3)/C(10,3)=1-56/120.
    r = evaluate(comp(price=10, mx=10, prizes=(Prize(verified_pence=100, count=3),)), k=2, tickets_sold_by_others=8)
    assert r.p_win_any == pytest.approx(1 - 56 / 120)
    assert r.expected_prize_value_pence == pytest.approx(2 / 10 * 300)


def test_value_bases_are_kept_separate():
    c = comp(prizes=(Prize(advertised_pence=60_000, cash_alternative_pence=45_000),))
    adv = evaluate(c, 1, 499, basis="advertised")
    cash = evaluate(c, 1, 499, basis="cash_alternative")
    assert adv.expected_prize_value_pence == pytest.approx(120) and cash.expected_prize_value_pence == pytest.approx(90)
    assert any("not independently verified" in n for n in adv.notes)
    with pytest.raises(ValueError):
        evaluate(c, 1, 499, basis="verified")


def test_input_guards():
    with pytest.raises(ValueError):
        evaluate(comp(), k=1, tickets_sold_by_others=1000)  # exceeds max
    with pytest.raises(ValueError):
        evaluate(comp(limit=5), k=6, tickets_sold_by_others=0)
    with pytest.raises(ValueError):
        evaluate(comp(), k=0, tickets_sold_by_others=0)


def test_fees_reduce_ev():
    r = evaluate(comp(), k=1, tickets_sold_by_others=499, fees_pence=30)
    assert r.expected_value_pence == pytest.approx(-30)


def test_sensitivity_monotone_in_sales():
    grid = sensitivity(comp(), 1, range(99, 1000, 100))
    evs = [ev for _, ev in grid]
    assert evs == sorted(evs, reverse=True)


def test_instant_win_ev():
    # 1,000 tickets left, prizes 5,000p + 3 x 1,000p = 8,000p. One 50p ticket: E=8p, EV=-42p.
    s = InstantWinState(50, 1000, (5000, 1000, 1000, 1000))
    r = s.expected_value(1)
    assert r["expected_prize_value_pence"] == pytest.approx(8)
    assert r["expected_value_pence"] == pytest.approx(-42)
    assert r["p_win_any"] == pytest.approx(4 / 1000)
