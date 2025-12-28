from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def who_command(client: Client, message: Message):
    try:
        target_user = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            user_input = message.command[1]
            try:
                target_user = await client.get_users(user_input)
            except:
                return await message.edit_text("❌ Пользователь не найден.")
        elif message.chat.type == ChatType.PRIVATE:
            target_user = await client.get_users(message.chat.id)

        if not target_user:
            return await message.edit_text("❌ Укажите пользователя.")

        info = (
            f"👤 <b>Ник:</b> {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 <b>ID:</b> <code>{target_user.id}</code>\n"
            f"🔗 <b>Username:</b> @{target_user.username if target_user.username else 'нет'}\n"
            f"📜 <b>Профиль:</b> <a href='tg://user?id={target_user.id}'>Ссылка</a>"
        )

        await message.edit_text(info)
    except Exception as e:
        print(f"Ошибка в who: {e}")