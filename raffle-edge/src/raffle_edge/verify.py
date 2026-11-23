"""Anti-fabrication check: every A_CONFIRMED quote must appear in its archived page.

Claims gathered by people or agents are merged only if `source_quote` can be
found (after whitespace/punctuation normalisation) in the text of the snapshot
identified by `snapshot_sha256`.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import unicodedata
from dataclasses import asdict
from pathlib import Path

from bs4 import BeautifulSoup

from .registry import Claim, RegistryError

log = logging.getLogger(__name__)

_PUNCT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", "£": "£"})


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_PUNCT)
    return re.sub(r"\s+", " ", text).strip().lower()


def snapshot_text(raw_dir: Path, sha256: str) -> str:
    path = Path(raw_dir) / sha256[:2] / f"{sha256}.bin"
    data = path.read_bytes()
    if data[:5] == b"%PDF-":
        if shutil.which("pdftotext"):
            return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
        from pypdf import PdfReader  # optional dependency

        return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    html = data.decode("utf-8", "replace")
    soup = BeautifulSoup(html, "lxml")
    # Include both rendered text and raw markup: some quotes live in attributes
    # or embedded JSON of client-rendered pages.
    return soup.get_text(" ") + "\n" + html


def quote_found(raw_dir: Path, sha256: str, quote: str) -> bool:
    text = normalise(snapshot_text(raw_dir, sha256))
    q = normalise(quote)
    if q in text:
        return True
    # Tolerate an ellipsis or a [REDACTED] gap joining verbatim fragments, in order.
    parts = [p.strip() for p in re.split(r"\.\.\.|…|\[redacted\]", q) if p.strip()]
    if len(parts) < 2:
        return False
    pos = 0
    for part in parts:
        pos = text.find(part, pos)
        if pos < 0:
            return False
        pos += len(part)
    return True


# Personal data must never enter the registry (UK GDPR; project policy).
_PII = re.compile(
    r'"(?:full_name|first_name|last_name|name|email|phone)"\s*:\s*"(?!\[REDACTED\])[^"]+"'
    r"|winner\s+(?!\[REDACTED\])[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+",
)


def contains_pii(text: str | None) -> bool:
    return bool(text and _PII.search(text))


def check_claims(raw_dir: Path, items: list[dict]) -> tuple[list[dict], list[str]]:
    """Return (accepted, rejection reasons). Items carry platform_slug + Claim fields."""
    accepted, rejected = [], []
    for i, item in enumerate(items):
        item = dict(item)
        slug = item.pop("platform_slug", None)
        tag = f"#{i} {slug}/{item.get('topic')}"
        try:
            claim = Claim(**item)
            claim.validate(slug or "?")
            if contains_pii(claim.source_quote) or contains_pii(claim.statement):
                raise RegistryError("possible personal data (e.g. a winner's name); redact with [REDACTED]")
            if claim.evidence_level == "A_CONFIRMED":
                if not (claim.snapshot_sha256 and claim.source_quote):
                    raise RegistryError("needs snapshot_sha256 and source_quote")
                if not (Path(raw_dir) / claim.snapshot_sha256[:2] / f"{claim.snapshot_sha256}.bin").exists():
                    raise RegistryError("snapshot not in local archive")
                if not quote_found(raw_dir, claim.snapshot_sha256, claim.source_quote):
                    raise RegistryError("quote not found verbatim in snapshot")
            accepted.append({"platform_slug": slug, **asdict(claim)})
        except (TypeError, RegistryError, OSError, subprocess.CalledProcessError) as exc:
            rejected.append(f"{tag}: {exc}")
    return accepted, rejected


def merge_files(raw_dir: Path, inputs: list[Path], out: Path) -> tuple[int, list[str]]:
    items: list[dict] = []
    for f in inputs:
        items.extend(json.loads(Path(f).read_text(encoding="utf-8")))
    accepted, rejected = check_claims(raw_dir, items)
    existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    seen = {json.dumps(c, sort_keys=True) for c in existing}
    new = [c for c in accepted if json.dumps(c, sort_keys=True) not in seen]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(existing + new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(new), rejected
