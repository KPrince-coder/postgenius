"""
Request models and enums for the API.
"""

import importlib
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# Force reload settings to pick up any changes
from ..config import settings

importlib.reload(settings)

from ..config.settings import MAX_TOPIC_LENGTH, MIN_TOPIC_LENGTH  # noqa: E402


class Platform(str, Enum):
    """Supported social media platforms"""

    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class PostGenerationRequest(BaseModel):
    """Request model for post generation"""

    topic: str = Field(
        min_length=MIN_TOPIC_LENGTH,
        max_length=MAX_TOPIC_LENGTH,
        description="The topic or idea for the social media post",
        examples=["The benefits of morning exercise"],
    )
    platform: Platform = Field(
        default=Platform.TWITTER,
        description="The social media platform to generate content for",
        examples=["twitter", "linkedin"],
    )

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        """Validate and sanitize topic input"""
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")

        # Basic content filtering
        forbidden_words = ["spam", "scam", "hack", "illegal"]
        if any(word in v.lower() for word in forbidden_words):
            raise ValueError("Topic contains inappropriate content")

        return v.strip()
