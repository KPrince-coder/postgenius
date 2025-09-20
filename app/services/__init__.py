"""
Business logic services for the application.
"""

from .post_generator import generate_social_post, get_platform_prompt

__all__ = [
    "generate_social_post",
    "get_platform_prompt",
]
