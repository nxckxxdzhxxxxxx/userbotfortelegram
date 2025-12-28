from pyrogram import Client
from pyrogram.types import Message

async def langs_command(client: Client, message: Message):
    text = (
        "🌍 <b>Коды популярных языков:</b>\n\n"
        "🇷🇺 Русский — <code>ru</code>\n"
        "🇺🇸 Английский — <code>en</code>\n"
        "🇩🇪 Немецкий — <code>de</code>\n"
        "🇫🇷 Французский — <code>fr</code>\n"
        "🇮🇹 Итальянский — <code>it</code>\n"
        "🇪🇸 Испанский — <code>es</code>\n"
        "🇹🇷 Турецкий — <code>tr</code>\n"
        "🇨🇳 Китайский — <code>zh</code>\n"
        "🇯🇵 Японский — <code>ja</code>\n"
        "🇰🇷 Корейский — <code>ko</code>\n"
        "🇺🇦 Украинский — <code>uk</code>\n"
        "🇰🇿 Казахский — <code>kk</code>\n"
        "🇵🇱 Польский — <code>pl</code>\n\n"
        "💡 <i>Используйте эти коды в команде .tr, например:</i> <code>.tr en</code>"
    )
    await message.edit_text(text)