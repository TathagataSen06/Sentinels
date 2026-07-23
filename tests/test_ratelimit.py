"""Tests for the token-bucket rate limiter."""

from __future__ import annotations

import pytest

from honeytrace.ratelimit import RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_burst_is_allowed_then_blocked():
    clock = FakeClock()
    limiter = RateLimiter(max_events_per_minute=60, burst=5, clock=clock)
    # First `burst` calls succeed with no time passing.
    assert sum(limiter.allow("1.2.3.4") for _ in range(5)) == 5
    # The next is blocked (bucket empty, no refill yet).
    assert limiter.allow("1.2.3.4") is False


def test_bucket_refills_over_time():
    clock = FakeClock()
    limiter = RateLimiter(max_events_per_minute=60, burst=1, clock=clock)
    assert limiter.allow("host") is True
    assert limiter.allow("host") is False
    # 60/min == 1/sec, so after one second a single token is available.
    clock.advance(1.0)
    assert limiter.allow("host") is True


def test_sources_are_independent():
    clock = FakeClock()
    limiter = RateLimiter(max_events_per_minute=60, burst=1, clock=clock)
    assert limiter.allow("a") is True
    assert limiter.allow("b") is True
    assert limiter.allow("a") is False


def test_stale_buckets_are_evicted():
    clock = FakeClock()
    limiter = RateLimiter(max_events_per_minute=600, burst=1, clock=clock)
    limiter.allow("old")
    assert len(limiter) == 1
    # Advance well past the idle-eviction window and touch a new key to sweep.
    clock.advance(RateLimiter._IDLE_EVICT_SECONDS + RateLimiter._SWEEP_INTERVAL + 1)
    limiter.allow("new")
    assert "old" not in limiter._buckets  # noqa: SLF001 - white-box check


@pytest.mark.parametrize("bad", [0, -1])
def test_invalid_parameters_rejected(bad):
    with pytest.raises(ValueError):
        RateLimiter(max_events_per_minute=bad, burst=1)
    with pytest.raises(ValueError):
        RateLimiter(max_events_per_minute=1, burst=bad)
