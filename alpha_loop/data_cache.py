"""
Thin wrapper around the vendored MoonDevAPI client that adds retry-with-
backoff on 429 (rate_limited) and 503 (fills_scanner_busy), and a simple
per-minute request budget so the loop self-throttles well under the
documented 3,600 req/min limit.

No order-placement code lives here or anywhere in alpha_loop/ -- this module
only ever calls the read-only data endpoints.
"""

import time
from collections import deque

import requests

from . import config
from vendor.moondev_api import MoonDevAPI


class RateBudget:
    """Self-throttle to config.MAX_REQUESTS_PER_MINUTE."""

    def __init__(self, max_per_minute):
        self.max_per_minute = max_per_minute
        self._calls = deque()

    def wait_if_needed(self):
        now = time.monotonic()
        while self._calls and now - self._calls[0] > 60:
            self._calls.popleft()
        if len(self._calls) >= self.max_per_minute:
            sleep_for = 60 - (now - self._calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
        self._calls.append(time.monotonic())


class CachedMoonDevAPI:
    """Calls MoonDevAPI methods with retry/backoff + a request budget."""

    def __init__(self, api_key=None):
        self.api = MoonDevAPI(api_key=api_key)
        self.budget = RateBudget(config.MAX_REQUESTS_PER_MINUTE)

    def call(self, method_name, *args, **kwargs):
        """Call a MoonDevAPI method by name, retrying on 429/503."""
        method = getattr(self.api, method_name)
        last_exc = None
        for attempt in range(config.RETRY_MAX_ATTEMPTS):
            self.budget.wait_if_needed()
            try:
                return method(*args, **kwargs)
            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                last_exc = exc
                if status in (429, 503):
                    backoff = config.RETRY_BASE_BACKOFF_SECONDS * (2 ** attempt)
                    time.sleep(backoff)
                    continue
                raise
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                backoff = config.RETRY_BASE_BACKOFF_SECONDS * (2 ** attempt)
                time.sleep(backoff)
                continue
        raise last_exc

    @property
    def has_key(self):
        return bool(self.api.api_key)
