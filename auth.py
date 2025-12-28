import os
import asyncio
from pyrogram import Client
from dotenv import load_dotenv

async def auth_owner():
    load_dotenv(override=True)
    
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    owner_id = os.getenv("OWNER_ID")

    if not owner_id:
        print("❌ Ошибка: В .env не указан OWNER_ID!")
        return

    print(f"🚀 Начинаем авторизацию владельца (ID: {owner_id})")
    print("Сессия будет сохранена в корень проекта.")

    # Создаем клиента в корне (workdir=".")
    app = Client(
        name="controller_bot", 
        api_id=int(api_id),
        api_hash=api_hash,
        workdir="."
    )

    async with app:
        me = await app.get_me()
        print(f"✅ Успешно! Аккаунт {me.first_name} авторизован.")
        print(f"Файл controller_bot.session создан в корне.")

if __name__ == "__main__":
    asyncio.run(auth_owner())