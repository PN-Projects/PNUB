"""
Plugin Description: Execute Python code dynamically and log results.
Commands:
- .eval <code>: Executes the given Python code and returns the result.
"""

from pyrogram import Client, filters
import redis
from pymongo import MongoClient
from io import StringIO
import sys

# MongoDB and Redis setup
from config import Config

redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
eval_logs_collection = db["eval_logs"]

@Client.on_message(filters.command("eval") & filters.me)
async def eval_handler(client, message):
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await message.reply_text("Usage: .eval <Python code>")
        return

    code = command_parts[1]

    # Check Redis cache for the result
    cache_key = f"eval_result:{code}"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        await message.reply_text(f"**Cached Result:**\n{cached_result.decode()}")
        return

    # Evaluate the code
    stdout = StringIO()
    stderr = StringIO()
    result = None

    try:
        # Redirect stdout and stderr to capture prints and errors
        sys.stdout = stdout
        sys.stderr = stderr
        result = eval(code)
        if result is not None:
            print(result)
    except Exception as e:
        result = f"Error: {e}"
    finally:
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Collect output and errors
    output = stdout.getvalue().strip() + "\n" + stderr.getvalue().strip()

    # Cache result in Redis for 1 hour
    redis_client.set(cache_key, output, ex=3600)

    # Log result in MongoDB
    eval_logs_collection.insert_one({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "code": code,
        "result": output,
        "chat_id": message.chat.id,
        "timestamp": message.date
    })

    # Reply with the result
    await message.reply_text(f"**Result:**\n{output or result}")
