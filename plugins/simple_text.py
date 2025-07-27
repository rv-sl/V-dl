from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("👋 **Hi!**\n\nSend me a video/audio URL and I’ll help you download and upload it to Telegram!")

@Client.on_message(filters.command("help"))
async def help(_, msg: Message):
    await msg.reply("📌 **Usage:**\nSend a video/audio link and select the format to upload it.")
