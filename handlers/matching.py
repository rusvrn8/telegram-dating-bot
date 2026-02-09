import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

import config
from utils import handle_errors, handle_callback_errors
from utils.exceptions import UserNotFoundError


@handle_callback_errors
async def search(update: Update, context: CallbackContext, database, matching_service, regions: tuple) -> None:
    logging.info('Запуск знакомства..')
    user_id = str(update.callback_query.from_user.id)

    filter_gender = context.user_data.get('filter_gender', False)
    filter_goal = context.user_data.get('filter_goal', False)
    filter_age = context.user_data.get('filter_age', False)
    filter_age_view = context.user_data.get('filter_age_view', False)
    filter_region = context.user_data.get('filter_region', False)

    filters = {
        'filter_gender': filter_gender,
        'filter_goal': filter_goal,
        'filter_age': filter_age,
        'filter_region': filter_region
    }

    if any(filter_gender or filter_goal or filter_age or filter_region):
        text = "Внимание, у тебя настроен фильтр:"
        if filter_gender:
            text += f" Пол - {filter_gender}."
        if filter_goal:
            text += f" Цель знакомства - {filter_goal}."
        if filter_region:
            text += f" Регион - {filter_region}."
        if filter_age:
            text += f" Возраст - {filter_age_view}."
        await context.bot.send_message(chat_id=user_id, text=text)

    try:
        random_user_id = matching_service.find_random_user(user_id, filters)
    except Exception as e:
        logging.error(f"Error finding user: {e}")
        await update.callback_query.message.reply_text("Ошибка при поиске анкеты. Попробуйте позже.")
        return

    if random_user_id:
        try:
            matching_service.mark_as_seen(user_id, random_user_id)
            database.save_users()

            try:
                random_user_data = database.get_user(random_user_id)
            except UserNotFoundError:
                logging.error(f"User {random_user_id} not found after search")
                await update.callback_query.message.reply_text("Ошибка при загрузке анкеты. Попробуйте снова.")
                return

            context.user_data['current_match'] = random_user_id
            context.user_data['state'] = 'matching'

            if random_user_id in database.photos:
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=database.photos[random_user_id])
                except Exception as e:
                    logging.error(f"Error sending photo: {e}")

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❤️ Лайк", callback_data='like'),
                 InlineKeyboardButton("💔 Дизлайк", callback_data='dislike')]
            ])

            try:
                await update.callback_query.message.reply_text(
                    "Привет! Тебе показана случайная анкета и фото другого пользователя.\n\n"
                    f"Имя: {random_user_data['name']}\n"
                    f"Пол: {random_user_data['gender']}\n"
                    f"Возраст: {random_user_data['age']}\n"
                    f"Цель знакомства: {random_user_data['goal']}\n"
                    f"Регион: {random_user_data['city']}\n\n"
                    "Что думаешь об этом человеке? 😊",
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f"Error sending profile: {e}")
                await update.callback_query.message.reply_text("Ошибка при отправке анкеты. Попробуйте позже.")

        except Exception as e:
            logging.error(f"Error marking user as seen: {e}")
            await update.callback_query.message.reply_text("Не удалось сохранить прогресс. Попробуйте позже.")
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Выйти", callback_data='exit')]
        ])
        await update.callback_query.message.reply_text(
            'Анкеты закончились, приходи позже...',
            reply_markup=reply_markup
        )


