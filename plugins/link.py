import os
import hashlib
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from plugins.auther import is_authorized
from rvx_ex import extract_video_info, extract_m3u8_qualities

# Store hash->URL mapping for callback lookup
Client.dl_cache = {}

@Client.on_message(filters.text & filters.private)
async def handle_url(client: Client, msg: Message):
    url = msg.text.strip()
    if not url.lower().startswith("http"):
        return

    status = await msg.reply("🔍 Extracting video info...")

    try:
        file_info = extract_video_info(url)
        streams = file_info.get("streams", [])

        # Check for master m3u8
        master_url = None
        for s in streams:
            if s.get("quality") == "auto" and s.get("type", "").endswith("mpegURL"):
                master_url = s["url"]
                break

        if master_url:
            formats = extract_m3u8_qualities(master_url)
        else:
            formats = [{"quality": s.get("quality", "unknown"), "url": s["url"]} for s in streams]

        if not formats:
            return await status.edit("❌ No stream formats found.")

        # Caption
        title = file_info.get("title", "Unknown Title")
        caption = (
            f"🎬 **{title}**\n"
            f"🆔 `{file_info.get('video_id')}`\n"
            f"📅 Uploaded: `{file_info.get('upload_date')}`\n"
            f"👤 By: [{file_info.get('uploaded_by')}]({file_info.get('uploader_url')})\n"
            f"⏱ Duration: `{file_info.get('duration')}s`\n"
            f"🌐 Language: `{file_info.get('language', 'n/a')}`\n"
            f"🔗 [Video Page]({file_info.get('video_page_url')})"
        )

        # Build buttons with size-safe callback_data
        buttons = []
        for fmt in formats:
            quality = fmt.get("quality", "unknown")
            url = fmt.get("url", "")
            if not url:
                continue

            # Create hash for URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            cb_data = f"dl|{quality}|{url_hash}"

            # Cache full URL safely
            client.dl_cache[url_hash] = url
            buttons.append([InlineKeyboardButton(f"{quality}p", callback_data=cb_data)])

        # Reply with photo + caption + buttons
        await msg.reply_photo(
            photo=file_info.get("thumbnail"),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error:\n`{e}`")
