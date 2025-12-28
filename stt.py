import os
import asyncio
from pyrogram import Client
from pyrogram.types import Message
import speech_recognition as sr
from pydub import AudioSegment

async def stt_command(client: Client, message: Message):
    target = message.reply_to_message
    if not target or not (target.voice or target.audio):
        return await message.edit_text("❌ Ответьте на голосовое сообщение.")

    status_msg = await message.edit_text("🎤 **Загружаю аудио...**")
    
    # Используем абсолютные пути, чтобы избежать путаницы с директориями
    base_path = os.path.abspath(os.getcwd())
    temp_ogg = os.path.join(base_path, f"stt_{message.id}.ogg")
    temp_wav = os.path.join(base_path, f"stt_{message.id}.wav")

    try:
        # Скачиваем файл и ждем завершения
        downloaded_file = await client.download_media(target, file_name=temp_ogg)
        
        if not downloaded_file or not os.path.exists(temp_ogg):
            return await status_msg.edit_text("❌ **Ошибка:** Не удалось сохранить файл.")

        await status_msg.edit_text("⚙️ **Расшифровываю...**")

        # Конвертация
        def convert_audio():
            audio = AudioSegment.from_file(temp_ogg)
            audio.export(temp_wav, format="wav")
        
        await asyncio.to_thread(convert_audio)

        # Распознавание
        def recognize():
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data, language="ru-RU")

        text = await asyncio.to_thread(recognize)
        await status_msg.edit_text(f"📝 **Расшифровка:**\n\n{text}")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Ошибка:** <code>{str(e)}</code>")
    
    finally:
        # Чистим временные файлы в любом случае
        for f in [temp_ogg, temp_wav]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass