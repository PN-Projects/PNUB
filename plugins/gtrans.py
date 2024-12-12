"""
Plugin Description: Translate replied text into a specified language.
Commands:
- .translate <language_code>: Translates the replied text into the specified language.
"""

from pyrogram import Client, filters
from googletrans import Translator
from utils import redis_client  # Import centralized Redis connection

# Supported Indian languages (ISO 639-1 codes)
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "gu": "Gujarati",
    "bn": "Bengali",
    "mr": "Marathi",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "en": "English"
}

translator = Translator()

@Client.on_message(filters.command("translate") & filters.me & filters.reply)
async def translate_handler(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text(
            "Usage: .translate <language_code>\n"
            "Supported languages:\n" +
            "\n".join([f"{code}: {lang}" for code, lang in SUPPORTED_LANGUAGES.items()])
        )
        return

    language_code = args[1].strip()
    if language_code not in SUPPORTED_LANGUAGES:
        await message.reply_text(
            f"Unsupported language code: {language_code}\n"
            f"Supported languages:\n" +
            "\n".join([f"{code}: {lang}" for code, lang in SUPPORTED_LANGUAGES.items()])
        )
        return

    # Handle replied text
    reply = message.reply_to_message
    text_to_translate = reply.text or reply.caption

    if not text_to_translate:
        await message.reply_text("No text found in the replied message.")
        return

    cache_key = f"translate:{text_to_translate}:{language_code}"
    cached_translation = redis_client.get(cache_key)
    if cached_translation:
        await message.reply_text(f"**Cached Translation ({SUPPORTED_LANGUAGES[language_code]}):**\n{cached_translation.decode()}")
        return

    try:
        # Perform translation
        translated = translator.translate(text_to_translate, dest=language_code)
        translated_text = translated.text

        # Cache translation result in Redis for 1 day
        redis_client.set(cache_key, translated_text, ex=86400)  # Cache for 1 day

        # Reply with the translated text
        await message.reply_text(f"**Translated Text ({SUPPORTED_LANGUAGES[language_code]}):**\n{translated_text}")

    except Exception as e:
        await message.reply_text(f"Error during translation: {e}")
            
