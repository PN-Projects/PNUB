"""
Plugin Description: Display available plugins and their descriptions.
Commands:
- .help: Lists all plugins with descriptions.
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import importlib
import os

PLUGIN_DIR = "plugins"
PLUGINS = {}

def load_plugins():
    """Dynamically load plugins from the plugins directory."""
    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and file != "__init__.py":
            plugin_name = file[:-3]
            module = importlib.import_module(f"{PLUGIN_DIR}.{plugin_name}")
            PLUGINS[plugin_name] = {
                "module": module,
                "doc": module.__doc__.strip() if module.__doc__ else "No description available."
            }

@Client.on_message(filters.command("help") & filters.me)
async def help_handler(client, message):
    """List available plugins and descriptions."""
    buttons = [
        [InlineKeyboardButton(plugin, callback_data=plugin)] for plugin in PLUGINS.keys()
    ]
    await message.reply_text(
        "Available plugins (click to view details):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query()
async def help_callback(client, callback_query):
    """Provide detailed information for a selected plugin."""
    plugin_name = callback_query.data
    plugin_info = PLUGINS.get(plugin_name, None)

    if plugin_info:
        doc = plugin_info["doc"]
        await callback_query.message.edit_text(f"**{plugin_name.capitalize()} Plugin**\n\n{doc}")
    else:
        await callback_query.message.edit_text("Plugin not found.")

# Load plugins on bot startup
load_plugins()
