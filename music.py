import os
import asyncio
import yt_dlp
from pyrogram import Client
from pyrogram.types import Message

async def music_search_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ **Введите название песни!**\nПример: `.m Scorpions - Still Loving You`")

    query = " ".join(message.command[1:])
    status_msg = await message.edit_text(f"🔍 **Ищу:** `{query}`...")
    
    # Путь для временного файла
    file_path = f"music_{message.id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',  # Ищем 1 результат
        'outtmpl': file_path + '.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        # 1. Поиск и загрузка
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(lambda: ydl.extract_info(query, download=True))
            # yt-dlp часто возвращает список, если используется ytsearch
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info.get('title', 'Unknown Title')
            performer = info.get('uploader', 'Unknown Artist')
            duration = int(info.get('duration', 0))
            final_file = file_path + ".mp3"

        # 2. Отправка аудио
        if os.path.exists(final_file):
            await status_msg.edit_text("📤 **Отправляю аудио...**")
            await client.send_audio(
                chat_id=message.chat.id,
                audio=final_file,
                title=title,
                performer=performer,
                duration=duration,
                caption=f"🎵 **Найдено по запросу:** `{query}`",
                reply_to_message_id=message.id
            )
            await status_msg.delete()
            os.remove(final_file)
        else:
            await status_msg.edit_text("❌ **Ошибка:** Не удалось создать аудиофайл.")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Ошибка поиска:** `{str(e)[:50]}`")
        # Подчищаем хвосты если файлы остались
        for f in os.listdir():
            if f.startswith(file_path):
                os.remove(f)