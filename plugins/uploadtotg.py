import os
from utils import generate_thumbnail, get_duration
from pyrogram.types import Message

async def upload_to_telegram(filepath: str, reply_to: Message, status_msg: Message, send: int = 1):
    try:
        await status_msg.edit("🖼 Generating thumbnail...")
        thumb = generate_thumbnail(filepath)
        duration = get_duration(filepath)

        await status_msg.edit("📤 Uploading to Telegram...")

        if send == 0:
            await reply_to.reply_document(
                document=filepath,
                thumb=thumb,
                caption="✅ Uploaded as document."
            )
        else:
            await reply_to.reply_video(
                video=filepath,
                thumb=thumb,
                duration=duration,
                supports_streaming=True,
                caption="✅ **Here is your video!** 🎉"
            )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ Upload failed:\n`{e}`")

    # Cleanup
    try:
        os.remove(filepath)
        if thumb:
            os.remove(thumb)
    except:
        pass
