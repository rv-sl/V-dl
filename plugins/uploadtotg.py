import os
import time
import asyncio
from utils import generate_thumbnail, get_duration, format_bytes, progress_bar
from pyrogram.types import Message
from pyrogram.errors import FloodWait

async def upload_to_telegram(filepath: str, chat_id: int, status_msg: Message, send: int = 1):
    try:
        await status_msg.edit("🖼 Generating thumbnail...")
        thumb = generate_thumbnail(filepath)
        duration = get_duration(filepath)
        file_size = os.path.getsize(filepath)
        file_name = os.path.basename(filepath)

        # Upload progress handler
        last_update_time = 0
        last_status_text = ""

        async def progress(current, total):
            nonlocal last_update_time, last_status_text
            now = time.time()
            if now - last_update_time >= 5 or current == total:
                uploaded_size = format_bytes(current)
                total_size = format_bytes(total)
                bar = progress_bar(current, total)
                text = (
                    f"📤 **Uploading to Telegram...**\n\n"
                    f"🎬 `{file_name}`\n"
                    f"{bar} `{uploaded_size} / {total_size}`"
                )
                if text != last_status_text:
                    try:
                        await status_msg.edit(text)
                        last_status_text = text
                        last_update_time = now
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except:
                        pass  # Prevent crashes on message edit failure

        # Upload the file
        if send == 0:
            await status_msg._client.send_document(
                chat_id=chat_id,
                document=filepath,
                thumb=thumb,
                caption="✅ Uploaded as document.",
                progress=progress
            )
        else:
            await status_msg._client.send_video(
                chat_id=chat_id,
                video=filepath,
                thumb=thumb,
                duration=duration,
                supports_streaming=True,
                caption="✅ **Here is your video!** 🎉",
                progress=progress
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
