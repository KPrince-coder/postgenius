"""
Entry point for the FastAPI Social Media Post Generator application.

This module imports and exposes the FastAPI app instance for uvicorn to run.
"""

from app.main import app

# Export the app instance for uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
