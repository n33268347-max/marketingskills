-- Raffle Edge research database (SQLite).
--
-- Design rules
--   * Every research table is APPEND-ONLY. Triggers below abort any UPDATE or
--     DELETE, so historical records cannot be overwritten by accident.
--     Corrections are new rows that reference the row they replace via
--     `supersedes_id`; the original stays in place for audit.
--   * Money is stored as integer pence to avoid floating-point drift.
--   * "Unknown" is NULL, never 0. A missing tickets_sold figure is not zero sales.
--   * No personal data about winners or participants is stored. There is
--     deliberately no column for winner names, locations or photos.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Platforms ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platforms (
    slug        TEXT PRIMARY KEY CHECK (length(slug) > 0 AND slug NOT GLOB '*[^a-z0-9-]*'),
    name        TEXT NOT NULL,
    base_url    TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Evidence-labelled statements about a platform (draw method, ticket
-- allocation, results page, etc.).
--   A_CONFIRMED   : confirmed fact read DIRECTLY from the primary source;
--                   must cite a source URL and access date
--   P_PROVISIONAL : reported (e.g. via search-engine snippet of the primary
--                   page, or a third party) but not yet read verbatim;
--                   must cite a source URL; needs direct verification
--   B_OBSERVATION : statistical observation, must cite an analysis reference
--   C_HYPOTHESIS  : requires further investigation
--   UNKNOWN       : explicitly recorded gap in knowledge
CREATE TABLE IF NOT EXISTS claims (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_slug  TEXT NOT NULL REFERENCES platforms(slug),
    topic          TEXT NOT NULL,
    statement      TEXT NOT NULL,
    evidence_level TEXT NOT NULL CHECK (evidence_level IN ('A_CONFIRMED','P_PROVISIONAL','B_OBSERVATION','C_HYPOTHESIS','UNKNOWN')),
    value          TEXT,               -- machine-readable value, e.g. 'yes' / 'no' / 'random_assigned'
    source_url     TEXT,
    source_kind    TEXT CHECK (source_kind IS NULL OR source_kind IN ('primary_direct','primary_search_snippet','third_party','regulator','none')),
    source_quote   TEXT,
    accessed_on    TEXT,               -- ISO date the source was read
    analysis_ref   TEXT,               -- for B_OBSERVATION
    snapshot_sha256 TEXT,              -- archived page the claim was read from
    recorded_by    TEXT NOT NULL DEFAULT 'unknown',
    recorded_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    supersedes_id  INTEGER REFERENCES claims(id),
    CHECK (evidence_level <> 'A_CONFIRMED' OR (source_url IS NOT NULL AND accessed_on IS NOT NULL)),
    CHECK (evidence_level <> 'A_CONFIRMED' OR source_kind IN ('primary_direct','regulator')),
    CHECK (evidence_level <> 'P_PROVISIONAL' OR source_url IS NOT NULL),
    CHECK (evidence_level <> 'B_OBSERVATION' OR analysis_ref IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_claims_platform_topic ON claims(platform_slug, topic);

-- Raw page snapshots: what was fetched, when, and whether robots.txt allowed it.
CREATE TABLE IF NOT EXISTS snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    url             TEXT NOT NULL,
    fetched_at      TEXT NOT NULL,
    http_status     INTEGER,
    content_type    TEXT,
    content_sha256  TEXT,
    content_path    TEXT,              -- relative path under data/raw
    robots_allowed  INTEGER NOT NULL CHECK (robots_allowed IN (0,1)),
    outcome         TEXT NOT NULL CHECK (outcome IN ('ok','http_error','blocked_by_robots','challenge_detected','network_error','skipped')),
    note            TEXT
);
CREATE INDEX IF NOT EXISTS ix_snapshots_url ON snapshots(url, fetched_at);

-- Accessibility probes (robots.txt + key pages) per platform.
CREATE TABLE IF NOT EXISTS probes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_slug    TEXT NOT NULL REFERENCES platforms(slug),
    probed_at        TEXT NOT NULL,
    target           TEXT NOT NULL,    -- 'robots' | 'homepage' | 'results' | 'terms'
    url              TEXT NOT NULL,
    outcome          TEXT NOT NULL,
    http_status      INTEGER,
    robots_allowed   INTEGER,
    snapshot_id      INTEGER REFERENCES snapshots(id),
    note             TEXT
);

-- Competitions: identity only. Everything that can change lives in observations.
CREATE TABLE IF NOT EXISTS competitions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_slug  TEXT NOT NULL REFERENCES platforms(slug),
    external_ref   TEXT NOT NULL,      -- the platform's own id/slug for the competition
    name           TEXT NOT NULL,
    first_seen_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (platform_slug, external_ref)
);

