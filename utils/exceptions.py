class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных"""
    pass


class FileOperationError(DatabaseError):
    """Ошибка при работе с файлами"""
    pass


class UserNotFoundError(DatabaseError):
    """Пользователь не найден"""
    pass


class UserDataError(DatabaseError):
    """Ошибка в данных пользователя"""
    pass


class BotError(Exception):
    """Базовое исключение для ошибок бота"""
    pass


class TelegramAPIError(BotError):
    """Ошибка Telegram API"""
    pass


class UserInputError(BotError):
    """Ошибка ввода пользователя"""
    pass


class ValidationError(BotError):
    """Ошибка валидации данных"""
    pass


class ServiceError(Exception):
    """Базовое исключение для сервисов"""
    pass


class MatchingError(ServiceError):
    """Ошибка при поиске совпадений"""
    pass


class LikeError(ServiceError):
    """Ошибка при работе с лайками"""
    pass
