# Commercial opportunity report (V2)

_Evidence: `COMMERCIAL_EVIDENCE_REGISTER.md` (market facts), `LEGAL_RESEARCH_REGISTER.md` (law), `src/raffle_edge/edge/commercial_model.py` (break-even). No customer has been interviewed. No demand or revenue is forecast._

## Market facts that survived primary-source checking

| Fact | Value | Class |
|---|---|---|
| Sector size (London Economics for DCMS, Nov 2023 data) | £1.3bn a year (range £0.7–2.1bn) | A |
| Adult entrants | 7.4m (95% CI 6.6–8.2m) | A |
| Operators found by web crawl | at least 401 | A |
| Omaze share | more than 60% of **players** (not revenue) | A |
| Prize-draw players scoring PGSI 8+ (problem gambling) | 12%, vs 5% of gamblers and 3% of the population | A |
| Code signatories (19 Oct 2026 list) | 138 operators, plus 30 other signatories | A (own count) |
| Government position | "The success of this Code will determine whether the Government decides to take further action, including legislation" | A |
| Winvia (BOTB, Click) FY25 prize draws | £40.3m revenue, £9.6m adjusted EBITDA | C (secondary) |
| Jumbo / Dream Car Giveaways | A$109.9m (£53.9m) at about 6.5x EBITDA, plus earnout up to £12m | C (secondary) |

**Correction to V1:** "88% of entrants also gamble" was wrong. In the report, 88% is the share of **operators offering free entry**.

## Business 1: independent draw verification

- **What exists now:**
  - A working prototype: a five-status classifier, a prototype audit report (`DRAW_AUDIT_7DAYS_PROTOTYPE.md`), and a reference commit-reveal protocol that tests show detects tampering.
- **Why it might sell:**
  - DCMS Code clause 2.2 asks for "a computer process that produces verifiably random and auditable results" or independent supervision.
  - CAP rule 8.25 needs an "independently audited statement" for instant wins.
  - The government links possible legislation to how well the Code works.
- **Competition (incumbents):**
  - **Already Code signatories:** PromoVeritas, The Fair Draw Register, UVS and OCSA.
  - **Test labs:** GLI (certifies Elite's and Omaze's systems).
  - **Other providers:** RANDOM.ORG, which prices by number of entries.
  - **Prices:** none of them publishes one (class E).
- **Differentiator:** reproducing draws from published data, independently of the operator, plus a standard that lets operators prove fairness publicly. Incumbents mostly supervise or certify privately.
- **Costs and break-even:**
  - Evidenced non-salary fixed costs are £1,090–£6,680 a year.
  - Covering those at £1,000 per operator per year needs **1.4–8.3 operators**. At £2,000 it needs 0.7–4.2.
  - One £35k salary at £2,000 per operator needs about **22 operators**, roughly 16% of the 138 signatories.
  - Insurance and legal costs for attestation work are **unknown** and are the largest uncertainty.
- **Risks:**
  - Liability for a wrong attestation.
  - Conflict between auditing operators and publishing research on them.
  - Personal data in entry lists (avoidable with the numbers-only protocol).
  - No accreditation standard exists.
- **Customer demand: UNKNOWN.** It needs interviews (below).

## Business 2: comparison site

- **Competitors:** CompWatch (a free aggregator with trust ratings, and itself a Code signatory) and RaffleScout. Several odds sites named in V1 could not be found.
- **Legal:**
  - Under Gambling Act s.252, publishing material or inviting entry can count as "promoting" a lottery. If a listed operator's free route fails Sch 2 para 8, the site may be promoting an illegal lottery.
  - Code clause 3.2 binds affiliates.
  - CAP comparative-claim rules apply.
- **Costs:** customer-acquisition cost and affiliate rates are unknown, so break-even ranges from 11 to 1,900 paying users depending on assumptions. That's too wide to be useful.
- **Assessment:** crowded and legally exposed, with no evidenced differentiator.

## Business 3: consumer expected-value intelligence

- **Legal:** DMCC Act 2024 Sch 20 para 18 bans, in all cases, "Claiming that products are able to facilitate winning in games of chance". Selling the E05 postal insight, or any "edge", as a product is very likely to fall foul of this. It needs a specialist solicitor before anything else.
- **Harm:** 12% of prize-draw players are problem gamblers (PGSI 8+). A product nudging people to enter more raises serious harm and reputation risk.
- **Substance:** the only supported positive-expected-value route is the free postal one, which is labour-intensive and lottery-like.
- **Assessment:** do not pursue.

## Verdict

Only Business 1 is worth testing, and only through customer interviews first. Nothing in this report shows that operators would pay.

## Interview plan (needs your approval: contacting third parties)

- **Who:**
  - 10–12 compliance leads at Code-signatory operators, mixing large (Winvia, Jumbo-owned DCG, Omaze) and small.
  - 3 existing verifiers.
  - 1 DCMS code contact, via prizedrawcode@dcms.gov.uk.
  - 1 gambling-law solicitor.
- **Ask:**
  - How they evidence clause 2.2 today.
  - What it costs.
  - What a regulator or ASA query would need.
  - Whether a public, reproducible verification would help or hurt them.
  - Who signs off spend, and at what budget.
- **Decision rule:** proceed only if at least 4 operators name a budget of £1,000 a year or more, **and** a solicitor confirms the liability can be insured at a known cost.
