# Raffle Edge: commercial evidence verification (v2)

_Accessed 2026-11-23. Not legal or financial advice. Verifies `docs/PHASE7_COMMERCIAL.md`._

## Access notes

- **gov.uk and Companies House** pages were fetched through the project fetcher (`raffle_edge.cli fetch --delay 10`), archived in `raffle-edge/data/raw/`, with text copies in `scratchpad/v2/commercial/snapshot-NNN.txt`. Two gov.uk `/search/all` URLs were **blocked by robots.txt** and not fetched.
- **assets.publishing.service.gov.uk** hosts the LE Annexes PDF (`/media/6852bceadf3015b374b7361b/Annexes.pdf`, 52 pp). It was **not fetched**, because that host is not allowed. The main report is HTML on www.gov.uk and was fetched in full.
- **WebFetch failed (DNS not resolvable) for every non-gov host tried**: lse.co.uk, marketindex.com.au, investorpa.com, proactiveinvestors.com, promoveritas.com, random.org. Those hosts need to be allowed in the session network settings. Everything outside gov.uk/Companies House therefore comes from **WebSearch result summaries (snippet-level)**. None of those pages was opened.
- No operator site was fetched. Nobody was contacted.

## Evidence classes

| Class | Meaning |
|---|---|
| **A** | Primary source read directly via the project fetcher, archived with SHA-256 |
| **B** | Reliable secondary or primary page opened directly (none achieved this session: WebFetch was blocked) |
| **C** | Search-result snippet or summary of a reliable source (RNS mirror, regulator, trade press); page not opened |
| **D** | Snippet of vendor or self-promotional content (broker or provider marketing pages, blogs) |
| **E** | Unknown or could not be verified |

## Source register

