import importlib
import os
from urllib.parse import urlparse

def get_extractor_module(url):
    netloc = urlparse(url).netloc.lower()
    site = netloc.split(".")[-2]  # "dailymotion", "vimeo", etc.
    try:
        return importlib.import_module(f"rvx.{site}")
    except ImportError:
        raise Exception(f"No extractor found for: {site}")

def extract_video_info(url):
    extractor = get_extractor_module(url)
    if hasattr(extractor, "extract"):
        return extractor.extract(url)
    raise Exception("Extractor missing `.extract()`")

def extract_m3u8_qualities(url):
    extractor = get_extractor_module(url)
    if hasattr(extractor, "extract_m3u8"):
        return extractor.extract_m3u8(url)
    return None
