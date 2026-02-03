# Настройка GitHub репозитория

## Репозиторий

`https://github.com/rusvrn8/telegram-dating-bot`

## Ветки

- **main** - основная (продуктивная) ветка
  - Защищена от прямого push
  - Требуется 1 approval для Pull Request
  - Требуется линейная история коммитов

- **develop** - ветка разработки
  - Для работы над новыми функциями

## Работа с ветками

См. `GITWORKFLOW.md` для подробностей по Gitflow workflow.

## Клонирование репозитория

```bash
git clone https://github.com/rusvrn8/telegram-dating-bot.git
cd telegram-dating-bot
```

## Получение изменений

```bash
git fetch origin
git pull origin main
git pull origin develop
```

## Создание Pull Request

1. Зафиксировать изменения в feature ветке
2. Запушить ветку в GitHub
3. Создать PR на GitHub: https://github.com/rusvrn8/telegram-dating-bot/compare
4. Описать изменения
5. Дождаться код-ревью

## Важные файлы

- `README.md` - документация проекта
- `AGENTS.md` - рекомендации для AI-агентов
- `GITWORKFLOW.md` - руководство по Gitflow
- `.env.example` - шаблон для переменных окружения
- `.gitignore` - список игнорируемых файлов

## Настройка окружения

```bash
cp .env.example .env
# Отредактировать .env с вашим BOT_TOKEN
```

## Установка зависимостей

```bash
# Активировать виртуальное окружение
# Windows:
new-env\Scripts\activate
# Linux/Mac:
source new-env/bin/activate

pip install -r req.txt
```

## Запуск бота

```bash
# Убедитесь, что виртуальное окружение активировано
python my_bot_new.py
```
