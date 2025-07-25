import subprocess
from PIL import Image
import random
import string
import os

def random_filename(ext=".mp4"):
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{name}{ext}"

def generate_thumbnail(video_path):
    thumb_path = "thumb.jpg"
    subprocess.call([
        "ffmpeg", "-ss", "00:00:02", "-i", video_path,
        "-frames:v", "1", thumb_path, "-y", "-loglevel", "quiet"
    ])
    if os.path.exists(thumb_path):
        img = Image.open(thumb_path)
        img = img.resize((320, 180))
        img.save(thumb_path)
    return thumb_path if os.path.exists(thumb_path) else None

def get_duration(video_path):
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", video_path
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return int(float(result.stdout))
    except:
        return 0
