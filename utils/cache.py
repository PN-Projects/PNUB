"""
Utility for Redis operations.
"""

import redis
from config import Config

class Cache:
    def __init__(self):
        self.client = redis.StrictRedis.from_url(Config.REDIS_URL)

    def set(self, key, value, ex=None):
        """Set a value in Redis with an optional expiration time."""
        self.client.set(key, value, ex=ex)

    def get(self, key):
        """Get a value from Redis."""
        return self.client.get(key)

    def delete(self, key):
        """Delete a key from Redis."""
        self.client.delete(key)

    def exists(self, key):
        """Check if a key exists in Redis."""
        return self.client.exists(key)
