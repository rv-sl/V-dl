import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from downloader import extract_formats, download_format
from utils import generate_thumbnail, get_duration
from progress import progress_bar, format_bytes

load_dotenv()
bot = Client("bot_upv",
    api_id=int(os.getenv("apiid")),
    api_hash=os.getenv("apihash"),
    bot_token=os.getenv("tk"))

os.makedirs("downloads", exist_ok=True)

@bot.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("👋 **Hi!**\nSend me any video/audio URL and I'll let you choose the quality to download and upload it to Telegram!")

@bot.on_message(filters.text & filters.private)
async def handle_url(_, msg):
    url = msg.text.strip()
    if not url.lower().startswith("http"):
        return
    status = await msg.reply("🔍 Extracting available formats...")

    try:
        formats, title = extract_formats(url)
    except Exception as e:
        return await status.edit(f"❌ Error extracting formats:\n`{e}`")

    buttons = [
        [InlineKeyboardButton(
            f"{f['resolution']}p - {round(f['filesize'] / 1024**2, 1)}MB",
            callback_data=f"{f['format_id']}|{url}"
        )] for f in formats
    ]
    await status.edit(
        f"🎬 **Select quality for:**\n`{title}`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query()
async def on_format_selected(_, query):
    await query.answer()
    format_id, url = query.data.split("|")
    progress_msg = await query.message.reply("📥 Starting download...")

    last_time = time.time()
    progress_data = {"msg": progress_msg, "last": last_time}

    def hook(d):
        if d["status"] == "downloading":
            now = time.time()
            if now - progress_data["last"] > 5:
                percent = d.get("downloaded_bytes", 0) / max(d.get("total_bytes", 1), 1)
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

    await progress_msg.edit("🖼 Generating thumbnail...")
    thumb = generate_thumbnail(filepath)
    duration = get_duration(filepath)

    await progress_msg.edit("📤 Uploading to Telegram...")

    try:
        await query.message.reply_video(
            video=filepath,
            thumb=thumb,
            duration=duration,
            supports_streaming=True,
            caption="✅ **Here is your video!** 🎉"
        )
        await progress_msg.delete()
    except Exception as e:
        await progress_msg.edit(f"❌ Upload failed:\n`{e}`")

    # Clean up
    try:
        os.remove(filepath)
        if thumb:
            os.remove(thumb)
    except:
        pass

bot.run()
