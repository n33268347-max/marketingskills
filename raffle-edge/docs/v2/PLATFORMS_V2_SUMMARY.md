# Platforms v2: summary (2026-11-23)

Claims file: `claims_v2_platforms.json`. It holds 69 claims, and all 69 pass `raffle_edge.verify.check_claims` (quote found in the archived snapshot, no PII).

## Task 1: Aspire Competitions (aspirecomps.co.uk)

- **robots.txt**: `User-Agent: * / Allow: /`. It sets no Crawl-delay and has no AI-agent groups.
- **T&Cs check: NOT COMPLETED.**
  - The site is a Firebase-backed SPA, so `/` and `/terms-conditions` return only a "Something went wrong" shell to a non-JS fetcher.
  - The terms text loads at runtime from the backend database (Firestore). I did not query that backend.
  - I therefore found no anti-AI or anti-scraping clause, but I also could not confirm that none exists.
  - **Recommendation:** a human should read https://aspirecomps.co.uk/terms-conditions in a browser before any further automated collection, and before merging the Aspire bundle-sourced claims.
- **Fetches:** 4 pages (robots.txt, the homepage, the JS bundle and /terms-conditions). I fetched nothing further.
- **Evidence (all from the operator's own JS bundle, static UI copy):**
  - **Operator:** Aspire Competitions Ltd, Company No. 12067448, 12 Oxford Rd, Yeovil BA21 5HR. Companies House confirms this. The registered office is in **Yeovil, not Taunton**.
  - **Formats:** live draws (Facebook/YouTube), auto draws, instant wins.
  - **RNG:** the in-house "Aspire Competitions Random Number Generator", which the site says is "independently certified by GLI". No independent draw party is named, and I did not see the certificate.
  - **Ticket allocation:** random, "Daily by 10pm".
  - **Disclosure:** "Max tickets" and "max tickets per person" are shown. I found no tickets-sold text, though there is a hint in the alert "odds are better than 75% sold".
  - **Draw timing:** live draws have a "Guaranteed draw date regardless of ticket sales! No Extensions!". Auto draws run at the stated time "or as soon as tickets sell out".
  - **Postal entry:**
    - One entry per postcard; an account is required.
    - Low-price multiplier: 49p = 2 entries, 25p = 3, 10p = 9.
    - Postal entries are eligible for instant wins.
    - I found no deadline text and no general equal-odds statement.
  - **Results:** the winner card shows the prize, an initialised name, the county, the winning ticket number and a Facebook live link.
  - **Promotions:**
    - Aspire Points, redeemable for checkout discounts.
    - Referral points.
    - Badger Bonus Points.
    - "Early Badger" extra-ticket draws.
    - A free entry for commenting on the live draw.
    - Discount-period chances of extra free tickets.
- **Not found:** refund policy text, DCMS code signatory statement, unsold-number handling and a bundle price ladder. These are probably in the unread T&Cs or FAQ.

## Task 2: Companies House (all Active)

| Slug | Registered name | No. | Incorporated | Registered office |
|---|---|---|---|---|
| 7days-performance | 7DAYS PERFORMANCE LIMITED | 11215119 | 20 Feb 2018 | 167-169 Great Portland St, London W1W 5PF |
| elite-competitions | HYDRO SOLUTIONS FYLDE LTD | 09612888 | 28 May 2015 | Turing Court, Bispham, Blackpool FY2 0QW |
| dream-car-giveaways | DREAM CAR GIVEAWAYS LIMITED | 11320154 | 19 Apr 2018 | Droitwich WR9 9AY |
| click-competitions | CLICK COMPETITIONS LIMITED | 12550861 | 7 Apr 2020 | Norwich NR7 0HR |
| botb | WINVIA ENTERTAINMENT PLC | 03755182 | 20 Apr 1999 | London SW6 2AG (formerly Best of the Best PLC) |
| omaze-uk | OMAZE UK LIMITED | 12056935 | 18 Jun 2019 | Altrincham WA14 2DT (formerly Omaze Limited) |
| rev-comps | **2SAVI LTD** | 11981806 | 7 May 2019 | Cheltenham GL51 4UA. Named REV CORP LTD until 04 Jul 2026 |
| raffall | RAFFALL LIMITED | 09930826 | 29 Dec 2015 | 167-169 Great Portland St, London W1W 5PF (same building as 7days) |
| aspire-competitions | ASPIRE COMPETITIONS LTD | 12067448 | 25 Jun 2019 | Pen Mill Trading Estate, Yeovil BA21 5HR |
| lucky-day-competitions | **ACE COMPETITION LTD** (singular) | NI659574 | 7 Mar 2019 | Forkhill, Newry BT35 9RX |

## Task 3: Refunds and promotions (from archived snapshots, nothing refetched)

**Elite Competitions**
- No refunds except under clause 6.9.
- Elite Club subscription: cancel any time, no partial refunds.
- Volume `discountZones` (5–25% off at ticket thresholds) are enabled on 3 of 31 listed competitions.
- Wallet, promotional and bonus credit is entry-only and not cashable.
- Golden Ball is a paid add-on: the example raises the price from £0.20 to £0.24. It is free for postal entrants and non-refundable.
- Up to 2,500 postal entries are allowed into the Elite Club monthly draw.
- Postal entries go on an open postcard. I found no per-card multiplier.

**Dream Car Giveaways**
- No refunds in any event (subject to s.13.3).
- Dream points: 1 per £1 spent, 200 on your birthday, 50 per referral.
- 15% off after spending your first £5.
- Subscription entries are discounted.
- Each postal entry must be sent separately, and a bulk entry counts as one.
- Multiplier: 49p = 2, 29p = 3, 9p = 10.

**Lucky Day**
- No refunds for any competition, including after disqualification.
- Multiple postal entries are allowed, each posted separately; a bulk envelope counts as one.
- I found no loyalty, referral or bundle terms in the T&Cs or FAQ. The site loads WooCommerce discount-rules and account-funds plugins, which is infrastructure only.

**Omaze**
- No refund of a subscription fee after a drawing has occurred; refunded entries are withdrawn.
- "Bonus entries" promotions and reduced-fee multi-draw offers are allowed.
- Entry bundles start at £10.
- Spend limit: £500 a month (£250 on a credit card).
- One postal entry per postcard or envelope, with no limit on the number of postal entries, and equal odds to one paid entry.

## Task 4: "The Competition Guys"

- I found **no UK operator by that exact name** in two web searches. I am not substituting another brand.
- Closest named candidates (unverified):
  - "The Giveaway Guys": https://www.feefo.com/cy-GB/reviews/the-giveaway-guys and https://find-competitions-master-vlkspv.laravel.cloud/operators/the-giveaway-guys

## Contradictions and flags

1. Rev Corp Ltd 11981806 is now named **2SAVI LTD** (renamed 04 Jul 2026). The platform registry entry needs updating, and it is unverified whether RevComps still trades through this company.
2. Lucky Day's registered name is "ACE COMPETITION LTD", not "Ace Competitions Ltd". The site footer has the plural, while T&Cs clause 1 has the singular.
3. Aspire is based in Yeovil (Somerset), not Taunton.
4. Raffall and 7days share the registered office at 167-169 Great Portland St. This is likely a formation or agent address and is not evidence of a link between the companies.
5. Aspire's terms are unread, so the AI-clause check for Aspire is still open.
