"""
Plugin Description: Display available plugins and their descriptions.
Commands:
- .help: Lists all plugins with descriptions.
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins import PLUGINS  # Import the shared PLUGINS dictionary

@Client.on_message(filters.command("help") & filters.me)
async def help_handler(client, message):
    """
    Display a list of all loaded plugins with descriptions.
    Users can click on a plugin name to view its detailed description.
    """
    if not PLUGINS:
        await message.reply_text("No plugins are currently available.")
        return

    # Generate buttons for each plugin
    buttons = [
        [InlineKeyboardButton(plugin.capitalize(), callback_data=f"help:{plugin}")] for plugin in sorted(PLUGINS.keys())
    ]
    await message.reply_text(
        "Available plugins (click a plugin for details):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex(r"^help:(.+)"))
async def plugin_details(client, callback_query):
    """
    Display detailed information about a specific plugin.
    """
    plugin_name = callback_query.data.split(":")[1]
    plugin_info = PLUGINS.get(plugin_name)

    if plugin_info:
        doc = plugin_info["doc"]
        await callback_query.message.edit_text(
            f"**{plugin_name.capitalize()} Plugin**\n\n{doc}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="help:back")]]
            )
        )
    else:
        await callback_query.message.edit_text("Plugin not found.")


@Client.on_callback_query(filters.regex(r"^help:back"))
async def back_to_help_menu(client, callback_query):
    """
    Navigate back to the main help menu from plugin details.
    """
    buttons = [
        [InlineKeyboardButton(plugin.capitalize(), callback_data=f"help:{plugin}")] for plugin in sorted(PLUGINS.keys())
    ]
    await callback_query.message.edit_text(
        "Available plugins (click a plugin for details):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
