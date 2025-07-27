import requests
import datetime
import re

def get_auto_stream_url(video_data):
    try:
        for stream in video_data.get("streams", []):
            if stream.get("quality") == "auto":
                return stream.get("url")
        return None  # If 'auto' not found
    except Exception as e:
        print("Error extracting stream URL:", e)
        return None

def extract_m3u8(master_url: str):
    if not isinstance(master_url, str):
        print("It's not a string")
        master_url = get_auto_stream_url(master_url)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(master_url, headers=headers, timeout=10)
        res.raise_for_status()

        content = res.text.strip()
        lines = content.splitlines()

        qualities = []
        for i in range(len(lines)):
            if lines[i].startswith("#EXT-X-STREAM-INF"):
                info = lines[i]
                url = lines[i+1] if (i + 1) < len(lines) else None

                # Extract bandwidth, resolution, and name
                bandwidth = re.search(r'BANDWIDTH=(\d+)', info)
                resolution = re.search(r'RESOLUTION=(\d+x\d+)', info)
                name = re.search(r'NAME="(.*?)"', info)

                qualities.append({
                    "quality": name.group(1) if name else None,
                    "resolution": resolution.group(1) if resolution else None,
                    "bandwidth": int(bandwidth.group(1)) if bandwidth else None,
                    "url": url
                })

        return qualities
    except Exception as e:
        return {"error": str(e)}


def extract(video_id: str) -> dict:
    url = f"https://geo.dailymotion.com/video/{video_id}.json"
    
    params = {
        "legacy": "true",
        "geo": "1",
        "player-id": "default",
        "locale": "en-US",
        "dmV1st": "random-session-id",
        "dmTs": "980000",
        "is_native_app": "0",
        "dmViewId": "random-view-id",
        "parallelCalls": "1"
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": f"https://geo.dailymotion.com/player.html?video={video_id}",
        "user-agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"Failed to fetch video metadata: {e}"}

    # Parse qualities and extract video URLs
    qualities = data.get("qualities", {})
    video_streams = []

    for quality, sources in qualities.items():
        if not isinstance(sources, list):
            continue
        for source in sources:
            url = source.get("url")
            if url:
                video_streams.append({
                    "quality": quality,
                    "type": source.get("type"),
                    "url": url
                })

    # Build final metadata
    metadata = {
        "video_id": data.get("id"),
        "title": data.get("title"),
        "duration": data.get("duration"),
        "thumbnail": data["thumbnails"].get("720") or data["thumbnails"].get("480") or None,
        "uploaded_by": data.get("owner", {}).get("screenname"),
        "uploader_url": data.get("owner", {}).get("url"),
        "upload_date": (
            datetime.datetime.fromtimestamp(data["created_time"]).isoformat()
            if "created_time" in data else None
        ),
        "language": data.get("language"),
        "channel": data.get("channel"),
        "is_private": data.get("private"),
        "is_password_protected": data.get("is_password_protected"),
        "video_page_url": data.get("url"),
        "streams": video_streams
    }

    return metadata


# Example usage
#if __name__ == "__main__":
    #video_id = "x843dhc" #"x5k8clg"  # Change this to the desired video ID
    #info = get_dailymotion_video_data(video_id)
    #m3u8 = extract_m3u8_qualities(get_auto_stream_url(info))
    #print(m3u8)
    #from pprint import pprint
    #pprint(info)
