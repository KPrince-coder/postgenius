"""
FastAPI Social Media Post Generator Application.

This module contains the main FastAPI application with route handlers
for both web interface and API endpoints.
"""

import logging
import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config.settings import (
    MAX_TOPIC_LENGTH,
    MIN_TOPIC_LENGTH,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
)
from .models import (
    ErrorResponse,
    Platform,
    PostGenerationRequest,
    PostGenerationResponse,
)
from .services import generate_social_post
from .utils import check_rate_limit, get_client_ip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

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


# Log current settings on startup
logger.info(f"Application starting with MAX_TOPIC_LENGTH: {MAX_TOPIC_LENGTH}")
logger.info(f"Application starting with MIN_TOPIC_LENGTH: {MIN_TOPIC_LENGTH}")


# Debug endpoint to check current settings
@app.get("/debug/settings", tags=["Debug"])
async def debug_settings():
    """Debug endpoint to check current validation settings"""
    return {
        "MAX_TOPIC_LENGTH": MAX_TOPIC_LENGTH,
        "MIN_TOPIC_LENGTH": MIN_TOPIC_LENGTH,
        "message": "Current validation settings",
    }


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
        platform_str = str(form_data.get("platform", "twitter")).strip()

        # Convert platform string to enum
        try:
            platform = Platform(platform_str)
        except ValueError:
            platform = Platform.TWITTER  # Default fallback

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
        generated_post = await generate_social_post(topic, platform)
        processing_time = time.time() - start_time

        platform_name = "X (Twitter)" if platform == Platform.TWITTER else "LinkedIn"
        logger.info(
            f"Generated {platform_name} post for topic: {topic[:50]}... (took {processing_time:.2f}s)"
        )

        return templates.TemplateResponse(
            "generate_post.html",
            {
                "request": request,
                "generated_post": generated_post,
                "topic": topic,
                "platform": platform.value,
                "platform_name": platform_name,
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
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


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

    - **topic**: The topic or idea for the social media post (3-1000 characters)
    - **platform**: The target social media platform (twitter or linkedin, defaults to twitter)

    Returns a JSON response with the generated post or error information.
    """
    # Debug logging for incoming request
    client_ip = get_client_ip(request)
    logger.info(f"API request received from IP: {client_ip}")
    logger.info(
        f"Request data - Topic length: {len(request_data.topic)}, Platform: {request_data.platform}"
    )
    logger.debug(
        f"Topic content: {request_data.topic[:100]}{'...' if len(request_data.topic) > 100 else ''}"
    )

    # Rate limiting check
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds.",
        )

    start_time = time.time()
    try:
        platform_name = (
            "X (Twitter)" if request_data.platform == Platform.TWITTER else "LinkedIn"
        )
        logger.info(
            f"API request for {platform_name} post on topic: {request_data.topic[:50]}... from IP: {client_ip}"
        )

        generated_post = await generate_social_post(
            request_data.topic, request_data.platform
        )
        processing_time = time.time() - start_time

        logger.info(f"API generation completed in {processing_time:.2f}s")

        return PostGenerationResponse(
            success=True,
            generated_post=generated_post,
            error_message=None,
            processing_time=processing_time,
            platform=request_data.platform,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating post: {str(e)}")
        return PostGenerationResponse(
            success=False,
            generated_post=None,
            error_message=str(e),
            processing_time=time.time() - start_time,
            platform=request_data.platform,
        )