| # | Source | URL | Accessed | Exact quote (abridged with …) | Finding | Class | Snapshot sha256 |
|---|---|---|---|---|---|---|---|
| S1 | DCMS publication page, LE research report | https://www.gov.uk/government/publications/research-report-online-prize-draws-and-competitions-market-study-assessment-of-harm-and-review-of-potential-interventions | 2026-11-23 | "London Economics' research into the market for prize draws and competitions in the UK … Published: 26 June 2025" | The report is by London Economics, published by DCMS on 26 Jun 2025. Annexes are a PDF on assets.publishing (not fetched). | A | d456df73cf9ed18dfaa5c858eca79f1969bdc1edaa0a8af27a005561d1dff973 |
| S2 | LE report (HTML), executive summary | https://www.gov.uk/government/publications/research-report-online-prize-draws-and-competitions-market-study-assessment-of-harm-and-review-of-potential-interventions/online-prize-draws-and-competitions-market-study-assessment-of-harm-and-review-of-potential-interventions | 2026-11-23 | "around 7.4 million adults (14% of the adult population) have participated in PDCs in the last year (as of November 2023), spending an estimated total of £1.3 billion (£700 million to £2.1 billion)" | Sector size and entrants confirmed | A | 49a108b2099b888a78307136f44fb34a0520eb9856021ed3e7b565dc7736a081 |
| S2a | LE report §2.1.1 | same | 2026-11-23 | "with a 95% confidence interval of 6.6 to 8.2 million" … "split across at least 401 operators. However, it is likely that there are further operators that have not been detected" | Entrants CI 6.6–8.2m. Operator count is a lower bound from a web crawl. | A | same |
| S2b | LE report, exec summary + Table 2 | same | 2026-11-23 | "one operator (Omaze) is estimated to account for more than 60% of the player base … several other relatively large operators, these each account for at most a 5% share"; Table 2: "Omaze UK 61.4%", "Best of the Best 4.7%", "Elite Competitions 4.3%", "Raffle House 4.2%" | Omaze share is 61.4% of survey respondents who had played with any of 11 large operators. It is a share of players, not of revenue. | A | same |
| S2c | LE report, Table 25 | same | 2026-11-23 | "Gambling with negative consequences and a possible loss of control (i.e., harmful gambling) (8+) 12% [PDC players] 5% [all gamblers] 3% [general population]" | **12% of PDC players score PGSI 8+**, against 5% of all gamblers and 3% of the general population. | A | same |
| S2d | LE report, harm section | same | 2026-11-23 | "individuals experiencing gambling harm spend on average far more (£712 per year) on PDCs than non-gamblers (£59 per year)"; "typical player … spends on average around £175 per year"; "40% of individuals experiencing a high level of gambling harm (8+ on PGSI) strongly agreed [instant win is a big reason]" | Spend and harm detail | A | same |
| S2e | LE report, free entry | same | 2026-11-23 | "PDCs often (88% of operators) offer a free entry option … on average only 6% of total entries they receive are free" | **88% refers to operators offering free entry, not entrants who gamble.** PHASE7's "88% of entrants also gamble" is a misattribution. | A | same |
| S2f | LE report, Table 16 | same | 2026-11-23 | "Tickets for the National Lottery Draw … 59% [PDC players, last 12 months] 44% [general population]" | Gambling overlap: 59% of PDC players played the National Lottery in the past year. | A | same |
| S2g | LE report, conclusions | same | 2026-11-23 | "Changes to gambling regulation represent the most direct and comprehensive means … A voluntary code of conduct could serve as a temporary or experimental step while further consideration is made of the case for regulatory intervention." | LE did not make a firm recommendation. It called regulation "most direct and comprehensive" and framed the code as an interim step. | A | same |
| S3 | Code publication page | https://www.gov.uk/government/publications/voluntary-code-of-good-practice-for-prize-draw-operators | 2026-11-23 | "Published: 20 November 2025 Last updated: 19 October 2026" … "The success of this Code will determine whether the Government decides to take further action, including legislation." | The legislation threat is confirmed on gov.uk. The change log records 55 removals on 19 Oct 2026, and Golden Egg Compliance and The Fair Draw Register added as ORS on 1 Sep 2026. | A | 78265f50ae64e5ac5cea4b3d19c1761310aced224b2a9c6bc45548fb5f0b77b3 |
| S4 | Code (HTML), review + signatories | https://www.gov.uk/government/publications/voluntary-code-of-good-practice-for-prize-draw-operators/voluntary-code-of-good-practice-for-prize-draw-operators | 2026-11-23 | "DCMS (or such industry trade body if delegated) will periodically review the effectiveness of the Code and its implementation/compliance … should the Code not be suitably implemented or complied with, DCMS will consider all available options."; "no later than 20 May 2026 (the "implementation date")" | Monitoring is by periodic review. The page publishes no review results. Counted from the snapshot: **138 Operator Signatories and 30 Other Relevant Signatories**. | A | 7125a1d4782db0daeed6397cb36aaf7b6a74c540b91c3b297f359d8f05a9f3e6 |
| S5 | DCMS press release | https://www.gov.uk/government/news/big-win-for-players-as-government-launches-voluntary-code-for-prize-draw-operators | 2026-11-23 | "Published: 20 November 2025" … "Omaze among more than 20 leading operators to sign up" … "7.4 million adults playing each year … worth £1.3 billion annually" … "A £250 monthly cap on credit card entries" | The Code launched 20 Nov 2025 with more than 20 operators. The release contains no "dictate … legislation" quote. | A | f5ae98fe5eb78941946ef1495354c28546576c9a38bed8fa97c08f70a0580b29 |
| S6 | Companies House: Omaze UK Ltd overview | https://find-and-update.company-information.service.gov.uk/company/12056935 | 2026-11-23 | "Incorporated on 18 June 2019 … Last accounts made up to 31 December 2025 … 82990 - Other business support service activities" | The company is active. Its FY2025 accounts are filed. | A | 2d7d77f47562f7248c1b87917d801ee4e1b2180213710c8cc6e84d9654207f4b |
| S7 | Companies House: Omaze UK filing history | https://find-and-update.company-information.service.gov.uk/company/12056935/filing-history | 2026-11-23 | "08 May 2026 AA Full accounts made up to 31 December 2025 … (33 pages)"; "30 Sep 2025 AA Full accounts made up to 31 December 2024 … (28 pages)"; "16 Dec 2025 MR01 Registration of charge 120569350001" | Full accounts for FY24 and FY25 exist but are PDFs (not read). **Revenue is not visible on the listing.** | A | e676c706ea433024f214f03fbe24a18840175185dec37ee93c3591f5c16a2877 |
| S8 | City AM (via PHASE7) | https://www.cityam.com/?p=2366264 | not opened | (snippet in PHASE7) £196.6m revenue 2024, up from £127.4m; PBT £6.2m | Omaze UK FY24 revenue. Not checked against the filing. FY25 figure unknown. | C | — |
| S9 | Winvia final results FY25 (RNS 19 May 2026), via search summary of LSE/Proactive/AJ Bell/HL mirrors | https://www.lse.co.uk/rns/WVIA/final-results-5lmaj3lqugcbheh.html (fetch failed) | 2026-11-23 | "Segment revenue was £40.3 million, up from £28.8 million, while adjusted EBITDA more than doubled to £9.6 million from £4.0 million"; group net revenue £170.3m (FY24 £38.1m), adj. EBITDA £31.2m; prize-draw active customers 1.7m (from 0.9m, +94%); subscriptions "9% of BOTB monthly revenue by the end of December … more than 20% by 31 March 2026" | PHASE7 figures are consistent with the snippets. Caveat: the Jan 2026 trading update reportedly said prize-draw actives rose 47%, so the basis may differ. | C | — |
| S10 | Companies House: Winvia search | https://find-and-update.company-information.service.gov.uk/search/companies?q=winvia+entertainment | 2026-11-23 | "WINVIA ENTERTAINMENT PLC 03755182 - Incorporated on 20 April 1999"; "BEST OF THE BEST LIMITED … Matching previous names: WINVIA ENTERTAINMENT LIMITED 13335459" | Entity identifiers only | A | a5bac65bc126001299d9cf89763daa3ff4629463a7656f20caf156e20437c19c |
| S11 | Jumbo Interactive ASX release "Acquisition of Dream Car Giveaways", 15 Oct 2025, via search summary (InvestorPA mirror, iGB, Motley Fool) | https://www.marketindex.com.au/asx/jin/announcements/acquisition-of-dream-car-giveaways-2A1629258 (fetch failed) | 2026-11-23 | "enterprise value of A$109.9 million (£53.9 million)"; "adjusted EBITDA of GBP8.3 million for the 12 months ended 30 April 2025 … approximately 6.5x"; upfront cash A$75.2m, equity A$10.2m, earnout up to A$24.5m (£12.0m) post-Dec 2026; total up to A$134.2m (£65.8m) | EV and multiple consistent with PHASE7. New detail: the earnout raises the potential total to £65.8m. | C | — |
| S12 | Companies House: Dream Car Giveaways Ltd filing history | https://find-and-update.company-information.service.gov.uk/company/11320154/filing-history | 2026-11-23 | "21 Oct 2025 TM01 Termination of appointment of Michael Andrews as a director on 14 October 2025"; "AP01 … Jatin Khosla as a director on 14 October 2025"; "30 Jan 2026 AA Full accounts made up to 30 April 2025"; "AA01 Current accounting period extended from 30 April 2026 to 30 June 2026" | The board changed on 14 Oct 2025, which corroborates completion on 14 Oct 2025. The year-end moved to 30 June (Jumbo's year-end, inferred). | A (board change); C (completion) | 254e70e9f58ff7dc1620b2dd48ba9a248220a4e3ad462cceb303cb07ec69bb5a |
| S13 | Companies House: DCG PSC | https://find-and-update.company-information.service.gov.uk/company/11320154/persons-with-significant-control | 2026-11-23 | "Mdm Holdings (Midlands) Ltd Active … Ownership of shares – 75% or more" | The PSC is still the holding company, so the purchase was presumably made at holding level (inferred) | A | f44cf6cb1a9c3e79c6db6107455f12ea317d3774d292b3681046e390bcbaf9d2 |
| S14 | GambleAware Annual GB Treatment & Support Survey 2024 (search summary) | https://www.gambleaware.org/media/5mpnibc4/gambleaware_2024_treatment-and-support_report_v60.pdf | not opened | "one in three (33%) had participated in a prize draw in the past year, which rose to two in three (67%) among those experiencing 'problem gambling'"; "(11%) … 'problem gambling' (PGSI 8+)" from prize draws | The 67% is **GambleAware, not LE**, and its base is people who gamble. | C | — |
| S15 | Gaming Minister quote "dictate … legislation" (iGB/Twycross, via search) | https://igamingbusiness.com/legal-compliance/dcms-voluntary-code-prize-draws/ | not opened | "the success of this code will dictate whether this government decides to take further action (including legislation)" | The wording is close to S3 (class A), which is the citable version. | C | — |
| S16 | Parliamentary answer, Ian Murray, 21 Apr 2026 (search summary, parallelparliament) | https://parallelparliament.co.uk/question/103003/prize-money-codes-of-practice | not opened | focus on "20 May 2026 deadline for signatories to comply" | No legislation announced | C | — |
| S17 | DCMS "compliance reviews" / evidence requests (Deadline News, sigma) | see PHASE7 | not opened | — | Not on any gov.uk page fetched | E | — |
| S18 | Companies House fees | https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees | 2026-11-23 | "Incorporation £100 £100 £124 … Confirmation statement fee … £50 £50 £110"; "Updated 25 September 2026" | Company costs | A | 8e3bb89e258ce10a106b4c1858526a7e1f4d1048c9712dc2e546b7daa8d9bd5e |
| S19 | gov.uk register your company | https://www.gov.uk/limited-company-formation/register-your-company | 2026-11-23 | "It costs £100 and can be paid by debit or credit card" | Same | A | 88a0edf4a9c74e470cc797147d941382f67bc0369058106202a15c5065d1aa6a |
| S20 | RANDOM.ORG Third-Party Draw Service (search summary) | https://random.org/draws/pricing | not opened | "the price depends only on the number of entries"; prepaid credit is debited when the drawing runs; "per-entrant cost decreases as your drawings grow" | The pricing model is confirmed. **No price figure was obtained** (calculator only). | D / E (price) | — |
| S21 | PromoVeritas (search summary of alliance directory pages) | https://allindependentagencies.org/directory/alliance-recommends/promoveritas-2/ | not opened | "independent promotional and broadcast verification specialists"; draw "up to 300 winners … single draw or a package of 10"; "charged … based on the services required from the brief" | Services confirmed; **no public price** | D | — |
| S22 | eGaming Integrity (iGB, search summary) | https://igamingbusiness.com/company-news/egaming-integrity-launches-voluntary-code-advisory-service-for-prize-draw-operators/ | not opened | "Voluntary Code Advisory Service … assess current practices and prepare clear, practical evidence of compliance"; led by "audit and risk specialists" | Direct competitor for Code-compliance evidence. No price found. eGaming Integrity is **not** on the signatory list. | C | — |
| S23 | GLI / Elite Competitions (gambling.com, search summary) | https://www.gambling.com/news/elite-competitions-puts-live-draw-machine-through-gli-testing | not opened | GLI "independently tested and certified both its random number generator and its mechanical ball machine" | Lab certification is used by a prize-draw operator. No price found. | C | — |
| S24 | CompWatch (Trustpilot snippet) + Code ORS list | https://uk.trustpilot.com/review/compwatch.co.uk | not opened | "free competition aggregator … across hundreds of websites"; trust ratings incl. "whether they follow the voluntary code"; "predicted odds" | Free consumer comparison tool that is also a Code ORS (S4). Not in PHASE7. | C (offer) / A (ORS listing) | — |
| S25 | Search results for RaffleRadar, CarRaffleOdds, RaffleCompare, Raffle Genius, Comp Tracker | (WebSearch, 5 queries) | 2026-11-23 | No result mentions these names | Existence unverified | E | — |
| S26 | PI insurance indicative premiums (Simply Business, getindemnity, NimbleFins, Hiscox) | https://www.simplybusiness.co.uk/business-insurance/consultants-insurance/ ; https://getindemnity.co.uk/professional-indemnity/cost ; https://www.hiscox.co.uk/node/6956 | not opened | Hiscox: "there is no average"; getindemnity: "£1m … low risk management consultant … around £250 a year"; NimbleFins: entry "about £130 a year"; Simply Business: 10% of consultants paid "£78.40 or less annually" | Indicative range only | D | — |
| S27 | Accountancy fees (Sleek, Accotax, accountancycloud, Unbiased) | https://sleek.com/uk/resources/limited-company-accountant-cost/ ; https://accotax.co.uk/limited-company-accountant-fees/ | not opened | "£150 to £500 for limited company accounts and a Corporation Tax return"; "£600–£1,800 for year-end accounts plus the CT600"; "£60 to £450 per month" packages | Indicative range | D | — |
| S28 | Solicitor fees (Sprintlaw, SRA price transparency) | https://sprintlaw.co.uk/articles/contract-review-cost-uk/ ; https://www.sra.org.uk/solicitors/guidance/ethics-guidance/price-transparency | not opened | consumer T&Cs "£550 to £750" | One price-guide data point. No B2B attestation pricing. | D | — |
| S29 | Hosting (DigitalOcean docs, Render article, Hetzner blogs) | https://docs.digitalocean.com/products/databases/postgresql/details/pricing/ ; https://render.com/articles/managed-postgresql-pricing-2026 | not opened | DO managed PG "$15/month" (1 GiB/10 GB); Render "~$6/mo (Basic-256mb)"; Hetzner cloud "from ~$4/mo" (self-managed) | Indicative | C (DO docs) / D | — |

