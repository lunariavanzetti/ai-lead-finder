import asyncio
import time
from collections import defaultdict


class DomainRateLimiter:
    """Enforces a minimum delay between requests to the same domain, independent
    of how many concurrent workers are active across other domains."""

    def __init__(self, delay_seconds: float = 2.5):
        self.delay_seconds = delay_seconds
        self._last_request_at: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, domain: str) -> None:
        async with self._locks[domain]:
            elapsed = time.monotonic() - self._last_request_at[domain]
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)
            self._last_request_at[domain] = time.monotonic()

    def set_delay(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
