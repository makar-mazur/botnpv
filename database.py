import sqlite3
import time
from datetime import datetime, timedelta

DB_NAME = "vpn_database.db"


# def get_connection():
#     conn = sqlite3.connect(DB_NAME, timeout=30)
#     conn.execute("PRAGMA journal_mode=WAL")  # Включаем WAL
#     return conn


# Функция для создания таблиц, если они еще не существуют
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            active BOOLEAN DEFAULT 0,
            referrer_id INTEGER DEFAULT 0,
            subscription_end_date TIMESTAMP,
            subscription_frozen_date TIMESTAMP,
            is_frozen BOOLEAN DEFAULT 0,
            promo_ban BOOLEAN DEFAULT 0,
            left BOOLEAN
         );
    ''')

    cursor.execute('''
        CREATE TABLE used_promo_codes (
            user_id INTEGER,
            promo_code TEXT,
            PRIMARY KEY (user_id, promo_code)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            promo_code VARCHAR(50) NOT NULL UNIQUE,
            used_promo_code_count INTEGER DEFAULT 0,
            bonus_days INT NOT NULL,
            referral_id VARCHAR(50) NOT NULL UNIQUE,
            total_amount DECIMAL(10, 2) DEFAULT 0.0,
            active_users INT DEFAULT 0,
            inactive_users INT DEFAULT 0,
            total_users INT DEFAULT 0,
            age_days INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructions (
            page INTEGER PRIMARY KEY,
            text TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def promo_code_already_used(user_id: int, promo_code: str) -> bool:
    # Запрос для проверки использования промокода
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "SELECT 1 FROM used_promo_codes WHERE user_id = ? AND promo_code = ?"
    result = cursor.execute(query, (user_id, promo_code)).fetchone()
    return result is not None


def save_used_promo_code(user_id: int, promo_code: str):
    # Сохранение использования промокода
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "INSERT INTO used_promo_codes (user_id, promo_code) VALUES (?, ?)"
    cursor.execute(query, (user_id, promo_code))
    conn.commit()


def if_ban_promo(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT promo_ban FROM users WHERE user_id = ?', (user_id,))
    promo_ban = cursor.fetchone()[0]
    conn.close()
    return promo_ban


def ban_promo(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET promo_ban = TRUE WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def add_used_promo_code_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE campaigns SET used_promo_code_count = used_promo_code_count + 1')
    conn.commit()
    conn.close()


def get_used_promo_code_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(used_promo_code_count) FROM campaigns')
    total_usages = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return total_usages if total_usages is not None else 0


# def add_user(user_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
#     conn.commit()
#     conn.close()


def add_user(user_id, referrer_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if referrer_id != None:
        return cursor.execute("INSERT INTO users (user_id, referrer_id) VALUES (?, ?)", (user_id, referrer_id,))
    else:
        return cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


# def user_exists(user_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
#     result = cursor.fetchone()
#     conn.close()
#
#     # Если результат не пустой, пользователь существует
#     return result is not None


def user_exists(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return bool(len(result))


def add_subscription(user_id, days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_end_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result and result[0]:
        try:
            end_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S") + timedelta(days=days)
        except ValueError:
            end_date = datetime.now() + timedelta(days=days)
    else:
        end_date = datetime.now() + timedelta(days=days)

    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, subscription_end_date) VALUES (?, ?)",
        (user_id, end_date.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def add_user_with_subscription(user_id, days, referrer_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Проверка, существует ли пользователь
    cursor.execute("SELECT subscription_end_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    # Если referrer_id указан, добавляем его
    if referrer_id is not None:
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, referrer_id) VALUES (?, ?)",
            (user_id, referrer_id)
        )
    else:
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )

    # Определение новой даты окончания подписки
    if result and result[0]:  # Если пользователь уже существует и у него есть дата подписки
        try:
            end_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S") + timedelta(days=days)
        except ValueError:
            end_date = datetime.now() + timedelta(days=days)
    else:
        end_date = datetime.now() + timedelta(days=days)

    # Обновление даты окончания подписки
    cursor.execute(
        "UPDATE users SET subscription_end_date = ? WHERE user_id = ?",
        (end_date.strftime("%Y-%m-%d %H:%M:%S"), user_id)
    )

    conn.commit()
    conn.close()



def is_subscription_active(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_end_date, is_frozen FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result and result[0] and not result[1]:
        end_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        return datetime.now() < end_date
    return False



def get_time_until_subscription_end(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_end_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        try:
            end_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            remaining_time = end_date - datetime.now()

            if remaining_time.total_seconds() > 0:
                days = remaining_time.days
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                time_str = f"{days} дней, {hours} часов, {minutes} минут, {seconds} секунд"
                return time_str
        except ValueError:
            return "Подписка не активна."
    return "Подписка истекла."


def freeze_subscription(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_frozen = ? WHERE user_id = ?', (1, user_id))  # 1 - заморозить
    conn.commit()
    conn.close()


def unfreeze_subscription(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_frozen = ? WHERE user_id = ?', (0, user_id))  # 0 - разморозить
    conn.commit()
    conn.close()


def is_subscription_frozen(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT is_frozen FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1


def get_campaign_by_promo_code(promo_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM campaigns WHERE promo_code = ?", (promo_code,)).fetchone()
    conn.commit()
    conn.close()
    return result


def get_instruction(page):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM instructions WHERE page = ?', (page,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else "Инструкция для этой страницы отсутствует."


def update_instruction(page, new_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO instructions (page, text) 
        VALUES (?, ?)
        ON CONFLICT(page) DO UPDATE SET text = ? 
    ''', (page, new_text, new_text))
    conn.commit()
    conn.close()


def add_campaign(name, promo_code, bonus_days, referral_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO campaigns (name, promo_code, bonus_days, referral_id) 
           VALUES (?, ?, ?, ?)''', (name, promo_code, bonus_days, referral_id)
    )
    conn.commit()
    conn.close()


def get_all_promo_codes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT promo_code FROM campaigns')
    promo_codes = [row[0] for row in cursor.fetchall()]
    # promo_codes = cursor.fetchall()
    conn.commit()
    conn.close()
    return promo_codes


def get_camp(camp_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM campaigns WHERE camp_id = ?', (camp_id,))
    camp = cursor.fetchone()
    conn.commit()
    conn.close()
    return camp


def get_all_campaigns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM campaigns')
    campaigns = cursor.fetchall()
    conn.commit()
    conn.close()
    return campaigns


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    return user


def get_total_user_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    user_ids = cursor.fetchall()
    conn.commit()
    conn.close()
    return user_ids


def get_total_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return total_users


def get_total_campaigns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM campaigns')
    total_campaigns = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return total_campaigns


def add_payment(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO payments (user_id, amount) VALUES (?, ?)', (user_id, amount,))
    conn.commit()
    conn.close()


def get_total_payments():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM payments')
    total_payments = cursor.fetchone()[0] or 0
    conn.commit()
    conn.close()
    return total_payments


# def set_bonus_received(user_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     try:
#         cursor.execute('UPDATE users SET bonus_received = ? WHERE user_id = ?', (True, user_id))
#         conn.commit()
#         print(f"Successfully updated bonus_received for user_id {user_id}")
#     except sqlite3.Error as e:
#         print(f"SQL error: {e}")
#     finally:
#         conn.close()


# def set_bonus_received(user_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute(f'UPDATE users SET bonus_received == ? WHERE user_id == ?', [True, user_id,])
#     conn.commit()
#     conn.close()


def activate_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET active = ? WHERE user_id = ?', (True, user_id,))
    conn.commit()
    conn.close()


def deactivate_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET active = ? WHERE user_id = ?', (False, user_id,))
    conn.commit()
    conn.close()


def get_active_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE active = ?', (True,))
    active_count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return active_count


def get_inactive_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE active = ?', (False,))
    inactive_count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return inactive_count
