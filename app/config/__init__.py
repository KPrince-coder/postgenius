"""
Configuration settings and constants.
"""

from .settings import (
    GROQ_API_KEY,
    GROQ_API_URL,
    MAX_TOPIC_LENGTH,
    MIN_TOPIC_LENGTH,
    MODEL,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    REQUEST_TIMEOUT,
)

__all__ = [
    "GROQ_API_KEY",
    "GROQ_API_URL", 
    "MODEL",
    "REQUEST_TIMEOUT",
    "MIN_TOPIC_LENGTH",
    "MAX_TOPIC_LENGTH",
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_WINDOW",
]
