from pathlib import Path

from raffle_edge.db.database import ensure_platform
from raffle_edge.ingest import DRAW_CSV_COLUMNS, import_draws_csv, record_observation
from raffle_edge.parsers.generic import extract

FX = Path(__file__).parent / "fixtures"


def test_extract_structured_page():
    ec = extract((FX / "synthetic_competition.html").read_text())
    assert ec.name == "Synthetic Test Hatchback"
    assert ec.ticket_price_pence == 149
    assert (ec.tickets_sold, ec.max_tickets) == (1265, 1999)
    assert ec.tickets_sold_basis == "disclosed_count"
    assert ec.tickets_remaining == 734
    assert ec.advertised_value_pence == 2_450_000
    assert ec.cash_alternative_pence == 2_100_000
    assert "json-ld" in ec.provenance["ticket_price_pence"]


def test_extract_result_page_and_percentage_derivation():
    ec = extract((FX / "synthetic_result.html").read_text())
    assert ec.max_tickets == 9999
    assert ec.tickets_sold == 7499 and ec.tickets_sold_basis == "derived_from_percentage"
    assert ec.warnings
    assert ec.winning_ticket_number == 4821
    assert ec.ticket_price_pence == 250


def test_extract_never_guesses():
    ec = extract("<html><body><p>Nothing useful here</p></body></html>")
    assert ec.max_tickets is None and ec.tickets_sold is None and ec.ticket_price_pence is None


def test_record_observation_marks_undisclosed(conn):
    ensure_platform(conn, "demo", "Demo", "https://d.test")
    ec = extract("<h1>Thing</h1>")
    oid = record_observation(conn, "demo", "thing", "https://d.test/thing", ec)
    row = conn.execute("SELECT * FROM competition_observations WHERE id=?", (oid,)).fetchone()
    assert row["tickets_sold"] is None and row["tickets_sold_basis"] == "not_disclosed"


def test_import_draws_csv(conn, tmp_path):
    ensure_platform(conn, "demo", "Demo", "https://d.test")
    conn.commit()
    f = tmp_path / "draws.csv"
    header = ",".join(DRAW_CSV_COLUMNS)
    good = "demo,c1,Comp 1,2026-01-05,1,42,1,100,80,live ball machine,unknown,,https://d.test/r/c1"
    no_evidence = "demo,c2,Comp 2,2026-01-06,1,7,1,100,,,unknown,,"
    out_of_range = "demo,c3,Comp 3,2026-01-07,1,101,1,100,,,unknown,,https://d.test/r/c3"
    f.write_text("\n".join([header, good, no_evidence, out_of_range]) + "\n")
    n, errors = import_draws_csv(conn, f)
    assert n == 1 and len(errors) == 2
    # Re-import is safe and adds nothing.
    n2, _ = import_draws_csv(conn, f)
    assert n2 == 0
