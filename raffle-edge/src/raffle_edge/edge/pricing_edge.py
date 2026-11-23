"""A1: what drives differences in expected value between competitions?

payout_if_sold_out = V / (price * max)   (designed return per £ if it sells out)
realised_return    = V / (price * sold)  (return per £ given final sales)
OLS on log(realised_return) with HC3 robust errors.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import statsmodels.api as sm


def load(path: Path):
    out = []
    for r in csv.DictReader(open(path)):
        if not r["cash_value_pence"]:
            continue
        price, mx, sold, v = int(r["ticket_price_pence"]), int(r["max_tickets"]), int(r["tickets_sold"]), int(r["cash_value_pence"])
        out.append({"competition": r["competition"], "price": price, "max": mx, "sold": sold, "value": v,
                    "cash_prize": int(r["is_cash_prize_title"]), "fill": sold / mx,
                    "payout_if_sold_out": v / (price * mx), "realised_return": v / (price * sold)})
    return out


def bands(rows, key, edges):
    res = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r for r in rows if lo <= r[key] < hi]
        if sel:
            res.append({"band": f"{lo}-{hi}", "n": len(sel),
                        "median_payout_if_sold_out": float(np.median([r["payout_if_sold_out"] for r in sel])),
                        "median_realised_return": float(np.median([r["realised_return"] for r in sel]))})
    return res


def regression(rows):
    y = np.log([r["realised_return"] for r in rows])
    X = np.column_stack([np.log([r["price"] for r in rows]), [r["cash_prize"] for r in rows],
                         np.log([r["max"] for r in rows]), [r["fill"] for r in rows]])
    X = sm.add_constant(X)
    m = sm.OLS(y, X).fit(cov_type="HC3")
    names = ["const", "log_price", "cash_prize", "log_max_tickets", "fill_rate"]
    return {"n": int(m.nobs), "r2": float(m.rsquared),
            "coef": {n: {"b": float(b), "se": float(s), "p": float(p), "ci": [float(c[0]), float(c[1])]}
                     for n, b, s, p, c in zip(names, m.params, m.bse, m.pvalues, m.conf_int())}}
