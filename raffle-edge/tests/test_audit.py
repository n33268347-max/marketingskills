from raffle_edge.audit.h8_sevendays import seed_from_unix_time
from raffle_edge.audit.php_mt import PhpMt, mt_rand_once


def test_operator_published_example():
    # 7days' "Draws Explained" page: mt_srand(1234560987123); mt_rand(1, 100) -> 55
    assert mt_rand_once(1234560987123, 1, 100) == 55


def test_mt19937_reference_output():
    assert PhpMt(5489).next_u32() == 3499211612  # standard MT19937 first output


def test_rand_range_bounds():
    g = PhpMt(42)
    vals = [g.rand(1, 6) for _ in range(2000)]
    assert min(vals) == 1 and max(vals) == 6


def test_seed_from_unix_time_is_exact():
    assert seed_from_unix_time("1779570244.696") == 1779570244696
    assert seed_from_unix_time("1779570244.7") == 1779570244700
    assert seed_from_unix_time("1779570244") == 1779570244000
