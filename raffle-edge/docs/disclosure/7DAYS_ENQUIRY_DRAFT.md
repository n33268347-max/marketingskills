# DRAFT: enquiry to 7days Performance about automated-draw verification

_Status: **draft, not sent**. Review the wording and the numbers before sending. Send from a named contact, through 7days' published contact route, to their compliance or support team._

---

**Subject:** Question about verifying automated draws since August 2026

Hello,

I'm carrying out non-commercial statistical research into how UK prize-draw operators document their draws. Your "Draws Explained" page stands out: it explains that automated draws use `mt_srand(seed)` and `mt_rand(1, N)`, with the seed derived from the current time. It also invites the public to check results using onlinephp.io. The draw-results feed publishes the seed, the winning index and the entry count for each automated draw.

Using that published method:

- Every automated draw we checked from May to 3 August 2026 (**302 of 302**) reproduces exactly from the published seed. This is a strong transparency result, and we intend to report it as one.
- **5 August – 20 October 2026:** the published `rng_seed` values became integers of varying length, some of them single digits. With the published method, none of these 315 draws reproduce, whether we use the timestamp or the published value as the seed.
- **From 21 October 2026:** `rng_seed` is a 64-character hexadecimal string. None of these 149 draws reproduce with the published method.

We also tried PHP 8.2's `Xoshiro256StarStar` engine with the published values. It does not reproduce the draws either.

We are not suggesting anything is wrong with the draws themselves. Our statistical tests on all 766 automated draws show no departure from uniformity. We'd simply like to describe your current process accurately.

1. Did the automated-draw method or the seed derivation change on about 4–5 August 2026, and again on about 21 October 2026?
2. How should the public verify a current automated draw from the published `rng_seed`?
3. Will the Draws Explained page be updated?
4. Would you consider publishing a numbers-only entry list (or its hash) and a pre-close seed commitment, so that every draw can be verified end to end? We have a short, free reference specification we'd be happy to share.

We'd be glad to share our reproduction code. We will not publish anything about this point before giving you a reasonable chance to reply (we propose 30 days).

Kind regards,
[name]
[contact]

---

Notes for the sender, not part of the message:

- Evidence: `docs/generated/ANALYSIS_7DAYS.md`, plus the archived snapshots of the Draws Explained page and the draw-results feed. Check their SHA-256 in the `snapshots` table.
- Do not include any winner's personal data.
- This is not a security vulnerability report. Even the old time-based seed gave entrants no usable edge, because ticket numbers are randomly allocated and the sold list is fixed at close. The issue is the auditability of published results.
