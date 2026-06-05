import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

TOKEN = '8959742179:AAGNoIWXDk04tYUmSnzayvYxAaSGEi4TqnE'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Linklarni vaqtincha saqlash
user_links = {}

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text
    user_links[message.from_user.id] = url
    
    # Link turini aniqlash uchun oddiy tekshiruv
    # (Haqiqiy holatda yt-dlp meta-data orqali aniqroq bo'ladi)
    if "pinterest" in url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Rasm yuklash", callback_data="down_photo")],
            [InlineKeyboardButton(text="🎥 Video yuklash", callback_data="down_video")]
        ])
    elif "instagram" in url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Video/Rasm yuklash", callback_data="down_video")],
            [InlineKeyboardButton(text="🎵 Qo'shiq (Audio) yuklash", callback_data="down_audio")]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Video", callback_data="down_video")],
            [InlineKeyboardButton(text="🎵 Audio", callback_data="down_audio")]
        ])
        
    await message.answer("Siz yuborgan link bo'yicha tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("down_"))
async def process_download(callback: types.CallbackQuery):
    url = user_links.get(callback.from_user.id)
    action = callback.data
    status = await callback.message.answer("⏳ Yuklanmoqda... Kuting.")
    
    try:
        # Formatlarni moslash
        ydl_opts = {
            'format': 'bestaudio/best' if action == "down_audio" else 'best',
            'outtmpl': 'download.%(ext)s',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Fayl turiga qarab yuborish
        if action == "down_photo":
            await callback.message.answer_photo(photo=FSInputFile(filename))
        elif action == "down_audio":
            await callback.message.answer_audio(audio=FSInputFile(filename))
        else:
            await callback.message.answer_video(video=FSInputFile(filename))
            
        if os.path.exists(filename): os.remove(filename)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Xatolik: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())