-- Point-in-time observations of a competition's public listing.
CREATE TABLE IF NOT EXISTS competition_observations (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id             INTEGER NOT NULL REFERENCES competitions(id),
    observed_at                TEXT NOT NULL,
    snapshot_id                INTEGER REFERENCES snapshots(id),
    source_url                 TEXT NOT NULL,
    prize_description          TEXT,
    advertised_value_pence     INTEGER CHECK (advertised_value_pence IS NULL OR advertised_value_pence >= 0),
    verified_value_pence       INTEGER CHECK (verified_value_pence IS NULL OR verified_value_pence >= 0),
    verified_value_source      TEXT,
    cash_alternative_pence     INTEGER CHECK (cash_alternative_pence IS NULL OR cash_alternative_pence >= 0),
    ticket_price_pence         INTEGER CHECK (ticket_price_pence IS NULL OR ticket_price_pence >= 0),
    max_tickets                INTEGER CHECK (max_tickets IS NULL OR max_tickets > 0),
    tickets_sold               INTEGER CHECK (tickets_sold IS NULL OR tickets_sold >= 0),
    tickets_sold_basis         TEXT CHECK (tickets_sold_basis IS NULL OR tickets_sold_basis IN ('disclosed_count','derived_from_percentage','derived_from_remaining','not_disclosed')),
    max_entries_per_person     INTEGER,
    number_of_prizes           INTEGER,
    closes_at                  TEXT,
    draw_at                    TEXT,
    winner_selection_method    TEXT,
    terms_url                  TEXT,
    supersedes_id              INTEGER REFERENCES competition_observations(id),
    CHECK (tickets_sold IS NULL OR max_tickets IS NULL OR tickets_sold <= max_tickets)
);
CREATE INDEX IF NOT EXISTS ix_obs_comp ON competition_observations(competition_id, observed_at);

-- Published draw results.
CREATE TABLE IF NOT EXISTS draw_results (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id         INTEGER NOT NULL REFERENCES competitions(id),
    drawn_at               TEXT,
    prize_rank             INTEGER NOT NULL DEFAULT 1,   -- 1 = main prize
    winning_ticket_number  INTEGER,
    ticket_range_min       INTEGER,
    ticket_range_max       INTEGER,
    tickets_sold_at_draw   INTEGER,
    selection_method       TEXT,
    independent_rng        TEXT NOT NULL DEFAULT 'unknown' CHECK (independent_rng IN ('yes','no','unknown')),
    rng_name               TEXT,
    evidence_url           TEXT NOT NULL,
    snapshot_id            INTEGER REFERENCES snapshots(id),
    recorded_at            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    supersedes_id          INTEGER REFERENCES draw_results(id),
    external_result_id     TEXT,      -- operator's own result id (dedupe key)
    draw_type              TEXT,      -- 'automated' | 'live' | 'instant_win' | NULL
    rng_published_seed     TEXT,      -- seed / commitment exactly as published
    rng_unix_time          TEXT,      -- draw timestamp exactly as published
    rng_index              INTEGER,   -- published winning position in the entry list
    rng_entries            INTEGER,   -- published number of entries in the list
    CHECK (winning_ticket_number IS NULL OR ticket_range_min IS NULL OR winning_ticket_number >= ticket_range_min),
    CHECK (winning_ticket_number IS NULL OR ticket_range_max IS NULL OR winning_ticket_number <= ticket_range_max)
);
CREATE INDEX IF NOT EXISTS ix_draws_comp ON draw_results(competition_id);

