"""
Rate limiting utilities.
"""

import time
from collections import defaultdict
from fastapi import Request

from ..config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

# Rate limiting (simple in-memory store - use Redis in production)
request_counts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> bool:
    """
    Simple rate limiting check.
    In production, use Redis or a proper rate limiting service.
    """
    current_time = time.time()

    # Clean old requests
    request_counts[client_ip] = [
        req_time
        for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check if limit exceeded
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False

    # Add current request
    request_counts[client_ip].append(current_time)
    return True


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
