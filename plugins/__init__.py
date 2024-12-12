"""
Initialize plugins by dynamically importing all Python files in the plugins folder.
This file is responsible for managing the plugin metadata (name and descriptions).
"""

import os
import importlib

PLUGIN_DIR = os.path.dirname(__file__)
PLUGINS = {}

def load_plugins():
    """
    Dynamically load plugins from the plugins directory.
    Extract plugin descriptions from their docstrings.
    """
    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and file != "__init__.py":
            plugin_name = file[:-3]  # Remove the .py extension
            try:
                module = importlib.import_module(f"plugins.{plugin_name}")
                PLUGINS[plugin_name] = {
                    "module": module,
                    "doc": module.__doc__.strip() if module.__doc__ else "No description available."
                }
            except Exception as e:
                print(f"Error loading plugin {plugin_name}: {e}")

# Load plugins on import
load_plugins()

