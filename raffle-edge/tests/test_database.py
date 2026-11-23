import sqlite3

import pytest

from raffle_edge.db.database import ImmutableRecordError, ensure_competition, ensure_platform, insert, transaction


def _setup(conn):
    ensure_platform(conn, "demo", "Demo", "https://example.test")
    cid = ensure_competition(conn, "demo", "c1", "Comp 1")
    did = insert(conn, "draw_results", {"competition_id": cid, "winning_ticket_number": 5,
                                        "ticket_range_min": 1, "ticket_range_max": 10, "evidence_url": "https://example.test/r"})
    conn.commit()
    return cid, did


@pytest.mark.parametrize("sql", [
    "UPDATE draw_results SET winning_ticket_number = 6",
    "DELETE FROM draw_results",
    "UPDATE competitions SET name = 'x'",
    "DELETE FROM competitions",
])
def test_history_is_immutable(conn, sql):
    _setup(conn)
    with pytest.raises(ImmutableRecordError):
        with transaction(conn):
            conn.execute(sql)
    assert conn.execute("SELECT winning_ticket_number FROM draw_results").fetchone()[0] == 5


def test_correction_by_superseding_row(conn):
    cid, did = _setup(conn)
    with transaction(conn):
        insert(conn, "draw_results", {"competition_id": cid, "winning_ticket_number": 7, "ticket_range_min": 1,
                                      "ticket_range_max": 10, "evidence_url": "https://example.test/r2", "supersedes_id": did})
    cur = conn.execute("SELECT winning_ticket_number FROM current_draw_results").fetchall()
    assert [r[0] for r in cur] == [7]
    assert conn.execute("SELECT COUNT(*) FROM draw_results").fetchone()[0] == 2


def test_winning_number_must_be_in_range(conn):
    cid, _ = _setup(conn)
    with pytest.raises(sqlite3.IntegrityError):
        insert(conn, "draw_results", {"competition_id": cid, "winning_ticket_number": 11, "ticket_range_min": 1,
                                      "ticket_range_max": 10, "evidence_url": "https://example.test/r"})


def test_tickets_sold_cannot_exceed_max(conn):
    cid, _ = _setup(conn)
    with pytest.raises(sqlite3.IntegrityError):
        insert(conn, "competition_observations", {"competition_id": cid, "observed_at": "2026-01-01T00:00:00Z",
                                                  "source_url": "https://example.test", "max_tickets": 10, "tickets_sold": 11})


def test_confirmed_claim_requires_direct_source(conn):
    ensure_platform(conn, "demo", "Demo", "https://example.test")
    with pytest.raises(sqlite3.IntegrityError):
        insert(conn, "claims", {"platform_slug": "demo", "topic": "results_page", "statement": "x",
                                "evidence_level": "A_CONFIRMED", "source_url": "https://example.test",
                                "accessed_on": "2026-01-01", "source_kind": "primary_search_snippet"})
