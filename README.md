# ALT Controller Bot

Универсальный Telegram-бот для администрирования каналов: мультиканальный постинг, очередь публикаций, реакции и аналитика.

## Возможности (MVP)

- Подключение и настройка каналов без правок кода.
- Мастер публикаций с поддержкой текста, медиа, кнопок и реакций.
- Очередь и отложенные публикации с учётом часовых поясов.
- Подсчёт кликов и реакций, экспорт CSV.
- Управление ролями владельцев, администраторов, редакторов и аналитиков.

## Архитектура

Проект разделён на три основные части:

- `alt_controller_bot.bot` — Telegram-бот на Aiogram 3.
- `alt_controller_bot.api` — FastAPI-приложение для health-check и будущего REST API.
- `alt_controller_bot.db` и `alt_controller_bot.services` — модели БД, репозитории и доменная логика.

### Основные зависимости

- [Aiogram 3](https://docs.aiogram.dev/) — обработка Telegram-апдейтов.
- [FastAPI](https://fastapi.tiangolo.com/) — HTTP API и health-check.
- [SQLAlchemy 2 + asyncpg](https://docs.sqlalchemy.org/) — доступ к PostgreSQL.
- [Redis](https://redis.io/) — хранилище FSM и очередей.
- [Alembic](https://alembic.sqlalchemy.org/) — миграции БД.

## Настройка окружения

1. Скопируйте `.env.example` в `.env` и заполните необходимые переменные:
   ```bash
   BOT_TOKEN=123456:ABC
   DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/alt_controller
   REDIS_URL=redis://redis:6379/0
   WEBHOOK_URL=https://your.domain/bot/webhook
   OWNER_IDS=12345,67890
   ```

2. Установите зависимости:
   ```bash
   pip install -e .[dev]
   ```

3. Запустите бота в режиме polling:
   ```bash
   python -m alt_controller_bot.bot.main
   ```

4. Для запуска API:
   ```bash
   uvicorn alt_controller_bot.api.main:app --host 0.0.0.0 --port 8000
   ```

## Структура БД

Модели соответствуют требованиям ТЗ (каналы, пользователи, посты, статистика, аудит). Стартовая схема задана в `alt_controller_bot.db.models`. Для миграций используйте Alembic.

## Развитие

Каркас обработчиков покрывает ключевые пользовательские сценарии (добавление каналов, мастер поста, статистика). Реализация бизнес-логики подразумевает дальнейшее расширение репозиториев, подключение планировщика публикаций и реакций, работу с Redis и интеграцию планировщиков очереди.
