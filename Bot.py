import requests
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Ваши ключи
BOT_TOKEN = "8369109357:AAFieFMzE2bX90up2SeTw2JR56QH_XEBxWQ"
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот с DeepSeek 3.1 Free активирован! Задавайте вопросы.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/DeepSeekFreeBot",
            "X-Title": "DeepSeek Telegram Bot"
        }
        
        data = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            url=OPENROUTER_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            
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
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Бот запущен с DeepSeek 3.1 Free...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
