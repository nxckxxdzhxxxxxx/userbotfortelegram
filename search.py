from pyrogram import Client
from pyrogram.types import Message

async def search_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ Введите текст для поиска в чате.")

    query = " ".join(message.command[1:])
    await message.edit_text(f"🔍 Ищу в сообщениях: <b>{query}</b>...")

    results = []
    # Поиск сообщений в текущем чате
    async for msg in client.search_messages(message.chat.id, query=query, limit=5):
        text_preview = (msg.text[:30] + "...") if msg.text and len(msg.text) > 30 else (msg.text or "Медиа")
        results.append(f"• <a href='{msg.link}'>{text_preview}</a>")

    if not results:
        await message.edit_text(f"❌ В этом чате ничего не найдено по запросу: <b>{query}</b>")
    else:
        output = f"✅ <b>Найдено в чате ({query}):</b>\n\n" + "\n".join(results)
        await message.edit_text(output, disable_web_page_preview=True)