-- Immutability triggers ------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_platforms_no_delete BEFORE DELETE ON platforms
BEGIN SELECT RAISE(ABORT, 'platforms is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_claims_no_update BEFORE UPDATE ON claims
BEGIN SELECT RAISE(ABORT, 'claims is append-only; insert a superseding row'); END;
CREATE TRIGGER IF NOT EXISTS trg_claims_no_delete BEFORE DELETE ON claims
BEGIN SELECT RAISE(ABORT, 'claims is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_snapshots_no_update BEFORE UPDATE ON snapshots
BEGIN SELECT RAISE(ABORT, 'snapshots is append-only'); END;
CREATE TRIGGER IF NOT EXISTS trg_snapshots_no_delete BEFORE DELETE ON snapshots
BEGIN SELECT RAISE(ABORT, 'snapshots is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_probes_no_update BEFORE UPDATE ON probes
BEGIN SELECT RAISE(ABORT, 'probes is append-only'); END;
CREATE TRIGGER IF NOT EXISTS trg_probes_no_delete BEFORE DELETE ON probes
BEGIN SELECT RAISE(ABORT, 'probes is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_competitions_no_update BEFORE UPDATE ON competitions
BEGIN SELECT RAISE(ABORT, 'competitions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS trg_competitions_no_delete BEFORE DELETE ON competitions
BEGIN SELECT RAISE(ABORT, 'competitions is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_obs_no_update BEFORE UPDATE ON competition_observations
BEGIN SELECT RAISE(ABORT, 'competition_observations is append-only; insert a superseding row'); END;
CREATE TRIGGER IF NOT EXISTS trg_obs_no_delete BEFORE DELETE ON competition_observations
BEGIN SELECT RAISE(ABORT, 'competition_observations is append-only'); END;

CREATE TRIGGER IF NOT EXISTS trg_draws_no_update BEFORE UPDATE ON draw_results
BEGIN SELECT RAISE(ABORT, 'draw_results is append-only; insert a superseding row'); END;
CREATE TRIGGER IF NOT EXISTS trg_draws_no_delete BEFORE DELETE ON draw_results
BEGIN SELECT RAISE(ABORT, 'draw_results is append-only'); END;

-- Views ----------------------------------------------------------------------
-- Current view of each claim chain: rows that no later row supersedes.
CREATE VIEW IF NOT EXISTS current_claims AS
SELECT c.* FROM claims c
WHERE NOT EXISTS (SELECT 1 FROM claims s WHERE s.supersedes_id = c.id);

CREATE VIEW IF NOT EXISTS current_draw_results AS
SELECT d.* FROM draw_results d
WHERE NOT EXISTS (SELECT 1 FROM draw_results s WHERE s.supersedes_id = d.id);

CREATE VIEW IF NOT EXISTS latest_observations AS
SELECT o.* FROM competition_observations o
WHERE o.id = (
    SELECT o2.id FROM competition_observations o2
    WHERE o2.competition_id = o.competition_id
      AND NOT EXISTS (SELECT 1 FROM competition_observations s WHERE s.supersedes_id = o2.id)
    ORDER BY o2.observed_at DESC, o2.id DESC LIMIT 1
);

-- Ledger of every hypothesis test run, successful or not (Phase 5).
CREATE TABLE IF NOT EXISTS hypothesis_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_id   TEXT NOT NULL,          -- e.g. 'H3', 'H1-forward'
    run_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    platform_slug   TEXT,
    method          TEXT NOT NULL,
    train_period    TEXT,
    test_period     TEXT,
    n_train         INTEGER,
    n_test          INTEGER,
    metric          TEXT NOT NULL,
    train_value     REAL,
    test_value      REAL,
    baseline_value  REAL,
    p_value         REAL,
    ci_low          REAL,
    ci_high         REAL,
    outcome         TEXT NOT NULL CHECK (outcome IN ('supported','not_supported','inconclusive')),
    code_version    TEXT,
    notes           TEXT
);
CREATE TRIGGER IF NOT EXISTS trg_hruns_no_update BEFORE UPDATE ON hypothesis_runs
BEGIN SELECT RAISE(ABORT, 'hypothesis_runs is append-only'); END;
CREATE TRIGGER IF NOT EXISTS trg_hruns_no_delete BEFORE DELETE ON hypothesis_runs
BEGIN SELECT RAISE(ABORT, 'hypothesis_runs is append-only'); END;

CREATE UNIQUE INDEX IF NOT EXISTS ux_draws_external ON draw_results(competition_id, external_result_id)
    WHERE external_result_id IS NOT NULL AND supersedes_id IS NULL;
