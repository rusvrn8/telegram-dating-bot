import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import config
from utils import handle_errors, handle_callback_errors, ValidationError
from utils.exceptions import UserNotFoundError


@handle_errors(error_message="Ошибка при загрузке фото")
async def upload_photo(update: Update, context: CallbackContext, database) -> None:
    user_id = str(update.message.from_user.id)

    try:
        if not update.message.photos:
            await update.message.reply_text("Пожалуйста, отправьте изображение.")
            return

        photo_id = update.message.photos[-1].file_id

        if not photo_id:
            await update.message.reply_text("Не удалось получить фото. Попробуйте другое фото.")
            return

        database.add_photo(user_id, photo_id)
        database.save_users()
        database.save_photos()

        await update.message.reply_text(
            "Фотография загружена! Ты выглядишь отлично! 😄",
            reply_markup=None
        )
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse'),
             InlineKeyboardButton("Выйти", callback_data='exit')]
        ])
        await update.message.reply_text(
            "Теперь ты готов начать знакомиться!\n\n"
            "Нажми кнопку 'Знакомиться', чтобы увидеть анкету и фото другого пользователя.",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error uploading photo for user {user_id}: {e}")
        await update.message.reply_text("Не удалось загрузить фото. Попробуйте позже.")
        raise


@handle_errors(error_message="Ошибка при просмотре профиля")
async def look_my_profile(update: Update, context: CallbackContext, database) -> None:
    user_id = str(update.message.from_user.id)

    try:
        user_profile = database.get_user(user_id)
    except UserNotFoundError:
        await update.message.reply_text("Профиль не найден. Пожалуйста, зарегистрируйтесь заново с команды /start")
        return

    try:
        if user_id in database.photos:
            await context.bot.send_photo(chat_id=user_id, photo=database.photos[user_id])
    except Exception as e:
        logging.error(f"Error sending photo for user {user_id}: {e}")
        await update.message.reply_text("Не удалось загрузить фото профиля")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="Вот твоя анкета.\n\n"
                 f"Имя: {user_profile.get('name', 'Не указано')}\n"
                 f"Пол: {user_profile.get('gender', 'Не указано')}\n"
                 f"Возраст: {user_profile.get('age', 'Не указано')}\n"
                 f"Цель знакомства: {user_profile.get('goal', 'Не указано')}\n"
                 f"Регион: {user_profile.get('city', 'Не указано')}"
        )
        context.user_data['state'] = 'look_profile'
    except Exception as e:
        logging.error(f"Error sending profile for user {user_id}: {e}")
        await update.message.reply_text("Не удалось загрузить анкету")


