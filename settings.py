import os
from pyrogram import Client
from pyrogram.types import Message
from dotenv import load_dotenv

async def settings_command(client: Client, message: Message):
    # Принудительно обновляем данные из .env
    load_dotenv(override=True) 

    # Получаем настройки
    max_size = os.getenv("MAX_DOWNLOAD_SIZE", "10")
    proxy_url = os.getenv("PROXY_URL")
    
    # Получаем номер и добавляем статус
    sub_raw = os.getenv("SUBSCRIPTION_NUMBER")
    if sub_raw:
        sub_info = f"<code>{sub_raw}</code> (Платный) ✅"
    else:
        sub_info = "<i>Бесплатная версия</i>"
    
    # Проверка прокси
    if proxy_url:
        host = proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url.split("//")[-1]
        proxy_status = f"✅ Подключен (<code>{host}</code>)"
    else:
        proxy_status = "❌ Выключен"

    # Формируем текст
    settings_text = (
        "⚙️ <b>Настройки Юзербота</b>\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💎 <b>Подписка:</b> {sub_info}\n"
        f"📥 <b>Лимит загрузки:</b> <code>{max_size} MB</code>\n"
        f"🌐 <b>Прокси (SOCKS5):</b> {proxy_status}\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "<i>Управление доступно через бота-контроллера.</i>"
    )

    await message.edit_text(settings_text)