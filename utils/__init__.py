"""
Initialize database and caching connections.
"""

from pymongo import MongoClient
import redis
from config import Config

# MongoDB connection
mongo_client = MongoClient(Config.MONGO_URI)
mongo_db = mongo_client["telegram_userbot"]

# Redis connection
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
