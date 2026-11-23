import json
from pathlib import Path

import pytest

from raffle_edge.ranking import rank_all, score_platform
from raffle_edge.registry import Claim, RegistryError, load_seed, sync_to_db

SEED = Path(__file__).resolve().parents[1] / "data" / "seed" / "platforms.json"


def test_seed_validates_and_has_no_confirmed_claims():
    meta, platforms = load_seed(SEED)
    assert len(platforms) == 10
    levels = {c.evidence_level for p in platforms for c in p.claims}
    # Phase 1 could not read primary pages directly, so nothing may be A_CONFIRMED.
    assert "A_CONFIRMED" not in levels


def test_sync_is_idempotent(conn):
    _, platforms = load_seed(SEED)
    first = sync_to_db(conn, platforms)
    assert first > 0
    assert sync_to_db(conn, platforms) == 0


def test_confirmed_scores_are_zero_without_confirmed_claims(conn):
    _, platforms = load_seed(SEED)
    sync_to_db(conn, platforms)
    assert all(s.research_potential == 0 for s in rank_all(conn, "confirmed"))
    assert any(s.research_potential > 0 for s in rank_all(conn, "provisional"))


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
