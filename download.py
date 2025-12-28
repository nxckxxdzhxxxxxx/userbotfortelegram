import os
import asyncio
import yt_dlp
from pyrogram import Client
from pyrogram.types import Message
from dotenv import load_dotenv

async def savett_command(client: Client, message: Message):
    # ПРИНУДИТЕЛЬНО обновляем лимиты из файла
    load_dotenv(override=True)
    MAX_SIZE_MB = int(os.getenv("MAX_DOWNLOAD_SIZE", 10))
    MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

    if len(message.command) < 2:
        return await message.edit_text(f"❌ Введите ссылку на видео!")

    link = message.command[1]
    status_msg = await message.edit_text("📡 **Анализ видео...**")
    file_path = f"dl_{message.id}.mp4"

    try:
        # 1. Сначала только получаем информацию без скачивания
        ydl_info_opts = {
            'quiet': True, 
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = await asyncio.to_thread(lambda: ydl.extract_info(link, download=False))
            file_size = info.get('filesize') or info.get('filesize_approx') or 0
            
            if file_size > MAX_BYTES:
                size_mb = round(file_size / (1024 * 1024), 1)
                return await status_msg.edit_text(
                    f"⚠️ **Файл слишком велик!**\n"
                    f"📦 Размер: `{size_mb} MB`\n"
                    f"🚫 Ваш лимит: `{MAX_SIZE_MB} MB`"
                )

        # 2. Настройки для гарантированного MP4 (кодек h264)
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Telegram лучше всего понимает чистый mp4
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
            'nocheckcertificate': True,
        }

        await status_msg.edit_text(f"📥 **Загрузка...** (`{round(file_size/1024/1024, 1)} MB`)")
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([link]))

        # --- ВСЕ ЧТО НИЖЕ, ДОЛЖНО БЫТЬ ВНУТРИ TRY (с отступом) ---
        if os.path.exists(file_path):
            await status_msg.edit_text("✅ **Загружено! Отправляю в Telegram...**")
            try:
                await client.send_video(
                    chat_id=message.chat.id,
                    video=file_path,
                    caption=f"🎬 **Готово!**\n🔗 <a href='{link}'>Источник</a>",
                    reply_to_message_id=message.id,
                    supports_streaming=True
                )
                await status_msg.delete()
            except Exception as send_err:
                await status_msg.edit_text(f"❌ **Ошибка отправки:** `{str(send_err)[:50]}`")
            
            if os.path.exists(file_path): 
                os.remove(file_path)
        else:
            await status_msg.edit_text("❌ **Ошибка:** Файл не был создан после загрузки.")

    except Exception as e:
        error_text = str(e)
        if "Unsupported URL" in error_text:
            await status_msg.edit_text("❌ **Ошибка:** Ссылка не поддерживается.")
        else:
            await status_msg.edit_text(f"❌ **Ошибка:** {error_text[:100]}")
        
        if os.path.exists(file_path): 
            os.remove(file_path)