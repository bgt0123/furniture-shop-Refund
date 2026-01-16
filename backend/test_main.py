"""Simple test to verify backend setup."""

import uvicorn
from src.main import app


def test_app():
    """Test that the app can be created."""
    assert app.title == "Furniture Shop Refund Microservice"
    assert app.description == "Customer support and refund processing system"


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
