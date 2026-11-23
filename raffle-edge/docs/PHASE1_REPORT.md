# Phase 1 report: platform research and prototype

_2026-11-23_

## 1. What was completed

| Item | State |
|---|---|
| R&D plan with pre-registered hypotheses H1–H7 | `docs/RESEARCH_PLAN.md` |
| First ten platforms identified and provisionally ranked | `docs/generated/PLATFORM_RANKING.md` |
| Per-platform dossiers (115 evidence-labelled claims) | `docs/generated/PLATFORM_DOSSIERS.md`, source in `scripts/build_seed.py` |
| Evidence model (A / P / B / C / UNKNOWN), enforced by DB constraints | `src/raffle_edge/db/schema.sql` |
| Immutable SQLite store (append-only triggers, supersede-not-overwrite) | same |
| Compliance-first fetcher | `collector/fetcher.py` |
| Accessibility probe | `collector/probe.py` |
| Conservative page extractor (records the provenance of each field, never guesses) | `parsers/generic.py` |
| Manual draw-result CSV import (evidence URL required, safe to re-run) | `ingest.py`, `data/templates/` |
| CLI and generated reports | `cli.py`, `reporting.py` |
| Compliance and disclosure policy | `docs/COMPLIANCE.md` |

The fetcher:
- obeys robots.txt, and treats an unreadable robots.txt as disallow
- enforces a per-host delay
- stops on any CAPTCHA or bot challenge
- archives every response by its SHA-256 hash

## 2. Evidence and test results

```
$ python -m pytest -q
27 passed
```

The tests cover:
- **Immutability:** UPDATE and DELETE are rejected; corrections go through superseding rows.
- **Range checks:** a winning number must fall inside its ticket range, and tickets sold cannot exceed the maximum.
- **Evidence rules:** an `A_CONFIRMED` claim is rejected unless it comes from a direct read.
- **Registry:** seed validation and idempotent sync.
- **Rubric:** points, gaps and negatives, and hypotheses never score.
- **Fetcher:**
  - obeys robots.txt
  - fails closed when robots.txt is unreachable
  - stops on a bot challenge
  - enforces the rate limit
  - archives snapshots
- **Parser:** extracts from structured data and from text, derives counts from percentages with a warning, and returns nothing when the page gives nothing.
- **CSV import:** validates rows and is safe to re-run.

**Live probe (real run):** `raffle-edge probe 7days-performance elite-competitions`. The sandbox's network proxy refused robots.txt, so the fetcher marked every path as disallowed and fetched nothing. This is the intended fail-closed behaviour. It also means **no platform page has been read directly by this project yet.**

## 3. Findings, labelled

**A. Confirmed facts:** none at the `A_CONFIRMED` standard yet. Direct reads were blocked.

**P. Provisional (search snippets or third parties; verify before use):**
- **7days Performance:**
  - Reportedly publishes winning ticket, draw time and sold/total for each draw.
  - Allocates ticket numbers at random.
  - Claims GLI certification.
- **Dream Car Giveaways:**
  - Two different winner-selection methods are described: PHP `random_int` for automated draws, and the Google RNG on Facebook Live. This needs clarifying; they may cover different eras or draw types.
  - Instant-win winning numbers are reportedly visible on the competition page. That would make the remaining instant-win expected value observable from public data (H2).
- **Rev Comps:** a past-entry-lists archive with total, sold and remaining tickets is the best candidate dataset for H1 (undersold competitions that still draw).
- **Several operators:** state that the draw goes ahead "regardless of tickets sold" (7days, Rev Comps, Elite, DCG). This is the structural condition for H1.
- **BOTB:** the main game is a judged spot-the-ball contest, so there is no winning ticket number and integrity tests on numbers do not apply.
- **Omaze:** uses entry codes with millions of entries and no public counts, so it supports value comparison only.

**C. Hypotheses:** H1–H7 in the plan. A reviewer's allegation of a time-seeded Mersenne Twister at one operator is logged as an unverified hypothesis only.

## 4. Missing information

- **Direct reads of every operator page and robots.txt.** This is blocked until the 10 hosts are added to the environment's network allowlist, or the work runs on a normal machine.
- **GOV.UK Code text and signatory list.** Not loaded.
- **Results archives:** how far back each one goes, and whether winning numbers come with a ticket range.
- **Ticket allocation method:** unknown for Elite, Rev Comps, Lucky Day and DCG. This blocks H3 for them; see plan §5.1.
- **Unsold winning numbers:** whether a draw can land on an unsold number, and what happens if it does. This determines N_eff in the calculator.
- **Terms of use per platform** regarding automated access.

