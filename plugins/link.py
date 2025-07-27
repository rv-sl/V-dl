import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from auther import is_authorized
from rvx_ex import extract_video_info, extract_m3u8_qualities

@Client.on_message(filters.text & filters.private & is_authorized())
async def handle_url(client: Client, msg: Message):
    url = msg.text.strip()
    if not url.lower().startswith("http"):
        return

    status = await msg.reply("🔍 Extracting video info...")

    try:
        file_info = extract_video_info(url)
        streams = file_info.get("streams", [])

        # Check if there is an 'auto' (master m3u8) stream
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

        # Create message caption
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

        # Inline buttons for each quality
        buttons = []
        for fmt in formats:
            label = f"{fmt['quality']}p"
            cb_data = f"dl||{fmt['quality']}||{fmt['url']}"
            if len(cb_data.encode()) <= 64:
                buttons.append([InlineKeyboardButton(label, callback_data=cb_data)])

        # Send the thumbnail with caption and buttons
        await msg.reply_photo(
            photo=file_info.get("thumbnail"),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await status.delete()

    except Exception as e:
        return await status.edit(f"❌ Error:\n`{e}`")
