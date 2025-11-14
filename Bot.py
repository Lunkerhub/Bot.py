import requests
import json
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

# Инициализация базы данных
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Без username"
    
    # Создаём пользователя если его нет
    if not db.get_user(user_id):
        db.create_user(user_id, username)
    
    stats = db.get_user_stats(user_id)
    
    welcome_msg = f"""🤖 Добро пожаловать в AI бота на базе Google Gemini 2.0!

👤 Пользователь: @{username}
📊 Подписка: {stats['subscription']}
📈 Запросов сегодня: {stats['requests_today']}/{stats['limit']}
📝 Всего запросов: {stats['total_requests']}

💬 Просто напишите мне любой вопрос!

📋 Доступные команды:
/start - Информация о боте
/status - Ваша статистика
/subscription - Информация о подписках"""
    
    await update.message.reply_text(welcome_msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику пользователя"""
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    if not stats:
        await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
        return
    
    status_msg = f"""📊 Ваша статистика:

👤 Пользователь: @{stats['username']}
💎 Подписка: {stats['subscription']}
📈 Использовано сегодня: {stats['requests_today']}/{stats['limit']}
📝 Всего запросов: {stats['total_requests']}"""
    
    await update.message.reply_text(status_msg)

async def subscription_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о подписках"""
    info_msg = """💎 Доступные подписки:

🆓 FREE (бесплатно)
   • 20 запросов в день
   • Базовые возможности
   
⭐ VIP
   • 100 запросов в день
   • Приоритетная обработка
   
💫 PREMIUM
   • 500 запросов в день
   • Максимальная скорость
   • Расширенные возможности
   
👑 ADMIN (только владелец)
   • Безлимитные запросы
   • Все функции
   
📧 Для улучшения подписки свяжитесь с @Honorpadx9lte"""
    
    await update.message.reply_text(info_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "Без username"
    
    try:
        # Проверка лимита запросов
        can_request, sub_type, requests_count = db.can_make_request(user_id, username)
        
        if not can_request:
            await update.message.reply_text(
                f"❌ Вы исчерпали дневной лимит запросов!\n\n"
                f"📊 Подписка: {sub_type}\n"
                f"📈 Использовано: {requests_count}\n\n"
                f"💡 Используйте /subscription для информации о подписках"
            )
            return
        
        logging.info(f"Получено сообщение от @{username}: {user_message[:50]}...")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/DeepSeekFreeBot",
            "X-Title": "DeepSeek Telegram Bot"
        }
        
        data = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        logging.info(f"Отправка запроса к OpenRouter...")
        response = requests.post(
            url=OPENROUTER_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        logging.info(f"Получен ответ от OpenRouter: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            
            # Увеличиваем счётчик запросов
            db.increment_request(user_id)
            
            # Отправляем ответ
            if len(bot_response) > 4000:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
                
        else:
            error_msg = f"❌ Ошибка API: {response.status_code}"
            try:
                error_detail = response.json().get('error', {}).get('message', 'Неизвестная ошибка')
                error_msg += f"\nДетали: {error_detail}"
            except:
                pass
            await update.message.reply_text(error_msg)
                
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при обработке запроса")

def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN environment variable is not set!")
        return
    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable is not set!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("subscription", subscription_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Бот запущен с Google Gemini 2.0...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
