"""
Basic in-memory rate limiting middleware.

Limits each client (identified by IP address) to a configurable number of
requests within a rolling time window. This is intentionally simple - no
external dependency (e.g. Redis) is required, which is appropriate for a
single-process/self-hosted deployment. Counters live in process memory, so
they reset on restart and are not shared across multiple worker processes.

Docs/health/meta endpoints are exempt so tooling and uptime checks are never
throttled.
"""
import time
from collections import deque

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Paths that should never be rate limited.
EXEMPT_PATHS = {"/", "/api/health", "/docs", "/redoc", "/openapi.json"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window-per-client rate limiter backed by an in-memory deque."""

    def __init__(self, app, requests: int, window_seconds: int):
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        # client_key -> deque[timestamp] of requests within the current window
        self._hits: dict[str, deque] = {}

    def _client_key(self, request: Request) -> str:
        # Respect a reverse proxy's forwarded header if present, otherwise
        # fall back to the direct connection address.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if self.requests <= 0 or request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        now = time.monotonic()
        key = self._client_key(request)
        hits = self._hits.setdefault(key, deque())

        # Drop timestamps that have fallen out of the window.
        cutoff = now - self.window_seconds
        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= self.requests:
            retry_after = max(1, int(self.window_seconds - (now - hits[0])))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        return await call_next(request)