## Corrected market facts

| Item | PHASE7 said | Verified / corrected | Class |
|---|---|---|---|
| Sector spend | ~£1.3bn (CI £0.7–2.1bn), 12m to Nov 2023 | **Confirmed.** £1.3bn a year, range £700m–£2.1bn, "as of November 2023" (S2) | A |
| Entrants | ~7.4m | **Confirmed.** 7.4m adults (14%), 95% CI 6.6–8.2m (S2, S2a) | A |
| Operators | 401 active | **Corrected wording:** "at least 401", from a web crawl, with more likely undetected (S2a). The "DCMS assumed 40–50" claim was not verified. | A / E |
| Omaze share | over 60% of participants | **Confirmed, with nuance:** "more than 60% of the player base". The figure is 61.4% of respondents among 11 large operators, which is a participation share, not a revenue share (S2b) | A |
| Gambling overlap "88% of entrants also gamble" | CONFIRMED (snippet) | **Wrong.** In LE, 88% is the share of operators offering free entry (S2e). LE says players "usually also engage in other gambling activities" and gives 59% for the National Lottery in the past year (S2f). Remove the 88% claim unless the PMC source is checked. | A |
| Problem gambling | 67% of PGSI 8+ gamblers entered a prize draw | **Source is GambleAware 2024**, not LE. The base is people who gamble (S14, C). The LE primary figure is **12% of PDC players at PGSI 8+**, against 5% of gamblers and 3% of the population (S2c, A). | A / C |
| LE recommendation | "recommended Gambling Commission oversight" | **Softer than stated.** LE calls regulation "the most direct and comprehensive means", not a recommendation, and frames a voluntary code as "a temporary or experimental step" (S2g) | A |
| Code launch date | Implied 26 Jun 2025 written statement | **The Code was published 20 Nov 2025** (S3, S5). 26 Jun 2025 is the LE report date. The June 2025 written statement was not verified (E). | A |
| Signatories | ~195 operators + 31 ORS (late Jul 2026) | **Today: 138 Operator + 30 ORS** (count of the S4 snapshot; the page was last updated 19 Oct 2026, after 55 removals). Launch: "more than 20" (S5). | A |
| Legislation | "No primary statement was found" | **Primary found:** "The success of this Code will determine whether the Government decides to take further action, including legislation." (S3) No bill or decision found. | A |
| DCMS monitoring | "reportedly begun compliance reviews" | The Code says DCMS "will periodically review", and "will consider all available options" if the Code is not complied with (S4). **Evidence requests to signatories remain unverified.** | A / E |
| Omaze UK revenue | £196.6m (2024) | Not visible on Companies House. FY24 full accounts (28 pp, filed 30 Sep 2025) and **FY25 full accounts (33 pp, filed 8 May 2026)** exist. The City AM figure stays C. **The FY25 figure is unknown.** | A (filings exist) / C (figure) |
| Winvia FY25 | Prize draws £40.3m rev, £9.6m adj. EBITDA, 1.7m customers | Consistent with RNS summaries (S9). Group £170.3m net revenue, £31.2m adj. EBITDA. | C |
| Jumbo / DCG | EV A$109.9m (£53.9m), ~6.5x £8.3m EBITDA, completed 14 Oct 2025 | EV and multiple consistent (S11, C). Completion is corroborated by DCG board changes on 14 Oct 2025 (S12, A). **Add:** earnout up to £12.0m, potential total £65.8m. | C / A |

