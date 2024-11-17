"""
Plugin Description: Translate replied text into a specified language.
Commands:
- .translate <language_code>: Translates the replied text into the specified language.
"""

from pyrogram import Client, filters
import redis
from pymongo import MongoClient
from googletrans import Translator
from config import Config

# MongoDB and Redis setup
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
translate_logs_collection = db["translate_logs"]

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

        # Cache translation result in Redis
        redis_client.set(cache_key, translated_text, ex=86400)  # Cache for 1 day

        # Log translation request and result in MongoDB
        translate_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "original_text": text_to_translate,
            "translated_text": translated_text,
            "source_language": translated.src,
            "target_language": language_code,
            "chat_id": message.chat.id,
            "timestamp": message.date
        })

        # Reply with the translated text
        await message.reply_text(f"**Translated Text ({SUPPORTED_LANGUAGES[language_code]}):**\n{translated_text}")

    except Exception as e:
        # Log the failure in MongoDB
        translate_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "original_text": text_to_translate,
            "target_language": language_code,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": f"failed: {e}"
        })
        await message.reply_text(f"Error during translation: {e}")
