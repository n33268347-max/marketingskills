"""Writes data/processed/v2/edge_register.json and docs/v2/MATHEMATICAL_EDGE_REGISTER.md.

Status vocabulary: UNTESTED, INVESTIGATING, REJECTED, INCONCLUSIVE, SUPPORTED,
VALIDATED, NOT PRACTICALLY EXPLOITABLE. Nothing is VALIDATED on historical data alone.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"UNTESTED", "INVESTIGATING", "REJECTED", "INCONCLUSIVE", "SUPPORTED", "VALIDATED", "NOT PRACTICALLY EXPLOITABLE"}
E = [
 dict(id="E01", platform="7days Performance", hypothesis="Winning positions are biased (non-uniform, endpoint bug, serial dependence)",
      maths="Under a fair draw the winning index is uniform on 1..N and independent across draws.",
      data="766 automated draws: winning index, entries (frozen V1)",
      historical="6 tests, none significant after Benjamini-Hochberg (chi-square p=0.20, KS p=0.12, runs p=0.57, lag-1 r=0.042)",
      validation="Independent re-check with SciPy on frozen data: KS p=0.119", significance="Not significant", ci="KS D=0.043",
      access="n/a", advantage="None", costs="n/a", legal="None", status="REJECTED"),
 dict(id="E02", platform="7days Performance", hypothesis="A 'hot' region of the ticket list keeps winning",
      maths="Pick the most frequent winning decile in training; test whether it beats its 10% baseline later.",
      data="766 automated draws, chronological split at 2026-09-01", historical="Train: decile 5 at 12.5%",
      validation="Test: 12.3% (95% CI 9.0-16.1%), one-sided p=0.098", significance="Not significant", ci="9.0-16.1%",
      access="Not accessible anyway: tickets are randomly allocated", advantage="None", costs="n/a", legal="None", status="REJECTED"),
 dict(id="E03", platform="7days Performance", hypothesis="Paid ticket has positive EV using only pre-purchase information",
      maths="EV floor per ticket = V/(max+1) - price (draw cannot exceed max).",
      data="200 sampled competitions: price, max, cash value", historical="0/200 competitions have positive floor EV",
      validation="n/a (no candidates)", significance="n/a", ci="Bayes 95% credible upper bound for share ~1.8%",
      access="n/a", advantage="None", costs="Ticket price", legal="None", status="REJECTED"),
 dict(id="E04", platform="7days Performance", hypothesis="Undersold paid tickets are profitable with perfect hindsight (upper bound)",
      maths="Optimal k* = sqrt(V*S/p) - S; profit = k*V/(S+k) - k*p using FINAL sold counts.",
      data="200 sampled competitions", historical="3/200 profitable; total best-case profit GBP 4.89 on GBP 100 spent across the whole sample",
      validation="Ex-post only by definition", significance="n/a", ci="3/200 = 1.5% (Wilson 0.5-4.3%)",
      access="Requires knowing final sales in advance: impossible", advantage="At most ~5% return even with perfect foresight",
      costs="Ticket price", legal="None", status="NOT PRACTICALLY EXPLOITABLE"),
 dict(id="E05", platform="7days Performance", hypothesis="Free postal entry on expensive tickets has positive EV (ex-ante rule)",
      maths="A postcard earns t = ceil(91p/price) tickets (min 1) with equal odds. Floor EV/card = t*V/(max+t). Rule: post only if floor EV > cost/card (91p stamp + 15p card = 106p).",
      data="200 sampled competitions incl. tickets_per_postcard; 7days T&Cs 3.5.7 (A)",
      historical="16/200 (8.4%, Bayes 95% CrI 5.0-12.6%) qualify; train period 7/103 selected, all realised EV > cost",
      validation="Test period (Sep-Nov) 9/97 selected; realised EV/cost mean 2.98 (bootstrap 95% CI 1.71-5.38); 100% above cost",
      significance="Floor EV > cost by construction for selected competitions; realised EV confirmed out of sample",
      ci="EV/cost 1.71-5.38", access="Legal, terms-permitted route (multiple postcards allowed up to the per-person limit, each posted separately; account required)",
      advantage="Mean ~GBP 3.16 expected value per GBP 1.06 card on qualifying competitions",
      costs="91p stamp + postcard + ~3 min per card; P(win) per card ~0.16%: ~442 cards (~GBP 470) for a 50% chance of one win",
      legal="Statutory free-entry route (Gambling Act 2005 Sch 2 para 8). Personal use only: selling it as a 'way to win' risks DMCC Act 2024 Sch 20 para 18.",
      status="SUPPORTED"),
 dict(id="E06", platform="All", hypothesis="Choosing or receiving particular ticket numbers changes the odds",
      maths="Winner uniform over sold tickets => every ticket has probability 1/N regardless of its number.",
      data="200 winning ticket numbers vs max (7days)", historical="Winning numbers uniform over 1..max (KS p=0.93)",
      validation="Mathematical identity", significance="n/a", ci="n/a", access="n/a", advantage="None", costs="n/a", legal="None",
      status="REJECTED"),
 dict(id="E07", platform="7days Performance", hypothesis="Prize type and structure change expected value",
      maths="OLS of log realised return on log price, cash-prize flag, log max, fill (HC3 errors).",
      data="200 sampled competitions", historical="Cash prizes return ~27% more per GBP (b=0.242, 95% CI 0.211-0.272); designed payout if sold out ~41-50p per GBP",
      validation="Not yet replicated on a second operator", significance="p<1e-50 (cash flag)", ci="0.211-0.272",
      access="Informative for choosing among competitions; does not make paid entries positive EV", advantage="Lower expected loss, not profit",
      costs="n/a", legal="None", status="SUPPORTED"),
 dict(id="E08", platform="7days Performance", hypothesis="Bundle / multi-ticket discounts lower effective price",
      maths="Effective price = bundle price / tickets.", data="Offers on 200 competition records",
      historical="All 200 records have a single price (no bundles)", validation="n/a", significance="n/a", ci="n/a",
      access="n/a", advantage="None at 7days", costs="n/a", legal="None", status="REJECTED"),
 dict(id="E09", platform="Rev Comps", hypothesis="Live draws that close well below break-even fill give paid tickets positive EV, observable before close",
      maths="Break-even fill = V/(price*max) (~38-45% observed). Rev Comps shows % sold before close and draws regardless of sell-out.",
      data="Pre-close % sold (forward observations from 23 Nov 2026) + final entry lists",
      historical="Last week's 6 live draws closed 47-75% full (above break-even). 3 draws on 23 Nov were 26-33% sold at 06:45 UTC.",
      validation="Forward test scheduled: observations 12:00/17:00/20:30 UTC, final lists 24 Nov",
      significance="Pending", ci="Pending", access="Paid tickets; % sold is public", advantage="Unknown",
      costs="Ticket price; per-person limits", legal="Personal use only (DMCC Sch 20 para 18 for any product)", status="INVESTIGATING"),
 dict(id="E10", platform="Rev Comps, Aspire, DCG, Omaze, Elite, Lucky Day", hypothesis="Free postal entry gives positive EV on other platforms",
      maths="As E05; depends on entries per card and price.",
      data="Terms confirmed: Rev Comps 1 entry/card, equal chance; Omaze 1 entry/card; Aspire extra entries for cheap comps; DCG 10 entries/card on 9p comps",
      historical="Not computed: needs price, max and cash value per competition", validation="n/a", significance="n/a", ci="n/a",
      access="Terms-permitted", advantage="Likely similar to E05 on expensive tickets (Rev Comps tickets up to GBP 27.27)",
      costs="As E05", legal="As E05", status="INVESTIGATING"),
 dict(id="E11", platform="7days Performance", hypothesis="Time-seeded Mersenne Twister (pre-Aug 2026) makes outcomes predictable",
      maths="Seed = millisecond timestamp; index depends on the sold list at close.",
      data="302 reproducible draws", historical="Draw reproducible after the fact",
      validation="Out of scope: predicting draws is not attempted", significance="n/a", ci="n/a",
      access="None for entrants: ticket numbers are randomly allocated and the sold list is fixed at close", advantage="None",
      costs="n/a", legal="Attempting to manipulate draws would be unlawful/unethical", status="NOT PRACTICALLY EXPLOITABLE"),
 dict(id="E12", platform="Rev Comps", hypothesis="Free/bonus draws (zero-cost entries) have positive EV",
      maths="EV per free entry = V/N with cost = 0 (time only).", data="Rev Comps 'FREE & BONUS DRAW: GBP 25,000' (9,999,999 tickets, 1% sold on 23 Nov)",
      historical="~GBP 0.25 per entry if ~100k entries", validation="Not tested", significance="n/a", ci="n/a",
      access="Account required; likely one entry per person", advantage="Pennies per entry", costs="Time", legal="None",
      status="NOT PRACTICALLY EXPLOITABLE"),
 dict(id="E13", platform="Dream Car Giveaways", hypothesis="Visible remaining instant-win numbers create positive-EV moments",
      maths="EV per ticket = sum(remaining instant prizes)/tickets remaining + end-prize EV.",
      data="Requires repeated live observation of instant-win pages", historical="Not collected", validation="n/a",
      significance="n/a", ci="n/a", access="Unknown", advantage="Unknown", costs="Ticket price", legal="None", status="UNTESTED"),
]
for e in E:
    assert e["status"] in STATUSES, e["id"]
out = ROOT / "data/processed/v2/edge_register.json"
out.write_text(json.dumps(E, indent=2) + "\n")
L = ["# Mathematical edge register", "", "_Generated by `scripts/build_edge_register.py` from `data/processed/v2/edge_register.json`. Nothing is VALIDATED on historical backtests alone._", "",
     "| ID | Platform | Hypothesis | Status | Estimated advantage |", "|---|---|---|---|---|"]
L += [f"| {e['id']} | {e['platform']} | {e['hypothesis']} | **{e['status']}** | {e['advantage']} |" for e in E]
for e in E:
    L += ["", f"## {e['id']}: {e['hypothesis']}", "", f"- **Platform:** {e['platform']}", f"- **Status:** {e['status']}"]
    for k, lbl in (("maths", "Mathematical explanation"), ("data", "Data requirements"), ("historical", "Historical results"),
                   ("validation", "Validation results"), ("significance", "Statistical significance"), ("ci", "Confidence interval"),
                   ("access", "Practical accessibility"), ("advantage", "Estimated advantage"), ("costs", "Costs"), ("legal", "Legal considerations")):
        L.append(f"- **{lbl}:** {e[k]}")
(ROOT / "docs/v2/MATHEMATICAL_EDGE_REGISTER.md").write_text("\n".join(L) + "\n")
print(len(E), "edges;", {s: sum(e["status"] == s for e in E) for s in sorted({e["status"] for e in E})})
