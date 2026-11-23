import hashlib

from raffle_edge.verify import check_claims


def _archive(tmp_path, body: bytes) -> str:
    sha = hashlib.sha256(body).hexdigest()
    d = tmp_path / sha[:2]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sha}.bin").write_bytes(body)
    return sha


def _claim(sha, quote):
    return {"platform_slug": "demo", "topic": "live_draw", "value": "yes", "statement": "s",
            "evidence_level": "A_CONFIRMED", "source_kind": "primary_direct", "source_url": "https://d.test",
            "source_quote": quote, "accessed_on": "2026-11-23", "snapshot_sha256": sha}


def test_verbatim_quote_accepted_with_normalisation(tmp_path):
    sha = _archive(tmp_path, "<p>All draws are streamed  <b>live</b> on Facebook – every week.</p>".encode())
    ok, bad = check_claims(tmp_path, [_claim(sha, "All draws are streamed live on Facebook - every week.")])
    assert len(ok) == 1 and not bad


def test_fabricated_quote_rejected(tmp_path):
    sha = _archive(tmp_path, b"<p>Draws use a ball machine.</p>")
    ok, bad = check_claims(tmp_path, [_claim(sha, "Draws are independently audited by PromoVeritas")])
    assert not ok and "not found" in bad[0]


def test_missing_snapshot_rejected(tmp_path):
    ok, bad = check_claims(tmp_path, [_claim("ab" * 32, "x")])
    assert not ok and "archive" in bad[0]
