"""
Plugin Description: Manage code snippets using MongoDB.
Commands:
- .savesnippet <title>: Save the replied code snippet with a title.
- .getsnippet <title>: Retrieve the code snippet by title.
- .listsnippets: List all saved code snippet titles.
- .deletesnippet <title>: Delete a saved code snippet by title.
"""

from pyrogram import Client, filters
from pymongo import MongoClient
from config import Config

# MongoDB setup
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
snippets_collection = db["snippets"]

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
    snippets_collection.update_one(
        {"title": title, "user_id": message.from_user.id},
        {"$set": {"code": code, "chat_id": message.chat.id, "timestamp": message.date}},
        upsert=True
    )
    await message.reply_text(f"Snippet '{title}' has been saved successfully.")

@Client.on_message(filters.command("getsnippet") & filters.me)
async def get_snippet(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .getsnippet <title>")
        return

    title = args[1].strip()
    snippet = snippets_collection.find_one({"title": title, "user_id": message.from_user.id})

    if not snippet:
        await message.reply_text(f"No snippet found with the title '{title}'.")
        return

    await message.reply_text(f"**Snippet '{title}':**\n\n{snippet['code']}")

@Client.on_message(filters.command("listsnippets") & filters.me)
async def list_snippets(client, message):
    snippets = snippets_collection.find({"user_id": message.from_user.id})
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
    result = snippets_collection.delete_one({"title": title, "user_id": message.from_user.id})

    if result.deleted_count == 0:
        await message.reply_text(f"No snippet found with the title '{title}'.")
    else:
        await message.reply_text(f"Snippet '{title}' has been deleted.")

