import os
import httpx
import asyncio
import random
from urllib.parse import quote
from pyrogram import Client
from pyrogram.types import Message

async def generate_image_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ **Введите описание!**\nПример: `.gen котик в космосе`")

    prompt = " ".join(message.command[1:])
    status_msg = await message.edit_text(f"🎨 **Рисую:** `{prompt}`...")

    # Временный файл
    file_path = f"gen_{message.id}.jpg"

    try:
        # Кодируем промпт
        encoded_prompt = quote(prompt)
        
        # Генерируем случайное число (seed), чтобы картинки всегда были разными
        seed = random.randint(1, 1000000)
        
        # Используем современную модель Flux (бесплатно через Pollinations)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&model=flux&nologo=true"

        # Скачиваем картинку
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.get(image_url)
            
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                # Отправляем файл в Telegram
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_path,
                    caption=f"✅ **Результат по запросу:** `{prompt}`",
                    reply_to_message_id=message.id
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text(f"❌ **Ошибка сервиса:** `{response.status_code}`. Попробуйте позже.")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Ошибка:** `{str(e)}`")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)