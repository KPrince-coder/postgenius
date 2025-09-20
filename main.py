import logging
import os
import time
from collections import defaultdict

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

# API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"  # Use a known working Groq model
REQUEST_TIMEOUT = 30.0
MAX_TOPIC_LENGTH = 200
MIN_TOPIC_LENGTH = 3

# Rate limiting (simple in-memory store - use Redis in production)
request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS: int = 10  # requests per window
RATE_LIMIT_WINDOW: int = 60  # seconds


# Pydantic Models
class PostGenerationRequest(BaseModel):
    """Request model for post generation"""

    topic: str = Field(
        min_length=MIN_TOPIC_LENGTH,
        max_length=MAX_TOPIC_LENGTH,
        description="The topic or idea for the social media post",
        examples=["The benefits of morning exercise"],
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


# FastAPI App Configuration
app = FastAPI(
    title="Social Media Post Generator",
    description="AI-powered social media post generation using Groq",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Utility Functions
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


# Route Handlers
@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def read_root(request: Request):
    """
    Home page with application overview and features.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/generate-post", response_class=HTMLResponse, tags=["Web Interface"])
async def generate_post_page(request: Request):
    """
    Display the post generation form.
    """
    return templates.TemplateResponse("generate_post.html", {"request": request})


@app.post("/generate-post", response_class=HTMLResponse, tags=["Web Interface"])
async def generate_post_form(request: Request):
    """
    Handle form submission for post generation (HTML response).
    """
    try:
        form_data = await request.form()
        topic = str(form_data.get("topic", "")).strip()

        if not topic:
            return templates.TemplateResponse(
                "generate_post.html",
                {"request": request, "error": "Please provide a topic"},
            )

        # Validate topic length
        if len(topic) < MIN_TOPIC_LENGTH:
            return templates.TemplateResponse(
                "generate_post.html",
                {
                    "request": request,
                    "error": f"Topic must be at least {MIN_TOPIC_LENGTH} characters long",
                },
            )

        if len(topic) > MAX_TOPIC_LENGTH:
            return templates.TemplateResponse(
                "generate_post.html",
                {
                    "request": request,
                    "error": f"Topic must be no more than {MAX_TOPIC_LENGTH} characters long",
                },
            )

        # Generate post
        start_time = time.time()
        generated_post = await generate_x_post(topic)
        processing_time = time.time() - start_time

        logger.info(
            f"Generated post for topic: {topic[:50]}... (took {processing_time:.2f}s)"
        )

        return templates.TemplateResponse(
            "generate_post.html",
            {
                "request": request,
                "generated_post": generated_post,
                "topic": topic,
                "processing_time": f"{processing_time:.2f}",
            },
        )

    except Exception as e:
        logger.error(f"Error in form submission: {str(e)}")
        return templates.TemplateResponse(
            "generate_post.html",
            {
                "request": request,
                "error": "An unexpected error occurred. Please try again.",
            },
        )


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "service": "Social Media Post Generator",
        "version": "1.0.0",
    }


# API Endpoints
@app.post(
    "/api/generate-post",
    response_model=PostGenerationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["API"],
    summary="Generate Social Media Post",
    description="Generate an engaging social media post based on the provided topic using AI.",
)
async def api_generate_post(
    request_data: PostGenerationRequest, request: Request
) -> PostGenerationResponse:
    """
    Generate a social media post via API endpoint.

    - **topic**: The topic or idea for the social media post (3-200 characters)

    Returns a JSON response with the generated post or error information.
    """
    # Rate limiting check
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds.",
        )

    start_time = time.time()
    try:
        logger.info(
            f"API request for topic: {request_data.topic[:50]}... from IP: {client_ip}"
        )

        generated_post = await generate_x_post(request_data.topic)
        processing_time = time.time() - start_time

        logger.info(f"API generation completed in {processing_time:.2f}s")

        return PostGenerationResponse(
            success=True,
            generated_post=generated_post,
            error_message=None,
            processing_time=processing_time,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"API generation error: {str(e)}")
        return PostGenerationResponse(
            success=False,
            generated_post=None,
            error_message="Failed to generate post. Please try again.",
            processing_time=time.time() - start_time,
        )


async def generate_x_post(usr_topic: str) -> str:
    """
    Generate a social media post using Groq API.

    Args:
        usr_topic: The topic for the social media post

    Returns:
        Generated social media post text

    Raises:
        ValueError: If the topic is invalid
        Exception: If API call fails
    """
    # Validate input
    if not usr_topic or not usr_topic.strip():
        raise ValueError("Topic cannot be empty")

    # Sanitize topic to prevent prompt injection
    sanitized_topic = usr_topic.replace("<", "&lt;").replace(">", "&gt;").strip()

    prompt = f"""You are an expert social media manager with decades of experience and expertise. You excel at crafting and optimizing social media content for maximum engagement and impact for X (X.com => formerly Twitter).

Your task is to generate a post that is concise, impactful, and tailored to the topic provided by the user.
Avoid using hashtags and lots of emojis (a few emojis are fine, but not too many and they should be relevant to the topic or the post's content).

Guidelines:
- Keep it short and focused (under 280 characters ideally)
- Structure it in a clean and readable format using line breaks and empty lines to enhance readability
- Use a conversational tone and avoid overly formal language
- Use a mix of short and long sentences to keep the reader engaged
- Use rhetorical questions to engage the audience and encourage them to share their thoughts
- Use humor and wit to make the post more engaging and memorable
- Use storytelling techniques to captivate the audience and evoke emotions
- Use metaphors and analogies to make complex ideas more relatable and understandable
- Use persuasive language to convince the audience to take action
- The post should be humanized and not appear AI-generated

Topic: {sanitized_topic}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            logger.debug(f"Making API request for topic: {usr_topic[:50]}...")
            logger.debug(f"API URL: {GROQ_API_URL}")
            logger.debug(f"Payload: {payload}")
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                logger.debug(f"Full API response: {response_data}")

                # Check if we have choices in the response
                if "choices" not in response_data or not response_data["choices"]:
                    logger.error(f"No choices in API response: {response_data}")
                    raise Exception("No choices returned from API")

                # Extract the generated text
                choice = response_data["choices"][0]
                if "message" not in choice or "content" not in choice["message"]:
                    logger.error(f"Invalid choice structure: {choice}")
                    raise Exception("Invalid response structure from API")

                generated_text = choice["message"]["content"]
                logger.debug(f"Generated text: '{generated_text}'")

                if not generated_text or not generated_text.strip():
                    logger.warning("API returned empty content")
                    raise Exception("API returned empty content")

                logger.debug("API request successful")
                return generated_text.strip()
            else:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

    except httpx.TimeoutException:
        error_msg = "Request timed out. Please try again."
        logger.error(error_msg)
        raise Exception(error_msg)
    except httpx.RequestError as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except KeyError as e:
        error_msg = f"Unexpected API response format: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error calling Groq API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


# def main():
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# if __name__ == "__main__":
#     main()