## Incumbents and prices

| Firm | Services | Serves prize-draw operators? | Public price | Class |
|---|---|---|---|---|
| PromoVeritas | Independent winner selection, verification, judging, T&Cs, prize fulfilment | Yes. Listed as a Code ORS (S4). | **None.** Quote "based on the brief". Alliance offer is a single draw or 10-pack, amount not shown. | A (ORS) / D |
| RANDOM.ORG Third-Party Draw Service | Recorded, publicly checkable draws. Prepaid credit. Price depends only on the number of entries; per-entrant cost falls with scale. | General purpose; not on the Code list | **Calculator only; no figure obtained** (fetch blocked) | D / E |
| The Fair Draw Register | Unknown | ORS added 1 Sep 2026 (S3) | Unknown | A (exists) / E |
| Golden Egg Compliance | Unknown (name implies compliance services) | ORS added 1 Sep 2026 (S3) | Unknown | A (exists) / E |
| eGaming Integrity | Voluntary Code Advisory Service: gap assessment and "evidence of compliance", led by internal-audit specialists | Yes (launch PR). Not an ORS. | None found | C |
| GLI | RNG and ball-machine testing and certification (certified Elite) | Yes (Elite) | None found | C |
| **Not in PHASE7, also ORS (S4):** UVS (Uncloned Verification Standard), Online Competition Standards Authority (OCSA), UK CPSA, OneID, CompWatch, RaffleScout, PrizeStack.io, CompEngine | Names suggest verification or standards bodies and platform vendors. Offers not checked. | ORS | Unknown | A (exists) / E |

