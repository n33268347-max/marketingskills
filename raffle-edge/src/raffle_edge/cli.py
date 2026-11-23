"""Command-line entry point: `python -m raffle_edge.cli <command>`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .collector.fetcher import PoliteFetcher
from .collector.probe import probe_platform
from .db.database import connect
from .ingest import import_draws_csv, record_observation
from .parsers.generic import extract
from .ranking import rank_all
from .registry import load_seed, sync_to_db
from .reporting import dossiers_report, ranking_report

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "db" / "raffle_edge.sqlite"
DEFAULT_SEED = ROOT / "data" / "seed" / "platforms.json"
DEFAULT_RAW = ROOT / "data" / "raw"


def _conn(args):
    return connect(args.db)


def cmd_init(args) -> int:
    _conn(args)
    print(f"database ready: {args.db}")
    return 0


def cmd_load(args) -> int:
    meta, platforms = load_seed(args.seed)
    n = sync_to_db(_conn(args), platforms, recorded_by=meta.get("compiled_on", "seed"))
    print(f"{len(platforms)} platforms validated; {n} new claims appended")
    return 0


def cmd_rank(args) -> int:
    conn = _conn(args)
    print(f"{'platform':28} {'potential':>9} {'access':>7} {'transp':>7} {'coverage':>8}   basis={args.basis}")
    for s in rank_all(conn, args.basis):
        print(f"{s.name[:28]:28} {s.research_potential:9.1f} {s.accessibility:7d} {s.transparency:7d} {s.evidence_coverage:8.0%}")
    return 0


def cmd_report(args) -> int:
    conn = _conn(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "PLATFORM_RANKING.md").write_text(ranking_report(conn), encoding="utf-8")
    (out / "PLATFORM_DOSSIERS.md").write_text(dossiers_report(conn), encoding="utf-8")
    print(f"wrote {out/'PLATFORM_RANKING.md'} and {out/'PLATFORM_DOSSIERS.md'}")
    return 0


def cmd_probe(args) -> int:
    conn = _conn(args)
    _, platforms = load_seed(args.seed)
    sync_to_db(conn, platforms)
    chosen = [p for p in platforms if args.all or p.slug in args.slugs]
    if not chosen:
        print("no platforms selected (give slugs or --all)", file=sys.stderr)
        return 2
    fetcher = PoliteFetcher(conn, args.raw, min_delay_s=args.delay)
    for p in chosen:
        for r in probe_platform(conn, fetcher, p):
            print(f"{p.slug:24} {r['target']:9} {r['outcome']:19} {r['http_status'] or '-':>4}  {r['note'] or ''}")
    return 0


def cmd_fetch(args) -> int:
    """Fetch URLs through the compliant fetcher; write readable text for review."""
    from bs4 import BeautifulSoup
    import re

    conn = _conn(args)
    fetcher = PoliteFetcher(conn, args.raw, min_delay_s=args.delay)
    out = Path(args.text_dir) if args.text_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for url in args.urls:
        res = fetcher.fetch(url)
        row = conn.execute("SELECT content_sha256, content_path FROM snapshots WHERE id=?", (res.snapshot_id,)).fetchone()
        line = f"{res.outcome:19} {res.status or '-':>4} snapshot={res.snapshot_id} sha={(row['content_sha256'] or '')[:12]} {url}"
        if out and res.body:
            soup = BeautifulSoup(res.text(), "lxml")
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            text = re.sub(r"\n\s*\n+", "\n", soup.get_text("\n", strip=True))
            dest = out / f"snapshot-{res.snapshot_id}.txt"
            dest.write_text(f"URL: {url}\nSNAPSHOT: {res.snapshot_id}\nSHA256: {row['content_sha256']}\n\n{text}", encoding="utf-8")
            line += f" -> {dest}"
        print(line, flush=True)
    return 0


def cmd_merge_verified(args) -> int:
    from .verify import merge_files

    out = Path(args.seed).with_name("verified_claims.json")
    n, rejected = merge_files(Path(args.raw), [Path(f) for f in args.files], out)
    print(f"{n} quote-checked claims added to {out}; {len(rejected)} rejected")
    for r in rejected:
        print("  REJECTED " + r)
    return 0


def cmd_extract(args) -> int:
    """Parse a locally saved HTML file (e.g. an archived snapshot) and optionally store it."""
    html = Path(args.html).read_text(encoding="utf-8", errors="replace")
    ec = extract(html)
    print(json.dumps(ec.as_dict(), indent=2))
    if args.store:
        if not (args.platform and args.ref and args.source_url):
            print("--store needs --platform, --ref and --source-url", file=sys.stderr)
            return 2
        oid = record_observation(_conn(args), args.platform, args.ref, args.source_url, ec)
        print(f"stored observation #{oid}")
    return 0


def cmd_import_draws(args) -> int:
    n, errors = import_draws_csv(_conn(args), args.csv)
    print(f"{n} draw results inserted")
    for e in errors:
        print("  " + e, file=sys.stderr)
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="raffle-edge", description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--seed", default=str(DEFAULT_SEED))
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db", help="create the database").set_defaults(fn=cmd_init)
    sub.add_parser("load-registry", help="validate seed and append new claims").set_defaults(fn=cmd_load)
    p = sub.add_parser("rank", help="print platform ranking")
    p.add_argument("--basis", choices=["confirmed", "provisional"], default="provisional")
    p.set_defaults(fn=cmd_rank)
    p = sub.add_parser("report", help="write Markdown reports")
    p.add_argument("--out", default=str(ROOT / "docs" / "generated"))
    p.set_defaults(fn=cmd_report)
    p = sub.add_parser("probe", help="robots-respecting accessibility probe")
    p.add_argument("slugs", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--raw", default=str(DEFAULT_RAW))
    p.add_argument("--delay", type=float, default=10.0, help="min seconds between requests per host (>=5)")
    p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("fetch", help="fetch URLs politely and archive them")
    p.add_argument("urls", nargs="+")
    p.add_argument("--raw", default=str(DEFAULT_RAW))
    p.add_argument("--delay", type=float, default=10.0)
    p.add_argument("--text-dir", help="write readable text of each page here")
    p.set_defaults(fn=cmd_fetch)
    p = sub.add_parser("merge-verified", help="quote-check claim files and merge into verified_claims.json")
    p.add_argument("files", nargs="+")
    p.add_argument("--raw", default=str(DEFAULT_RAW))
    p.set_defaults(fn=cmd_merge_verified)
    p = sub.add_parser("extract", help="parse a saved competition page")
    p.add_argument("html")
    p.add_argument("--store", action="store_true")
    p.add_argument("--platform")
    p.add_argument("--ref")
    p.add_argument("--source-url")
    p.set_defaults(fn=cmd_extract)
    p = sub.add_parser("import-draws", help="import transcribed draw results CSV")
    p.add_argument("csv")
    p.set_defaults(fn=cmd_import_draws)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if getattr(args, "delay", 10.0) < 5:
        print("refusing --delay below 5 seconds", file=sys.stderr)
        return 2
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
