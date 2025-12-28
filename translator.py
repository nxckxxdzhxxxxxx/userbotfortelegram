from pyrogram import Client
from pyrogram.types import Message
from deep_translator import GoogleTranslator

# Словарь для красивого отображения языков
LANGUAGES_DICT = {
    "ru": "Русский",
    "en": "Английский",
    "de": "Немецкий",
    "fr": "Французский",
    "it": "Итальянский",
    "es": "Испанский",
    "tr": "Турецкий",
    "zh": "Китайский",
    "ja": "Японский",
    "ko": "Корейский",
    "uk": "Украинский",
    "kk": "Казахский"
}

async def translate_command(client: Client, message: Message):
    target_lang = "ru"
    text_to_translate = None

    # 1. Логика определения текста и языка
    if message.reply_to_message:
        text_to_translate = message.reply_to_message.text or message.reply_to_message.caption
        if len(message.command) > 1:
            target_lang = message.command[1].lower()
    elif len(message.command) > 1:
        first_arg = message.command[1].lower()
        if len(first_arg) == 2 and first_arg.isalpha():
            target_lang = first_arg
            text_to_translate = " ".join(message.command[2:])
        else:
            text_to_translate = " ".join(message.command[1:])

    if not text_to_translate:
        return await message.edit_text("❌ **Нечего переводить!**")

    await message.edit_text("🔄 **Перевожу...**")

    try:
        # Перевод
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text_to_translate)
        
        # Получаем красивое название языка из словаря (или код, если языка нет в списке)
        lang_name = LANGUAGES_DICT.get(target_lang, target_lang.upper())
        
        # Формируем ваш стиль вывода
        result = (
            f"🌍 **Перевод [{lang_name}]:**\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"{translated}"
        )
        
        await message.edit_text(result)
    except Exception as e:
        await message.edit_text(f"❌ **Ошибка:** <code>{str(e)}</code>")