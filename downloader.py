import os
import subprocess
import random
import string
import requests
import re
from urllib.parse import urlparse

# Max file size from env (MB), default 2048MB = 2GB
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 2048))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def random_filename(ext=".mp4"):
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{name}{ext}"

def format_headers(headers: dict):
    return ["-headers", "\r\n".join(f"{k}: {v}" for k, v in headers.items()) + "\r\n"]

def infer_extension(url):
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        return os.path.splitext(path)[1].lower()
    return ""

def is_video_ext(ext):
    return ext in [".mp4", ".mkv", ".webm", ".mov", ".ts", ".m3u8", ".flv", ".avi"]

def ffmpeg_progress_line_parser(line, duration):
    if "time=" in line and duration:
        match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
        if match:
            h, m, s = map(float, match.groups())
            current = h * 3600 + m * 60 + s
            percent = (current / duration) * 100
            return {
                "percent": round(percent, 2),
                "current": current,
                "total": duration
            }
    return None

async def download_video(url, headers=None, progress_hook=None):
    if headers is None:
        headers = {}

    ext = infer_extension(url)
    if "m3u8" in url:
        ext = ".m3u8"
    elif not ext:
        ext = ".bin"

    os.makedirs("downloads", exist_ok=True)
    filename = random_filename(".mp4" if is_video_ext(ext) else ext)
    output_path = os.path.join("downloads", filename)

    # Determine if it's a stream
    is_stream = ".m3u8" in url or ".mpd" in url or ".ism" in url

    # HEAD request to check file size
    try:
        head = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
        size = int(head.headers.get("content-length", 0))
        if size > 0 and size > MAX_FILE_SIZE_BYTES:
            raise Exception(f"❌ File too large ({round(size / (1024 * 1024), 2)} MB > {MAX_FILE_SIZE_MB} MB)")
    except Exception as e:
        print("⚠️ Could not validate file size:", e)

    if is_stream:
        # Download and convert stream to mp4
        cmd = ["ffmpeg", "-y"]
        if headers:
            cmd += format_headers(headers)
        cmd += ["-i", url, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-movflags", "+faststart", output_path]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        duration = None
        for line in process.stderr:
            line = line.strip()
            if not duration:
                match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
                if match:
                    h, m, s = map(float, match.groups())
                    duration = h * 3600 + m * 60 + s

            if progress_hook and duration:
                prog = ffmpeg_progress_line_parser(line, duration)
                if prog:
                    #progress_hook(prog)
                    import asyncio
                    awaitable = getattr(progress_hook, '__call__', None)
                    if awaitable:
                        try:
                            await progress_hook(prog)
                        except:
                            pass

        process.wait()
        if process.returncode != 0 or not os.path.exists(output_path):
            raise Exception("❌ FFmpeg stream download failed")

    else:
        # Direct download
        temp_path = output_path + ".part"
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            if total and total > MAX_FILE_SIZE_BYTES:
                raise Exception(f"❌ File too large ({round(total / (1024 * 1024), 2)} MB > {MAX_FILE_SIZE_MB} MB)")

            downloaded = 0
            with open(temp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_hook and total > 0:
                            percent = (downloaded / total) * 100
                            progress_hook({
                                "percent": round(percent, 2),
                                "current": downloaded,
                                "total": total
                            })

        # Convert if it's a video
        if is_video_ext(ext):
            convert_cmd = [
                "ffmpeg", "-y", "-i", temp_path,
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-movflags", "+faststart",
                output_path
            ]
            process = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            duration = None
            for line in process.stderr:
                line = line.strip()
                if not duration:
                    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
                    if match:
                        h, m, s = map(float, match.groups())
                        duration = h * 3600 + m * 60 + s

                if progress_hook and duration:
                    prog = ffmpeg_progress_line_parser(line, duration)
                    if prog:
                        #progress_hook(prog)
                        import asyncio
                        awaitable = getattr(progress_hook, '__call__', None)
                        if awaitable:
                            try:
                                await progress_hook(prog)
                            except:
                                pass

            process.wait()
            os.remove(temp_path)
            if process.returncode != 0 or not os.path.exists(output_path):
                raise Exception("❌ FFmpeg conversion failed")
        else:
            # Not a video, just rename
            os.rename(temp_path, output_path)

    return output_path
