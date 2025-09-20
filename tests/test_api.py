"""
Simple test script to verify the API endpoints work correctly.
Run this after starting the FastAPI server.
"""

import asyncio

import httpx


async def test_health_endpoint():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200


async def test_api_generate_post():
    """Test the API post generation endpoint."""
    async with httpx.AsyncClient() as client:
        payload = {"topic": "The benefits of morning exercise"}
        response = await client.post(
            "http://localhost:8000/api/generate-post", json=payload
        )
        print(f"API Generate Post (default platform): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Platform: {data.get('platform', 'not specified')}")
            print(f"Generated Post: {data['generated_post'][:100]}...")
            print(f"Processing Time: {data['processing_time']}s")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200


async def test_api_generate_post_platforms():
    """Test the API post generation endpoint with different platforms."""
    async with httpx.AsyncClient() as client:
        platforms = ["twitter", "linkedin"]

        for platform in platforms:
            payload = {
                "topic": "The benefits of morning exercise",
                "platform": platform,
            }
            response = await client.post(
                "http://localhost:8000/api/generate-post", json=payload
            )
            print(f"API Generate Post ({platform}): {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data['success']}")
                print(f"Platform: {data.get('platform', 'not specified')}")
                print(f"Generated Post: {data['generated_post'][:100]}...")
                print(f"Processing Time: {data['processing_time']}s")
            else:
                print(f"Error: {response.text}")
            print()
        return True


async def test_rate_limiting():
    """Test rate limiting by making multiple requests."""
    async with httpx.AsyncClient() as client:
        payload = {"topic": "Test topic"}

        print("Testing rate limiting...")
        for i in range(12):  # Exceed the limit of 10
            response = await client.post(
                "http://localhost:8000/api/generate-post", json=payload
            )
            print(f"Request {i + 1}: {response.status_code}")
            if response.status_code == 429:
                print("Rate limiting working correctly!")
                break
            await asyncio.sleep(0.1)  # Small delay between requests


async def main():
    """Run all tests."""
    print("Starting API tests...\n")

    # Test health endpoint
    print("1. Testing health endpoint...")
    await test_health_endpoint()
    print()

    # Test API generation (this will fail without Groq API key)
    print("2. Testing API generation...")
    try:
        await test_api_generate_post()
    except Exception as e:
        print(f"Expected error (no Groq API key): {e}")
    print()

    # Test API generation with platforms
    print("3. Testing API generation with platforms...")
    try:
        await test_api_generate_post_platforms()
    except Exception as e:
        print(f"Expected error (no Groq API key): {e}")
    print()

    # Test rate limiting
    print("4. Testing rate limiting...")
    try:
        await test_rate_limiting()
    except Exception as e:
        print(f"Rate limiting test error: {e}")
    print()

    print("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
