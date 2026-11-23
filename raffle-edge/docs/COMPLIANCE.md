# Compliance and ethics

_This document is not legal advice. Get a UK solicitor's review before any commercial use._

## Hard rules, enforced in code where possible

| Rule | Enforcement |
|---|---|
| Obey robots.txt | `PoliteFetcher` checks every URL. If robots.txt is unreachable, every path is treated as **disallowed**. If it serves HTML, there is no robots file (RFC 9309); this is flagged. |
| No CAPTCHA or bot-challenge bypass | Challenge markers stop all requests to that host for the rest of the run. Nothing is solved or evaded. |
| No authentication or account areas | GET only, no cookies, no credentials, no form posts. |
| Rate limits | ≥ 5 s per host minimum (CLI refuses lower); 10 s default; raised to the site's `Crawl-delay`. |
| AI-agent robots rules | Rules for `Claude-User` are obeyed too, because an AI agent operates the tool. |
| Terms that forbid AI/scraping | `data/seed/collection_blocklist.json` lists such hosts (currently BOTB and Click Competitions). The fetcher refuses them before any request. Data from them is manual-only, or obtained by asking the operator. |
| Personal data in evidence | `merge-verified` rejects quotes that look like names; redact with `[REDACTED]`. Raw snapshots under `data/raw/` can contain winner names. They are gitignored, kept only locally for audit, and must not be published. |
| Identify ourselves | The User-Agent names the project as non-commercial research. |
| No automated entries | The codebase has no purchase or entry code and will not get any. |
| No personal data | The schema has no column for winner names, locations or photos. Parsers must drop them. |
| Immutable history | Append-only tables enforced by SQLite triggers. |

## Relevant UK law and codes (to verify with counsel)

- **Gambling Act 2005.**
  - s.14 and Sch 2 para 8: a free-draw exemption applies where a free entry route is offered.
  - s.339: genuine prize competitions based on skill.

  Our work analyses these products. It does not run them.
- **Computer Misuse Act 1990.** Unauthorised access is excluded by design.
- **UK GDPR / Data Protection Act 2018.** Winner names are personal data, so they are not collected.
- **Copyright and Rights in Databases Regulations 1997.** Repeated extraction of substantial parts of a results database may infringe sui generis database right. This is the **main commercial legal risk**.
- **Website terms of use.** Review each platform's terms before collecting from it. Where the terms forbid automated access, use manual transcription with source citations, or ask the operator.
- **CAP Code (section 8, promotional marketing) and the ASA.** These are relevant if we ever publish comparative or value claims.
- **DCMS Voluntary Code of Good Practice for Prize Draw Operators** (Nov 2025, in force May 2026). It is useful as a transparency benchmark.

## If a genuine weakness is found

1. Stop. Do not use it, and do not enter the affected competitions.
2. Document it with the minimum evidence needed, using only public data.
3. Disclose it privately to the operator with a reasonable fix window, around 90 days. Where appropriate, also tell the Gambling Commission or the DCMS code administrator.
4. Publish aggregate findings only after the fix, or at the end of the disclosure window.

## Responsible framing

Nothing produced by this project may present competitions as an income source or a "likely win". Every value output must show the expected loss alongside the expected value. A positive-EV label is allowed only when it was computed from verified inputs (final sold count and verified prize value).
