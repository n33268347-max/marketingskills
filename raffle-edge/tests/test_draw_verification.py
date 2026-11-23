from raffle_edge.edge.draw_verification import SEVENDAYS_V1, DrawRecord, verify
from raffle_edge.edge.verifiable_draw_spec import PublishedDraw, run_draw, verify_published
from raffle_edge.audit.php_mt import mt_rand_once


def rec(**kw):
    base = dict(operator="op", draw_id="1", competition="c", drawn_at="2026-06-01", draw_type="automated",
                published_seed=None, unix_time=None, index=None, entries=None, winning_ticket=None)
    base.update(kw)
    return DrawRecord(**base)


def test_status_classification():
    seed, n = 1779570244696, 500
    good = rec(published_seed=str(seed), unix_time="1779570244.696", entries=n, index=mt_rand_once(seed, 1, n))
    bad = rec(published_seed=str(seed), unix_time="1779570244.696", entries=n, index=(mt_rand_once(seed, 1, n) % n) + 1)
    live = rec(draw_type="live_or_unspecified")
    newfmt = rec(published_seed="ab" * 32, unix_time="1779570244.696", entries=n, index=3)
    broken = rec(published_seed="1", entries=10, index=11)
    s = [v.status for v in verify([good, bad, live, newfmt, broken], [SEVENDAYS_V1])]
    assert s == ["REPRODUCIBLE", "NOT_INDEPENDENTLY_REPRODUCIBLE", "INSUFFICIENT_INFORMATION",
                 "NOT_INDEPENDENTLY_REPRODUCIBLE", "INCONSISTENT_EVIDENCE"]


def test_entry_list_upgrades_to_verified():
    seed, n = 1779570244696, 5
    i = mt_rand_once(seed, 1, n)
    tickets = [11, 22, 33, 44, 55]
    r = rec(published_seed=str(seed), unix_time="1779570244.696", entries=n, index=i, winning_ticket=tickets[i - 1], entry_list=tickets)
    assert verify([r], [SEVENDAYS_V1])[0].status == "VERIFIED"


def test_commit_reveal_protocol_detects_tampering():
    d = run_draw(b"secret-seed-0001", "comp-42", [7, 3, 19, 4, 88, 61])
    assert verify_published(d) == []
    forged = PublishedDraw(**{**d.__dict__, "winning_ticket": 7 if d.winning_ticket != 7 else 3})
    assert verify_published(forged)
    swapped = PublishedDraw(**{**d.__dict__, "revealed_seed_hex": b"other-seed".hex()})
    assert "revealed seed does not match pre-close commitment" in verify_published(swapped)
    added = PublishedDraw(**{**d.__dict__, "tickets": d.tickets + [99]})
    assert "entry list does not match published entry hash" in verify_published(added)


def test_protocol_index_is_uniform():
    from collections import Counter
    c = Counter(run_draw(f"s{i}".encode(), "d", list(range(1, 6))).winning_index for i in range(5000))
    assert all(900 < c[k] < 1100 for k in range(1, 6))
