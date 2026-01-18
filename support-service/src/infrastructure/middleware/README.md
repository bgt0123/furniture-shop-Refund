# Support Service Middleware

## Components

- `auth.py` - Authentication middleware and role-based access control
- `error_handler.py` - Global error handling middleware
- `__init__.py` - Module exports

## Usage

```python
from support_service.src.infrastructure.middleware import error_handler, get_current_user

# Use in FastAPI
app.middleware("http")(error_handler)

# Protect routes with authentication
@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["user_id"]}
```