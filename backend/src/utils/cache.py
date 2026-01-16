import redis


class Cache:
    """Redis cache wrapper."""

    def __init__(self):
        self.client = redis.Redis.from_url("redis://localhost:6379/0")

    def get(self, key: str):
        """Get value from cache."""
        return self.client.get(key)

    def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache."""
        self.client.set(key, value, ex=expire)

    def delete(self, key: str):
        """Delete value from cache."""
        self.client.delete(key)


cache = Cache()
