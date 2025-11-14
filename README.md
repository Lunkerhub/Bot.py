# AI Telegram Bot с Системой Подписок

Telegram бот на базе Google Gemini 2.0 с полноценной системой подписок и учётом пользователей.

## Возможности

- 🤖 Умные ответы на базе Google Gemini 2.0
- 💎 Система подписок (FREE, VIP, PREMIUM, ADMIN)
- 📊 Учёт запросов для каждого пользователя
- 🗄️ База данных SQLite
- 🔄 Автоматическое разбиение длинных ответов
- 🔒 Безопасное хранение API ключей
- 👑 Безлимитный доступ для владельца (@Honorpadx9lte)

## Setup

### Prerequisites

1. **Telegram Bot Token**: Get one from [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` to BotFather
   - Follow the instructions to create your bot
   - Copy the API token provided

2. **OpenRouter API Key**: Sign up at [openrouter.ai](https://openrouter.ai)
   - Create an account
   - Navigate to API Keys section
   - Generate a new API key

### Environment Variables

The bot requires two environment variables to be set in Replit Secrets:

- `BOT_TOKEN`: Your Telegram bot token
- `OPENROUTER_API_KEY`: Your OpenRouter API key

### Running the Bot

The bot starts automatically via the configured workflow. You can also run it manually:

```bash
python Bot.py
```

## Система Подписок

### 🆓 FREE (по умолчанию)
- **20 запросов в день**
- Базовые возможности
- Автоматически для всех новых пользователей

### ⭐ VIP
- **100 запросов в день**
- Приоритетная обработка

### 💫 PREMIUM
- **500 запросов в день**
- Максимальная скорость
- Расширенные возможности

### 👑 ADMIN (владелец)
- **Безлимитные запросы**
- Автоматически для @Honorpadx9lte
- Все функции

## Использование

### Команды бота:

- `/start` - Запуск бота и показ статистики
- `/status` - Проверить свою статистику
- `/subscription` - Информация о подписках

### Как пользоваться:

1. Найдите бота в Telegram
2. Отправьте `/start` для активации
3. Напишите любой вопрос
4. Получите ответ от AI
5. Используйте `/status` для проверки лимитов

## Технические Детали

- **Язык**: Python 3.12
- **Фреймворк**: python-telegram-bot 22.5
- **AI Модель**: Google Gemini 2.0 Flash (бесплатная)
- **API Provider**: OpenRouter
- **База данных**: SQLite 3
- **Лимиты**: Автоматический сброс каждый день

## Структура Проекта

```
.
├── Bot.py              # Основной код бота
├── database.py         # Система подписок и БД
├── users.db            # База данных пользователей (создаётся автоматически)
├── pyproject.toml      # Python зависимости
├── .gitignore         # Git ignore
└── README.md          # Документация
```

## База Данных

Бот автоматически создаёт SQLite базу данных `users.db` со следующей структурой:

**Таблица users:**
- `user_id` - ID пользователя Telegram
- `username` - Username пользователя
- `subscription_type` - Тип подписки (FREE/VIP/PREMIUM/ADMIN)
- `requests_today` - Количество запросов сегодня
- `last_request_date` - Дата последнего запроса
- `total_requests` - Всего запросов за всё время
- `created_at` - Дата регистрации

## Error Handling

The bot includes comprehensive error handling:
- API errors are caught and reported to users
- Missing environment variables are detected at startup
- Long messages are automatically split into chunks
- Request timeouts are configured (30 seconds)

## Development

To modify the bot behavior, edit `Bot.py`. The main components are:

- `start()`: Handles the /start command
- `handle_message()`: Processes user messages and queries the AI
- `main()`: Sets up the bot and starts polling

## Security

- API keys are stored as environment variables, not in code
- The original hardcoded keys have been removed
- .gitignore prevents sensitive files from being committed
