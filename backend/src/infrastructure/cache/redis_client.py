"""Redis client configuration."""

import redis.asyncio as redis
import json
from typing import Any, Optional
from src.infrastructure.config.config import settings


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )

    async def set(
        self, key: str, value: Any, expire_seconds: Optional[int] = None
    ) -> bool:
        """Set a value with optional expiration."""
        serialized_value = json.dumps(value)
        if expire_seconds:
            return bool(await self.client.setex(key, expire_seconds, serialized_value))
        else:
            return bool(await self.client.set(key, serialized_value))

    async def get(self, key: str) -> Optional[Any]:
        """Get a value."""
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def delete(self, key: str) -> bool:
        """Delete a key."""
        return bool(await self.client.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.client.exists(key))

    async def expire(self, key: str, expire_seconds: int) -> bool:
        """Set expiration for a key."""
        return bool(await self.client.expire(key, expire_seconds))

    async def incr(self, key: str) -> int:
        """Increment a counter."""
        return await self.client.incr(key)

    async def get_keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern."""
        return await self.client.keys(pattern)

    async def flush_db(self) -> bool:
        """Flush the database."""
        return bool(await self.client.flushdb())


# Global Redis client instance
redis_client = RedisClient()