**Implication.** The "verification or standards" space now has several self-styled standards bodies (UVS, OCSA, UK CPSA, Fair Draw Register) on the signatory list. Model 3 must differentiate from them, not just from PromoVeritas and GLI. **ESTIMATE.**

## Existing consumer tools

| Site | Exists? | Offer | Charges? | Class |
|---|---|---|---|---|
| RaffleScout | **Yes.** Code ORS since 28 Apr 2026 (S3, S4). | Odds (per PHASE7; not re-verified) | Unknown | A (exists) / E |
| Comp Tracker (compoddstracker.co.uk) | Not found in search | — | — | E |
| RaffleRadar | Not found in search | — | — | E |
| CarRaffleOdds | Not found in search | — | — | E |
| RaffleCompare | Not found in search | — | — | E |
| Raffle Genius | Not found in search | — | — | E |
| **CompWatch** (new) | Yes. Code ORS since 10 Aug 2026 (S3). | Free aggregator of "hundreds of websites"; trust ratings incl. Code adherence; predicted odds | Described as free | A (exists) / C |
| Fair Shout, Find Competitions, Car Competition Hub (new) | Appear in search | Odds ranking and calculators; Car Competition Hub has affiliate links | Unknown | D |

PHASE7 says these sites were "fetched 2026-11-23". This session could not confirm that for five of the six. Treat them as **unverified** until opened.

