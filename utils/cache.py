"""
Utility for Redis operations.
"""

from . import redis_client

class Cache:
    def set(self, key, value, ex=None):
        """Set a value in Redis with an optional expiration time."""
        redis_client.set(key, value, ex=ex)

    def get(self, key):
        """Get a value from Redis."""
        return redis_client.get(key)

    def delete(self, key):
        """Delete a key from Redis."""
        redis_client.delete(key)

    def exists(self, key):
        """Check if a key exists in Redis."""
        return redis_client.exists(key)
        
