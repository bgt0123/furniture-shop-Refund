import redis
import json
from typing import Optional, Any


class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        self.redis_client = redis.Redis.from_url(redis_url)
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        cached_data = self.redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    def set(self, key: str, value: Any) -> bool:
        """Set cache value with key"""
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, self.ttl, serialized_value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete cached value by key"""
        return self.redis_client.delete(key) > 0

    def clear(self, pattern: str = "*") -> int:
        """Clear cache by pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            return self.redis_client.delete(*keys)
        return 0


# Global cache instance
cache = RedisCache()