@handle_callback_errors
async def handle_matching_choice(update: Update, context: CallbackContext, database, like_service, regions: tuple) -> None:
    logging.info('Запуск лайки и дислайка..')
    user_id = str(update.callback_query.from_user.id)
    choice = update.callback_query.data
    liked_user_id = context.user_data.get('current_match')

    if not liked_user_id:
        await update.callback_query.message.reply_text("Ошибка. Попробуйте снова.")
        return

    if choice == 'like':
        try:
            is_mutual = like_service.add_like(user_id, liked_user_id)
            database.save_likes()

            try:
                matched_user_data = database.get_user(liked_user_id)
            except UserNotFoundError:
                logging.error(f"Matched user {liked_user_id} not found")
                await update.callback_query.message.reply_text("Ошибка. Попробуйте позже.")
                return

            if is_mutual:
                like_service.mark_like_as_seen(user_id, liked_user_id)
                database.save_likes()
                await update.callback_query.answer("Поздравляю! Взаимный лайк! 🎉")

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Продолжить знакомиться", callback_data='browse'),
                     InlineKeyboardButton("Выйти", callback_data='exit')]
                ])

                await update.callback_query.message.reply_text(
                    "Отлично! У вас обоих взаимный лайк! 🎉\n\n"
                    f"Вы можете связаться друг с другом по телеграму.\n\n"
                    f"Логин телеграма владельца анкеты: {matched_user_data['username']}",
                    reply_markup=reply_markup
                )
            else:
                await update.callback_query.answer("Твой лайк отправлен!")
                await update.callback_query.message.reply_text(
                    "Хорошо, твой лайк отправлен! 👍\n\n"
                    "Если вы тоже кому-то понравитесь, я дам вам знать."
                )
        except Exception as e:
            logging.error(f"Error processing like: {e}")
            await update.callback_query.message.reply_text("Не удалось обработать лайк. Попробуйте позже.")

    elif choice == 'dislike':
        await update.callback_query.answer("Ты прошел к следующей анкете!")
        await update.callback_query.message.reply_text("Окей, продолжаем знакомиться! 🔄")
        await search(update, context, database, like_service.matching_service, regions)


@handle_errors()
async def check_new_profiles(context: CallbackContext, database) -> None:
    logging.info('Запуск check_new_profiles')
    user_id = context.user_data['user_id']
    registered_users_count = database.get_users_count()

    if registered_users_count > context.user_data.get('registered_users_count', 0):
        context.user_data['registered_users_count'] = registered_users_count
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="Появилась новая анкета! Начинайте знакомиться 😉",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Failed to send new profiles notification: {e}")
    else:
        logging.info('Новых пользователей нет')


@handle_errors()
async def check_likes(context: CallbackContext, database, like_service) -> None:
    logging.info('Запуск check_likes...')
    user_id = context.user_data['user_id']
    user_id = str(user_id)

    try:
        for like_user_id in like_service.get_new_mutual_likes(user_id):
            logging.info(f'Нашли взаимный лайк с {like_user_id}...')
            like_service.mark_like_as_seen(user_id, like_user_id)
            database.save_likes()

            try:
                matched_user_data = database.get_user(like_user_id)
            except UserNotFoundError:
                logging.error(f"Mutual like user {like_user_id} not found")
                continue

            try:
                await context.bot.send_message(chat_id=user_id, text="Поздравляю! Взаимный лайк! 🎉")
            except Exception as e:
                logging.error(f"Failed to send mutual like notification: {e}")
                continue

            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Продолжить знакомиться", callback_data='browse'),
                 InlineKeyboardButton("Выйти", callback_data='exit')]
            ])

            if like_user_id in database.photos:
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=database.photos[like_user_id])
                except Exception as e:
                    logging.error(f"Failed to send mutual like photo: {e}")

            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="Вот анкета и фото другого пользователя.\n\n"
                         f"Имя: {matched_user_data['name']}\n"
                         f"Пол: {matched_user_data['gender']}\n"
                         f"Возраст: {matched_user_data['age']}\n"
                         f"Цель знакомства: {matched_user_data['goal']}\n"
                         f"Регион: {matched_user_data['city']}"
                )
            except Exception as e:
                logging.error(f"Failed to send mutual like profile: {e}")

            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Вы можете связаться друг с другом по телеграму.\n\n"
                         f"Логин телеграма владельца анкеты: {matched_user_data['username']}",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Failed to send mutual like contact: {e}")
    except Exception as e:
        logging.error(f"Error in check_likes: {e}")
