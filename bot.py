import os
from pyrogram import Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

# Bot init
bot = Client(
    "bot",
    api_id=int(os.getenv("apiid")),
    api_hash=os.getenv("apihash"),
    bot_token=os.getenv("tk"),
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    bot.run()
