"""Polite, compliance-first HTTP fetcher.

Guarantees:
  * robots.txt is fetched and obeyed for every host before any other request.
    If robots.txt cannot be read, the host is treated as disallowed.
  * A minimum delay per host (default 10 s) is enforced.
  * No cookies are kept, no logins, no form posts. GET only.
  * If a CAPTCHA / bot challenge / access block is detected the fetcher records
    it and refuses further requests to that host for the rest of the run.
    It never tries to solve or evade challenges.
  * Every response is archived (content-addressed by SHA-256) and logged in the
    append-only `snapshots` table.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
import time
import urllib.robotparser
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol
from urllib.parse import urlsplit

from ..db.database import insert, transaction

log = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "RaffleEdgeResearch/0.1 (+non-commercial statistical research; obeys robots.txt)"

CHALLENGE_MARKERS = (
    "cf-chl-",
    "challenge-platform",
    "g-recaptcha",
    "h-captcha",
    "hcaptcha.com",
    "recaptcha/api",
    "are you a robot",
    "verify you are human",
    "attention required! | cloudflare",
    "access denied",
    "px-captcha",
    "datadome",
)


@dataclass
class HttpResponse:
    status: int
    body: bytes
    content_type: str = ""
    headers: dict | None = None


class Transport(Protocol):
    def __call__(self, url: str, headers: dict[str, str], timeout: float) -> HttpResponse: ...


def requests_transport(url: str, headers: dict[str, str], timeout: float) -> HttpResponse:
    import requests  # imported lazily so tests need no network stack

    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    return HttpResponse(r.status_code, r.content, r.headers.get("Content-Type", ""), dict(r.headers))


@dataclass
class FetchResult:
    url: str
    outcome: str  # ok | http_error | blocked_by_robots | challenge_detected | network_error | skipped
    status: int | None
    body: bytes | None
    snapshot_id: int | None
    note: str | None = None

    @property
    def ok(self) -> bool:
        return self.outcome == "ok"

    def text(self) -> str:
        return (self.body or b"").decode("utf-8", errors="replace")


def looks_like_challenge(status: int, body: bytes) -> bool:
    head = body[:200_000].decode("utf-8", errors="ignore").lower()
    if status in (401, 403, 429, 503) and any(m in head for m in CHALLENGE_MARKERS):
        return True
    # Some challenges return 200 with an interstitial page.
    return bool(re.search(r"cf-chl-|g-recaptcha|h-captcha|px-captcha", head))


class PoliteFetcher:
    def __init__(
        self,
        conn: sqlite3.Connection,
        raw_dir: str | Path,
        transport: Transport = requests_transport,
        user_agent: str = DEFAULT_USER_AGENT,
        min_delay_s: float = 10.0,
        timeout_s: float = 20.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.conn = conn
        self.raw_dir = Path(raw_dir)
        self.transport = transport
        self.user_agent = user_agent
        self.min_delay_s = min_delay_s
        self.timeout_s = timeout_s
        self.clock = clock
        self.sleep = sleep
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._last_hit: dict[str, float] = {}
        self._blocked_hosts: dict[str, str] = {}

    # -- helpers --------------------------------------------------------------
    @staticmethod
    def _host(url: str) -> str:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise ValueError(f"unsupported URL {url!r}")
        return f"{parts.scheme}://{parts.netloc}"

    def _throttle(self, host: str) -> None:
        last = self._last_hit.get(host)
        if last is not None:
            wait = self.min_delay_s - (self.clock() - last)
            if wait > 0:
                self.sleep(wait)
        self._last_hit[host] = self.clock()

    def _raw_get(self, url: str) -> HttpResponse:
        host = self._host(url)
        self._throttle(host)
        return self.transport(url, {"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml,*/*;q=0.5"}, self.timeout_s)

    def _archive(self, body: bytes) -> tuple[str, str]:
        sha = hashlib.sha256(body).hexdigest()
        rel = Path(sha[:2]) / f"{sha}.bin"
        dest = self.raw_dir / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
        return sha, str(rel)

    def _record(self, url: str, outcome: str, robots_allowed: bool, resp: HttpResponse | None, note: str | None) -> int:
        sha = path = None
        if resp is not None and resp.body:
            sha, path = self._archive(resp.body)
        with transaction(self.conn):
            return insert(
                self.conn,
                "snapshots",
                {
                    "url": url,
                    "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "http_status": resp.status if resp else None,
                    "content_type": resp.content_type if resp else None,
                    "content_sha256": sha,
                    "content_path": path,
                    "robots_allowed": 1 if robots_allowed else 0,
                    "outcome": outcome,
                    "note": note,
                },
            )

    # -- robots ---------------------------------------------------------------
    def robots_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        host = self._host(url)
        if host in self._robots:
            return self._robots[host]
        robots_url = f"{host}/robots.txt"
        rp: urllib.robotparser.RobotFileParser | None
        try:
            resp = self._raw_get(robots_url)
        except Exception as exc:  # network failure => treat as disallowed
            log.warning("robots.txt unreachable for %s: %s", host, exc)
            self._record(robots_url, "network_error", False, None, f"robots.txt unreachable: {exc}")
            self._robots[host] = None
            return None
        if looks_like_challenge(resp.status, resp.body):
            self._blocked_hosts[host] = "challenge on robots.txt"
            self._record(robots_url, "challenge_detected", False, resp, "bot challenge on robots.txt; host disabled")
            self._robots[host] = None
            return None
        rp = urllib.robotparser.RobotFileParser()
        if resp.status in (401, 403):
            rp.disallow_all = True
        elif 400 <= resp.status < 500:
            rp.allow_all = True  # RFC 9309: no robots.txt => no restrictions
        elif resp.status >= 500:
            rp = None  # server error => be conservative
        else:
            rp.parse(resp.body.decode("utf-8", "replace").splitlines())
        self._record(robots_url, "ok" if resp.status < 400 else "http_error", True, resp, None)
        self._robots[host] = rp
        return rp

    def allowed(self, url: str) -> bool:
        rp = self.robots_for(url)
        return bool(rp and rp.can_fetch(self.user_agent, url))

    # -- public ---------------------------------------------------------------
    def fetch(self, url: str) -> FetchResult:
        host = self._host(url)
        if host in self._blocked_hosts:
            sid = self._record(url, "skipped", False, None, f"host disabled this run: {self._blocked_hosts[host]}")
            return FetchResult(url, "skipped", None, None, sid, self._blocked_hosts[host])
        if not self.allowed(url):
            reason = "robots.txt disallows" if self._robots.get(host) else "robots.txt unavailable (treated as disallow)"
            sid = self._record(url, "blocked_by_robots", False, None, reason)
            log.info("not fetching %s: %s", url, reason)
            return FetchResult(url, "blocked_by_robots", None, None, sid, reason)
        try:
            resp = self._raw_get(url)
        except Exception as exc:
            sid = self._record(url, "network_error", True, None, str(exc)[:500])
            return FetchResult(url, "network_error", None, None, sid, str(exc)[:500])
        if looks_like_challenge(resp.status, resp.body):
            self._blocked_hosts[host] = "bot challenge detected"
            sid = self._record(url, "challenge_detected", True, resp, "challenge page; not bypassed; host disabled")
            log.warning("challenge detected at %s; stopping requests to %s", url, host)
            return FetchResult(url, "challenge_detected", resp.status, resp.body, sid, "challenge detected")
        outcome = "ok" if 200 <= resp.status < 400 else "http_error"
        sid = self._record(url, outcome, True, resp, None)
        return FetchResult(url, outcome, resp.status, resp.body, sid)
