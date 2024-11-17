import os
from pyrogram import Client
from plugins.help import load_plugins

# Load configuration from config.py or environment variables
from config import Config

# Initialize the Pyrogram Client for the user account
userbot = Client(
    "userbot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING,  # Using a session string for user accounts
    plugins=dict(root="plugins")
)

# Load all plugins dynamically
load_plugins()

# Start the userbot
if __name__ == "__main__":
    print("Starting the userbot...")
    userbot.run()
