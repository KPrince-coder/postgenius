# Social Media Post Generator

AI-powered social media post generation using FastAPI, Jinja2, and Groq's API.

## Features

- 🤖 **AI-Powered Generation**: Uses Groq's fast LLaMA models to create engaging social media posts
- 🌐 **Web Interface**: Clean, responsive web interface for easy post generation
- 🔌 **REST API**: Full REST API with comprehensive documentation
- 📊 **Rate Limiting**: Built-in rate limiting to prevent abuse
- 🛡️ **Input Validation**: Comprehensive input validation and sanitization
- 📝 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 📚 **Auto Documentation**: Automatic API documentation with Swagger/OpenAPI

## Quick Start

### Prerequisites

- Python 3.13+
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi_jinja2_try
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
# Create a .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

4. Run the application:
```bash
uvicorn main:app --reload
```

5. Open your browser and navigate to:
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc

## API Endpoints

### Web Interface

- `GET /` - Home page with application overview
- `GET /generate-post` - Post generation form
- `POST /generate-post` - Handle form submission

### REST API

- `GET /health` - Health check endpoint
- `POST /api/generate-post` - Generate social media post

### API Usage Example

```bash
curl -X POST "http://localhost:8000/api/generate-post" \
     -H "Content-Type: application/json" \
     -d '{"topic": "The benefits of morning exercise"}'
```

Response:
```json
{
  "success": true,
  "generated_post": "🌅 Starting your day with exercise isn't just about fitness—it's about setting the tone for everything that follows...",
  "error_message": null,
  "processing_time": 2.34
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

```
├── main.py              # Main FastAPI application
├── templates/           # Jinja2 templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   └── generate_post.html # Post generation page
├── static/             # Static files (CSS, JS)
├── test_api.py         # API tests
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

### Running Tests

```bash
# Start the server first
uvicorn main:app --reload

# In another terminal, run tests
python test_api.py
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