## Cost inputs

| Item | Range / figure | Assumption | Source | Class |
|---|---|---|---|---|
| Company incorporation | **£100** online (£124 paper) | One-off | S18, S19 | A |
| Confirmation statement | **£50**/yr online | Annual | S18 | A |
| Accountant (accounts + CT600) | **£150–£1,800/yr** fixed fee; packages £60–£450/month | Micro company, no VAT or payroll at the low end | S27 | D |
| PI insurance, £1m cover | **~£130–£500/yr** indicative for low-risk consultancy. Statistical attestation for gambling-adjacent clients may price higher and needs a broker quote. | No claims; turnover under £100k | S26 | D (price for this risk class: E) |
| Cyber / data liability | Unknown | Needed if handling entry lists | — | E |
| Solicitor: consumer T&Cs | **£550–£750** (one price-guide data point) | Model 1/2 site terms | S28 | D |
| Solicitor: B2B audit engagement letter, attestation wording, DPA | Unknown. Needs quotes from gambling or commercial firms. | Model 3 | — | E |
| Hosting: managed Postgres | **$6–$15/month** entry (Render, DigitalOcean); $30–$50 for 2–4 GB | Small Python + Postgres service | S29 | C / D |
| Hosting: self-managed VPS | **from ~$4/month** (Hetzner) | Ops time not costed | S29 | D |
| ICO data protection fee | Required if processing personal data. Amount not verified this session. | — | — | E |

