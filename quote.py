import httpx
import os
import io
import base64
from PIL import Image, ImageFilter, ImageDraw
from pyrogram import Client
from pyrogram.types import Message

async def quote_command(client: Client, message: Message):
    target = message.reply_to_message
    if not target or not (target.text or target.caption):
        return await message.edit_text("❌ **Ответьте на сообщение!**")

    status_msg = await message.edit_text("🌌 **Создаю крупный план...**")

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1b1b", 
        "messages": [{
            "entities": [],
            "avatar": True,
            "from": {
                "id": target.from_user.id,
                "first_name": target.from_user.first_name or "User",
                "last_name": target.from_user.last_name or "",
                "username": target.from_user.username or "",
                "language_code": target.from_user.language_code or "en"
            },
            "text": target.text or target.caption,
            "replyMessage": {}
        }]
    }

    file_path = f"large_quote_{message.id}.jpg"
    bg_path = "bg.jpg" 

    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://bot.lyo.su/quote/generate", 
                json=payload, 
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                image_base64 = data["result"]["image"]
                img_bytes = base64.b64decode(image_base64)
                quote_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

                # --- РАБОТА С ФОНОМ (1280x720) ---
                if os.path.exists(bg_path):
                    base = Image.open(bg_path).convert("RGB")
                    base = base.resize((1280, 720), Image.LANCZOS)
                    base = base.filter(ImageFilter.GaussianBlur(radius=2))
                else:
                    base = Image.new("RGB", (1280, 720), (15, 15, 30))
                    # Простой градиент
                    draw = ImageDraw.Draw(base)
                    for i in range(720):
                        draw.line([(0, i), (1280, i)], fill=(int(20+i/20), 15, int(40+i/15)))

                # --- УВЕЛИЧЕННАЯ КОМПОЗИЦИЯ ---
                
                # Задаем целевую ширину (90% от ширины фона)
                target_width = int(base.width * 0.9)
                
                # Рассчитываем множитель масштаба
                width_ratio = target_width / quote_img.width
                
                # Новые размеры
                new_w = int(quote_img.width * width_ratio)
                new_h = int(quote_img.height * width_ratio)
                
                # Если цитата стала слишком высокой и не влезает в экран (85% высоты)
                if new_h > base.height * 0.85:
                    height_ratio = (base.height * 0.85) / quote_img.height
                    new_w = int(quote_img.width * height_ratio)
                    new_h = int(quote_img.height * height_ratio)

                # Изменяем размер (используем LANCZOS для сохранения четкости текста)
                quote_img = quote_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Центрируем на фоне
                x = (base.width - quote_img.width) // 2
                y = (base.height - quote_img.height) // 2

                # Накладываем
                base.paste(quote_img, (x, y), quote_img)
                
                # Сохраняем
                base.save(file_path, "JPEG", quality=100, optimize=True)

                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_path,
                    caption=f"🌌 **Цитата:** {target.from_user.first_name}",
                    reply_to_message_id=target.id
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Ошибка API.")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Ошибка:** `{str(e)}`")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)