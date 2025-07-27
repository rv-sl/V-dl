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

def get_eta(current, total, start_time):
    elapsed = time.time() - start_time
    if current == 0 or elapsed <= 0:
        return "Calculating..."
    speed = current / elapsed
    remaining = total - current
    eta = remaining / speed if speed > 0 else 0
    return time.strftime("%M:%S", time.gmtime(eta))

def create_progress_hook(tg_message, filename):
    start_time = time.time()
    last_update = [0]  # mutable so it persists

    async def hook(data):
        now = time.time()
        if now - last_update[0] >= 5 or data["percent"] >= 100:
            bar = progress_bar(data["current"], data["total"])
            text = (
                f"📥 **Downloading:** `{filename}`\n"
                f"{bar}\n"
                f"**Progress:** {format_bytes(data['current'])} / {format_bytes(data['total'])}\n"
                f"🚀 **Speed:** {format_bytes(data['current'] / (now - start_time + 1))}/s\n"
                f"⏳ **ETA:** {get_eta(data['current'], data['total'], start_time)}"
            )
            try:
                await tg_message.edit_text(text)
                last_update[0] = now
            except Exception as e:
                print("⚠️ Message edit failed:", e)

    return hook
