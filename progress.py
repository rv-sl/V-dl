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
