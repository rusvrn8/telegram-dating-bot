@echo off
chcp 65001 >nul
echo ========================================
echo Telegram Dating Bot
echo ========================================
echo.

echo Как запустить бота:
echo 1. Убедитесь, что .env файл создан и содержит BOT_TOKEN
echo 2. Запустить: python my_bot_new.py или run_me.bat
echo.

echo Для запуска тестов: test_basic.bat
echo Для документации: откройте README.md или TESTING.md
echo ========================================
pause

.\venv\Scripts\python.exe my_bot_new.py
