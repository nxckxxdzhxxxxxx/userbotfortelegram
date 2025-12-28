import os
import asyncio
import glob
from dotenv import load_dotenv
from pyrogram import Client, idle
from handlers import register_handlers
from bot_handlers import register_bot_handlers
from database import init_db

load_dotenv(override=True)

active_users = {} 
SESSIONS_DIR = "sessions"

# Создаем папку для пользовательских сессий, если её нет
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

async def start_specific_user_bot(session_name, is_controller=False):
    """
    Запуск сессии юзербота с подробным выводом инфо в консоль.
    """
    global active_users
    try:
        workdir = "." if is_controller else SESSIONS_DIR
        
        client = Client(
            name=session_name,
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            workdir=workdir,
            device_model="ControllerBot" if is_controller else "UserBot",
            system_version="Windows 11"
        )
        
        register_handlers(client)
        await client.start()
        
        # Получаем данные об аккаунте для красивого лога
        me = await client.get_me()
        active_users[me.id] = client
        
        # Формируем имя для вывода (Юзернейм или Имя + Фамилия)
        display_name = f"@{me.username}" if me.username else f"{me.first_name} {me.last_name or ''}".strip()
        type_label = "👑 КОНТРОЛЛЕР" if is_controller else "👤 ЮЗЕРБОТ"
        
        print(f"✅ {type_label} запущен | {display_name} (ID: {me.id}) | Файл: {session_name}.session")
        
    except Exception as e:
        print(f"❌ Ошибка запуска [{session_name}.session]: {e}")

async def run_bot():
    init_db()
    
    # 1. Запуск бота-регистратора (интерфейс управления)
    public_bot = Client(
        name="bot_service", 
        api_id=int(os.getenv("API_ID")),
        api_hash=os.getenv("API_HASH"),
        bot_token=os.getenv("BOT_TOKEN"),
        workdir="." 
    )
    register_bot_handlers(public_bot)
    await public_bot.start()
    print("🤖 Бот-регистратор активен.")

    # 2. Запуск ГЛАВНОГО КОНТРОЛЛЕРА (из корня)
    if os.path.exists("controller_bot.session"):
        print("⚙️ Инициализация контроллера...")
        await start_specific_user_bot("controller_bot", is_controller=True)
    else:
        print("⚠️ Файл controller_bot.session не найден в корне.")

    # 3. Загрузка ПОЛЬЗОВАТЕЛЬСКИХ сессий (из папки sessions)
    session_files = glob.glob(os.path.join(SESSIONS_DIR, "*.session"))
    
    if session_files:
        user_sessions = [f for f in session_files if "controller_bot" not in f]
        print(f"📂 Найдено пользовательских сессий: {len(user_sessions)}")
        
        # Запускаем все сессии параллельно для скорости
        for s_path in user_sessions:
            name = os.path.basename(s_path).replace(".session", "")
            asyncio.create_task(start_specific_user_bot(name, is_controller=False))
            # Небольшая пауза между запусками, чтобы не нагружать процессор
            await asyncio.sleep(0.1) 
    else:
        print("ℹ️ В папке 'sessions' пока нет активных юзерботов.")

    # Ожидание завершения
    await idle()
    
    print("\n🛑 Завершение работы, остановка всех аккаунтов...")
    for app in active_users.values():
        try:
            await app.stop()
        except:
            pass
    await public_bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass