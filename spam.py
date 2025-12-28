import asyncio
from pyrogram import Client
from pyrogram.types import Message

# Глобальный флаг
spam_active = False

async def spam_command(client: Client, message: Message):
    global spam_active
    args = message.command
    
    if len(args) < 2:
        return await message.edit_text("❌ Использование: `.spam [интервал] [текст]`")

    try:
        interval = float(args[1])
    except ValueError:
        return await message.edit_text("❌ Интервал должен быть числом.")

    spam_active = True
    await message.delete()

    while spam_active:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(message.chat.id)
            else:
                if len(args) < 3: break
                await client.send_message(message.chat.id, " ".join(args[2:]))
            await asyncio.sleep(interval)
        except Exception:
            break

async def stop_spam(client: Client, message: Message):
    global spam_active
    spam_active = False
    await message.edit_text("🛑 **Спам остановлен!**")