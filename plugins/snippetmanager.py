"""
Plugin Description: Manage code snippets using MongoDB with Redis caching.
Commands:
- .savesnippet <title>: Save the replied code snippet with a title.
- .getsnippet <title>: Retrieve the code snippet by title.
- .listsnippets: List all saved code snippet titles.
- .deletesnippet <title>: Delete a saved code snippet by title.
"""

from pyrogram import Client, filters
from config import Config
from utils.db import Database  # Using the Database utility
from utils.cache import Cache  # Using the Cache utility

# MongoDB and Redis setup via Database and Cache utility
db = Database()
cache = Cache()

@Client.on_message(filters.command("savesnippet") & filters.me & filters.reply)
async def save_snippet(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .savesnippet <title>")
        return

    title = args[1].strip()
    code = message.reply_to_message.text or message.reply_to_message.caption

    if not code:
        await message.reply_text("No code found in the replied message.")
        return

    # Save snippet to MongoDB
    db.update_document(
        collection_name="snippets",
        query={"title": title, "user_id": message.from_user.id},
        update_data={"code": code, "chat_id": message.chat.id, "timestamp": message.date},
        upsert=True
    )

    # Clear the cache for the title in case it exists
    cache.delete(f"snippet:{message.from_user.id}:{title}")

    await message.reply_text(f"Snippet '{title}' has been saved successfully.")

@Client.on_message(filters.command("getsnippet") & filters.me)
async def get_snippet(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .getsnippet <title>")
        return

    title = args[1].strip()
    cache_key = f"snippet:{message.from_user.id}:{title}"

    # Check Redis cache for the snippet
    cached_snippet = cache.get(cache_key)
    if cached_snippet:
        await message.reply_text(f"**Snippet '{title}':**\n\n{cached_snippet.decode()}")
        return

    # If not found in cache, query MongoDB
    snippet = db.find_document(collection_name="snippets", query={"title": title, "user_id": message.from_user.id})

    if not snippet:
        await message.reply_text(f"No snippet found with the title '{title}'.")
        return

    # Cache the snippet in Redis
    cache.set(cache_key, snippet["code"], ex=86400)  # Cache for 1 day

    await message.reply_text(f"**Snippet '{title}':**\n\n{snippet['code']}")

@Client.on_message(filters.command("listsnippets") & filters.me)
async def list_snippets(client, message):
    # Retrieve snippet titles from MongoDB
    snippets = db.get_collection("snippets").find({"user_id": message.from_user.id})
    titles = [snippet["title"] for snippet in snippets]

    if not titles:
        await message.reply_text("No snippets saved yet.")
        return

    await message.reply_text("**Saved Snippets:**\n" + "\n".join(f"- {title}" for title in titles))

@Client.on_message(filters.command("deletesnippet") & filters.me)
async def delete_snippet(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .deletesnippet <title>")
        return

    title = args[1].strip()

    # Delete snippet from MongoDB
    result = db.get_collection("snippets").delete_one({"title": title, "user_id": message.from_user.id})

    if result.deleted_count == 0:
        await message.reply_text(f"No snippet found with the title '{title}'.")
    else:
        # Clear the cache for the deleted snippet
        cache.delete(f"snippet:{message.from_user.id}:{title}")
        await message.reply_text(f"Snippet '{title}' has been deleted.")
    
