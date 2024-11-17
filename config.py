import os


class Config:
    # Pyrogram Configuration
    API_ID = int(os.getenv("API_ID", "123456"))  # Replace with your API ID
    API_HASH = os.getenv("API_HASH", "your_api_hash")  # Replace with your API Hash
    SESSION_STRING = os.getenv("SESSION_STRING", "your_session_string")  # Replace with your Session String

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Replace with your MongoDB URI

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Replace with your Redis URL

    # Throwbin API Key
    THROWBIN_API_KEY = os.getenv("THROWBIN_API_KEY", "your_throwbin_api_key")  # Replace with your Throwbin API Key
