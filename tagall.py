import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def tag_all_command(client: Client, message: Message):
    # Проверяем, что это группа или супергруппа
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return await message.edit_text("❌ **Эту команду можно использовать только в группах!**")

    # Текст, который будет идти перед упоминаниями
    text = " ".join(message.command[1:]) if len(message.command) > 1 else "Внимание всем!"
    
    await message.delete() # Удаляем команду .tagall
    
    members = []
    # Собираем всех участников (кроме ботов и самого себя)
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot and not member.user.is_self:
            # Используем упоминание через ник (если есть) или через скрытую ссылку (если ника нет)
            mention = member.user.mention(member.user.first_name or "User")
            members.append(mention)

    # Разбиваем список на порции по 5 человек
    chunk_size = 5
    for i in range(0, len(members), chunk_size):
        # Если юзербот был остановлен, прерываем цикл
        chunk = members[i:i + chunk_size]
        tag_line = f"📢 **{text}**\n\n" + ", ".join(chunk)
        
        await client.send_message(message.chat.id, tag_line)
        
        # Небольшая пауза между сообщениями, чтобы не спамить слишком быстро
        await asyncio.sleep(1.5)