import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from collections import defaultdict

# Phase 8 Minimal Memory Rule: In-memory sliding rate limiter dictionary
# Maps IP address -> list of request timestamps
VISITOR_LOGS = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 1 minute
MAX_REQUESTS_PER_WINDOW = 30  # Allow 30 downloads/page hits per minute per IP

class InfinitySecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Rate Limiting Logic (Exempting static files for UI performance)
        if not request.url.path.startswith("/static"):
            client_ip = request.client.host
            current_time = time.time()
            
            # Filter out timestamps older than the window
            VISITOR_LOGS[client_ip] = [
                t for t in VISITOR_LOGS[client_ip] 
                if current_time - t < RATE_LIMIT_WINDOW
            ]
            
            if len(VISITOR_LOGS[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
                raise HTTPException(
                    status_code=429, 
                    detail="Too many requests. Slow down your infinity engines!"
                )
            
            # Log current request timestamp
            VISITOR_LOGS[client_ip].append(current_time)

        # Proceed with the request pipeline
        response: Response = await call_next(request)
        
        # 2. Hardened Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' https://api.qrserver.com data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline';"
        )
        return response
