"""
Social media post generation service using Groq API.
"""

import logging

import httpx

from ..config.settings import GROQ_API_KEY, GROQ_API_URL, MODEL, REQUEST_TIMEOUT
from ..models.requests import Platform

logger = logging.getLogger(__name__)


# Platform-specific prompt templates
TWITTER_PROMPT_TEMPLATE = """You are an expert social media manager with decades of experience and expertise. You excel at crafting and optimizing social media content for maximum engagement and impact for X (X.com => formerly Twitter).

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

Topic: {topic}"""

LINKEDIN_PROMPT_TEMPLATE = """You are an expert professional content creator and thought leader with extensive experience in LinkedIn content strategy. You excel at crafting engaging, professional content that drives meaningful conversations and builds professional networks.

Your task is to generate a LinkedIn post that is professional, insightful, and valuable to a business audience.

Guidelines:
- Create content suitable for a professional audience (business leaders, professionals, entrepreneurs)
- Length should be 150-300 words for optimal engagement
- Use a professional yet conversational tone
- Include industry insights, career advice, or business perspectives
- Structure with clear paragraphs and line breaks for readability
- Start with a compelling hook or question
- Include actionable takeaways or thought-provoking questions
- Use storytelling to illustrate points when relevant
- Focus on value creation for the reader
- Encourage professional discussion and networking
- Avoid excessive emojis (1-2 professional ones are acceptable)
- End with a call-to-action or discussion prompt
- The content should establish thought leadership and expertise
- Make it shareable and discussion-worthy

Topic: {topic}"""


def get_platform_prompt(platform: Platform, topic: str) -> str:
    """
    Get platform-specific prompt for content generation.

    Args:
        platform: The target social media platform
        topic: The topic for the post

    Returns:
        Platform-optimized prompt string
    """
    if platform == Platform.TWITTER:
        return TWITTER_PROMPT_TEMPLATE.format(topic=topic)

    elif platform == Platform.LINKEDIN:
        return LINKEDIN_PROMPT_TEMPLATE.format(topic=topic)

    else:
        # Default to Twitter format for unknown platforms
        return get_platform_prompt(Platform.TWITTER, topic)


async def generate_social_post(
    usr_topic: str, platform: Platform = Platform.TWITTER
) -> str:
    """
    Generate a social media post using Groq API with platform-specific optimization.

    Args:
        usr_topic: The topic for the social media post
        platform: The target social media platform

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

    # Get platform-specific prompt
    prompt = get_platform_prompt(platform, sanitized_topic)

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
