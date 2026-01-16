from setuptools import setup, find_packages

setup(
    name="furniture-shop-refund-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.4.0",
        "pydantic-settings>=2.0.0",
        "sqlalchemy>=2.0.0",
        "python-multipart>=0.0.6",
        "PyJWT>=2.10.0",
        "passlib[bcrypt]>=1.7.4",
        "redis>=5.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "email-validator>=2.1.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "httpx>=0.25.0",
        "alembic>=1.12.0",
        "greenlet>=3.0.0",
    ],
)
