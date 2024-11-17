"""
Plugin Description: Paste text to Throwbin.in and get a shareable link.
Commands:
- .throw: Replied text or caption from a file/image is pasted to Throwbin.in, generating a shareable link.
"""

import requests
import redis
from pymongo import MongoClient
from pyrogram import Client, filters
from config import Config

# MongoDB and Redis setup
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
throw_logs_collection = db["throw_logs"]

THROWBIN_API_URL = "https://throwbin.in/api/create"
THROWBIN_API_KEY = Config.throwbin_api_key

@Client.on_message(filters.command("throw") & filters.me & (filters.reply | filters.text))
async def throw_handler(client, message):
    # Extract text from the message or reply
    if message.reply_to_message:
        if message.reply_to_message.text:
            content = message.reply_to_message.text
        elif message.reply_to_message.caption:
            content = message.reply_to_message.caption
        else:
            await message.reply_text("Error: Replied message contains no text or caption.")
            return
    elif message.text:
        content = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
        if not content:
            await message.reply_text("Error: No text provided.")
            return
    else:
        await message.reply_text("Error: No text or reply found.")
        return

    # Check Redis cache for existing paste
    cache_key = f"throw_paste:{content}"
    cached_link = redis_client.get(cache_key)
    if cached_link:
        await message.reply_text(f"**Cached Link:** {cached_link.decode()}")
        return

    try:
        # API call to Throwbin
        response = requests.post(
            THROWBIN_API_URL,
            data={
                "api_key": THROWBIN_API_KEY,
                "content": content
            }
        )
        response_data = response.json()

        if response_data.get("success"):
            paste_url = f"https://throwbin.in/{response_data['url']}"

            # Cache the link in Redis for 1 day
            redis_client.set(cache_key, paste_url, ex=86400)

            # Log the paste in MongoDB
            throw_logs_collection.insert_one({
                "user_id": message.from_user.id,
                "username": message.from_user.username,
                "content": content,
                "paste_url": paste_url,
                "chat_id": message.chat.id,
                "timestamp": message.date,
                "status": "success"
            })

            # Reply with the generated link
            await message.reply_text(f"**Your Paste Link:** {paste_url}")
        else:
            raise Exception("Failed to generate paste link. API did not return success.")

    except Exception as e:
        # Log the failure in MongoDB
        throw_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "content": content,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": f"failed: {e}"
        })
        await message.reply_text(f"Error: {e}")
