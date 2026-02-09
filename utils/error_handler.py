import logging
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from .exceptions import (
    DatabaseError,
    TelegramAPIError,
    UserInputError,
    ValidationError,
    ServiceError
)


def log_error(error: Exception, context: str = "") -> None:
    """Логирование ошибки"""
    logging.error(f"{context}: {type(error).__name__}: {str(error)}", exc_info=True)


async def send_error_message(update: Update, context: CallbackContext, error_message: str) -> None:
    """Отправка сообщения об ошибке пользователю"""
    try:
        if update.message:
            await update.message.reply_text(error_message)
        elif update.callback_query:
            await update.callback_query.answer(error_message, show_alert=True)
            await update.callback_query.message.reply_text(error_message)
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение об ошибке: {e}")


DEFAULT_ERROR_MESSAGE = "Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с поддержкой."


def handle_errors(error_message: str = DEFAULT_ERROR_MESSAGE, notify_admin: bool = False):
    """Декоратор для обработки ошибок в async функциях"""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except DatabaseError as e:
                log_error(e, f"Database error in {func.__name__}")
                await send_error_message(update, context, "Ошибка базы данных. Попробуйте позже.")
            except TelegramAPIError as e:
                log_error(e, f"Telegram API error in {func.__name__}")
                await send_error_message(update, context, "Ошибка соединения с Telegram. Попробуйте позже.")
            except UserInputError as e:
                log_error(e, f"User input error in {func.__name__}")
                await send_error_message(update, context, str(e))
            except ValidationError as e:
                log_error(e, f"Validation error in {func.__name__}")
                await send_error_message(update, context, str(e))
            except ServiceError as e:
                log_error(e, f"Service error in {func.__name__}")
                await send_error_message(update, context, "Ошибка сервиса. Попробуйте позже.")
            except Exception as e:
                log_error(e, f"Unexpected error in {func.__name__}")
                await send_error_message(update, context, error_message)

                if notify_admin:
                    try:
                        from config import SUPPORT_CHAT_ID
                        await context.bot.send_message(
                            chat_id=SUPPORT_CHAT_ID,
                            text=f"🚨 Critical error in {func.__name__}:\n{type(e).__name__}: {str(e)}"
                        )
                    except:
                        pass
        return wrapper
    return decorator


def handle_callback_errors(func):
    """Декоратор для обработки ошибок в callback функциях"""
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log_error(e, f"Callback error in {func.__name__}")
            try:
                await update.callback_query.answer("Произошла ошибка", show_alert=True)
            except:
                pass
    return wrapper
