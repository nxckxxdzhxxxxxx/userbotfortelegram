import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, 
    Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from pyrogram.errors import SessionPasswordNeeded
# Импортируем обновленные функции базы данных
from database import is_authorized, check_premium, set_premium, get_premium_remaining
from auth_engine import finalize_session 

login_data = {}            
active_login_clients = {}  

def get_code_kb():
    """Клавиатура для ввода кода (Inline)"""
    btns = []
    for i in range(1, 10, 3):
        btns.append([InlineKeyboardButton(str(j), callback_data=f"num_{j}") for j in range(i, i+3)])
    btns.append([
        InlineKeyboardButton("❌ Сброс", callback_data="num_cls"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("✅ Войти", callback_data="num_ok")
    ])
    return InlineKeyboardMarkup(btns)

async def finalize_login(user_id, temp_client, message_obj):
    """Вызывает движок авторизации и сообщает результат"""
    success, text = await finalize_session(user_id, temp_client)
    
    active_login_clients.pop(user_id, None)
    login_data.pop(user_id, None)

    if isinstance(message_obj, Message):
        await message_obj.reply(text, reply_markup=ReplyKeyboardRemove())
    else:
        await message_obj.edit_text(text)

def register_bot_handlers(bot: Client):
    
    @bot.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message):
        user_id = message.from_user.id
        days_left = get_premium_remaining(user_id)
        
        if is_authorized(user_id):
            status_text = f"✅ **Ваш юзербот активен!**\n📅 Подписка: еще {days_left} дн."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Управление", callback_data="none")]])
        elif days_left > 0:
            status_text = f"💎 **Подписка активна!** (осталось {days_left} дн.)\nТеперь вы можете привязать свой аккаунт."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔑 Привязать аккаунт", callback_data="start_login")]])
        else:
            status_text = "👋 **Привет!**\nДля использования юзербота необходимо приобрести подписку."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить подписку (0₽)", callback_data="buy_premium")]])
        
        await message.reply(status_text, reply_markup=kb)

    @bot.on_callback_query(filters.regex("^buy_premium$"))
    async def process_payment(client, query: CallbackQuery):
        user_id = query.from_user.id
        # Начисляем 30 дней подписки
        set_premium(user_id, days=30)
        
        await query.answer("🎉 Подписка успешно оформлена!", show_alert=True)
        await query.message.edit_text(
            "💎 **Премиум доступ активирован на 30 дней!**\n\nТеперь вы можете поделиться контактом для авторизации вашего юзербота.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Начать привязку", callback_data="start_login")]])
        )

    @bot.on_callback_query(filters.regex("^start_login$"))
    async def login_step_1(client, query: CallbackQuery):
        user_id = query.from_user.id
        
        if not check_premium(user_id):
            return await query.answer("❌ Срок вашей подписки истек!", show_alert=True)

        await query.answer()
        await query.message.reply(
            "📱 Нажмите кнопку ниже, чтобы отправить свой номер телефона через контакт:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📲 Поделиться контактом", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        login_data[user_id] = {"step": "wait_contact"}

    @bot.on_message(filters.private & (filters.contact | filters.text))
    async def message_handler(client, message):
        user_id = message.from_user.id
        if user_id not in login_data: return
        state = login_data[user_id]

        if state.get("step") == "wait_contact":
            phone = message.contact.phone_number if message.contact else message.text.strip()
            if not phone.startswith("+"): phone = "+" + phone
            
            await message.reply("⏳ Инициализация сессии...", reply_markup=ReplyKeyboardRemove())
            
            temp = Client(f"temp_{user_id}", int(os.getenv("API_ID")), os.getenv("API_HASH"), in_memory=True)
            await temp.connect()
            try:
                sent_code = await temp.send_code(phone)
                state.update({"step": "code", "phone": phone, "hash": sent_code.phone_code_hash, "code": ""})
                active_login_clients[user_id] = temp
                await message.reply(f"Введите код для `{phone}`:", reply_markup=get_code_kb())
            except Exception as e:
                await message.reply(f"❌ Ошибка: {e}")
                await temp.disconnect()
                login_data.pop(user_id, None)

        elif state.get("step") == "2fa" and message.text:
            temp = active_login_clients.get(user_id)
            try:
                await temp.check_password(message.text.strip())
                await finalize_login(user_id, temp, message)
            except Exception:
                await message.reply("❌ Неверный пароль 2FA.")

    @bot.on_callback_query(filters.regex("^num_"))
    async def code_callback(client, query: CallbackQuery):
        user_id = query.from_user.id
        if user_id not in login_data:
            return await query.answer("Сессия истекла.", show_alert=True)

        action = query.data.replace("num_", "")
        state = login_data[user_id]
        temp = active_login_clients.get(user_id)

        if action == "ok":
            await query.answer("Проверка...")
            try:
                await temp.sign_in(state["phone"], state["hash"], state["code"])
                await finalize_login(user_id, temp, query.message)
            except SessionPasswordNeeded:
                state["step"] = "2fa"
                await query.message.edit_text("🔐 Введите облачный пароль (2FA) текстом:")
            except Exception as e:
                await query.message.edit_text(f"❌ Ошибка: {e}")
        elif action == "cls":
            state["code"] = ""
            await query.message.edit_text("Код сброшен. Введите заново:", reply_markup=get_code_kb())
        else:
            await query.answer()
            state["code"] += action
            await query.message.edit_text(f"Код: `{'*' * len(state['code'])}`", reply_markup=get_code_kb())