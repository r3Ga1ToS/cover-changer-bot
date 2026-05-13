import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import API_TOKEN

# Initialize bot and dispatcher with HTML parse mode for bold text
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Temporary in-memory storage for user thumbnails {user_id: photo_file_id}
user_thumbnails = {}

# Flask health check server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.reply("Jinda hun. Photo bej cover laga dunga.")

@dp.message(F.photo)
async def auto_save_thumbnail(message: Message):
    # Automatically grab the highest quality photo sent and save its file_id
    user_thumbnails[message.from_user.id] = message.photo[-1].file_id
    await message.reply("Cover saved! Now send the file.")

@dp.message(F.document | F.video)
async def process_file(message: Message):
    user_id = message.from_user.id
    
    # Check if user has sent a photo first
    if user_id not in user_thumbnails:
        await message.reply("Please send a photo first so I can use it as a cover.")
        return

    status_msg = await message.reply("Processing... please wait.")

    try:
        # 1. Format the caption to bold if it exists
        caption = message.caption or ""
        bold_caption = f"<b>{caption}</b>" if caption else ""

        # 2. Download the cover photo
        thumb_file_id = user_thumbnails[user_id]
        thumb_info = await bot.get_file(thumb_file_id)
        thumb_path = f"thumb_{user_id}.jpg"
        await bot.download_file(thumb_info.file_path, thumb_path)

        # 3. Download the main document/video
        file_obj = message.video if message.video else message.document
        file_info = await bot.get_file(file_obj.file_id)
        file_name = getattr(file_obj, 'file_name', f"file_{user_id}.mp4")
        file_path = f"dl_{file_name}"
        
        await bot.download_file(file_info.file_path, file_path)
        await status_msg.edit_text("Uploading with new cover...")

        # 4. Upload back to Telegram
        main_input = FSInputFile(file_path)
        thumb_input = FSInputFile(thumb_path)

        if message.video:
            await message.reply_video(
                video=main_input,
                caption=bold_caption,
                thumbnail=thumb_input,
                supports_streaming=True
            )
        else:
            await message.reply_document(
                document=main_input,
                caption=bold_caption,
                thumbnail=thumb_input
            )

        # 5. Cleanup local files to save space
        os.remove(file_path)
        os.remove(thumb_path)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"An error occurred: {e}")

async def main():
    print("🚀 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print(r'''
    ____  ____  ________
   / __ )/ __ \/_  __/ /
  / __  / / / / / / / / 
 / /_/ / /_/ / / / /_/  
/_____/\____/ /_/ (_)   
                        
  BOT WORKING PROPERLY....
    ''')
    print("Starting Bot...")
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
