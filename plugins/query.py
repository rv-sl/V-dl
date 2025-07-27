import os
import time
import asyncio
from pyrogram import Client
from pyrogram.types import CallbackQuery

from downloader import download_format
from plugins.uploadtotg import upload_to_telegram

@Client.on_callback_query()
async def on_format_selected(_, query: CallbackQuery):
    await query.answer()

    try:
        format_id, url = query.data.split("|||")
    except ValueError:
        return await query.message.edit("⚠️ Invalid selection or expired data.")

    progress_msg = await query.message.reply("📥 Starting download...")

    last_time = time.time()
    progress_data = {"msg": progress_msg, "last": last_time}

    def hook(d):
        if d["status"] == "downloading":
            now = time.time()
            if now - progress_data["last"] > 5:
                text = f"""📥 **Downloading...**

**File:** `{os.path.basename(d.get('filename', 'file.mp4'))}`
{progress_bar(d.get("downloaded_bytes", 0), d.get("total_bytes", 1))}
**Size:** {format_bytes(d.get("downloaded_bytes", 0))} / {format_bytes(d.get("total_bytes", 1))}
"""
                asyncio.create_task(progress_data["msg"].edit(text))
                progress_data["last"] = now

    try:
        filepath = download_format(url, format_id, hook)
    except Exception as e:
        return await progress_msg.edit(f"❌ Download failed:\n`{e}`")

    await upload_to_telegram(filepath, query.message, progress_msg, send=1)
  
