import asyncio
import httpx
from urllib.parse import quote # Стандартная библиотека Python
from pyrogram import Client
from pyrogram.types import Message

async def web_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Введите запрос!</b>")

    query = " ".join(message.command[1:])
    await message.edit_text(f"📡 <b>Думаю...</b>")

    try:
        # Безопасно кодируем запрос для URL
        encoded_query = quote(query)
        
        # Используем Pollinations AI (бесплатно, стабильно, без HAR/Cookies)
        url = f"https://text.pollinations.ai/{encoded_query}?model=openai&cache=false"

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as ai_client:
            response = await ai_client.get(url)
            
            if response.status_code == 200:
                response_text = response.text
                
                if not response_text:
                    return await message.edit_text("❌ Я ничего не нашел")

                output = f"🤖 <b>Ответ на ваш запрос:</b>\n\n{response_text}"
                
                # Лимит Telegram 4096 символов
                if len(output) > 4096:
                    output = output[:4090] + "..."
                
                await message.edit_text(output)
            else:
                await message.edit_text(f"❌ <b>Ошибка сервера ({response.status_code})</b>")

    except Exception as e:
        await message.edit_text(f"❌ <b>Ошибка:</b>\n<code>{str(e)}</code>")