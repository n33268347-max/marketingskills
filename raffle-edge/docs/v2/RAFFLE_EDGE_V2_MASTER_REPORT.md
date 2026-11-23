# RAFFLE EDGE V2: master report

_23 November 2026. Evidence classes: A primary source read directly; B reliable secondary; C statistical inference; D hypothesis; E unknown. Every number below is in `EXPERIMENT_LOG.md` (experiment IDs X1–X18) and the edge register._

## Decision

**Recommendation A: a genuine mathematical opportunity exists and deserves controlled testing. It is small, slow and high-variance, and only for personal use.**

- **The opportunity:** the **free postal entry route on competitions whose ticket price is well above the cost of a stamp** (edge E05).
  - It is positive expected value: about £2.98 of expected prize value per £1 spent on postage (out-of-sample 95% CI 1.71–5.38).
  - The qualifying competitions can be identified **before** entering, from published information only.
  - It is a route the law requires operators to offer.
- **What it is not:** a way to make money with £50–£100.
  - Each card has about a 0.16% chance of winning, so a £100 budget most likely wins nothing (P(any win) ≈ 9–12%).
  - About 442 cards (about £470 and 22 hours of handwriting) give a 50% chance of a single win.
  - It cannot lawfully be sold as a winning system (DMCC Act 2024 Sch 20 para 18).

**The paid-ticket route has no reliable advantage.** The verification business is the most credible commercial direction, but **its demand is unproven**. No operator has been asked, and asking needs your approval.

## The eight questions

**1. Is there any genuine mathematical advantage available to a UK entrant?**
Yes, one, and it isn't in paid tickets.
- **7days postal entry:**
  - A postcard earns ceil(91p ÷ price) tickets, at least 1, with equal odds (7days T&Cs 3.5.7, class A).
  - For tickets priced at £2.49–£19.99, one 91p stamp buys one full ticket.
  - Applying the advance rule (worst-case expected value per card > 106p): 8.4% of competitions qualify (credible interval 5.0–12.6%).
  - Out of sample, every selected competition beat its cost (E05: SUPPORTED, not VALIDATED).
- **Paid tickets:** 0 of 200 are positive value using pre-purchase information (E03). Even with perfect hindsight, the best possible profit on the whole sample was £4.89 on £100 (E04).

**2. Which competition mechanics produce the biggest differences in expected value?**
In order:
1. **Entry route.** A postal ticket on an expensive competition costs 91p instead of the full price.
2. **Fill rate.** Expected value per ticket scales with 1/sold. Draws close at a median 80% full.
3. **Prize type.** Cash prizes return about 27% more per £ than goods (CI 23–31%), because goods are valued at the operator's advertised price.
4. **Cap size and price:** small negative effects.

The designed payout if a draw sells out is only **41–50p per £1** (7days) and **about 40p per £1** (Rev Comps, from titles). Bundles (7days) and ticket numbers (E06) make no difference.

**3. Can an entrant identify a potentially favourable competition before buying?**
- **For postal entry: yes, with certainty about the floor.** Prize value, maximum tickets and tickets per postcard are published before entry, and the worst case assumes the draw fills.
- **For paid tickets: not at 7days** (0 of 200 have a positive floor).
- **At Rev Comps:** % sold is shown before close. Three live draws were below break-even fill on the morning of 23 Nov. Whether they stay there is being forward-tested (E09: INVESTIGATING, results on 24 Nov). Last week's six live draws all closed above break-even (47–75% against about 40%).

**4. Are there platforms where public information creates a measurable advantage?**
- **7days:** max tickets, sold counts, postal tickets per card and per-person limits are all published. That makes E05 computable in advance.
- **Rev Comps:** shows pre-close % sold and cash alternatives. Postal entry is 1 per card with equal chance, so the E05 logic extends to its expensive tickets (up to £27.27), but it hasn't been computed yet (E10).
- **Elsewhere:** Dream Car Giveaways shows remaining instant-win numbers (E13: untested).
- **Paid-ticket advantage:** not found anywhere.

**5. Can we independently verify more operators' draws?**
- **Today, only partly, and only at 7days.**
  - 302 automated draws are reproducible.
  - 464 since 5 August are not independently reproducible.
  - 884 (live draws and instant wins) have insufficient information.
  - 0 are inconsistent.
- **Every other operator** uses a physical ball machine or an unpublished RNG seed. Their draws can't be verified from public data.
- **A reference protocol now exists** (commit-reveal with a numbers-only entry list) that would make any operator's draws publicly verifiable without exposing systems or personal data.

**6. Would competition companies pay for independent verification?**
**Unknown (E).**
- The regulatory pull is real (Code clause 2.2, CAP 8.25, the threat of legislation).
- Four verification firms are already signatories.
- Nobody has been asked. Interviews need your approval.

**7. What would it cost to build a commercial service?**
- Evidenced non-salary fixed costs: **£1.1k–£6.7k a year** (company, accountant, hosting, basic insurance, basic legal).
- **Unknown, and probably the largest costs:** professional indemnity insurance for attestation work, specialist legal terms, and sales time.
- Break-even on non-salary costs at £1,000 per operator per year: about 1–8 operators. One £35k salary at £2,000 per operator: about 22 operators (16% of signatories).

**8. What should we investigate next?**
See `NEXT_ACTIONS.md`. In short:
1. A tiny, approved postal **mechanics** test.
2. The Rev Comps forward-test result.
3. E10 (postal value on Rev Comps and others).
4. Operator interviews.
5. A specialist solicitor on DMCC Sch 20 para 18, s.252 and attestation liability.

## Baseline integrity

Every V1 headline was re-derived from frozen data with independent code (X2): 302 of 302, 1 of 464, 3 of 200, the fairness tests, and 1,650 results. One clarification: V1's "55p per £1" was the **median** (54.5p). The mean is 57.3p, and weighted by revenue it is 58.6p.

## What changed from V1

- **New positive finding:** the postal entry edge (E05).
- **Independent draw verification**, now a working prototype: the five-status classifier, the prototype audit report and the verifiable-draw protocol.
- **Legal facts that reshape the business options:**
  - DMCC Act Sch 20 para 18 effectively rules out Business 3.
  - Gambling Act s.252 exposes Business 2.
- **Corrected market facts:** 138 signatories (not about 195); the "88%" statistic was misread; London Economics calls the voluntary code a "temporary or experimental step".

## Limitations

- **Value analysis covers one operator in depth:** 200 sampled 7days competitions, May–Nov 2026.
- **Cash alternatives are the operator's own figures.** Goods have no independent valuation.
- **E05 assumptions:**
  - Postal entries are processed as the terms say. This is untested, and testing it is the purpose of the controlled test.
  - The per-person limit applies to postal and paid entries combined.
  - A postcard costs 15p (assumption).
- **Rev Comps** data is limited to server-rendered pages. The full history is behind a third-party API, which was not used.
- **Aspire** terms are unread, so automated access is paused.
- **This is research, not legal advice.**
