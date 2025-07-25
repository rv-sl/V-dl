from yt_dlp import YoutubeDL
import os
from utils import random_filename

def extract_formats(url):
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get("formats", []):
            if f.get("filesize") and (f.get("vcodec") != "none" or f.get("acodec") != "none"):
                formats.append({
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("height", "audio"),
                    "filesize": f["filesize"],
                })
        return formats[:10], info.get("title", "Untitled")

def download_format(url, format_id, hook):
    rand_name = random_filename()
    out_path = f"downloads/{rand_name}"
    ydl_opts = {
        "format": format_id,
        "outtmpl": out_path,
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return out_path
