"""
Plugin Description: Parse LaTeX code, generate a PDF, and cache or log results.
Commands:
- .latex <LaTeX code>: Parses LaTeX code and sends the generated PDF.
"""

import os
import subprocess
import redis
from pymongo import MongoClient
from pyrogram import Client, filters
from config import Config
import uuid

# MongoDB and Redis setup
redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client["telegram_userbot"]
latex_logs_collection = db["latex_logs"]

@Client.on_message(filters.command("latex") & filters.me)
async def latex_handler(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text("Usage: .latex <LaTeX code>")
        return

    latex_code = args[1]
    cache_key = f"latex_pdf:{latex_code}"

    # Check Redis cache for the result
    cached_pdf = redis_client.get(cache_key)
    if cached_pdf:
        pdf_path = f"./temp_{uuid.uuid4().hex}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(cached_pdf)
        await client.send_document(
            chat_id=message.chat.id,
            document=pdf_path,
            caption="Cached PDF generated from LaTeX."
        )
        os.remove(pdf_path)
        return

    # Temporary file setup
    temp_dir = f"./temp_{uuid.uuid4().hex}"
    os.makedirs(temp_dir, exist_ok=True)
    tex_file = os.path.join(temp_dir, "document.tex")
    pdf_file = os.path.join(temp_dir, "document.pdf")

    try:
        # Write LaTeX code to a .tex file
        with open(tex_file, "w") as f:
            f.write(r"\documentclass{article}" + "\n")
            f.write(r"\usepackage[utf8]{inputenc}" + "\n")
            f.write(r"\begin{document}" + "\n")
            f.write(latex_code + "\n")
            f.write(r"\end{document}")

        # Generate the PDF using pdflatex
        result = subprocess.run(
            ["pdflatex", "-output-directory", temp_dir, tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            await message.reply_text(f"Error: Failed to compile LaTeX.\n{result.stderr.decode()}")
            return

        # Cache the PDF content in Redis
        with open(pdf_file, "rb") as f:
            pdf_content = f.read()
        redis_client.set(cache_key, pdf_content, ex=86400)  # Cache for 1 day

        # Log LaTeX code and result in MongoDB
        latex_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "latex_code": latex_code,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": "success"
        })

        # Send the PDF file
        await client.send_document(
            chat_id=message.chat.id,
            document=pdf_file,
            caption="Here is your generated PDF."
        )

    except Exception as e:
        # Log the failure in MongoDB
        latex_logs_collection.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "latex_code": latex_code,
            "chat_id": message.chat.id,
            "timestamp": message.date,
            "status": f"failed: {e}"
        })
        await message.reply_text(f"Error: {e}")

    finally:
        # Clean up temporary files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(temp_dir)
