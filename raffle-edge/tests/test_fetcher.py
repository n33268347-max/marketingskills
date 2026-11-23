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


def test_captcha_reference_on_normal_page_is_not_a_challenge():
    from raffle_edge.collector.fetcher import looks_like_challenge
    page = b"<html><head><title>Win a House | Example</title></head><body>" + b"x" * 60_000 + \
        b"<script>const d=['g-recaptcha-response','h-captcha-response']</script></body></html>"
    assert not looks_like_challenge(200, page)


def test_interstitial_200_is_a_challenge():
    from raffle_edge.collector.fetcher import looks_like_challenge
    assert looks_like_challenge(200, b"<html><head><title>Just a moment...</title></head></html>")
    assert looks_like_challenge(200, b"<html><script src='/cdn-cgi/challenge-platform/x.js'></script></html>")


def test_crawl_delay_is_honoured(conn, tmp_path):
    pages = {"https://x.test/robots.txt": (200, b"User-agent: *\nCrawl-delay: 60\n"),
             "https://x.test/a": (200, b"a"), "https://x.test/b": (200, b"b")}
    f, _, clock = make(conn, tmp_path, pages, delay=10)
    f.fetch("https://x.test/a")
    f.fetch("https://x.test/b")
    assert clock.slept and max(clock.slept) >= 60


def test_claude_user_rules_are_honoured(conn, tmp_path):
    pages = {"https://x.test/robots.txt": (200, b"User-agent: Claude-User\nDisallow: /\n\nUser-agent: *\nAllow: /\n"),
             "https://x.test/a": (200, b"a")}
    f, calls, _ = make(conn, tmp_path, pages)
    assert f.fetch("https://x.test/a").outcome == "blocked_by_robots"
    assert "https://x.test/a" not in calls


def test_html_robots_treated_as_absent(conn, tmp_path):
    pages = {"https://x.test/robots.txt": (200, b"<!doctype html><html><body>app</body></html>"),
             "https://x.test/a": (200, b"a")}
    f, _, _ = make(conn, tmp_path, pages)
    assert f.fetch("https://x.test/a").ok
    assert "HTML" in f.robots_notes["https://x.test"]


def test_policy_blocked_host_gets_no_requests_at_all(conn, tmp_path):
    from raffle_edge.collector.fetcher import PoliteFetcher
    calls = []

    def transport(url, headers, timeout):
        calls.append(url)
        return HttpResponse(200, b"x")

    f = PoliteFetcher(conn, tmp_path, transport=transport, min_delay_s=0,
                      policy_blocked_hosts={"https://x.test": "terms forbid AI tools"})
    r = f.fetch("https://x.test/winners")
    assert r.outcome == "skipped" and "terms" in r.note
    assert calls == []  # not even robots.txt
