from yt_dlp import YoutubeDL
import os
from utils import random_filename
import subprocess
import random
import string
import re

def random_filename(ext=".mp4"):
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{name}{ext}"

def parse_progress_line(line):
    """
    Parses yt-dlp progress line from stderr.
    This is a simplified example parsing key values like:
    [download]  10.0% of 50.00MiB at 1.50MiB/s ETA 00:30
    """
    progress = {}
    # Example regex for percentage and ETA
    m = re.search(r"\[download\]\s+(\d+\.\d+)%.*ETA\s+([\d:]+)", line)
    if m:
        progress["percent"] = float(m.group(1))
        progress["eta"] = m.group(2)
    return progress

def download_format(url, format_id, hook):
    rand_name = random_filename()
    out_path = os.path.join("downloads", rand_name)

    cmd = [
        "yt-dlp",
        "-f", format_id,
        "-o", out_path,
        url,
    ]

    # Run yt-dlp subprocess
    with subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True) as proc:
        for line in proc.stderr:
            line = line.strip()
            if line:
                progress = parse_progress_line(line)
                if progress:
                    hook(progress)

        proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed with code {proc.returncode}")

    return out_path

def extract_formats_old(url):
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

def extract_formats(url):
    try:
        # Get title
        title_result = subprocess.run(
            ["yt-dlp", "--get-title", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        title = title_result.stdout.strip()

        # Get formats list (as string)
        formats_result = subprocess.run(
            ["yt-dlp", "-F", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = formats_result.stdout.strip().splitlines()

        formats = []
        started = False
        for line in lines:
            if not started:
                if line.strip().startswith("format code"):
                    started = True
                continue
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) < 4:
                continue
            format_id = parts[0]
            ext = parts[1]
            resolution = parts[2]
            size_match = re.search(r'(\d+(?:\.\d+)?)([KMG]iB)', line)
            if size_match:
                size = size_match.group(1)
                unit = size_match.group(2)
                multiplier = {
                    "KiB": 1024,
                    "MiB": 1024**2,
                    "GiB": 1024**3
                }.get(unit, 1)
                filesize = float(size) * multiplier
            else:
                filesize = None

            # Skip formats with no file size or both audio+video missing
            if not filesize:
                continue

            formats.append({
                "format_id": format_id,
                "ext": ext,
                "resolution": resolution,
                "filesize": int(filesize),
            })

        return formats, title
    except subprocess.CalledProcessError as e:
        print(f"Error extracting formats: {e.stderr}")
        return [], "Unknown"


def download_format_err(url, format_id, hook):
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
