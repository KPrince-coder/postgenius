"""
Response models for the API.
"""

from pydantic import BaseModel, ConfigDict, Field

from .requests import Platform


class PostGenerationResponse(BaseModel):
    """Response model for post generation"""

    success: bool = Field(
        description="Whether the generation was successful", examples=[True]
    )
    generated_post: str | None = Field(
        None,
        description="The generated social media post",
        examples=[
            "🌅 Starting your day with exercise isn't just about fitness—it's about setting the tone for everything that follows.\n\nWhen you move your body first thing in the morning, you're telling yourself: 'I prioritize my well-being.'\n\nWhat's your morning ritual? 💪"
        ],
    )
    error_message: str | None = Field(
        None, description="Error message if generation failed"
    )
    processing_time: float | None = Field(
        None, description="Time taken to generate the post in seconds", examples=[2.34]
    )
    platform: Platform | None = Field(
        None,
        description="The platform the post was generated for",
        examples=["twitter"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "generated_post": "🌅 Starting your day with exercise isn't just about fitness—it's about setting the tone for everything that follows.\n\nWhen you move your body first thing in the morning, you're telling yourself: 'I prioritize my well-being.'\n\nWhat's your morning ritual? 💪",
                "error_message": None,
                "processing_time": 2.34,
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str = Field(..., description="Error description")
    error_code: str | None = Field(None, description="Specific error code")
