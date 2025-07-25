import os
import time
import asyncio
#from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from downloader import extract_formats, download_format
from utils import generate_thumbnail, get_duration
from progress import progress_bar, format_bytes

# Load environment
#load_dotenv()

# Init bot
bot = Client(
    "bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Ensure download dir
os.makedirs("downloads", exist_ok=True)

@bot.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("👋 **Hi!**\n\nSend me a video/audio URL and I’ll help you download and upload it to Telegram!")


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

    buttons = []
    for f in formats:
        label = f"{f['resolution']}p - {round(f['filesize'] / 1024**2, 1)}MB"
        callback = f"{f['format_id']}|||{url[:40]}"
        if len(callback.encode()) <= 64:  # Ensure under Telegram limit
            buttons.append([InlineKeyboardButton(label, callback_data=callback)])

    if not buttons:
        return await status.edit("❌ No suitable formats found.")

    await status.edit(
        f"🎬 **Select quality for:**\n`{title[:64]}`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@bot.on_callback_query()
async def on_format_selected(_, query):
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

    # Cleanup
    try:
        os.remove(filepath)
        if thumb:
            os.remove(thumb)
    except:
        pass

# Run the bot
if __name__ == "__main__":
    bot.run()
