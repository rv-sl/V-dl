import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from downloader import extract_formats

@Client.on_message(filters.text & filters.private)
async def handle_url(_, msg: Message):
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
        if len(callback.encode()) <= 64:
            buttons.append([InlineKeyboardButton(label, callback_data=callback)])

    if not buttons:
        return await status.edit("❌ No suitable formats found.")

    await status.edit(
        f"🎬 **Select quality for:**\n`{title[:64]}`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
