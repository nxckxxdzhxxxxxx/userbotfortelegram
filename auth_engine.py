import os
import asyncio
from pyrogram import Client

SESSIONS_DIR = "sessions"

async def finalize_session(user_id, temp_client):
    new_app = None
    try:
        from handlers import register_handlers
        import main
        from database import add_user
        
        # 1. Получаем реальный ID аккаунта из временного клиента
        if not temp_client.is_connected:
            await temp_client.connect()
        
        me = await temp_client.get_me()
        real_id = str(me.id)
        
        # 2. Экспортируем данные авторизации (ключи), а не просто строку
        # Мы НЕ останавливаем temp_client сразу, чтобы не потерять ключи в памяти
        
        # 3. Путь к файлу
        file_path = os.path.abspath(os.path.join(SESSIONS_DIR, f"{real_id}.session"))

        # 4. СОЗДАЕМ КЛИЕНТ БЕЗ session_string
        # Это заставит Pyrogram создать нормальный SQLite файл
        new_app = Client(
            name=real_id,
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            workdir=SESSIONS_DIR,
            device_model=f"UserBot_{real_id}"
        )

        # 5. ХАК ДЛЯ ПЕРЕНОСА: Копируем ключи напрямую в хранилище нового клиента
        # Это позволит избежать ввода номера телефона, так как ключи уже будут в файле
        await new_app.storage.open()
        await new_app.storage.dc_id(await temp_client.storage.dc_id())
        await new_app.storage.test_mode(await temp_client.storage.test_mode())
        await new_app.storage.auth_key(await temp_client.storage.auth_key())
        await new_app.storage.user_id(await temp_client.storage.user_id())
        await new_app.storage.is_bot(await temp_client.storage.is_bot())
        await new_app.storage.close() # Закрываем, чтобы SQLite записал данные на диск

        # Теперь можно закрыть временный клиент
        try:
            await temp_client.stop(block=False)
        except:
            pass

        # 6. Запускаем основной клиент уже из созданного файла
        register_handlers(new_app)
        await new_app.start()
        
        # Принудительно сохраняем и закрываем/открываем для Windows
        await new_app.storage.save()
        
        add_user(me.id)
        main.active_users[me.id] = new_app

        print(f"🚀 Файл {real_id}.session успешно создан и записан!")
        return True, f"✅ Аккаунт {real_id} привязан. Файл сохранен в папке sessions."

    except Exception as e:
        print(f"❌ Ошибка в auth_engine: {e}")
        return False, f"❌ Ошибка: {e}"