"""
Plugin Description: Carbonize code using carbon-now CLI tool and send the image to the user.
Commands:
- .carbon <flags>: Generates a carbonized image of the code and sends it back. 
  Example: .carbon --theme dracula --start 3 --end 6
"""

import os
import asyncio
from pyrogram import Client, filters
from utils.cache import Cache

cache = Cache()

async def run_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(), stderr.decode(), proc.returncode

@Client.on_message(filters.command("carbon") & filters.me)
async def carbon_handler(client, message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.reply_text("Usage: `.carbon <flags>`\nExample: `.carbon --theme dracula --start 3 --end 6`")
        return

    flags = command_parts[1].strip()
    if not flags.startswith("--"):
        await message.reply_text("Invalid flags. Ensure they start with `--`.")
        return

    if message.reply_to_message and message.reply_to_message.document:
        file_path = await message.reply_to_message.download()
    elif message.reply_to_message and message.reply_to_message.text:
        file_path = f"/tmp/carbon_code_{message.message_id}.txt"
        with open(file_path, "w") as f:
            f.write(message.reply_to_message.text)
    else:
        await message.reply_text("Reply to a code file or text message containing the code.")
        return

    cache_key = f"carbonize:{message.chat.id}:{message.message_id}"
    cache.set(cache_key, file_path, ex=3600)

    try:
        cmd = f"carbon-now {file_path} {flags}"
        stdout, stderr, returncode = await run_command(cmd)

        if returncode != 0:
            raise RuntimeError(f"Error running carbon-now-cli: {stderr}")

        carbon_image = "/tmp/carbon_output.png"
        if not os.path.exists(carbon_image):
            raise FileNotFoundError("The carbonized image could not be generated.")

        await message.reply_photo(carbon_image, caption=f"Here is your carbonized code with flags: `{flags}`")
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

    finally:
        # Proper cleanup: Remove both the original code file and the generated carbon image
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if os.path.exists("/tmp/carbon_output.png"):
            os.remove("/tmp/carbon_output.png")

        # Clean up the cache
        if cache.exists(cache_key):
            cache.delete(cache_key)

