from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from downloader import download_video
from progress import create_progress_hook
from plugins.uploadtotg import upload_to_telegram
from callback_data import store_callback_data, get_callback_data


@Client.on_callback_query(filters.regex(r"^dl\|\|"))
async def handle_download_button(client, callback_query: CallbackQuery):
    await callback_query.answer()

    _, quality, vkey = callback_query.data.split("||", 2)
    video_url = get_callback_data(vkey)
    if not video_url:
        await callback_query.message.reply("Sorry i think it was older buttons or data....")
        return
    downloading_msg = await callback_query.message.reply(f"📥 Starting download `{quality}p`...")

    try:
        filename = f"video_{quality}.mp4"
        progress_hook = create_progress_hook(downloading_msg, filename)

        # Start download
        path = await download_video(video_url, progress_hook=progress_hook)

        # Upload to Telegram
        #await downloading_msg.edit("📤 Uploading to Telegram...")
        #await callback_query.message.reply_document(document=path)
        await upload_to_telegram(
            filepath=path, 
            chat_id=downloading_msg.chat.id, 
            status_msg=downloading_msg, 
            send=1
        )
        #await downloading_msg.delete()
        #os.remove(path)

    except Exception as e:
        await downloading_msg.edit(f"❌ Failed:\n`{str(e)}`")
