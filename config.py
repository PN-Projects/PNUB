import os
from dotenv import load_dotenv

class Config:
    # Check if the .env file exists and load it
    try:
        if os.path.exists(".env"):
            load_dotenv()
        else:
            raise FileNotFoundError(".env file is missing.")
    except FileNotFoundError as e:
        print(e)

    # Pyrogram Configuration
    API_ID = int(os.getenv("API_ID", "123456"))  # Default to 123456 if not set
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    SESSION_STRING = os.getenv("SESSION_STRING", "your_session_string")

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASS = os.getenv("REDIS_PASS", "NON")

    # Throwbin API Key
    # THROWBIN_API_KEY = os.getenv("THROWBIN_API_KEY", "your_throwbin_api_key")
    
