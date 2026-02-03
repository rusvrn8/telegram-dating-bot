@echo off
echo ========================================
echo Тестирование Telegram Dating Bot
echo ========================================
echo.

echo [1] Проверка Python...
.\new-env\Scripts\python.exe --version
if %errorlevel% neq 0 (
    echo Ошибка: Python не найден!
    pause
    exit /b 1
)
echo.

echo [2] Запуск тестов...
.\new-env\Scripts\python.exe test_basic.py
if %errorlevel% neq 0 (
    echo Ошибка при запуске тестов!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Тестирование завершено!
echo ========================================
pause
