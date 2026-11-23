> **Corrected H1 figures.** The final sample (200 competitions, cash prizes valued correctly) gives positive EV at cash value in 3 of 200 (1.5%, 95% CI 0.5–4.3%), each worth only pennies, and in 11 of 200 at advertised value. Figures in the body that say otherwise came from a partial sample and are superseded. See `docs/PHASE2_7_REPORT.md`.

# Raffle Edge Phase 7: desk research on three business models

_Prepared 2026-11-23. Not legal advice._

## Method and evidence labels

**Access limits.** The sandbox could not resolve www.gov.uk, so no page was fetched live in this session. Each figure is therefore labelled:

| Label | Meaning |
|---|---|
| **CONFIRMED (snippet)** | Taken from a search-result snippet. The URL is given, but the page was not opened. |
| **CONFIRMED (project read)** | Read directly by the project earlier today and archived with a SHA-256 hash. See `raffle-edge/docs/DCMS_CODE_SUMMARY.md`. |
| **ESTIMATE / UNVERIFIED** | Inference or unverified. |

Before you rely on any figure, re-check it against its primary source.

## Executive summary

- **The market is large and concentrated.** The DCMS-commissioned London Economics study (26 Jun 2025) put turnover at about **£1.3bn a year (range £0.7–2.1bn)**. It found about **7.4m UK adult entrants** and **401 active operators**. Omaze reportedly accounts for **over 60% of participants**. All of these are CONFIRMED (snippet), from secondary write-ups.
- **Model 1 (paid entrant intelligence) is the weakest.** At least six free UK odds and comparison sites already exist. Raffle Edge's own data finds no entrant edge:
  - 3 of 200 sampled 7days competitions (1.5%) had positive expected value (EV) at cash value, each worth only pennies.
  - Draw positions show no departure from uniformity.
  - Selling "value" tips also attracts the harm and CAP problems below.
- **Model 2 (free comparison site) is crowded and low-margin.**
  - Affiliate programmes exist: Awin listings for 7days and Elite, and 15% commission at some smaller operators.
  - Code clause 3.2 binds affiliates to the Code.
  - Comparative "best value" claims fall under CAP/ASA scrutiny.