**Indicative first-year fixed costs**, excluding salaries, legal drafting and sales: roughly **£0.6k–£3k**. That is the sum of the A/D rows above, and it is a **calculation from estimates (D)**. PHASE7's £10–30k Model 3 estimate is therefore driven mainly by legal drafting, insurance for the actual risk class, and sales. None of those has a verified figure.

## What still needs customer interviews (or quotes)

1. Prices actually paid to PromoVeritas, GLI, RANDOM.ORG, eGaming Integrity and Golden Egg for draw verification or Code evidence, and whether the arrangement is one-off or recurring.
2. What the Fair Draw Register, UVS, OCSA and UK CPSA offer, what they charge, and whether operators value them.
3. Whether DCMS has asked signatories for evidence, in what form, and whether any of the 55 operators removed on 19 Oct 2026 were removed for non-compliance (the page gives no reason).
4. Broker quotes for PI and cyber cover for statistical attestation to prize-draw operators.
5. Solicitor quotes for an audit engagement letter, attestation template and DPA.
6. Whether entrants pay for any data, given free tools (CompWatch, RaffleScout); and affiliate rates at large operators.
7. Omaze UK FY25 and DCG FY25 revenue: read the filed accounts PDFs, or allow document-api access.
8. Hosts to allow for a primary-source re-run: lse.co.uk or investegate.co.uk (Winvia RNS), asx.com.au or marketindex.com.au (Jumbo), random.org (pricing calculator), promoveritas.com, assets.publishing.service.gov.uk (LE Annexes).
