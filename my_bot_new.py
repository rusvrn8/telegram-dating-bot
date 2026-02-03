import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Message
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ApplicationBuilder
)

import config
from storage import Database, load_regions
from services import MatchingService, LikeService
from handlers import (
    send_question,
    check_answer,
    register,
    input_name,
    input_gender,
    input_age,
    input_goal,
    input_city,
    exit_app,
    search,
    handle_matching_choice,
    check_new_profiles,
    check_likes,
    upload_photo,
    look_my_profile,
    edit_profile,
    delete_profile,
    send_support_message,
    manual,
    show_filter_options,
    handle_filter_input,
    delete_filter,
    support
)

logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)

database = Database(
    config.USERS_FILE,
    config.PHOTOS_FILE,
    config.LIKES_FILE
)

matching_service = MatchingService(database)
like_service = LikeService(database)

regions = load_regions(config.REGIONS_FILE)

job_monitor = None
job_like = None


async def start(update: Update, context) -> None:
    logging.info('Запуск старт..')
    user_id = update.message.from_user.id

    if str(user_id) not in database.users:
        await send_question(update, context, database)
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Привет! Готов к новым знакомствам? ", reply_markup=reply_markup)
        await start_monitor(update, context)


async def prev_upload_photo(update: Update, context) -> None:
    await update.callback_query.message.reply_text("Жду твоё фото...")


async def before_upload_photo(update: Update, context) -> None:
    await update.message.reply_text("Жду твоё фото...")


async def no_upload_photo(update: Update, context) -> None:
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Знакомиться", callback_data='browse'),
         InlineKeyboardButton("Выйти", callback_data='exit')]
    ])
    await update.callback_query.message.reply_text(
        "Если захочешь загрузить фото позже, то выбери в меню 'Загрузить фото'.",
        reply_markup=Message.ReplyKeyboardRemove()
    )
    await update.callback_query.message.reply_text(
        "Теперь можешь начать знакомиться!\n\n"
        "Нажми кнопку 'Знакомиться', чтобы увидеть анкету и фото другого пользователя.",
        reply_markup=reply_markup
    )


async def exit_bot(update: Update, context) -> None:
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.callback_query.message.reply_text(
        "Спасибо за использование бота!\n\n"
        "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉"
    )


def start_monitor(update: Update, context) -> None:
    global job_monitor
    logging.info('Запуск start_monitor')
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    job_queue = context.job_queue
    job_monitor = job_queue.run_repeating(
        lambda c: check_new_profiles(c, database),
        interval=config.PROFILE_CHECK_INTERVAL,
        first=0,
        user_id=user_id
    )


def start_monitor_like(update: Update, context) -> None:
    global job_like
    logging.info('Запуск start_monitor_like')
    user_id = update.callback_query.from_user.id
    context.user_data['user_id'] = user_id
    job_queue = context.job_queue
    job_like = job_queue.run_repeating(
        lambda c: check_likes(c, database, like_service),
        interval=config.LIKES_CHECK_INTERVAL,
        first=0,
        user_id=user_id
    )


async def exit_handler(update: Update, context) -> None:
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.message.reply_text(
        "Спасибо за использование бота!\n\n"
        "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉"
    )


async def input_data(update: Update, context) -> None:
    logging.info('Сохранение данных...')
    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_name = update.message.from_user.username
    state = context.user_data.get('state')
    logging.info(f'{state = }')

    if state == 'name':
        await input_name(update, context)
    elif state == 'gender':
        await input_gender(update, context)
    elif state == 'age':
        await input_age(update, context)
    elif state == 'goal':
        await input_goal(update, context, regions)
    elif state == 'city':
        await input_city(update, context, database)
    elif state == 'verification':
        await check_answer(update, context, database)
    elif state == 'filter':
        await handle_filter_input(update, context, regions)
    elif state == 'support':
        await send_support_message(update, context, user_name, config.SUPPORT_CHAT_ID)


async def register_callback(update: Update, context) -> None:
    await register(update, context)


async def browse_callback(update: Update, context) -> None:
    await search(update, context, database, matching_service, regions)


async def photo_callback(update: Update, context) -> None:
    await prev_upload_photo(update, context)


async def no_photo_callback(update: Update, context) -> None:
    await no_upload_photo(update, context)


async def matching_callback(update: Update, context) -> None:
    await handle_matching_choice(update, context, database, like_service)


async def exit_callback(update: Update, context) -> None:
    await exit_bot(update, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("exit", exit_handler))
    application.add_handler(CommandHandler("upload_photo", before_upload_photo))
    application.add_handler(CommandHandler("filter", show_filter_options))
    application.add_handler(CommandHandler("delete_filter", delete_filter))
    application.add_handler(CommandHandler("manual", manual))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("my_profile", look_my_profile))
    application.add_handler(CommandHandler("correct_profile", edit_profile))
    application.add_handler(CommandHandler("delete_profile", delete_profile))

    application.add_handler(
        MessageHandler(
            (filters.TEXT & (~filters.COMMAND)) | filters.Regex("^(Парень|Девушка|Общение|Дружба|Отношения|Интим|12-17|18-25|26-35|36-45|46-55|56-70|[А-Яа-яА-Яа-яЁё]+ область|[А-Яа-яА-Яа-яЁё]+ край|[А-Яа-яА-Яа-яЁё]+ респ.*)$"),
            input_data
        )
    )
    application.add_handler(MessageHandler(filters.PHOTO, upload_photo))

    application.add_handler(CallbackQueryHandler(register_callback, pattern='^register$'))
    application.add_handler(CallbackQueryHandler(browse_callback, pattern='^browse$'))
    application.add_handler(CallbackQueryHandler(photo_callback, pattern='photo'))
    application.add_handler(CallbackQueryHandler(no_photo_callback, pattern='no_photo'))
    application.add_handler(CallbackQueryHandler(matching_callback, pattern='^(like|dislike)$'))
    application.add_handler(CallbackQueryHandler(exit_callback, pattern='exit'))

    application.run_polling()
