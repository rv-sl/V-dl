import os
from pyrogram import filters

# Load authorized user IDs from environment
raw_ids = os.getenv("auth", "")
AUTHORIZED_USERS = [int(uid.strip()) for uid in raw_ids.split(",") if uid.strip().isdigit()]

def is_authorized():
    return filters.user(AUTHORIZED_USERS)
