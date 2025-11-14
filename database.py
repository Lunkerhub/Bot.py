import sqlite3
from datetime import datetime, timedelta
import logging

class Database:
    def __init__(self, db_file="users.db"):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                subscription_type TEXT DEFAULT 'FREE',
                requests_today INTEGER DEFAULT 0,
                last_request_date TEXT,
                total_requests INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Получить пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def create_user(self, user_id, username):
        """Создать нового пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Владелец получает ADMIN подписку
        subscription = 'ADMIN' if username == 'Honorpadx9lte' else 'FREE'
        
        cursor.execute('''
            INSERT INTO users (user_id, username, subscription_type, last_request_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, subscription, datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Создан новый пользователь: {username} ({subscription})")
    
    def can_make_request(self, user_id, username):
        """Проверка, может ли пользователь сделать запрос"""
        user = self.get_user(user_id)
        
        if not user:
            self.create_user(user_id, username)
            user = self.get_user(user_id)
        
        user_id, username, sub_type, requests_today, last_date, total, created = user
        
        # ADMIN = безлимит
        if sub_type == 'ADMIN':
            return True, sub_type, -1
        
        # Проверка даты
        today = datetime.now().strftime('%Y-%m-%d')
        if last_date != today:
            # Новый день - сброс счётчика
            requests_today = 0
        
        # Лимиты по подпискам
        limits = {
            'FREE': 20,
            'VIP': 100,
            'PREMIUM': 500
        }
        
        limit = limits.get(sub_type, 20)
        
        if requests_today >= limit:
            return False, sub_type, requests_today
        
        return True, sub_type, requests_today
    
    def increment_request(self, user_id):
        """Увеличить счётчик запросов"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            UPDATE users 
            SET requests_today = requests_today + 1,
                total_requests = total_requests + 1,
                last_request_date = ?
            WHERE user_id = ?
        ''', (today, user_id))
        
        # Сброс счётчика если новый день
        cursor.execute('''
            UPDATE users 
            SET requests_today = 1
            WHERE user_id = ? AND last_request_date != ?
        ''', (user_id, today))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id):
        """Получить статистику пользователя"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        user_id, username, sub_type, requests_today, last_date, total, created = user
        
        # Проверка даты
        today = datetime.now().strftime('%Y-%m-%d')
        if last_date != today:
            requests_today = 0
        
        limits = {
            'FREE': 20,
            'VIP': 100,
            'PREMIUM': 500,
            'ADMIN': 'Безлимит'
        }
        
        return {
            'username': username,
            'subscription': sub_type,
            'requests_today': requests_today,
            'limit': limits.get(sub_type, 20),
            'total_requests': total
        }
    
    def upgrade_subscription(self, user_id, new_sub_type):
        """Изменить подписку пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET subscription_type = ? WHERE user_id = ?', 
                      (new_sub_type, user_id))
        
        conn.commit()
        conn.close()
