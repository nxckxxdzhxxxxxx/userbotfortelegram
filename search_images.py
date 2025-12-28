import asyncio
from pyrogram import Client
from pyrogram.types import Message, InputMediaPhoto
from duckduckgo_search import DDGS

async def search_images_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ **Введите запрос!**\nПример: `.img океан`")

    query = " ".join(message.command[1:])
    status_msg = await message.edit_text(f"🔍 **Ищу картинки в DuckDuckGo:** `{query}`...")

    try:
        # Используем современный метод поиска
        def fetch_images():
            with DDGS() as ddgs:
                # Берем первые 8 результатов
                results = [r['image'] for r in ddgs.images(query, max_results=8)]
                return results

        urls = await asyncio.to_thread(fetch_images)

        if not urls:
            return await status_msg.edit_text(f"❌ **По запросу `{query}` ничего не найдено.**")

        # Формируем альбом
        media_group = []
        for i, url in enumerate(urls):
            caption = f"🖼 **Результат:** `{query}`" if i == 0 else ""
            media_group.append(InputMediaPhoto(url, caption=caption))

        # Отправляем
        await client.send_media_group(
            chat_id=message.chat.id,
            media=media_group,
            reply_to_message_id=message.id
        )
        await status_msg.delete()

    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            await status_msg.edit_text("❌ **Ошибка:** Доступ заблокирован поисковиком. Попробуй включить/выключить прокси.")
        else:
            await status_msg.edit_text(f"❌ **Ошибка поиска:** `{error_msg[:100]}`")