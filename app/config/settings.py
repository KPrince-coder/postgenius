"""
Configuration settings and environment variables.
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"  # Use a known working Groq model
REQUEST_TIMEOUT = 30.0

# Validation Constants
MAX_TOPIC_LENGTH = 1000
MIN_TOPIC_LENGTH = 3

# Rate Limiting Configuration
RATE_LIMIT_REQUESTS: int = 10  # requests per window
RATE_LIMIT_WINDOW: int = 60  # seconds
