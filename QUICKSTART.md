# Быстрый старт - Telegram Dating Bot

## ⚡ Самый быстрый запуск

### Для Windows (рекомендуется)

 1. **Установите зависимости** (в PowerShell):
    ```
     cd C:\Users\ruslan\PycharmProjects\tg_bot
     .\new-env\Scripts\pip.exe install -r req.txt
     .\new-env\Scripts\pip.exe install python-dotenv
    ```


2. **Настройте токен**:
   - Скопируйте `.env.example` в `.env`
   - Вставьте ваш BOT_TOKEN в `.env`

 3. **Запустите бота**:
     - Двойной клик на `run_me.bat`
     - **ИЛИ** в PowerShell: `.\new-env\Scripts\python.exe my_bot_new.py`


### Для PyCharm

1. Откройте `my_bot_new.py`
2. Нажмите Зеленую кнопку ▶️ "Run"
3. Следуйте инструкциям в терминале

## 🧪 Тестирование

### Запуск базовых тестов

Двойной клик на `run_test.bat` или в PowerShell:
```
.\new-env\Scripts\python.exe test_basic.py
```

### Сценарии тестирования

См. `TESTING.md` для детальных инструкций:
- ✅ Регистрация пользователя (с валидацией)
- ✅ Загрузка фото
- ✅ Поиск анкет и лайки
- ✅ Фильтры по критериям
- ✅ Удаление профиля
- ❌ Обработка ошибок

## 📚 Документация

| Файл | Описание |
|------|----------|
| `README.md` | Основная документация проекта |
| `TESTING.md` | Руководство по тестированию |
| `GITWORKFLOW.md` | Работы с Git и ветками |
| `SETUP.md` | Настройка GitHub репозитория |

## 📁 Структура проекта

```
tg_bot/
├── my_bot_new.py          ← ГЛАВНЫЙ ФАЙЛ (запускать его)
├── run_me.bat            ← Windows: запуск бота
├── run_test.bat          ← Windows: запуск тестов
├── test_basic.py         ← Скрипт тестов
│
├── config.py             ← Конфигурация
├── .env.example          ← Шаблон токенов (скопируйте в .env)
│
├── storage/              ← Работа с данными
├── services/             ← Бизнес-логика
├── handlers/             ← Обработчики Telegram
└── utils/                ← Утилиты и ошибки
```

## 🔧 Возможные проблемы

### Bot не запускается?
```
<<<<<<< HEAD
=======
Ошибка: ModuleNotFoundError: No module named 'telegram'
>>>>>>> 84f482a (feat: обновление проекта для использования new-env и улучшение тестов)
Решение: .\new-env\Scripts\pip.exe install python-telegram-bot==20.8
```

### Ошибка токена?
```
Ошибка: APIError
Решение: Проверьте токен в .env файле
```

## 🆘 Поддержка

Для вопросов:
1. 查看 `TESTING.md`
2. 查看 `README.md`
3. 查看 `AGENTS.md` (для AI-агентов)

## 🎯 Главное

**Запускайте:** `my_bot_new.py`
**Тестируйте:** `test_basic.py`
**Читайте:** `TESTING.md`

Удачи! 🚀
