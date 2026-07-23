"""Per-source token-bucket rate limiting.

Honeypots are, by design, exposed to hostile traffic including aggressive
scanners that can open thousands of connections per second. The rate limiter
caps the amount of work (and log volume) a single source can induce, while
still recording that the abusive source was seen.

The implementation is a classic token bucket keyed by source IP. It is safe
to use from a single asyncio event loop (no locking is required because the
loop is cooperatively scheduled). Stale buckets are evicted lazily to bound
memory use under IP-spraying attacks.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(slots=True)
class _Bucket:
    tokens: float
    last_refill: float
    last_seen: float


class RateLimiter:
    """A token-bucket rate limiter keyed by an arbitrary string (source IP)."""

    #: Buckets untouched for longer than this (seconds) are eligible for eviction.
    _IDLE_EVICT_SECONDS = 600.0
    #: Run a sweep at most this often (seconds) to keep the common path cheap.
    _SWEEP_INTERVAL = 60.0

    def __init__(
        self,
        max_events_per_minute: int,
        burst: int,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_events_per_minute <= 0:
            raise ValueError("max_events_per_minute must be positive")
        if burst <= 0:
            raise ValueError("burst must be positive")
        self._rate_per_second = max_events_per_minute / 60.0
        self._capacity = float(burst)
        self._clock = clock
        self._buckets: dict[str, _Bucket] = {}
        self._last_sweep = clock()

    def allow(self, key: str) -> bool:
        """Consume one token for ``key``; return whether the action is allowed."""
        now = self._clock()
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self._capacity, last_refill=now, last_seen=now)
            self._buckets[key] = bucket

        elapsed = now - bucket.last_refill
        if elapsed > 0:
            bucket.tokens = min(
                self._capacity, bucket.tokens + elapsed * self._rate_per_second
            )
            bucket.last_refill = now
        bucket.last_seen = now

        self._maybe_sweep(now)

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True
        return False

    def _maybe_sweep(self, now: float) -> None:
        if now - self._last_sweep < self._SWEEP_INTERVAL:
            return
        self._last_sweep = now
        cutoff = now - self._IDLE_EVICT_SECONDS
        stale = [key for key, b in self._buckets.items() if b.last_seen < cutoff]
        for key in stale:
            del self._buckets[key]

    def __len__(self) -> int:
        return len(self._buckets)
