import json
from pathlib import Path

import pytest

from raffle_edge.ranking import rank_all, score_platform
from raffle_edge.registry import Claim, RegistryError, load_seed, sync_to_db

SEED = Path(__file__).resolve().parents[1] / "data" / "seed" / "platforms.json"


def test_seed_validates_and_curated_file_has_no_confirmed_claims(tmp_path):
    # The hand-curated seed (desk research) must never contain A_CONFIRMED claims;
    # confirmed claims only arrive via quote-checked verified_claims.json.
    meta, platforms = load_seed(SEED, verified_path=tmp_path / "none.json")
    assert len(platforms) >= 10
    assert "A_CONFIRMED" not in {c.evidence_level for p in platforms for c in p.claims}


def test_every_confirmed_claim_cites_snapshot_and_quote():
    _, platforms = load_seed(SEED)
    confirmed = [c for p in platforms for c in p.claims if c.evidence_level == "A_CONFIRMED"]
    assert confirmed
    for c in confirmed:
        assert c.source_quote and c.source_url and c.accessed_on
        if c.source_kind == "primary_direct":
            assert c.snapshot_sha256 and len(c.snapshot_sha256) == 64


def test_sync_is_idempotent(conn):
    _, platforms = load_seed(SEED)
    first = sync_to_db(conn, platforms)
    assert first > 0
    assert sync_to_db(conn, platforms) == 0


def test_confirmed_scores_never_exceed_provisional(conn):
    _, platforms = load_seed(SEED)
    sync_to_db(conn, platforms)
    prov = {s.slug: s for s in rank_all(conn, "provisional")}
    for s in rank_all(conn, "confirmed"):
        assert s.evidence_coverage <= prov[s.slug].evidence_coverage


@pytest.mark.parametrize("bad", [
    dict(topic="made_up_topic", statement="x", evidence_level="UNKNOWN"),
    dict(topic="results_page", statement="x", evidence_level="A_CONFIRMED", source_url="https://a", source_kind="primary_search_snippet", accessed_on="2026-01-01"),
    dict(topic="results_page", statement="x", evidence_level="P_PROVISIONAL"),
    dict(topic="results_page", statement="x", evidence_level="B_OBSERVATION"),
])
def test_claim_validation_rejects(bad):
    with pytest.raises(RegistryError):
        Claim(**bad).validate("p")


def test_rubric_points_and_gaps(conn, tmp_path):
    seed = {"platforms": [{"slug": "demo", "name": "Demo", "base_url": "https://d.test", "claims": [
        {"topic": "results_page", "value": "yes", "statement": "s", "evidence_level": "A_CONFIRMED",
         "source_url": "https://d.test/w", "source_kind": "primary_direct", "accessed_on": "2026-01-01", "snapshot_sha256": "ab"},
        {"topic": "independent_rng", "value": "no", "statement": "s", "evidence_level": "A_CONFIRMED",
         "source_url": "https://d.test/t", "source_kind": "primary_direct", "accessed_on": "2026-01-01", "snapshot_sha256": "cd"},
        {"topic": "live_draw", "value": "yes", "statement": "s", "evidence_level": "C_HYPOTHESIS"},
    ]}]}
    f = tmp_path / "s.json"
    f.write_text(json.dumps(seed))
    sync_to_db(conn, load_seed(f)[1])
    s = score_platform(conn, "demo")
    assert s.accessibility == 30
    assert s.transparency == 0
    assert "named independent random source" in s.negatives
    assert "public live/recorded draw" in s.gaps  # hypotheses never score


def test_confirmed_overrides_provisional(conn, tmp_path):
    seed = {"platforms": [{"slug": "demo", "name": "Demo", "base_url": "https://d.test", "claims": [
        {"topic": "results_show_ticket_number", "value": "yes", "statement": "snippet", "evidence_level": "P_PROVISIONAL",
         "source_url": "https://d.test/w", "source_kind": "primary_search_snippet", "accessed_on": "2026-01-01"},
        {"topic": "results_show_ticket_number", "value": "no", "statement": "read", "evidence_level": "A_CONFIRMED",
         "source_url": "https://d.test/w2", "source_kind": "primary_direct", "accessed_on": "2026-01-02", "snapshot_sha256": "ef"},
    ]}]}
    f = tmp_path / "s.json"
    f.write_text(json.dumps(seed))
    sync_to_db(conn, load_seed(f, verified_path=tmp_path / "none.json")[1])
    s = score_platform(conn, "demo", "provisional")
    assert "results include winning ticket number" in s.negatives
