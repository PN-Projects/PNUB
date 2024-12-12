"""
Plugin Description: Execute shell commands and log results.
Commands:
- .sh <command>: Executes the given shell command and returns the output.
"""

import subprocess
from pyrogram import Client, filters
from config import Config
from utils.cache import Cache  # Using the Cache utility

# Redis caching utility
cache = Cache()

@Client.on_message(filters.command("sh") & filters.me)
async def sh_handler(client, message):
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await message.reply_text("Usage: .sh <command>")
        return

    command = command_parts[1]

    # Check Redis cache for the result
    cache_key = f"sh_result:{command}"
    cached_result = cache.get(cache_key)
    if cached_result:
        await message.reply_text(f"**Cached Result:**\n{cached_result.decode()}")
        return

    try:
        # Execute the shell command
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        result = f"Error:\n{e.output}"

    # Cache the result in Redis for 1 hour
    cache.set(cache_key, result, ex=3600)

    # Reply with the result
    await message.reply_text(f"**Result:**\n{result}")
    
