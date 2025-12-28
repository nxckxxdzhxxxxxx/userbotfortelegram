import os
import asyncio
from pyrogram import Client
from pyrogram.types import Message
from PIL import Image

# Попытка импорта библиотек для анимации
try:
    from lottie.exporters.gif import export_gif
    from lottie.importers.lottie import import_lottie
    HAS_LOTTIE = True
except ImportError:
    HAS_LOTTIE = False

async def sticker_command(client: Client, message: Message):
    """Создает стикер из фото (.st)"""
    target = message.reply_to_message
    if not target or not (target.photo or target.document or target.sticker):
        return await message.edit_text("❌ Ответьте на фото/файл.")

    status_msg = await message.edit_text("🔄 **Создаю стикер...**")
    
    # Список для отслеживания файлов к удалению
    to_delete = []
    
    try:
        # Скачиваем оригинал
        path = await client.download_media(target)
        to_delete.append(path)
        
        sticker_path = f"sticker_{message.id}.webp"
        to_delete.append(sticker_path)

        def process_sticker():
            with Image.open(path) as img:
                img.thumbnail((512, 512), Image.LANCZOS)
                img.save(sticker_path, "WEBP")

        await asyncio.to_thread(process_sticker)
        await client.send_sticker(chat_id=message.chat.id, sticker=sticker_path, reply_to_message_id=target.id)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")
    finally:
        # Удаляем всё, что насоздавали
        for f in to_delete:
            if os.path.exists(f):
                os.remove(f)

async def kang_command(client: Client, message: Message):
    """Конвертирует стикер в фото/гиф (.kang)"""
    target = message.reply_to_message
    if not target or not target.sticker:
        return await message.edit_text("❌ Ответьте на стикер.")
    
    status_msg = await message.edit_text("⏳ **Конвертирую...**")
    to_delete = []

    try:
        path = await client.download_media(target)
        to_delete.append(path)
        
        # 1. АНИМИРОВАННЫЕ STICKERS (.tgs) -> GIF
        if target.sticker.is_animated:
            if not HAS_LOTTIE:
                return await status_msg.edit_text("❌ Установите библиотеку: `pip install lottie`")
            
            out_gif = f"kang_{message.id}.gif"
            to_delete.append(out_gif)
            
            def convert_tgs():
                animation = import_lottie(path)
                export_gif(animation, out_gif)
            
            await asyncio.to_thread(convert_tgs)
            await client.send_animation(chat_id=message.chat.id, animation=out_gif, reply_to_message_id=target.id)

        # 2. ВИДЕО-СТИКЕРЫ (.webm) -> GIF
        elif target.sticker.is_video:
            out_gif = f"kang_{message.id}.gif"
            to_delete.append(out_gif)
            
            cmd = f'ffmpeg -i "{path}" -vf "fps=15,scale=320:-1:flags=lanczos" -loop 0 "{out_gif}" -y'
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process.communicate()
            
            await client.send_animation(chat_id=message.chat.id, animation=out_gif, reply_to_message_id=target.id)

        # 3. ОБЫЧНЫЕ СТИКЕРЫ (.webp) -> JPG
        else:
            out_jpg = f"kang_{message.id}.jpg"
            to_delete.append(out_jpg)
            
            def convert_webp():
                with Image.open(path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(out_jpg, "JPEG", quality=95)
            
            await asyncio.to_thread(convert_webp)
            await client.send_photo(chat_id=message.chat.id, photo=out_jpg, reply_to_message_id=target.id)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Ошибка:**\n<code>{str(e)}</code>")
    finally:
        # Финальная чистка
        for f in to_delete:
            if os.path.exists(f):
                os.remove(f)