## 5. Assumptions

- Search snippets reflect the operators' pages around Nov 2026. They may be stale or paraphrased.
- The ten platforms are representative of the UK numbered-ticket market. Omaze and BOTB are included for scale even though their formats limit the integrity tests.
- The rubric weights (accessibility 60%, transparency 40%) reflect what the statistical work needs. They are a judgement call and are kept in one place (`ranking.py`).

## 6. Recommended next step

**Phase 1b (short):** run the prototype from a network that can reach the platforms.

1. Run `raffle-edge probe --all`.
2. Read terms of use and robots.txt for the top 6.
3. Promote verified claims to `A_CONFIRMED`, with snapshots.
4. Load the GOV.UK Code and signatory list.

**Then Phase 2:** build parsers for 7days and Rev Comps first.
- 7days has the richest per-draw fields.
- Rev Comps' entry lists feed H1.

Bring the Phase 3 value calculator forward alongside Phase 2. H1 is the most plausible genuine edge, and it needs no pattern-finding at all.

---

# Phase 1b: direct verification

_2026-11-23_

## What was completed

- **Network access.** A personal cloud environment, `raffle-edge research`, now allows the 10 platform hosts and www.gov.uk.
- **Live probe.** All 10 platforms were probed. Every robots.txt was archived. Every homepage, results page and terms page we requested was archived, apart from the challenged help.raffall.com.
- **Direct reads.** 155 claims are now `A_CONFIRMED` from direct reads of operator pages and GOV.UK.
  - Each claim cites the SHA-256 of the page it came from.
  - The `merge-verified` command rejects any claim whose quote is not verbatim in that saved page. It was re-run over all 155 claims: 0 failures.
- **Fetcher fixes found during the live run** (tests added for each):
  - It now honours `Crawl-delay`. Click and Rev Comps set 60 s; the first probe used 6 s, which was faster than requested.
  - It now obeys rules for `Claude-User` as well as our own User-Agent.
  - An HTML page served at `/robots.txt` (7days) is treated as "no robots file" and flagged.
  - A CAPTCHA false positive on Omaze, caused by a script merely *naming* `g-recaptcha-response`, is fixed.
- **Terms-based blocklist** (`data/seed/collection_blocklist.json`). It is enforced before any request, including robots.txt, and covers:
  - **BOTB:** T&Cs prohibit "any artificial intelligence tools … or data mining or extraction methods intended to scrape or extract data".
  - **Click Competitions:** the same clause (7.9). Both are Winvia Entertainment companies.

  Six BOTB pages had already been read before the clause was found, one of them the T&Cs themselves. Some Click pages were read before the agent reached clause 7.9, and it stopped fetching Click there. No further automated access to either.
- **Personal-data guard.** Two quotes contained winner names; they were redacted. Claim merging now rejects quotes that look like personal data. **Note:** the Elite name was pushed in an earlier commit on this branch and is redacted in the current version.

## Results: 41 tests pass

## Confirmed findings (A)

