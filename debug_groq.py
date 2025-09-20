#!/usr/bin/env python3
"""
Debug script to test Groq API directly
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def test_groq_api():
    """Test Groq API directly"""

    # Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    print(f"🔑 API Key found: {'Yes' if GROQ_API_KEY else 'No'}")
    if GROQ_API_KEY:
        print(f"🔑 API Key (first 10 chars): {GROQ_API_KEY[:10]}...")

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in environment variables")
        return

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": "Write a short social media post about coffee. Keep it under 100 words.",
            }
        ],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    print("🔍 Testing Groq API...")
    print(f"URL: {GROQ_API_URL}")
    print(f"Model: {payload['model']}")
    print(f"Payload: {payload}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print()

            if response.status_code == 200:
                response_data = response.json()
                print("✅ Success! Full response:")
                print(response_data)
                print()

                if "choices" in response_data and response_data["choices"]:
                    content = response_data["choices"][0]["message"]["content"]
                    print(f"📝 Generated content: '{content}'")
                else:
                    print("❌ No choices in response")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_groq_api())
