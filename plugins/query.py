from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from downloader import download_video
from progress import create_progress_hook

@Client.on_callback_query(filters.regex(r"^dl\|\|"))
async def handle_download_button(client, callback_query: CallbackQuery):
    await callback_query.answer()

    _, quality, video_url = callback_query.data.split("||", 2)
    downloading_msg = await callback_query.message.reply(f"📥 Starting download `{quality}p`...")

    try:
        filename = f"video_{quality}.mp4"
        progress_hook = create_progress_hook(downloading_msg, filename)

        # Start download
        path = download_video(video_url, progress_hook=progress_hook)

        # Upload to Telegram
        await downloading_msg.edit("📤 Uploading to Telegram...")
        await callback_query.message.reply_document(document=path)
        await downloading_msg.delete()
        os.remove(path)

    except Exception as e:
        await downloading_msg.edit(f"❌ Failed:\n`{str(e)}`")