| Platform | Draw mechanism (operator's own words) | Unsold number drawn? | Draw regardless of sell-out | Results data |
|---|---|---|---|---|
| 7days Performance | Live: ball machine. Auto: "Mersenne Twister to find the winning ticket's position in the sorted list"; "The seed: This is calculated from the current time". Claims GLI-certified RNG. | Live: "keep re-spinning … until a number is generated that has been sold" | Yes (e.g. 1,278 of 1,299 sold) | Winning ticket number, seed, index, entries count. ~1,650 results back to May 2026. |
| Elite | RNG (GLI-certified) assigns tickets; "physical random ball machine" picks the winner | Redraw until a sold ticket | Prizes awarded in full; T&Cs reserve a right to cancel | Date, prize, ticket number; past competition pages from 2024 |
| Dream Car Giveaways | Live presenter, or "PHP's random_int" for Automated Draws. Compliance page: certified ball machine or RNG software. | Not stated | "regardless of the number of entries" | Winners page: name + date only, ~1 month. Ticket number on closed competitions not checked. |
| Rev Comps | Ball machine live (Google RNG fallback); in-house algorithm over sold tickets for auto | Not stated (live) | Yes (e.g. 45,347 of 69,999 sold) | Entry lists show total/sold/remaining. Older data on prev.revcomps.com (not fetched). |
| Lucky Day | Google RNG on Facebook Live; system pick for auto | Not stated | "no minimum number of entries" | Per-date winning ticket numbers back to Oct 2023; no sold counts |
| Click | Certified RNG (certifier unnamed); auto over sold tickets only | "respins for undersold competitions" | Yes | **Manual only**: terms prohibit AI/scraping |
| Omaze | Internal engine "certified by Gaming Labs, Inc (GLI)" | n/a (entry codes) | n/a | 73 winning entry codes (2026); past house draws to 2024; no entry counts |
| BOTB | Spot-the-ball judged by panel with lawyer; other draws via "PromoVeritas or similar" | n/a | — | **Manual only**: terms prohibit AI/scraping |
| Raffle House | JS-rendered; nothing readable | — | — | robots.txt disallows `/winners` |
| Raffall | JS-rendered; help centre returned a CAPTCHA (not bypassed) | — | — | `/winners/raffles` 404 |

**DCMS Code signatories** (GOV.UK list updated 19 Oct 2026):
- **Listed:** 7 Days Performance, Click Competitions, Rev Comps, Dream Car Giveaways, Elite Competitions, BOTB, Omaze, Raffle House.
- **Not listed:** Lucky Day.
- **Removed:** Raffall, in a GOV.UK update.

The Code requires one of three draw methods:
- an independent person,
- "a computer process that produces verifiably random and auditable results", or
- "a certified physical drawing machine".

It also bars cancelling a draw or reducing a prize because of low sales. It does **not** require publishing winners.

**Provisional claims the direct reads overturned:**
- **Omaze:** we had recorded no results page. In fact one exists.
- **Dream Car Giveaways:**
  - The "Google RNG" wording is no longer on its pages.
  - Its winners page shows no ticket numbers.
- **BOTB:** PromoVeritas is not named for Spot the Ball.
- **Lucky Day:** it does disclose max tickets.

## What this changes for the research

1. **The null model is now known for several platforms.** At Elite, 7days live draws and the Click and Rev Comps auto draws, the winner is drawn only from **sold** tickets. The H3 uniformity test must therefore use the sold set, not the 1..max range (plan §5.1). For 7days, ticket numbers are also randomly allocated.
2. **H1 (undersold draws) is structurally supported.** At least five operators state that draws go ahead regardless of sales, and the Code forbids cancelling for low sales. 7days and Rev Comps publish sold/total figures, which are exactly the H1 inputs.
3. **H8 (new): auditing 7days' automated draws.** The operator publishes the seed, the winning index and the entry count, and names Mersenne Twister. If those published figures let us *reproduce* past results, every automated draw becomes independently auditable. That would be a positive transparency finding.
   - It is **not** an entrant advantage. Tickets are randomly allocated and the sold list is fixed at close, so an entrant cannot use it.
   - A time-based seed is technically weak, but its main risk is operator-side, not player-side.
   - Scope: reproduce **past published draws only**. No prediction of future draws. Any discrepancy goes to the disclosure process in `COMPLIANCE.md`.

## Still unverified

- Raffall and Raffle House: everything except robots.txt and signatory status. Their pages are JS-rendered, and Raffall's help centre returned a CAPTCHA.
- Dream Car Giveaways: whether closed competition pages show the winning number.
- Rev Comps and Click: whether results include ticket numbers. Their results pages are JS-rendered.
- Elite: whether "total amount of entries" on past pages means tickets sold or the cap.
- Main-draw ticket allocation: Elite, Rev Comps, Lucky Day, Click.
- 7days: GLI certificate scope. We saw only the claim.

## Recommended next step: Phase 2

Phase 2 is the historical database plus the Phase 3 value calculator, run together. Work in this order:

1. **7days:**
   - Collect the draw-results archive through its public JSON feed, with names dropped at ingest.
   - Reproduce past automated draws from the published seeds (H8).
   - Compute EV for undersold draws (H1).
2. **Rev Comps:** collect entry lists (total/sold/remaining) to measure how often competitions close undersold.
3. **Elite and Lucky Day:** collect winning ticket numbers for H3, once the sold counts are confirmed.
4. **BOTB and Click:** use them only for manual value comparisons, or ask the operators for data.
