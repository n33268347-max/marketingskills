"""Builds data/seed/platforms.json from the Phase 1 desk research (2026-11-23).

Every claim here came from search-engine result snippets or third-party pages,
because direct fetches of the operator sites were blocked by the research
sandbox's network policy. They are therefore P_PROVISIONAL (or UNKNOWN /
C_HYPOTHESIS) and NONE is A_CONFIRMED. Promote a claim to A_CONFIRMED only after
reading the page directly and archiving a snapshot.

Run:  python scripts/build_seed.py
"""
import json
from pathlib import Path

D = "2026-11-23"
SNIP, TP, REG = "primary_search_snippet", "third_party", "regulator"


def P(topic, value, statement, url, kind=SNIP, quote=None):
    return dict(topic=topic, value=value, statement=statement, evidence_level="P_PROVISIONAL",
                source_url=url, source_kind=kind, source_quote=quote, accessed_on=D)


def U(topic, statement):
    return dict(topic=topic, value="unknown", statement=statement, evidence_level="UNKNOWN", source_kind="none")


def H(topic, statement, value=None):
    return dict(topic=topic, value=value, statement=statement, evidence_level="C_HYPOTHESIS", source_kind="none")


ROBOTS = U("robots_results_allowed", "robots.txt not yet fetched (sandbox network policy blocked the host).")
CODE_URL = "https://cms.law/en/gbr/legal-updates/dcms-publishes-voluntary-code-of-good-practice-for-prize-draw-operators"

