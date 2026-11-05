"""Bounded, process-local login attempt limiter.

This is a first defense against online guessing and memory exhaustion, not a
substitute for trusted reverse-proxy abuse controls or shared multi-node policy.
The peer key is the address provided by ASGI, never an untrusted request header.
"""
from __future__ import annotations

from collections import OrderedDict, deque
import threading
import time
from typing import Callable


class LoginAttemptLimiter:
    def __init__(
        self, *,
        window_seconds: float = 300.0,
        username_limit: int = 5,
        peer_limit: int = 40,
        global_limit: int = 300,
        max_buckets: int = 4096,
        clock: Callable[[], float] = time.monotonic,
    ):
        if min(window_seconds, username_limit, peer_limit, global_limit, max_buckets) <= 0:
            raise ValueError("Attempt limiter settings must be positive")
        self.window_seconds = window_seconds
        self.username_limit = username_limit
        self.peer_limit = peer_limit
        self.global_limit = global_limit
        self.max_buckets = max_buckets
        self.clock = clock
        self._lock = threading.Lock()
        self._global: deque[float] = deque()
        self._buckets: OrderedDict[tuple[str, str], deque[float]] = OrderedDict()

    def _prune(self, timestamps: deque[float], now: float) -> None:
        while timestamps and now - timestamps[0] >= self.window_seconds:
            timestamps.popleft()

    def allow(self, username: str, peer: str) -> bool:
        """Atomically reserve capacity before expensive password verification.

        Count all attempts, successful or not, to bound scrypt CPU pressure.
        A successful login clears the username throttle, but not the peer/global
        budget, so one account cannot bypass a shared attack limit.
        """
        username = username.casefold()
        peer = peer or "unknown"
        now = self.clock()
        keys = (("user", username), ("peer", peer))
        limits = (self.username_limit, self.peer_limit)
        with self._lock:
            self._prune(self._global, now)
            if len(self._global) >= self.global_limit:
                return False
            for key, limit in zip(keys, limits):
                bucket = self._buckets.get(key)
                if bucket is not None:
                    self._prune(bucket, now)
                    if len(bucket) >= limit:
                        return False
            # Reclaim only expired entries when capacity is tight. Evicting
            # live buckets would erase unexpired password-guessing attempts,
            # allowing a caller to reset an account/peer budget by churning
            # unrelated names or peers. Refuse the whole reservation instead.
            missing = sum(key not in self._buckets for key in keys)
            if len(self._buckets) + missing > self.max_buckets:
                for key, bucket in list(self._buckets.items()):
                    self._prune(bucket, now)
                    if not bucket:
                        del self._buckets[key]
                if len(self._buckets) + missing > self.max_buckets:
                    return False
            self._global.append(now)
            for key in keys:
                bucket = self._buckets.get(key)
                if bucket is None:
                    bucket = deque()
                    self._buckets[key] = bucket
                bucket.append(now)
                self._buckets.move_to_end(key)
            return True

    def clear_user(self, username: str) -> None:
        with self._lock:
            self._buckets.pop(("user", username.casefold()), None)