@handle_errors()
async def edit_profile(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск изменение анкеты..')
    await update.message.reply_text("Напиши своё новое имя! 📝")
    context.user_data['state'] = 'name'


@handle_errors(error_message="Ошибка при удалении профиля")
async def delete_profile(update: Update, context: CallbackContext, database) -> None:
    user_id = str(update.message.from_user.id)

    try:
        database.get_user(user_id)
    except UserNotFoundError:
        await update.message.reply_text("Профиль не найден.")
        return

    try:
        database.delete_user(user_id)
        database.save_users()
        database.save_photos()
        database.save_likes()

        await update.message.reply_text("Твоя анкета удалена, будем ждать твоего возвращения!")
        context.user_data.clear()
    except Exception as e:
        logging.error(f"Error deleting profile for user {user_id}: {e}")
        await update.message.reply_text("Не удалось удалить профиль. Попробуйте позже.")
        raise


@handle_errors(error_message="Ошибка при отправке сообщения поддержки")
async def send_support_message(update: Update, context: CallbackContext, username: str, support_chat_id: int) -> None:
    message = update.message.text.strip()

    if not message:
        await update.message.reply_text("Пожалуйста, введите сообщение для поддержки.")
        return

    if len(message) > 1000:
        await update.message.reply_text("Сообщение слишком длинное (максимум 1000 символов).")
        return

    try:
        await context.bot.send_message(
            chat_id=support_chat_id,
            text=f'📩 Сообщение от @{username} (ID: {update.message.from_user.id}):\n\n{message}'
        )
        await update.message.reply_text("Ваше сообщение отправлено в поддержку! 📨")
    except Exception as e:
        logging.error(f"Failed to send support message: {e}")
        await update.message.reply_text("Не удалось отправить сообщение. Попробуйте позже.")
        raise


@handle_errors()
async def manual(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск инструкции..')
    await update.message.reply_text(
        "1. Начните работу с чат-ботом, отправив команду 'start'. Бот поприветствует вас и предложит выбрать дальнейшие действия.\n"
        "2. Если вы хотите настроить фильтр для поиска пользователя, отправьте команду 'filter'. Бот попросит вас указать критерии, которые вам важны при знакомстве.\n"
        "3. Чтобы загрузить свое фото в профиль, используйте команду 'upload_photo'. Бот попросит вас отправить фотографию.\n"
        "4. Если вы решили удалить фильтр поиска, отправьте команду 'delete_filter'. Бот удалит все настроенные критерии поиска.\n"
        "5. Если вы хотите посмотреть свою анкету, отправьте команду 'my_profile'.\n"
        "6. Если вы хотите редактировать вашу анкету, отправьте команду 'correct_profile'.\n"
        "7. В случае необходимости получить инструкцию по использованию чат-бота, отправьте команду 'manual'.\n"
        "8. Если у вас возникли вопросы или предложения, обратитесь за поддержкой, отправив команду 'support'.\n"
        "9. Чтобы завершить работу с чат-ботом, отправьте команду 'exit'. Бот попрощается с вами и завершит сеанс общения.\n"
        "10. Чтобы удалить анкету, отправьте команду 'delete_profile'.\n\n"
        "Следуйте инструкциям и командам чат-бота для эффективного использования и успешного знакомства с новыми людьми."
    )


@handle_errors()
async def show_filter_options(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск поиска пользователей...')
    keyboards = ["Пол", "Цель знакомства", "Возраст", "Регион"]
    context.user_data['state'] = 'filter'

    from telegram import ReplyKeyboardMarkup

    await update.message.reply_text(
        "Для поиска пользователей выбери один из критериев:",
        reply_markup=ReplyKeyboardMarkup(
            [[keyboard] for keyboard in keyboards],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


@handle_errors(error_message="Ошибка при настройке фильтра")
async def handle_filter_input(update: Update, context: CallbackContext, regions: tuple) -> None:
    from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

    query = update.message.text
    state = context.user_data.get('state')

    if state == 'filter':
        if query == "Пол":
            logging.info('Сохранение поиска по гендеру...')
            reply_keyboard = [["Парень", "Девушка"]]
            await update.message.reply_text(
                "Выбери с кем желаешь познакомиться 🚹🚺.",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            context.user_data['state'] = 'filter_gender'
        elif query == "Цель знакомства":
            logging.info('Сохранение поиска по цели...')
            keyboards = ["Дружба", "Общение", "Отношения", "Интим"]
            await update.message.reply_text(
                "Выбери цель знакомства  🎯.",
                reply_markup=ReplyKeyboardMarkup(
                    [[keyboard] for keyboard in keyboards],
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            context.user_data['state'] = 'filter_goal'
        elif query == "Возраст":
            logging.info('Сохранение поиска по возрасту...')
            keyboards = ["12-17", "18-25", "26-35", "36-45", "46-55", "56-70"]
            await update.message.reply_text(
                "Выбери желаемый возраст для поиска.",
                reply_markup=ReplyKeyboardMarkup(
                    [[keyboard] for keyboard in keyboards],
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            context.user_data['state'] = 'filter_age'
        elif query == "Регион":
            logging.info('Сохранение поиска по региону...')
            if not regions:
                await update.message.reply_text("Не удалось загрузить список регионов")
                return
            keyboard = ReplyKeyboardMarkup(
                [[region] for region in regions],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            await update.message.reply_text(
                "Выбери желаемый регион для поиска 🏙️.",
                reply_markup=keyboard
            )
            context.user_data['state'] = 'filter_region'

    elif state == 'filter_gender':
        if query not in ["Парень", "Девушка"]:
            await update.message.reply_text("Пожалуйста, выберите 'Парень' или 'Девушка'")
            return
        context.user_data['filter_gender'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)

    elif state == 'filter_goal':
        if query not in ["Общение", "Дружба", "Отношения", "Интим"]:
            await update.message.reply_text("Пожалуйста, выберите из предложенных целей")
            return
        context.user_data['filter_goal'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)

    elif state == 'filter_age':
        context.user_data['filter_age'] = query
        context.user_data['filter_age_view'] = query
        try:
            start, end = map(int, query.split('-'))
            age_list = list(map(str, range(start, end + 1)))
            context.user_data['filter_age'] = age_list
        except:
            await update.message.reply_text("Некорректный формат возраста")
            return
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)

    elif state == 'filter_region':
        context.user_data['filter_region'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)


@handle_errors()
async def delete_filter(update: Update, context: CallbackContext) -> None:
    logging.info('Удаление фильтра пользователей...')
    context.user_data.pop('filter_gender', None)
    context.user_data.pop('filter_goal', None)
    context.user_data.pop('filter_age', None)
    context.user_data.pop('filter_age_view', None)
    context.user_data.pop('filter_region', None)
    context.user_data['state'] = 'del_filter'

    await update.message.reply_text("Фильтр для поиска очищен!")
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Знакомиться", callback_data='browse')]
    ])
    await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)


@handle_errors()
async def support(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск поддержки...')
    context.user_data['state'] = 'support'
    await update.message.reply_text("Привет! Если у тебя возникли вопросы, то смело пиши нам!")