platforms = [
  dict(slug="7days-performance", name="7days Performance", base_url="https://7daysperformance.co.uk",
       results_url="https://7daysperformance.co.uk/draw-result/", claims=[
    P("operator", None, "7days Performance Limited, company 11215119 (business directory listing; not checked at Companies House).", "https://7daysperformance.co.uk", TP),
    P("formats", None, "Standard draws (live and automatic), instant wins with end prize, spins, coin-drop, free daily instant wins.", "https://7daysperformance.co.uk"),
    P("discloses_max_tickets", "yes", "Competition pages show sold/total, e.g. '37,999 / 37,999'.", "https://7daysperformance.co.uk/product/win-1-000-tax-free-cash-67", quote="Sold: 100%, 37,999 / 37,999"),
    P("discloses_tickets_sold", "yes", "Tickets sold out of cap shown, including on finished competitions.", "https://7daysperformance.co.uk/product/win-1-000-tax-free-cash-67"),
    P("results_page", "yes", "Per-competition /draw-result/ pages exist; snippets show results back to at least Jan 2026.", "https://7daysperformance.co.uk/draw-result/prize-every-time-instant-win-4-winners"),
    P("results_show_ticket_number", "yes", "Result pages show winning ticket, draw date/time and auto/live flag.", "https://7daysperformance.co.uk/draw-result/prize-every-time-instant-win-4-winners"),
    P("ticket_allocation", "random_assigned", "Ticket numbers are randomly generated after payment.", "https://7daysperformance.co.uk", quote="Ticket numbers are randomly generated once you make your payment"),
    P("winner_selection", "auto_draw_or_live", "End prize decided by an auto-draw system, or a live draw; draw takes place regardless of tickets sold.", "https://7daysperformance.co.uk"),
    P("live_draw", "yes", "Live draws re-watchable on YouTube and Facebook.", "https://7daysperformance.co.uk"),
    P("independent_rng", "yes", "A page states 'Independently Certified by GLI'. Certificate scope not seen; GLI certification is of a system, not per-draw supervision.", "https://7daysperformance.co.uk", quote="Independently Certified by GLI"),
    P("instant_wins", "predetermined", "Instant-win outcomes predetermined by a random process; matching allocated ticket numbers win.", "https://7daysperformance.co.uk", quote="All outcomes are predetermined, using a random process"),
    P("free_entry_route", "yes", "Free postal entry via unenclosed postcard.", "https://7daysperformance.co.uk"),
    H("notes", "H8: The operator itself states automated draws use Mersenne Twister seeded from the current time and publishes seed, index and entry count (see confirmed claims). Hypothesis: published past automated draws can be independently REPRODUCED from the published seed, giving a full audit. Scope: verification of past results only; no prediction of future draws."),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="elite-competitions", name="Elite Competitions", base_url="https://elitecompetitions.co.uk",
       results_url="https://elitecompetitions.co.uk/all-winners", terms_url="https://elitecompetitions.co.uk/tnc", claims=[
    P("operator", None, "Hydro Solutions Fylde Ltd (09612888), Blackpool; corroborated by ASA rulings naming that company for Elite.", "https://asa.org.uk/rulings/hydro-solutions-fylde-ltd-G19-1023824.html", TP),
    P("formats", None, "End-prize draws, 'InstaWins', Elite Club monthly draws.", "https://elitecompetitions.co.uk/competitions/past/every-tickets-a-winner-pound1000-end-prize-4999x-instawins-110400"),
    P("results_page", "yes", "All-winners page and per-competition pages under /competitions/past/.", "https://elitecompetitions.co.uk/all-winners"),
    P("results_show_ticket_number", "yes", "Winners page shows winner, ticket number and draw date.", "https://elitecompetitions.co.uk/all-winners"),
    P("discloses_max_tickets", "yes", "Past competition pages show entry totals (e.g. 4,999 entries).", "https://elitecompetitions.co.uk/competitions/past/every-tickets-a-winner-pound1000-end-prize-4999x-instawins-110400"),
    U("discloses_tickets_sold", "Whether actual tickets sold (vs cap) is shown is not established."),
    P("winner_selection", "random_ball_machine", "Live draw using a 'verified random ball selector'; T&Cs refer to a 'random ball machine' for end prizes; draws regardless of sales.", "https://elitecompetitions.co.uk/how-to-play"),
    P("live_draw", "yes", "Draws streamed on YouTube and Facebook.", "https://elitecompetitions.co.uk/how-to-play"),
    U("independent_rng", "'Verified' is not explained; no independent party named."),
    U("ticket_allocation", "Not established."),
    P("free_entry_route", "yes", "Free open postcard route; capped at 2,500 postal entries per Elite Club draw.", "https://elitecompetitions.co.uk/tnc"),
    P("regulatory_history", None, "ASA rulings (2019) against Hydro Solutions Fylde Ltd: free entry route not clear/prominent; CAP 1.7 non-response; referred to CAP Compliance.", "https://www.asa.org.uk/rulings/hydro-solutions-fylde-ltd-g19-1044086-hydro-solutions-fylde-ltd.html", REG),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="rev-comps", name="Rev Comps", base_url="https://www.revcomps.com",
       results_url="https://www.revcomps.com/past-entry-lists", terms_url="https://www.revcomps.com/terms-conditions", claims=[
    P("operator", None, "Promoter reported as Rev Competitions Limited (Gibraltar), linked to UK Rev Corp Ltd.", "https://www.revcomps.com/terms-conditions", TP),
    P("formats", None, "Live draws, auto-draws, free bonus draw.", "https://www.revcomps.com/entry-free/"),
    P("results_page", "yes", "Past entry lists archive (lists for competitions before 1 April 2026 noted there).", "https://www.revcomps.com/past-entry-lists"),
    P("discloses_max_tickets", "yes", "Entry lists show total tickets per draw (e.g. 1,999 total).", "https://www.revcomps.com/past-entry-lists"),
    P("discloses_tickets_sold", "yes", "Entry lists show sold and remaining (e.g. 1,265 sold of 1,999).", "https://www.revcomps.com/past-entry-lists"),
    U("results_show_ticket_number", "Whether the archive shows the winning ticket number is not established."),
    P("winner_selection", "ball_machine_or_algorithm", "Live draws use ball machines; auto-draws use a 'random algorithm'; drawn regardless of sell-out.", "https://www.revcomps.com/faqs"),
    P("live_draw", "yes", "Draws streamed on Facebook, Instagram, YouTube.", "https://www.revcomps.com/faqs"),
    U("independent_rng", "No independent party named."),
    U("ticket_allocation", "Not established."),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="click-competitions", name="Click Competitions", base_url="https://www.clickcompetitions.co.uk",
       results_url="https://www.clickcompetitions.co.uk/draw-results", terms_url="https://www.clickcompetitions.co.uk/legal/terms-and-conditions", claims=[
    P("operator", None, "Click Competitions Limited, Companies House 12550861, Norwich (Companies House search snippet).", "https://find-and-update.company-information.service.gov.uk/company/12550861", REG),
    P("formats", None, "Skill-question draws, live and automatic draws, instant wins with end prizes, free competitions.", "https://www.clickcompetitions.co.uk/legal/terms-and-conditions"),
    P("results_page", "yes", "Draw results pages for main draws and instant wins.", "https://www.clickcompetitions.co.uk/draw-results"),
    P("results_show_ticket_number", "yes", "Results list winner name and ticket number.", "https://www.clickcompetitions.co.uk/draw-results"),
    P("discloses_max_tickets", "yes", "Ticket caps published per competition (e.g. 249,999).", "https://www.clickcompetitions.co.uk", TP),
    P("discloses_tickets_sold", "yes", "Company states it publicly displays all entry lists prior to the draw at /entry-lists/ (company reply on Trustpilot; contents not seen).", "https://www.clickcompetitions.co.uk/entry-lists/", TP),
    P("ticket_allocation", "assigned_on_entry", "T&Cs 16.5: a number is produced for each entry once made; random vs sequential not stated.", "https://www.clickcompetitions.co.uk/legal/terms-and-conditions"),
    P("winner_selection", "certified_rng", "Drawn using certified random number generator software, live or automated.", "https://www.clickcompetitions.co.uk/legal/terms-and-conditions", quote="drawn by using a certified random number generator software"),
    P("live_draw", "yes", "Live draws on Facebook on set weekdays; others are autodraws.", "https://www.clickcompetitions.co.uk"),
    U("independent_rng", "RNG described as 'certified' but no certifier named."),
    P("instant_wins", "predetermined", "Instant-win winning entries randomly selected before the competition goes live.", "https://www.clickcompetitions.co.uk/legal/terms-and-conditions"),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="lucky-day-competitions", name="Lucky Day Competitions", base_url="https://www.luckydaycompetitions.com",
       results_url="https://www.luckydaycompetitions.com/past-winners/", claims=[
    P("operator", None, "Ace Competitions Ltd t/a Lucky Day Competitions, NI659574, Newry.", "https://www.luckydaycompetitions.com"),
    P("formats", None, "Main draws, instant wins incl. 'Every Ticket Wins', auto draws.", "https://www.luckydaycompetitions.com"),
    P("results_page", "yes", "Past-winners pages (27+ pages) and per-date /draw_results/<date>/ pages.", "https://www.luckydaycompetitions.com/past-winners/"),
    P("results_show_ticket_number", "yes", "Per-date results list prize, winner and winning ticket number; no tickets sold or price shown.", "https://www.luckydaycompetitions.com/past-winners/"),
    U("discloses_max_tickets", "Not established."),
    U("discloses_tickets_sold", "Not shown on results pages; elsewhere not established."),
    P("winner_selection", "google_rng_live_or_auto", "Pages say draws are videoed live on Facebook using Google's random number generator; T&Cs say auto draws are system-selected. Descriptions inconsistent.", "https://www.luckydaycompetitions.com"),
    P("live_draw", "yes", "Draws videoed live on Facebook.", "https://www.luckydaycompetitions.com"),
    U("independent_rng", "No independent party named."),
    P("free_entry_route", "yes", "Postal route to Newry address; tickets cheaper than a stamp earn multiple entries.", "https://www.luckydaycompetitions.com"),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="dream-car-giveaways", name="Dream Car Giveaways", base_url="https://dreamcargiveaways.co.uk",
       results_url="https://dreamcargiveaways.co.uk/competition-winners/", terms_url="https://dreamcargiveaways.co.uk/terms-conditions", claims=[
    P("operator", None, "Registered number 11320154; reported owned by Jumbo Interactive since Oct 2025 (third party).", "https://dreamcargiveaways.co.uk"),
    P("formats", None, "Standard draws, instant wins (Golden Ticket, Ticket Hoops, Chase The Ace), automated draws, Spin to Win LIVE.", "https://dreamcargiveaways.co.uk/competitions/instant-wins"),
    P("discloses_max_tickets", "yes", "Terms: maximum entries will be stated on the website (e.g. 'Only 9999 Entries').", "https://dreamcargiveaways.co.uk/terms-conditions", quote="The maximum number entries to a Competition will be stated on the Website"),
    P("discloses_tickets_sold", "yes", "FAQ: full entry list published after close. (Second researcher could not confirm sold counts on past draws.)", "https://dreamcargiveaways.co.uk/faqs/draws-winners"),
    P("results_page", "yes", "Winners and past-competition pages exist (/competition-winners/, also reported /winners).", "https://dreamcargiveaways.co.uk/competition-winners/"),
    P("results_show_ticket_number", "yes", "Closed competition pages show the winning number.", "https://dreamcargiveaways.co.uk/competition-winners/"),
    P("winner_selection", "php_random_int", "Automated draws picked 'randomly, using PHP's random_int'.", "https://dreamcargiveaways.co.uk"),
    P("winner_selection", "google_rng_live", "Another page: draws videoed LIVE on Facebook using Google's random number generator. Conflicts with the random_int statement; may describe different draw types or eras.", "https://dreamcargiveaways.co.uk/faqs/draws-winners"),
    P("live_draw", "yes", "Live draws with presenter on Draws page, Facebook or YouTube.", "https://dreamcargiveaways.co.uk/faqs/draws-winners"),
    U("independent_rng", "No independent party named."),
    P("instant_wins", "predetermined_visible", "Instant prizes allocated at random to numbers in a spreadsheet; pages list winning numbers as 'already won' / 'still available'.", "https://dreamcargiveaways.co.uk/competitions/instant-wins"),
    P("code_of_practice", "yes", "Named by CMS law-firm update as an early backer of the Code (not checked on GOV.UK list).", CODE_URL, TP),
    H("notes", "Visible pre-allocated instant-win numbers mean the remaining instant-win prize pool is observable; expected value of an instant-win ticket can then be computed from public data (Phase 3)."),
    ROBOTS,
  ]),
  dict(slug="botb", name="BOTB (Best of the Best)", base_url="https://www.botb.com",
       results_url="https://www.botb.com/winners", terms_url="https://cdn.botb.com/media/v14domvf/botb-tcs-30-01-2026.pdf", claims=[
    P("operator", None, "Company 03755182 (T&Cs); part of Winvia Entertainment (AIM-listed).", "https://cdn.botb.com/media/v14domvf/botb-tcs-30-01-2026.pdf"),
    P("formats", "spot_the_ball_and_draws", "Dream Car is spot-the-ball (judged skill game); also instant wins and random prize draws.", "https://www.botb.com/how-to-play"),
    P("winner_selection", "judged_spot_the_ball", "Ball position set by an independent panel of judges in the presence of a qualified lawyer; closest coordinate wins, calculated by PromoVeritas.", "https://cdn.botb.com/media/v14domvf/botb-tcs-30-01-2026.pdf"),
    P("winner_selection", "promoveritas_rng", "Other draws: drawn by an independent promotional verification service such as PromoVeritas using its certified RNG.", "https://cdn.botb.com/media/v14domvf/botb-tcs-30-01-2026.pdf"),
    P("independent_rng", "yes", "PromoVeritas and an independent lawyer named.", "https://cdn.botb.com/media/v14domvf/botb-tcs-30-01-2026.pdf"),
    P("results_page", "yes", "Weekly winners pages (e.g. /winners/dc4626) back to at least 2023.", "https://www.botb.com/winners"),
    P("results_show_ticket_number", "not_applicable", "Main game is spot-the-ball: there is no winning ticket number to test for uniformity.", "https://www.botb.com/winners"),
    U("discloses_tickets_sold", "Not established; a third-party review says entry numbers are not published."),
    U("discloses_max_tickets", "T&Cs mention a 'Competition Entry Limit' without a figure."),
    P("code_of_practice", "yes", "Named as early backer of the Code.", CODE_URL, TP),
    ROBOTS,
  ]),
  dict(slug="omaze-uk", name="Omaze UK", base_url="https://omaze.co.uk",
       terms_url="https://omaze.co.uk/pages/official-rules-uk", claims=[
    P("formats", None, "House prize draws, Monthly Millionaire, weekly subscriber cash draw, free Dream List draw.", "https://omaze.co.uk/pages/official-rules-uk"),
    P("ticket_price_range", None, "Entry bundles from £10; subscriptions £15/100, £25/200, £50/640 entries.", "https://omaze.co.uk/pages/faqs"),
    P("winner_selection", "internal_engine_gli_certified", "Internal randomised draw engine certified by Gaming Labs (GLI); independent scrutineer Civica selected a winning entry code in at least one house draw.", "https://omaze.freshdesk.com/support/solutions/articles/103000157707", quote="Our draw engine has been certified by Gaming Labs, Inc (GLI)."),
    P("independent_rng", "yes", "Civica named as independent scrutineer for a house draw.", "https://omaze.co.uk/blogs/news/cheshire-house-winner-process"),
    U("results_page", "Only per-draw 'winner process' blog posts found; no structured archive."),
    U("discloses_tickets_sold", "FAQ only says 'typically millions of entries'."),
    P("discloses_max_tickets", "no", "No total-entries cap found; per-person spend cap £500/month (£250 credit card).", "https://omaze.co.uk/pages/official-rules-uk"),
    P("free_entry_route", "yes", "Postal entry route published.", "https://omaze.co.uk/pages/postal-entry-route"),
    P("code_of_practice", "yes", "Reported as a founding signatory.", "https://www.civilsociety.co.uk", TP),
    P("regulatory_history", None, "ASA ruling G20-1073875 (2020) upheld: free entry route not clear/prominent.", "https://www.asa.org.uk/rulings/omaze-inc-g20-1073875-omaze-inc.html", REG),
    H("notes", "Prize-draw with millions of entries and entry codes rather than bounded ticket numbers: winning-number uniformity tests are not feasible from public data. Value analysis only."),
    ROBOTS,
  ]),
  dict(slug="raffall", name="Raffall", base_url="https://raffall.com", claims=[
    P("operator", None, "Raffall Limited, 09930826 (third-party listing).", "https://raffall.com", TP),
    P("formats", "marketplace", "Marketplace: individual hosts run raffles with their own prizes and rules.", "https://raffall.com", TP),
    P("winner_selection", "in_house_automated", "All tickets entered into an automated draw where the system selects winners at random.", "https://help.raffall.com/hc/en-gb/articles/360015952479", quote="our system selects winners at random"),
    P("live_draw", "no", "Manual or live-hosted draws are not possible; social broadcasts do not affect outcomes.", "https://help.raffall.com/hc/en-gb/articles/360018833999"),
    U("independent_rng", "No certifier named."),
    U("results_page", "No public results archive found; entrants notified by email."),
    ROBOTS, U("code_of_practice", "Signatory status not established."),
  ]),
  dict(slug="aspire-competitions", name="Aspire Competitions", base_url="https://aspirecomps.co.uk", claims=[
    U("robots_results_allowed", "robots.txt allows all; terms not yet readable (rendered client-side). Automated access paused pending human review of terms."),
  ]),
  dict(slug="raffle-house", name="Raffle House", base_url="https://rafflehouse.com", claims=[
    H("code_of_practice", "Reported in search results as a Code signatory; source not pinned. Not researched further in Phase 1.", value=None),
    U("winner_selection", "Not yet researched."),
    U("results_page", "Not yet researched."),
    ROBOTS,
  ]),
]

out = {
    "meta": {
        "compiled_on": D,
        "method": "Desk research via web search snippets; direct operator page reads blocked by sandbox network policy.",
        "evidence_note": "No claim is A_CONFIRMED. All P_PROVISIONAL claims require a direct read + archived snapshot before promotion.",
    },
    "platforms": platforms,
}
path = Path(__file__).resolve().parents[1] / "data" / "seed" / "platforms.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {path} ({len(platforms)} platforms, {sum(len(p['claims']) for p in platforms)} claims)")
