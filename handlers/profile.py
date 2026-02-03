import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import CallbackContext

import config


async def upload_photo(update: Update, context: CallbackContext, database) -> None:
    user_id = update.message.from_user.id
    user_id = str(user_id)
    photo_id = update.message.photo[-1].file_id

    database.add_photo(user_id, photo_id)
    database.save_users()
    database.save_photos()

    await update.message.reply_text(
        "Фотография загружена! Ты выглядишь отлично! 😄",
        reply_markup=Message.ReplyKeyboardRemove()
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


async def look_my_profile(update: Update, context: CallbackContext, database) -> None:
    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_profile = database.get_user(user_id)

    if user_id in database.photos:
        await context.bot.send_photo(chat_id=user_id, photo=database.photos[user_id])

    await context.bot.send_message(
        chat_id=user_id,
        text="Вот твоя анкета.\n\n"
             f"Имя: {user_profile['name']}\n"
             f"Пол: {user_profile['gender']}\n"
             f"Возраст: {user_profile['age']}\n"
             f"Цель знакомства: {user_profile['goal']}\n"
             f"Регион: {user_profile['city']}"
    )
    context.user_data['state'] = 'look_profile'


async def edit_profile(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск изменение анкеты..')
    await update.message.reply_text("Напиши своё новое имя! 📝")
    context.user_data['state'] = 'name'


async def delete_profile(update: Update, context: CallbackContext, database) -> None:
    user_id = update.message.from_user.id
    user_id = str(user_id)

    database.delete_user(user_id)
    database.save_users()
    database.save_photos()
    database.save_likes()

    await update.message.reply_text("Твоя анкета удалена, будем ждать твоего возвращения!")
    context.user_data.clear()


async def send_support_message(update: Update, context: CallbackContext, username: str, support_chat_id: int) -> None:
    message = update.message.text
    await context.bot.send_message(
        chat_id=support_chat_id,
        text=f'Пользователь @{username} написал: {message}'
    )


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
        context.user_data['filter_gender'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)

    elif state == 'filter_goal':
        context.user_data['filter_goal'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)

    elif state == 'filter_age':
        context.user_data['filter_age'] = query
        context.user_data['filter_age_view'] = query
        age_list = list(map(str, range(int(query.split('-')[0]), int(query.split('-')[1]) + 1)))
        context.user_data['filter_age'] = age_list
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


async def support(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск поддержки...')
    context.user_data['state'] = 'support'
    await update.message.reply_text("Привет! Если у тебя возникли вопросы, то смело пиши нам!")
