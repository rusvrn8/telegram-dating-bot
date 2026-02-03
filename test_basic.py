"""
Тестовый скрипт для проверки базового функционала бота
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Установить кодировку UTF-8 для вывода
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 60)
print("Тестирование Telegram Dating Bot")
print("=" * 60)

# Тест 1: Импорты
print("\n[1] Проверка импортов modules...")
try:
    import config
    print("  + config.py - OK")
except Exception as e:
    print(f"  - config.py - Ошибка: {e}")

try:
    from storage import Database, load_regions
    print("  + storage/ - OK")
except Exception as e:
    print(f"  - storage/ - Ошибка: {e}")

try:
    from services import MatchingService, LikeService
    print("  + services/ - OK")
except Exception as e:
    print(f"  - services/ - Ошибка: {e}")

try:
    from utils import handle_errors, ValidationError
    print("  + utils/ - OK")
except Exception as e:
    print(f"  - utils/ - Ошибка: {e}")

# Тест 2: Создание Database
print("\n[2] Проверка Database...")
try:
    from storage import load_from_json, Database
    db = Database('users_test.json', 'photos_test.json', 'likes_test.json')
    print(f"  + Database создан")
    print(f"  # Пользователей: {db.get_users_count()}")
    print(f"  # Фотографий: {len(db.photos)}")
    print(f"  # Лайков: {len(db.likes)}")
except Exception as e:
    print(f"  - Database - Ошибка: {e}")
    db = None

# Тест 3: Services
print("\n[3] Проверка Services...")
try:
    from services import MatchingService, LikeService
    if db:
        matching = MatchingService(db)
        likes = LikeService(db)
        print("  + MatchingService - OK")
        print("  + LikeService - OK")
except Exception as e:
    print(f"  - Services - Ошибка: {e}")

# Тест 4: Обработка ошибок
print("\n[4] Проверка обработки ошибок...")
try:
    from utils import ValidationError
    try:
        raise ValidationError("Тестовая ошибка")
    except ValidationError as e:
        print(f"  + ValidationError работает: {e}")
except Exception as e:
    print(f"  - Ошибки - Ошибка: {e}")

# Тест 5: Поиск пользователя (если есть данные)
print("\n[5] Проверка поиска пользователя...")
try:
    if db and db.users:
        user_id = list(db.users.keys())[0]
        user = db.get_user(user_id)
        print(f"  + Получен пользователь: {user.get('name', 'Unknown')}")
    else:
        print("  ! Нет пользователей для теста")
except Exception as e:
    print(f"  - Поиск - Ошибка: {e}")

# Тест 6: Фильтр пользователей
print("\n[6] Проверка фильтрации...")
try:
    from services import filter_users
    if db and db.users and len(db.users) > 0:
        test_user_id = list(db.users.keys())[0]
        filters = filter_users('gender', 'Парень', db.users, test_user_id)
        print(f"  + Фильтрация работает. Найдено: {len(filters)}")
    else:
        print("  ! Нет пользователей для фильтрации")
except Exception as e:
    print(f"  - Фильтрация - Ошибка: {e}")

# Тест 7: Валидация данных
print("\n[7] Проверка валидации данных...")
try:
    from utils.exceptions import ValidationError

    if db:
        user_data = {
            'name': 'Test',
            'username': '@test',
            'gender': 'Парень',
            'age': '25',
            'goal': 'Общение',
            'city': 'Москва',
            'photo': None,
            'seen': []
        }

        db.add_user('999999', user_data)
        print(f"  + Валидные данные добавлены")

        try:
            db.add_user('999999', {'name': 'X'})
            print(f"  - Невалидные данные были добавлены!")
        except Exception:
            print(f"  + Невалидные данные отклонены")
    else:
        print("  ! Database не создан")
except Exception as e:
    print(f"  - Валидация - Ошибка: {e}")

print("\n" + "=" * 60)
print("Тестирование завершено!")
print("=" * 60)

print("\nЗапустите бота командой:")
print("  python my_bot_new.py")
print("или")
print("  new-env\\Scripts\\python.exe my_bot_new.py")
