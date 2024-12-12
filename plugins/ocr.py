"""
Plugin Description: Extract text from images using Tesseract OCR.
Commands:
- .ocr: Extracts text from the replied image.
"""

import pytesseract
from PIL import Image
from pyrogram import Client, filters
import redis
import os
from config import Config
from utils.cache import Cache  # Using the Cache utility

# Redis caching utility
cache = Cache()

# Path to Tesseract (update this path if needed)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

@Client.on_message(filters.command("ocr") & filters.me & filters.reply)
async def ocr_handler(client, message):
    # Ensure the replied message contains an image
    if not message.reply_to_message.photo and not message.reply_to_message.document:
        await message.reply_text("Please reply to an image or document to extract text.")
        return

    # Download the image or document
    file_path = await message.reply_to_message.download()
    cache_key = f"ocr_result:{file_path}"

    # Check Redis cache for the OCR result
    cached_result = cache.get(cache_key)
    if cached_result:
        await message.reply_text(f"**Cached OCR Result:**\n{cached_result.decode()}")
        os.remove(file_path)  # Clean up downloaded file
        return

    try:
        # Open and process the image using Tesseract OCR
        with Image.open(file_path) as img:
            extracted_text = pytesseract.image_to_string(img)

        if not extracted_text.strip():
            await message.reply_text("No text detected in the image.")
            os.remove(file_path)
            return

        # Cache the OCR result in Redis for 1 day
        cache.set(cache_key, extracted_text, ex=86400)

        # Reply with the extracted text
        await message.reply_text(f"**Extracted Text:**\n{extracted_text}")

    except Exception as e:
        await message.reply_text(f"Error during OCR: {e}")

    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
    