- **Model 3 (B2B draw-integrity audit) fits best and has the clearest regulatory pull.**
  - Clause 2.2 requires an independent person, a "verifiably random and auditable" computer process, or a certified machine.
  - About 195 operator signatories were reported by late July 2026. DCMS has reportedly begun compliance reviews.
  - Incumbents already serve this need: PromoVeritas (an Other Relevant Signatory), GLI (which certified Elite's RNG and ball machine), RANDOM.ORG, eGaming Integrity, Golden Egg Compliance and the Fair Draw Register.
- **Regulation is a swing factor.** The minister reportedly said the Code's success "will dictate whether this government decides to take further action (including legislation)". Statutory regulation would raise demand for independent audit (Model 3) and raise risk for Models 1 and 2. No primary statement was found.

## Market evidence

| Item | Figure | Label / source / date |
|---|---|---|
| Sector turnover | ~£1.3bn a year (CI £700m–£2.1bn); 12 months to Nov 2023 | CONFIRMED (snippet). [PromoVeritas summary](https://www.promoveritas.com/the-uks-1-3-billion-prize-draw-market-what-the-governments-new-study-means-for-operators/); [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13486910/). Report published 26 Jun 2025: [GOV.UK](https://www.gov.uk/government/publications/research-report-online-prize-draws-and-competitions-market-study-assessment-of-harm-and-review-of-potential-interventions) |
| Entrants | ~7.4m UK adults | CONFIRMED (snippet), same sources |
| Operators | 401 active (glass.ai web crawl); DCMS had assumed 40–50 | CONFIRMED (snippet). [glass.ai](https://brass-sailfish-pnag.squarespace.com/glass-news/glassai-uncovers-that-the-online-prize-draws-and-competitions-sector-is-far-bigger-than-expected) |
| Operators (2026) | "over 1,000"; ~20% signed the Code | UNVERIFIED. Rokker white paper via [Gaming Intelligence](https://www.gamingintelligence.com/insight/the-draw-of-the-raffle/) |
| Omaze share | over 60% of participants | CONFIRMED (snippet), secondary |
| Omaze UK revenue | £196.6m (2024), up from £127.4m; pre-tax profit £6.2m | CONFIRMED (snippet). [City AM](https://www.cityam.com/?p=2366264); not checked at Companies House (12056935) |
| Overlap with gambling | 88% of entrants also gamble on licensed products | CONFIRMED (snippet), PMC |
| Problem gambling | 67% of PGSI 8+ gamblers entered a prize draw in the past year | CONFIRMED (snippet). [GambleAware 2024](https://www.gambleaware.org/media/5mpnibc4/gambleaware_2024_treatment-and-support_report_v60.pdf) |
| Winvia FY25 (to 31 Dec 2025) | Group net revenue £170.3m. Prize draws segment £40.3m (from £28.8m), adjusted EBITDA £9.6m. 1.7m active prize-draw customers. BOTB Pass subscriptions >20% of BOTB monthly revenue by Mar 2026. Includes Click Competitions (acquired), so not like-for-like. | CONFIRMED (snippet). [HL/Sharecast](https://www.hl.co.uk/shares/stock-market-news/aim-and-small-cap-news/aim-bulletin/winvia-entertainment-repots-sharp-rise-in-annual-revenue,-earnings); [RNS 19 May 2026](https://www.lse.co.uk/rns/WVIA/final-results-5lmaj3lqugcbheh.html) |
| Jumbo acquires Dream Car Giveaways | EV A$109.9m (~£53.9m), ~6.5x adjusted EBITDA of £8.3m (12 months to Apr 2025); completed 14 Oct 2025 | CONFIRMED (snippet). [iGB](https://igamingbusiness.com/strategy/ma/jumbo-interactive-dcg-acquisition/); [ASX announcement](https://www.marketindex.com.au/asx/jin/announcements/acquisition-of-dream-car-giveaways-2A1629258) |
| Code signatories | ~195 operators plus 31 "other relevant signatories" (late Jul 2026); 55 operators removed on 19 Oct 2026 | CONFIRMED (snippet) [sigma](https://sigma.world/news/uk-prize-draw-code-demonstrable-compliance-may-2026/); CONFIRMED (project read) for the removals |
| Trade body | Prize Competition Council, launched Jul 2026, 50–65 members | CONFIRMED (snippet), secondary |

**Implication.** The buyer pool is roughly 200–1,000 operators, heavily skewed to a handful of large ones. **ESTIMATE.**

## Model 1: subscription intelligence for entrants

### Competitors (all fetched 2026-11-23; pricing not visible in snippets)

| Site | Offer | Price |
|---|---|---|
| [RaffleScout](https://rafflescout.co.uk/) | Odds from max tickets, plus live odds where sales are published | UNVERIFIED (appears free) |
| [Comp Tracker](https://compoddstracker.co.uk/) | Projects final sales from sales velocity | UNVERIFIED |
| [RaffleRadar](https://raffleradar.com/) | Multi-operator odds, price and sell-out progress | UNVERIFIED |
| [CarRaffleOdds](https://www.carraffleodds.com/) | Car raffles across 5 sites, "best value" view | UNVERIFIED |
| [RaffleCompare](https://rafflecompare.com/) | Live odds plus operator trust rating | UNVERIFIED |
| [Raffle Genius](https://rafflegenius.co.uk/) | Sort by odds, price, entries | UNVERIFIED |
| Loquax / ThePrizeFinder / Prizeology | Free-comping listings | Loquax says it is free (Trustpilot snippet); others not found |

### Customers and willingness to pay

**Who.** Heavy entrants. Willingness to pay is unknown.

- BOTB Pass shows entrants will subscribe to an operator. That is a subscription to entries, not to data. **CONFIRMED (snippet)**
- No paid entrant-intelligence product was found. **UNVERIFIED**

### Fit with what Raffle Edge has found (7days data)

| Analysis | Result |
|---|---|
| H1 ex-post EV | **3 of 200** competitions had positive EV at cash value (max +5.3p/ticket). 11 of 200 were positive at advertised value. |
| H3–H5 draw position | No departure from uniformity: KS p=0.12; BH-adjusted p all ≥0.47. |
| Instant wins | Ticket numbers are randomly allocated, so there is no position edge. |

Source: `raffle-edge/docs/generated/ANALYSIS_7DAYS.md` and the dashboard export. **CONFIRMED (project data).** The product would sell an "edge" the project's own data says does not exist.

### Legal risks (ranked)

1. **Harm and responsible-gambling expectations.**
   - Selling tips to increase entries targets a population with high problem-gambling overlap.
   - The Code expects 18+ only (1.1), spend limits (1.4) and harm monitoring (1.6–1.8). **CONFIRMED (project read)**
   - Reputational and political exposure is high.
2. **CAP Code and the CPRs on value claims.** "Best value" or "undersold" claims need substantiation (CAP rules 3.1 and 3.7). The ASA has acted on exaggerated odds, e.g. Clarson's "insane odds" ruling. **CONFIRMED (snippet)** [Osborne Clarke](https://marketinglaw.osborneclarke.com/advertising-regulation/chances-of-winning-free-entry-routes-and-charitable-giving-asa-pulls-ex-love-islander-for-a-chat/)
3. **Database right and website terms.**
   - Regulation 16(2) of the 1997 Regulations treats repeated, systematic extraction of insubstantial parts as extraction of a substantial part. **CONFIRMED (snippet)** [legislation.gov.uk](https://www.legislation.gov.uk/uksi/1997/3032/regulation/16)
   - Mitigation: BHB v William Hill (CJEU C‑203/02) found that investment in *creating* data does not count. That may weaken operators' claim over their own ticket counts. **ESTIMATE**; needs counsel.
   - BOTB and Click terms forbid scraping (project blocklist).
4. **UK GDPR.** Low risk if no winner data is collected.

### Cost drivers

- Continuous multi-operator collection (polite, so slow) and parser maintenance.
- Hosting (low).
- Legal review of claims.
- Paid acquisition in a niche dominated by free tools.

**ESTIMATE:** £20–60k/yr excluding founder time.

### Scores (1–5)

| Need | Defensibility | Legal risk (5 = low) | Fit |
|---|---|---|---|
| 2 | 1 | 2 | 1 |

## Model 2: free comparison and value site (ad- or affiliate-funded)

### Competitors

The same six odds sites as Model 1, plus "best raffle sites" affiliate blogs. None of these blogs were verified individually.

### Revenue signals

| Signal | Detail | Label |
|---|---|---|
| Awin programmes | 7days Performance (30-day cookie, rate not shown), Elite Competitions (30-day cookie, affiliates must be 18+), Premier Prize Competitions, Bullpen, and others | CONFIRMED (snippet). [Awin listing, merchant ID not mapped](https://ui.awin.com/merchant-profile/122354), [Elite terms](https://ui.awin.com/merchant-profile-terms/122560) |
| Commission rates | 15% at Jispwin and Prize Draw UK | CONFIRMED (snippet). [openPR](https://www.openpr.com/news/3661984/prize-draw-uk-launches-affiliate-scheme-utilising-trusted) |
| Large operators' rates | Not found | UNVERIFIED |

### Customers

- **Readers:** entrants seeking trust and transparency signals.
- **Payers:** operators, via affiliate commission.

### Fit

Moderate. The project's transparency rubric and platform ranking (`PLATFORM_RANKING.md`) is the differentiator: integrity first, not "best odds". Affiliate income, however, conflicts with independent ratings.

### Legal risks (ranked)

1. **Affiliate obligations and conflict of interest.**
   - Code 3.2 requires operators to ensure affiliates follow the Code. **CONFIRMED (project read)**
   - Operators also require CAP/BCAP-compliant, socially responsible ads (1.11).
   - Undisclosed commissions risk breaching the CPRs, now the DMCC Act 2024 unfair-practices regime. **ESTIMATE** (not re-verified this session).
2. **Comparative claims (CAP 3.33 onward) and the accuracy of live odds.** Sites compute odds differently: max capacity, live sales, or projected sales. **CONFIRMED (snippet)**
3. **Under-18s.** An open content site attracts minors. Age-gating of affiliate links would be expected. **ESTIMATE**
4. **Database right and terms.** As in Model 1, but lower if the site lists only headline data.
5. **Statutory regulation.** If prize draws are brought under the Gambling Commission, gambling affiliate rules would apply. **ESTIMATE**

### Cost drivers

- Content and SEO.
- Data collection.
- Legal review of the ratings methodology.
- Affiliate compliance monitoring.

**ESTIMATE:** £15–40k/yr. Revenue is unknown.

### Scores (1–5)

| Need | Defensibility | Legal risk (5 = low) | Fit |
|---|---|---|---|
| 3 | 2 | 3 | 3 |

## Model 3: B2B statistical research and draw-integrity audit for operators

### Regulatory hook (CONFIRMED, project read, Code updated 19 Oct 2026)

- **Clause 2.2:** draws "should be by an independent person, or under the supervision of an independent person, unless winners are selected by a computer process that produces verifiably random and auditable results, or by a certified physical drawing machine." Operators "should provide details of the mechanism used".
- **Clause 2.5:** no cancelling or downgrading draws for low sales.
- **Clause 3.1:** operators monitor their own compliance.
- **Clause 3.2:** third-party draw partners must comply.
- **DCMS review:** DCMS reportedly began asking signatories to evidence their position against each clause. **UNVERIFIED** (snippet: [Deadline News](https://www.deadlinenews.co.uk/2026/09/17/uk-prize-draw-rules-are-tightening-what-the-dcms-voluntary-code-means-for-operators-and-entrants/), [sigma](https://sigma.world/news/uk-prize-draw-code-demonstrable-compliance-may-2026/))

### Competitors

| Firm | Offer | Price |
|---|---|---|
| PromoVeritas | Independent draws, verification letters, video; used by BOTB; listed as an Other Relevant Signatory | Not published (CONFIRMED snippet: none found) |
| GLI | RNG and ball-machine certification; certified Elite Competitions' systems | Not published. [gambling.com](https://www.gambling.com/news/elite-competitions-puts-live-draw-machine-through-gli-testing) |
| RANDOM.ORG Third-Party Draw Service | Recorded, publicly checkable draws; prepaid credit priced by number of entries | Price calculator only. [random.org](https://random.org/draws/pricing) |
| eGaming Integrity | Voluntary Code advisory service | Not found. [iGB](https://igamingbusiness.com/company-news/egaming-integrity-launches-voluntary-code-advisory-service-for-prize-draw-operators/) |
| Golden Egg Compliance; The Fair Draw Register | Other Relevant Signatories | Not found; offer unverified |
| Law firms (Harris Hagan, Wiggin, Mishcon, CMS, Irwin Mitchell, and others) | Code and Gambling Act advice | Hourly rates; not found |

### Customers and willingness to pay

**Who.** Mid-sized operators: signatories without in-house compliance staff, and operators dropped from the list who want to rejoin.

**Willingness-to-pay signals (CONFIRMED, snippet):**

- Elite chose to pay GLI for certification.
- BOTB pays PromoVeritas.
- Elite hired a head of compliance from bet365.
- Operator EBITDA is material: DCG ~£8.3m, Winvia prize draws £9.6m.

**Price point:** unknown. **ESTIMATE:** £1–10k per audit, or a monthly monitoring retainer.

### What Raffle Edge can uniquely show

**Third-party reproduction of published draws.**

| Period | Result |
|---|---|
| May to early Aug 2026 | 302 of 302 7days automated draws reproduce from the published seed |
| From 5 Aug 2026 | None reproduce after the seed format changed |

That is exactly the "verifiable and auditable" test in clause 2.2. Uniformity tests (H3–H5) are also already built. **CONFIRMED (project data).**

### Legal risks (ranked)

1. **Independence conflict.** Being paid by the operator you audit, while also publishing on operators, conflicts. Ring-fence the research, or stop publishing. **ESTIMATE**
2. **Professional liability and negligent misstatement.** Attestation wording must be scoped to the tested systems only, as GLI's is. Professional indemnity insurance is needed. **ESTIMATE**
3. **Defamation and the disclosure process.** Publishing non-reproduction (e.g. 7days) before the operator replies carries risk. The project's 30-day draft-letter process mitigates this.
4. **UK GDPR.** Audits will touch entry lists, which are personal data. You need a controller-to-processor contract, minimisation and retention rules. **ESTIMATE**
5. **Accreditation gap.** "Certified physical drawing machine" implies a test lab such as GLI. A statistician is not a certifying body, so the offer should be framed as independent verification of computer processes. **ESTIMATE**
6. **Statutory regulation.** This is upside: an Act or Gambling Commission oversight would likely require accredited testing, which favours labs. **ESTIMATE**

### Cost drivers

- Sales: about 200 named targets, reached through the trade body and events.
- Professional indemnity and cyber insurance.
- Solicitor-drafted terms and attestation templates.
- Secure data handling.
- Possible ISO 17025-style quality processes.

**ESTIMATE:** £10–30k first year excluding salaries.

### Scores (1–5)

| Need | Defensibility | Legal risk (5 = low) | Fit |
|---|---|---|---|
| 3 | 3 | 4 | 5 |

Defensibility is limited because incumbents are established, but statistical depth and the method of published reproductions are differentiators.

## Cross-cutting legal notes

**Gambling Act 2005**
- s.14 and Sch 2 para 8: a free draw needs a genuine free route, "neither more expensive nor less convenient" (Code 2.4).
- s.339: skill must deter a "significant proportion" of people. Gambling Commission guidance says this, and very easy questions fail. **CONFIRMED (snippet)** [Gambling Commission](https://www.gamblingcommission.gov.uk/guidance/lotteries-and-the-gambling-act-2005/lotteries-and-the-ga05-when-is-a-lottery-not-a-lottery)
- None of the three models runs draws, so the Act bites only indirectly, through what Raffle Edge promotes.

**Future regulation**
- The London Economics study reportedly found that formal regulation could be most effective and recommended Gambling Commission oversight. **CONFIRMED (snippet)** [GamblingNews](https://www.gamblingnews.com/news/dcms-study-urges-ukgc-oversight-for-prize-draw-operators/)
- The government chose the voluntary Code (26 Jun 2025 written statement) and will review its effectiveness periodically. **CONFIRMED (snippet)** [iGB](https://igamingbusiness.com/legal-compliance/dcms-voluntary-code-prize-draws/)
- No legislative decision was found as of 2026-11-23.

## Key unknowns (only interviews can answer)

1. Will operators pay a non-lab third party for clause 2.2 verification? How much, and is it a one-off or recurring?
2. Has DCMS actually asked signatories for evidence, and what evidence satisfies it?
3. Does PromoVeritas's or GLI's scope cover computer-draw reproduction and statistical monitoring, or is there a gap?
4. Would an operator accept an auditor that also publishes independent research?
5. Do entrants pay for data at all, given the free tools? What do they distrust most: odds, fairness or prize value?
6. What affiliate rates do the major operators pay, and do they restrict comparison or ratings content?

## Suggested interview plan (about 6 weeks, 20–25 interviews)

**Ground rules**
- Approach people only through published business contact routes, with consent.
- No incentives tied to entries.

| Group | Number | Ask |
|---|---|---|
| Compliance or operations leads at mid-sized signatory operators, including some delisted on 19 Oct | 8–10 | How do you evidence clause 2.2 today? What does it cost? Who approved it? What did DCMS ask for? What would make an independent report credible? What is your budget? |
| Large operators (Omaze, BOTB/Winvia, DCG, Elite, 7days) | 3–4 | Same questions, plus procurement, and whether they would switch from a lab or PromoVeritas |
| Incumbent verifiers and labs (PromoVeritas, GLI, eGaming Integrity, Golden Egg) | 3 | Scope, demand trend since May 2026, partnership or subcontract potential |
| Prize Competition Council, the Fair Draw Register, and a gambling-law solicitor | 3 | Minimum standards in development; liability and attestation wording; outlook for regulation |
| Adult entrants via comping forums (screened 18+; exclude self-reported problem gamblers or signpost support) | 6–8 | Trust signals, whether integrity ratings change behaviour, willingness to pay; do not ask about increasing spend |

**Decision rule**
- Pursue Model 3 if at least 4 operators name a budget of £2k or more per year and a buying trigger. **ESTIMATE** threshold.
- Drop Model 1 unless at least 3 of 8 entrants would pay for something other than an "edge".
