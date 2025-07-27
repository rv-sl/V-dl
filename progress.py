import time

def progress_bar(current, total):
    try:
        percent = (current / total) * 100 if total > 0 else 0
    except:
        percent = 0
    bar = "█" * int(percent // 5) + "░" * (20 - int(percent // 5))
    return f"[{bar}] {percent:.1f}%"

def format_bytes(size):
    try:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    except:
        return "N/A"

async def update_progress(msg, start_time, current, total, filename):
    now = time.time()
    speed = current / (now - start_time + 1)
    eta = (total - current) / speed if speed > 0 else 0

    text = (
        f"📥 **Downloading:** `{filename}`\n"
        f"{progress_bar(current, total)}\n"
        f"**Progress:** {format_bytes(current)} / {format_bytes(total)}\n"
        f"🚀 **Speed:** {format_bytes(speed)}/s\n"
        f"⏳ **ETA:** {time.strftime('%M:%S', time.gmtime(eta))}"
    )
    await msg.edit(text)
