"""
Plugin Description: Display available plugins and their descriptions.
Commands:
- .help: Lists all plugins with descriptions.
"""

from pyrogram import Client, filters
from plugins import PLUGINS  # Import the shared PLUGINS dictionary

@Client.on_message(filters.command("help") & filters.me)
async def help_handler(client, message):
    """
    Display a list of all loaded plugins with descriptions in an ordered list.
    """
    if not PLUGINS:
        await message.reply_text("No plugins are currently available.")
        return

    # Build an ordered list of plugins and their descriptions
    plugin_list = "\n".join(
        [f"\n{index + 1}. **{plugin.capitalize()}**: \n{plugin_info['doc']}" for index, (plugin, plugin_info) in enumerate(PLUGINS.items())]
    )

    # Send the list of plugins with descriptions
    await message.reply_text(
        f"Here are all the available plugins:\n\n{plugin_list}"
    )
    
