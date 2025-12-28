import os
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Импорт вашей функции проверки из БД
from database import is_authorized

# Импортируем модули команд
import who, utils, commands, spam, search, web, download, settings, music
import search_images, stt, translator, lang_codes, sticker, generate, tagall, quote

load_dotenv(override=True)

def register_handlers(app: Client):
    @app.on_message(filters.text & ~filters.service)
    async def main_handler(client: Client, message: Message):
        try:
            # 1. ГЛАВНОЕ ИСПРАВЛЕНИЕ: 
            # Бот должен обрабатывать команду ТОЛЬКО если ее отправил владелец ЭТОГО аккаунта.
            # Это предотвращает ошибку 403 (пытаться редактировать чужое сообщение).
            if not message.from_user or not message.from_user.is_self:
                return 

            # Проверяем наличие текста и префикса (точки)
            if not message.text or not message.text.startswith("."):
                return

            # Отладочный принт в консоль
            print(f"DEBUG: [Acc: {client.name}] Выполняю свою команду: {message.text}")

            parts = message.text.split(maxsplit=1)
            cmd = parts[0][1:].lower()

            # Карта команд
            cmd_map = {
                "who": who.who_command, 
                "restart": utils.restart_command, 
                "commands": commands.commands_command, 
                "spam": spam.spam_command, 
                "stopspam": spam.stop_spam, 
                "search": search.search_command,
                "web": web.web_command, 
                "dl": download.savett_command, 
                "settings": settings.settings_command, 
                "m": music.music_search_command, 
                "img": search_images.search_images_command, 
                "stt": stt.stt_command, 
                "tr": translator.translate_command, 
                "langs": lang_codes.langs_command,
                "st": sticker.sticker_command, 
                "kang": sticker.kang_command, 
                "gen": generate.generate_image_command, 
                "tagall": tagall.tag_all_command, 
                "quote": quote.quote_command
            }

            if cmd in cmd_map:
                # Нарезаем команду для модулей, которым нужен message.command
                message.command = message.text.split()
                await cmd_map[cmd](client, message)

        except Exception as e:
            print(f"❌ Ошибка в обработчике [{client.name}]: {e}")
            traceback.print_exc()