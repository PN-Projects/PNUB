"""
Plugin Description: Generate stylish code snippet images using the Carbon API.
Commands:
- .carbon <code>: Generates a Carbon image of the given code.
"""

import requests
import redis
from pymongo import MongoClient
from pyrogram import Client, filters
from config import Config
import uuid
import os

# MongoDB and Redis setup
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
carbon_logs_collection = db["carbon_logs"]

CARBON_API_URL = "https://carbonara.solopov.dev/api/cook"

@Client.on_message(filters.command("carbon") & filters.me)
async def carbon_handler(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .carbon <code>")
        return

    code_snippet = args[1].strip()
    cache_key = f"carbon_image:{code_snippet}"

    # Check Redis cache for the generated image
    cached_image = redis_client.get(cache_key)
    temp_image_path = f"./temp_{uuid.uuid4().hex}.png"

    if cached_image:
        # Serve from cache
        with open(temp_image_path, "wb") as f:
            f.write(cached_image)
        await client.send_photo(
            chat_id=message.chat.id,
            photo=temp_image_path,
            caption="Here is your cached Carbon image."
        )
        os.remove(temp_image_path)
        return

    try:
        # Call the Carbon API to generate the image
        response = requests.post(CARBON_API_URL, json={"code": code_snippet})

        if response.status_code != 200:
            await message.reply_text(f"Error: Failed to generate Carbon image.\nHTTP Status: {response.status_code}")
            return

        # Save the image temporarily
        with open(temp_image_path, "wb") as f:
            f.write(response.content)

        # Cache the image in Redis for 1 day
        redis_client.set(cache_key, response.content, ex=86400)

        # Log the Carbon request in MongoDB
        carbon_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "code_snippet": code_snippet,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": "success"
        })

        # Send the generated image
        await client.send_photo(
            chat_id=message.chat.id,
            photo=temp_image_path,
            caption="Here is your Carbon image."
        )

    except Exception as e:
        # Log the failure in MongoDB
        carbon_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "code_snippet": code_snippet,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": f"failed: {e}"
        })
        await message.reply_text(f"Error: {e}")

    finally:
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
