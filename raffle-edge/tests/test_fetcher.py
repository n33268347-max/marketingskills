from raffle_edge.collector.fetcher import HttpResponse, PoliteFetcher


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.slept = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def make(conn, tmp_path, pages, delay=10.0):
    calls = []

    def transport(url, headers, timeout):
        calls.append(url)
        if url not in pages:
            return HttpResponse(404, b"not found")
        v = pages[url]
        if isinstance(v, Exception):
            raise v
        status, body = v
        return HttpResponse(status, body, "text/html")

    clock = FakeClock()
    f = PoliteFetcher(conn, tmp_path, transport=transport, min_delay_s=delay, clock=clock.now, sleep=clock.sleep)
    return f, calls, clock


ROBOTS = b"User-agent: *\nDisallow: /account/\n"


def test_obeys_robots(conn, tmp_path):
    f, calls, _ = make(conn, tmp_path, {"https://x.test/robots.txt": (200, ROBOTS), "https://x.test/ok": (200, b"<p>hi</p>")})
    assert f.fetch("https://x.test/ok").ok
    r = f.fetch("https://x.test/account/orders")
    assert r.outcome == "blocked_by_robots"
    assert "https://x.test/account/orders" not in calls


def test_unreachable_robots_means_disallow(conn, tmp_path):
    f, calls, _ = make(conn, tmp_path, {"https://x.test/robots.txt": OSError("blocked")})
    assert f.fetch("https://x.test/page").outcome == "blocked_by_robots"
    assert calls == ["https://x.test/robots.txt"]


def test_missing_robots_allows(conn, tmp_path):
    f, _, _ = make(conn, tmp_path, {"https://x.test/page": (200, b"ok")})
    assert f.fetch("https://x.test/page").ok


def test_challenge_stops_host(conn, tmp_path):
    pages = {"https://x.test/robots.txt": (200, b""),
             "https://x.test/a": (403, b"<html>Attention Required! | Cloudflare cf-chl-xyz</html>"),
             "https://x.test/b": (200, b"fine")}
    f, calls, _ = make(conn, tmp_path, pages)
    assert f.fetch("https://x.test/a").outcome == "challenge_detected"
    assert f.fetch("https://x.test/b").outcome == "skipped"
    assert "https://x.test/b" not in calls


def test_rate_limit_per_host(conn, tmp_path):
    pages = {"https://x.test/robots.txt": (200, b""), "https://x.test/a": (200, b"a"), "https://x.test/b": (200, b"b")}
    f, _, clock = make(conn, tmp_path, pages, delay=10)
    f.fetch("https://x.test/a")
    f.fetch("https://x.test/b")
    assert clock.slept and all(abs(s - 10) < 1e-9 for s in clock.slept)


def test_snapshots_archived_and_logged(conn, tmp_path):
    f, _, _ = make(conn, tmp_path, {"https://x.test/robots.txt": (200, b""), "https://x.test/a": (200, b"body")}, delay=0)
    r = f.fetch("https://x.test/a")
    row = conn.execute("SELECT * FROM snapshots WHERE id=?", (r.snapshot_id,)).fetchone()
    assert row["outcome"] == "ok" and row["content_sha256"]
    assert (tmp_path / row["content_path"]).read_bytes() == b"body"
