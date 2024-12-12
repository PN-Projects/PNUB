"""
Plugin Description: Download ZIP file of public GitHub repositories.
Commands:
- .ghdown <repository_url>: Downloads the ZIP file of the given public GitHub repository.
"""
import asyncio
import requests
from pyrogram import Client, filters
import os
import uuid
from utils import redis_client, mongo_db  # Import centralized connections

# MongoDB collection for GitHub logs
gh_logs_collection = mongo_db["gh_logs"]

@Client.on_message(filters.command("ghdown") & filters.me)
async def ghdown_handler(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .ghdown <repository_url>\nExample: .ghdown https://github.com/username/repository")
        return

    repo_url = args[1].strip()
    if not repo_url.startswith("https://github.com/"):
        await message.reply_text("Error: Invalid GitHub repository URL.")
        return

    # Extract repository details
    try:
        _, username, repository = repo_url.rstrip("/").split("/")[:3]
    except ValueError:
        await message.reply_text("Error: Unable to parse repository URL.")
        return

    cache_key = f"gh_repo_zip:{username}/{repository}"
    cached_zip = redis_client.get(cache_key)
    temp_zip_path = f"./temp_{uuid.uuid4().hex}.zip"

    if cached_zip:
        # Serve from cache
        with open(temp_zip_path, "wb") as f:
            f.write(cached_zip)
        await client.send_document(
            chat_id=message.chat.id,
            document=temp_zip_path,
            caption=f"Here is the cached ZIP file for the repository: {repo_url}"
        )
        os.remove(temp_zip_path)
        return

    # Construct the GitHub ZIP URL
    zip_url = f"https://github.com/{username}/{repository}/archive/refs/heads/main.zip"

    try:
        # Download the ZIP file
        await message.reply_text("Downloading repository ZIP file...")
        response = requests.get(zip_url, stream=True)

        if response.status_code != 200:
            await message.reply_text(f"Error: Unable to download the repository. HTTP Status: {response.status_code}")
            return

        with open(temp_zip_path, "wb") as zip_file:
            for chunk in response.iter_content(chunk_size=1024):
                zip_file.write(chunk)

        # Cache the ZIP content in Redis for 1 day
        with open(temp_zip_path, "rb") as zip_file:
            redis_client.set(cache_key, zip_file.read(), ex=86400)

        # Log the download in MongoDB
        gh_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "repository_url": repo_url,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": "success"
        })

        # Send the ZIP file to Telegram
        await client.send_document(
            chat_id=message.chat.id,
            document=temp_zip_path,
            caption=f"Here is the ZIP file for the repository: {repo_url}"
        )

    except Exception as e:
        # Log the failure in MongoDB
        gh_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "repository_url": repo_url,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": f"failed: {e}"
        })
        await message.reply_text(f"Error: {e}")

    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        
