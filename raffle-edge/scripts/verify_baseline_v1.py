"""Phase V2-1: independently re-verify the V1 headline findings from the FROZEN CSVs.

Independence: uses NumPy's MT19937 (not our php_mt port), plain csv parsing (not
the database layer), and fresh EV arithmetic (not the calculator module).
"""
import csv, json, statistics
from pathlib import Path

import numpy as np
from scipy import stats

F = Path(__file__).resolve().parents[1] / "data/frozen/v1"


def php_mt_rand(seed: int, lo: int, hi: int) -> int:
    rs = np.random.RandomState(seed & 0xFFFFFFFF)  # legacy seeding = MT19937 init_genrand
    umax = hi - lo + 1
    limit = 0xFFFFFFFF - (0xFFFFFFFF % umax) - 1 if umax & (umax - 1) else None
    while True:
        r = int(rs.randint(0, 2**32, dtype=np.uint32))
        if limit is None or r <= limit:
            return lo + r % umax


def seed_ms(t: str) -> int:
    whole, _, frac = t.partition(".")
    return int(whole) * 1000 + int((frac + "000")[:3])


out = {}
draws = list(csv.DictReader(open(F / "draw_results.csv")))
auto = [d for d in draws if d["draw_type"] == "automated" and d["rng_index"]]
out["results_total"] = len(draws)
out["automated_draws"] = len(auto)
out["published_example_55"] = php_mt_rand(1234560987123, 1, 100)
pre = [d for d in auto if d["drawn_at"] < "2026-08-04"]
post = [d for d in auto if d["drawn_at"] >= "2026-08-04"]
ok = lambda d: php_mt_rand(seed_ms(d["rng_unix_time"]), 1, int(d["rng_entries"])) == int(d["rng_index"])
out["reproduced_pre_cutover"] = f"{sum(map(ok, pre))}/{len(pre)}"
out["reproduced_post_cutover"] = f"{sum(map(ok, post))}/{len(post)}"

pos = np.array([int(d["rng_index"]) for d in auto]); n = np.array([int(d["rng_entries"]) for d in auto])
out["ks_midpoint_p"] = round(float(stats.kstest((pos - 0.5) / n, "uniform").pvalue), 4)
out["index_out_of_range"] = int(np.sum((pos < 1) | (pos > n)))

obs = list(csv.DictReader(open(F / "competition_observations.csv")))
superseded = {o["supersedes_id"] for o in obs if o["supersedes_id"]}
cur = [o for o in obs if o["observation_id"] not in superseded and o["platform_slug"] == "7days-performance"]
ev, ret = [], []
for o in cur:
    price, mx, sold, cash = int(o["ticket_price_pence"]), int(o["max_tickets"]), int(o["tickets_sold"]), o["cash_alternative_pence"]
    if not cash or price <= 0:
        continue
    others = min(sold, mx - 1)
    e = int(cash) / (others + 1) - price
    ev.append(e); ret.append((e + price) / price)
out["h1_competitions_valued"] = len(ev)
out["h1_positive_ev_cash"] = sum(e > 0 for e in ev)
out["h1_max_ev_pence"] = round(max(ev), 2)
out["return_per_pound_median"] = round(statistics.median(ret), 3)
out["return_per_pound_mean"] = round(statistics.mean(ret), 3)
out["return_per_pound_revenue_weighted"] = round(
    sum(int(o["cash_alternative_pence"]) for o in cur if o["cash_alternative_pence"]) /
    sum(int(o["ticket_price_pence"]) * int(o["tickets_sold"]) for o in cur if o["cash_alternative_pence"]), 3)
print(json.dumps(out, indent=2))
