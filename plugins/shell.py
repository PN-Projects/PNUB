"""
Plugin Description: Execute shell commands and log results.
Commands:
- .sh <command>: Executes the given shell command and returns the output.
"""

import subprocess
import redis
from pymongo import MongoClient
from pyrogram import Client, filters
from config import Config

# MongoDB and Redis setup
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
sh_logs_collection = db["sh_logs"]

@Client.on_message(filters.command("sh") & filters.me)
async def sh_handler(client, message):
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await message.reply_text("Usage: .sh <command>")
        return

    command = command_parts[1]

    # Check Redis cache for the result
    cache_key = f"sh_result:{command}"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        await message.reply_text(f"**Cached Result:**\n{cached_result.decode()}")
        return

    try:
        # Execute the shell command
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        result = f"Error:\n{e.output}"

    # Cache the result in Redis for 1 hour
    redis_client.set(cache_key, result, ex=3600)

    # Log the command and result in MongoDB
    sh_logs_collection.insert_one({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "command": command,
        "result": result,
        "chat_id": message.chat.id,
        "timestamp": message.date
    })

    # Reply with the result
    await message.reply_text(f"**Result:**\n{result}")
