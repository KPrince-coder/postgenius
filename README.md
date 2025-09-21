# Social Media Post Generator

AI-powered social media post generation using FastAPI, Jinja2, HTMX, and Groq's API.

## Features

- 🤖 **AI-Powered Generation**: Uses Groq's fast LLaMA models to create engaging social media posts
- 🎯 **Multi-Platform Support**: Generate optimized content for Twitter/X and LinkedIn
- 🌐 **Web Interface**: Clean, responsive web interface with platform selection
- 🔌 **REST API**: Full REST API with comprehensive documentation
- 📊 **Rate Limiting**: Built-in rate limiting to prevent abuse
- 🛡️ **Input Validation**: Comprehensive input validation and sanitization
- 📝 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 📚 **Auto Documentation**: Automatic API documentation with Swagger/OpenAPI
- 🏗️ **Clean Architecture**: Proper Python package structure following best practices

## Quick Start

### Prerequisites

- Python 3.13+
- Groq API key

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd postgenius
```

2. Install dependencies:

```bash
uv sync
```

3. Set up environment variables:

```bash
# Create a .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

4. Run the application:

```bash
# Using uvicorn directly with new package structure
uv run uvicorn app.main:app --reload

# Using the entry point script
uv run python run.py



5. Open your browser and navigate to:
   - **Web Interface**: <http://localhost:8000>
   - **API Documentation**: <http://localhost:8000/docs>
   - **Alternative API Docs**: <http://localhost:8000/redoc>

## Platform Support

The application supports generating content optimized for different social media platforms:

### 🐦 **Twitter/X Posts**

- **Character limit**: Under 280 characters ideally
- **Style**: Conversational, engaging, with strategic use of emojis
- **Focus**: Quick engagement, retweets, and discussions

### 💼 **LinkedIn Posts**

- **Length**: 150-300 words for optimal engagement
- **Style**: Professional, thought leadership content
- **Focus**: Business insights, career advice, networking

### Platform Selection

- **Web Interface**: Use the dropdown to select your target platform
- **API**: Include `"platform": "twitter"` or `"platform": "linkedin"` in your request
- **Default**: Twitter/X if no platform is specified

## API Endpoints

### Web Interface

- `GET /` - Home page with application overview
- `GET /generate-post` - Post generation form with platform selection
- `POST /generate-post` - Handle form submission with platform support

### REST API

- `GET /health` - Health check endpoint
- `POST /api/generate-post` - Generate social media post

### API Usage Examples

**Twitter/X Post Generation:**

```bash
curl -X POST "http://localhost:8000/api/generate-post" \
     -H "Content-Type: application/json" \
     -d '{"topic": "The benefits of morning exercise", "platform": "twitter"}'
```

**LinkedIn Post Generation:**

```bash
curl -X POST "http://localhost:8000/api/generate-post" \
     -H "Content-Type: application/json" \
     -d '{"topic": "The benefits of morning exercise", "platform": "linkedin"}'
```

**Response:**

```json
{
  "success": true,
  "generated_post": "🌅 Starting your day with exercise isn't just about fitness—it's about setting the tone for everything that follows...",
  "error_message": null,
  "processing_time": 2.34,
  "platform": "twitter"
}
```

## Configuration

### Environment Variables

- `GROQ_API_KEY` - Your Groq API key (required)

### Rate Limiting

- **Requests**: 10 requests per 60 seconds per IP
- **Note**: In production, use Redis or a dedicated rate limiting service

## Development

### Project Structure

```text
postgenius/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app and route handlers
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py    # Request models and enums
│   │   └── responses.py   # Response models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   └── post_generator.py # Post generation service
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   └── rate_limiter.py # Rate limiting utilities
│   └── config/            # Configuration
│       ├── __init__.py
│       └── settings.py    # Environment variables and constants
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── generate_post.html # Post generation page
├── static/               # Static files (CSS, JS)
├── tests/                # Test package
│   ├── __init__.py
│   └── test_api.py       # API tests
├── run.py                # Entry point script
├── pyproject.toml        # Project dependencies and configuration
└── README.md             # This file
```

**Package Organization:**

- **`app/`** - Main application package with proper separation of concerns
- **`app/models/`** - Pydantic models for request/response validation
- **`app/services/`** - Business logic and external API integrations
- **`app/utils/`** - Utility functions and helpers
- **`app/config/`** - Configuration management and environment variables
- **`tests/`** - Test package with organized test modules

### Architecture Benefits

The refactored package structure provides:

- **🏗️ Separation of Concerns**: Each module has a single, well-defined responsibility
- **🔧 Maintainability**: Code is organized logically and easy to navigate
- **🧪 Testability**: Components can be tested in isolation
- **📈 Scalability**: Easy to add new features in appropriate modules
- **📚 Best Practices**: Follows Python PEP 8 and package organization standards
- **🔄 Clean Imports**: No circular dependencies or messy import structures

### Running Tests

```bash
# Start the server first (using new package structure)
uv run uvicorn app.main:app --reload

# In another terminal, run tests
uv run python tests/test_api.py

# Or run tests directly
cd tests && uv run python test_api.py
```

## Production Deployment

### Security Considerations

1. **Environment Variables**: Store sensitive data in environment variables
2. **Rate Limiting**: Implement proper rate limiting with Redis
3. **HTTPS**: Use HTTPS in production
4. **API Key Security**: Rotate API keys regularly
5. **Input Validation**: All inputs are validated and sanitized

### Performance Optimizations

1. **Async Operations**: All API calls are asynchronous
2. **Connection Pooling**: HTTP client uses connection pooling
3. **Timeout Handling**: Proper timeout configuration
4. **Error Handling**: Comprehensive error handling and logging

## API Documentation

The application automatically generates comprehensive API documentation:

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

## Error Handling

The application includes comprehensive error handling:

- **Input Validation**: Pydantic models validate all inputs
- **Rate Limiting**: 429 status code for rate limit exceeded
- **API Errors**: Proper HTTP status codes and error messages
- **Logging**: All errors are logged with appropriate levels

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
