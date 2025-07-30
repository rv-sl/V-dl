import os
from downloader import download_video
from progress import create_progress_hook
from plugins.uploadtotg import upload_to_telegram
from rvx_ex import extract_video_info, extract_m3u8_qualities

def get_best_quality(streams: list, desired_quality: str = "720") -> dict | None:
    # Filter out streams missing 'quality' or 'url'
    valid_streams = [s for s in streams if "quality" in s and "url" in s]

    # Sort by quality (converted to int) in descending order
    sorted_streams = sorted(valid_streams, key=lambda s: int(s["quality"]), reverse=True)

    # Try to find exact match
    for stream in sorted_streams:
        if stream["quality"] == desired_quality:
            return stream

    # If no match, return best (highest) quality
    return sorted_streams[0] if sorted_streams else None

async def runner(client, data):
  ntext = (
    f"⏱️Starting Task!\n",
    f"Url: {data.get('link','None')}"
  )
  status = await client.send_message(chat_id=data.get("chat"),text=ntext)
  try:
      url = data.get("link")
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

      best = get_best_quality(formats)
      video_url = best.get("url")
      filename = file_info.get("title", f"video_{quality}.mp4")
      dl_msg = await status.reply("🔰Starting Download...")
    
      progress_hook = create_progress_hook(dl_msg, filename)

      # Start download
      path = await download_video(video_url, progress_hook=progress_hook)

      # Upload to Telegram
      #await downloading_msg.edit("📤 Uploading to Telegram...")
      #await callback_query.message.reply_document(document=path)
      await upload_to_telegram(
            filepath=path, 
            chat_id=status.chat.id, 
            status_msg=dl_msg, 
            caption=caption,
            send=1
      )
      #await downloading_msg.delete()
      #os.remove(path)
  except Exception as e:
        await status.edit(f"❌ Error:\n`{e}`")

    
