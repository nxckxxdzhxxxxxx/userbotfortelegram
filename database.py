import sqlite3
from datetime import datetime, timedelta

DB_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # premium_until хранит дату в формате ISO (ГГГГ-ММ-ДД ЧЧ:ММ:СС)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            premium_until TEXT,
            is_auth INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def check_premium(user_id):
    """Проверяет, активна ли подписка на текущий момент"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        try:
            expire_date = datetime.fromisoformat(result[0])
            return datetime.now() < expire_date
        except ValueError:
            return False
    return False

def set_premium(user_id, days=30):
    """Начисляет подписку на X дней от текущего момента"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Вычисляем дату истечения
    new_expire_date = (datetime.now() + timedelta(days=days)).isoformat()
    
    cursor.execute("""
        INSERT INTO users (user_id, premium_until) 
        VALUES (?, ?) 
        ON CONFLICT(user_id) DO UPDATE SET premium_until = excluded.premium_until
    """, (user_id, new_expire_date))
    
    conn.commit()
    conn.close()

def get_premium_remaining(user_id):
    """Возвращает количество оставшихся дней (для вывода пользователю)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        expire_date = datetime.fromisoformat(result[0])
        remaining = expire_date - datetime.now()
        if remaining.days >= 0:
            return remaining.days
    return 0

def is_authorized(user_id):
    """Проверка, привязан ли уже юзербот"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_auth FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def add_user(user_id):
    """Помечает пользователя как авторизованного"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, is_auth) 
        VALUES (?, 1) 
        ON CONFLICT(user_id) DO UPDATE SET is_auth = 1
    """, (user_id,))
    conn.commit()
    conn.close()