import os
import sys
import asyncio
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import MessageIdInvalid

async def restart_command(client: Client, message: Message):
    try:
        # Пытаемся изменить текст сообщения
        await message.edit_text("🔄 **Система перезагружается...**\n*Подождите 2-3 секунды*")
    except MessageIdInvalid:
        # Если сообщение нельзя изменить, отправляем новое
        await client.send_message(message.chat.id, "🔄 **Система перезагружается...**")
    
    await asyncio.sleep(2)
    
    # Полный путь к python.exe
    executable = sys.executable
    # Полный путь к основному файлу main.py
    script = os.path.abspath(sys.argv[0])
    # Аргументы запуска
    args = sys.argv[1:]

    print(f"♻️ Перезапуск: {executable} {script}")

    # Исправленная строка (без ошибки SyntaxError):
    # Оборачиваем пути в кавычки специально для Windows и папок с пробелами
    os.execv(executable, [f'"{executable}"', f'"{script}"'] + args)