import time
import logging
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# -----------------------------
# Rate Limiter Configuration
# -----------------------------

VISITOR_LOGS = defaultdict(list)

RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 30


class InfinitySecurityMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # Skip static resources
        if not request.url.path.startswith("/static"):

            client_ip = (
                request.client.host
                if request.client
                else "unknown"
            )

            current_time = time.time()

            # Remove expired timestamps
            timestamps = [
                ts
                for ts in VISITOR_LOGS[client_ip]
                if current_time - ts < RATE_LIMIT_WINDOW
            ]

            VISITOR_LOGS[client_ip] = timestamps

            if len(timestamps) >= MAX_REQUESTS_PER_WINDOW:

                logger.warning(
                    "Rate limit exceeded: %s",
                    client_ip,
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": (
                            "Too many requests. "
                            "Please try again later."
                        )
                    },
                )

            VISITOR_LOGS[client_ip].append(current_time)

            # Remove empty IP entries to prevent memory growth
            if not VISITOR_LOGS[client_ip]:
                VISITOR_LOGS.pop(client_ip, None)

        response: Response = await call_next(request)

        # -----------------------------
        # Security Headers
        # -----------------------------

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https://api.qrserver.com; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self';"
        )

        return response