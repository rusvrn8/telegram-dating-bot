from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationBuilder
import logging
import json
import os
import random
import threading

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

users_file_path = 'users.json'
photos_file_path = 'photos_test.json'
likes_file_path = 'likes_test.json'

SUPPORT_CHAT_ID = 6700302188

with open('regions_rf.txt', 'r', encoding="utf-8") as file:
    regions_list = file.readlines()
    regions = tuple(elem.replace('\n', '') for elem in regions_list)

def filter(fil_key, fil_val, users_dict, id):
    if fil_val and isinstance(fil_val, str):
        filter_users = {u for u in users_dict if u != id and u not in users_dict[id]['seen'] and users_dict[u][fil_key] == fil_val}
    elif fil_val and isinstance(fil_val, list):
        filter_users = {u for u in users_dict if u != id and u not in users_dict[id]['seen'] and users_dict[u][fil_key] in fil_val}
    else:
        filter_users = {u for u in users_dict if u != id and u not in users_dict[id]['seen']}
    return filter_users

read_lock = threading.Lock()
write_lock = threading.Lock()

# Функция для сохранения данных в JSON-файл
def save_to_json(data, file_path):
    with write_lock:
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)

# Функция для загрузки данных из JSON-файла
def load_from_json(file_path):
    with read_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        return {}

users = load_from_json(users_file_path)
photos = load_from_json(photos_file_path)
likes = load_from_json(likes_file_path)

async def start(update: Update, context):
    logging.info('Запуск старт..')
    user_id = update.message.from_user.id
    if str(user_id) not in users:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Регистрация", callback_data='register')]
        ])
        await update.message.reply_text("Привет! 😄 Давай начнем знакомство? ", reply_markup=reply_markup)
        context.user_data['registered_users_count'] = len(users.keys()) + 1
        await start_monitor(update, context)
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Привет! Готов к новым знакомствам? ", reply_markup=reply_markup)
        # context.user_data['registered_users_count'] = len(users.keys())
        await start_monitor(update, context)

async def register(update: Update, context):
    logging.info('Запуск регистрации..')
    await update.callback_query.message.reply_text("Как тебя зовут? 📝")
    context.user_data['state'] = 'name'

async def manual(update, context):
    logging.info('Запуск инструкции..')
    await update.message.reply_text("1. Начните работу с чат-ботом, отправив команду 'start'. Бот поприветствует вас и предложит выбрать дальнейшие действия.\n"
        "2. Если вы хотите настроить фильтр для поиска пользователя, отправьте команду 'filter'. Бот попросит вас указать критерии, которые вам важны при знакомстве.\n"
        "3. Чтобы загрузить свое фото в профиль, используйте команду 'upload_photo'. Бот попросит вас отправить фотографию.\n"
        "4. Если вы решили удалить фильтр поиска, отправьте команду 'delete_filter'. Бот удалит все настроенные критерии поиска.\n"
        "5. Если вы хотите посмотреть свою анкету, отправьте команду 'my_profile'.\n"
        "6. Если вы хотите редактировать вашу анкету, отправьте команду 'correct_profile'.\n"
        "7. В случае необходимости получить инструкцию по использованию чат-бота, отправьте команду 'manual'.\n"
        "8. Если у вас возникли вопросы или предложения, обратитесь за поддержкой, отправив команду 'support'.\n"
        "9. Чтобы завершить работу с чат-ботом, отправьте команду 'exit'. Бот попрощается с вами и завершит сеанс общения.\n"
        "10. Чтобы удалить анкету, отправьте команду 'delete_profile'.\n\n"
        "Следуйте инструкциям и командам чат-бота для эффективного использования и успешного знакомства с новыми людьми.")

async def input_data(update, context):
    logging.info('Сохранение данных...')
    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_name = update.message.from_user.username
    state = context.user_data.get('state')
    logging.info(f'{state = }')
    if state == 'name':
        # Сохраняем имя пользователя
        name = update.message.text
        context.user_data['name'] = name
        context.user_data['state'] = 'gender'

        reply_keyboard = [["Парень", "Девушка"]]
        await update.message.reply_text("Какой у тебя пол? 🚹🚺",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == 'filter':
        query = update.message.text
        if query == "Пол":
            logging.info('Сохранение поиска по гендеру...')
            reply_keyboard = [["Парень", "Девушка"]]
            await update.message.reply_text(
                "Выбери с кем желаешь познакомиться 🚹🚺.",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
            context.user_data['state'] = 'filter_gender'
        elif query == "Цель знакомства":
            logging.info('Сохранение поиска по цели...')
            keyboards = ["Дружба", "Общение", "Отношения", "Интим"]
            await update.message.reply_text("Выбери цель знакомства  🎯.",
                reply_markup=ReplyKeyboardMarkup([[keyboard] for keyboard in keyboards], one_time_keyboard=True, resize_keyboard=True))
            context.user_data['state'] = 'filter_goal'
        elif query == "Возраст":
            logging.info('Сохранение поиска по возрасту...')
            keyboards = ["12-17", "18-25", "26-35", "36-45", "46-55", "56-70"]
            await update.message.reply_text("Выбери желаемый возраст для поиска.",
                reply_markup=ReplyKeyboardMarkup([[keyboard] for keyboard in keyboards], one_time_keyboard=True, resize_keyboard=True))
            context.user_data['state'] = 'filter_age'
        elif query == "Регион":
            logging.info('Сохранение поиска по региону...')
            keyboard = ReplyKeyboardMarkup([[region] for region in regions], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("Выбери желаемый регион для поиска 🏙️.", reply_markup=keyboard)
            context.user_data['state'] = 'filter_region'
    elif state == 'filter_gender':
        query = update.message.text
        context.user_data['filter_gender'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)
    elif state == 'filter_goal':
        query = update.message.text
        context.user_data['filter_goal'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)
    elif state == 'filter_age':
        age = update.message.text
        start, end = map(int, age.split("-"))
        age_list = list(map(str, range(start, end + 1)))
        context.user_data['filter_age'] = age_list
        context.user_data['filter_age_view'] = age
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)
    elif state == 'filter_region':
        query = update.message.text
        context.user_data['filter_region'] = query
        await update.message.reply_text("Твои пожелания учтены!", reply_markup=ReplyKeyboardRemove())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await update.message.reply_text("Продолжим знакомства!", reply_markup=reply_markup)
    elif state == 'support':
        message = update.message.text
        await context.bot.send_message(chat_id=SUPPORT_CHAT_ID, text=f'Пользователь @{user_name} написал: {message}')
    elif state == 'gender':
        # Сохраняем пол пользователя
        gender = update.message.text
        logging.info(f'Сохранение гендера...')
        context.user_data['gender'] = gender
        await update.message.reply_text("Сколько тебе лет? 🎂")
        context.user_data['state'] = 'age'
    elif state == 'age':
        # Сохраняем возраст пользователя
        age = update.message.text
        context.user_data['age'] = age
        context.user_data['state'] = 'goal'

        keyboards = ["Общение", "Дружба", "Отношения", "Интим"]
        await update.message.reply_text(
            "Какая у тебя цель знакомства? 🎯",
            reply_markup=ReplyKeyboardMarkup([[keyboard] for keyboard in keyboards], one_time_keyboard=True, resize_keyboard=True))
    elif state == 'goal':
        # Сохраняем цель знакомства пользователя
        goal = update.message.text
        context.user_data['goal'] = goal
        keyboard = ReplyKeyboardMarkup([[region] for region in regions], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Из какого ты региона? 🏙️", reply_markup=keyboard)
        context.user_data['state'] = 'city'
    elif state == 'city':
        # Сохраняем Регион пользователя
        city = update.message.text
        context.user_data['city'] = city

    # Сохраняем информацию о пользователе
        users[user_id] = {
            'name': context.user_data.get('name'),
            'username': '@' + user_name,
            'gender': context.user_data.get('gender'),
            'age': context.user_data.get('age'),
            'goal': context.user_data.get('goal'),
            'city': context.user_data.get('city'),
            'photo': None,
            'seen': []
        }
        save_to_json(users, users_file_path)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Загрузить фото", callback_data='photo'),
             InlineKeyboardButton("Без фото", callback_data='no_photo')]
        ])
        await update.message.reply_text(
            "Вот так, мы познакомились! Я сохранил твою анкету. Теперь скажи мне, хочешь ли ты загрузить своё фото?",
            reply_markup=reply_markup)

async def prev_upload_photo(update, context):
    await update.callback_query.message.reply_text("Жду твоё фото...")

async def before_upload_photo(update, context):
    await update.message.reply_text("Жду твоё фото...")

async def upload_photo(update, context):
    user_id = update.message.from_user.id
    user_id = str(user_id)
    photo_id = update.message.photo[-1].file_id
    users[user_id]['photo'] = photo_id
    photos[user_id] = photo_id

    save_to_json(photos, photos_file_path)
    save_to_json(users, users_file_path)

    await update.message.reply_text("Фотография загружена! Ты выглядишь отлично! 😄", reply_markup=ReplyKeyboardRemove())
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Знакомиться", callback_data='browse'),
         InlineKeyboardButton("Выйти", callback_data='exit')]
    ])
    await update.message.reply_text("Теперь ты готов начать знакомиться!\n\n"
    "Нажми кнопку 'Знакомиться', чтобы увидеть анкету и фото другого пользователя.", reply_markup=reply_markup)

async def no_upload_photo(update, context):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Знакомиться", callback_data='browse'),
         InlineKeyboardButton("Выйти", callback_data='exit')]
    ])
    await update.callback_query.message.reply_text("Если захочешь загрузить фото позже, то выбери в меню 'Загрузить фото'.",
                                                   reply_markup=ReplyKeyboardRemove())
    await update.callback_query.message.reply_text("Теперь можешь начать знакомиться!\n\n"
    "Нажми кнопку 'Знакомиться', чтобы увидеть анкету и фото другого пользователя.", reply_markup=reply_markup)

async def search(update, context):
    logging.info('Запуск знакомства..')
    user_id = update.callback_query.from_user.id
    user_id = str(user_id)
    logging.info(f'{user_id = }')
    filter_gender = context.user_data.get('filter_gender', False)
    filter_goal = context.user_data.get('filter_goal', False)
    filter_age = context.user_data.get('filter_age', False)
    filter_age_view = context.user_data.get('filter_age_view', False)
    filter_region = context.user_data.get('filter_region', False)
    logging.info(f'{filter_gender = }')
    logging.info(f'{filter_goal = }')
    logging.info(f'{filter_age = }')
    logging.info(f'{filter_region = }')

    filter_list = [{'gender': filter_gender}, {'goal': filter_goal}, {'city': filter_region}, {'age': filter_age}]

    unseen_users = {u for u in users if u != user_id and u not in users[user_id]['seen']}

    if filter_gender or filter_goal or filter_age or filter_region:
        text = "Внимание, у тебя настроен фильтр:"
        filter_list = [val for val in filter_list if val[list(val.keys())[0]] is not False]
        for elem in filter_list:
            list_key = list(elem.keys())
            key = list_key[0]
            filter_set = filter(key, elem.get(key), users, user_id)
            unseen_users.intersection_update(filter_set)
            if key == 'gender' and filter_gender:
                message = f"Пол - {filter_gender}."
            elif key == 'goal' and filter_goal:
                message = f"Цель знакомства - {filter_goal}."
            elif key == 'city' and filter_region:
                message = f"Регион - {filter_region}."
            elif key == 'age' and filter_age:
                message = f"Возраст - {filter_age_view}."

            text = text + " " + message

        await context.bot.send_message(chat_id=user_id, text=text)

    # Разкомментить когда появиться реклама
    # insert_ad = random.randint(1, 5)

    # if insert_ad == 1:
    #     await context.bot.send_message(chat_id=user_id,
    #                              text="📢 Рекламное сообщение: Специальное предложение!")

    if unseen_users:
        unseen_users_list = list(unseen_users)
        random_user_id = random.choice(unseen_users_list)
        users[user_id]['seen'].append(random_user_id)
        save_to_json(users, users_file_path)
        random_user_data = users[random_user_id]
        context.user_data['current_match'] = random_user_id
        context.user_data['state'] = 'matching'
        if random_user_id in photos:
            await context.bot.send_photo(chat_id=user_id, photo=photos[random_user_id])
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❤️ Лайк", callback_data='like'),
                     InlineKeyboardButton("💔 Дизлайк", callback_data='dislike')]])
        await update.callback_query.message.reply_text(
            "Привет! Тебе показана случайная анкета и фото другого пользователя.\n\n"
            f"Имя: {random_user_data['name']}\n"
            f"Пол: {random_user_data['gender']}\n"
            f"Возраст: {random_user_data['age']}\n"
            f"Цель знакомства: {random_user_data['goal']}\n"
            f"Регион: {random_user_data['city']}\n\n"
            "Что думаешь об этом человеке? 😊",
            reply_markup=keyboard)
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Выйти", callback_data='exit')]
        ])
        await update.callback_query.message.reply_text('Анкеты закончились, приходи позже...', reply_markup=reply_markup)

async def handle_matching_choice(update, context):
    logging.info('Запуск лайки и дислайка..')
    user_id = update.callback_query.from_user.id
    user_id = str(user_id)
    logging.info(f'{user_id = }')
    choice = update.callback_query.data
    liked_user_id = context.user_data.get('current_match')
    logging.info(f'{liked_user_id = }')
    if choice == 'like':
        if user_id not in likes:
            likes[user_id] = {'likes': [], 'seen': []}
        likes[user_id]['likes'].append(liked_user_id)
        if liked_user_id not in likes:
            likes[liked_user_id] = {'likes': [], 'seen': []}
        save_to_json(likes, likes_file_path)
        if user_id in likes[liked_user_id]['likes']:
            likes[user_id]['seen'].append(liked_user_id)
            save_to_json(likes, likes_file_path)

            matched_user_data = users.get(liked_user_id, dict())
            await update.callback_query.answer("Поздравляю! Взаимный лайк! 🎉")

            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Продолжить знакомиться", callback_data='browse'),
                 InlineKeyboardButton("Выйти", callback_data='exit')]
            ])
            await update.callback_query.message.reply_text("Отлично! У вас обоих взаимный лайк! 🎉\n\n"
                                                     f"Вы можете связаться друг с другом по телеграму.\n\n"
                                                     f"Логин телеграма владельца анкеты: {matched_user_data['username']}", reply_markup=reply_markup)
        else:
            await update.callback_query.answer("Твой лайк отправлен!")
            await update.callback_query.message.reply_text("Хорошо, твой лайк отправлен! 👍\n\n"
                                                     "Если вы тоже кому-то понравитесь, я дам вам знать.") # добавить мониторинг встречных лайков
            await start_monitor_like(update, context)
            await search(update, context)

    elif choice == 'dislike':
        await update.callback_query.answer("Ты прошел к следующей анкете!")
        await update.callback_query.message.reply_text("Окей, продолжаем знакомиться! 🔄")
        await search(update, context)

async def check_new_profiles(context):
    logging.info('Запуск check_new_profiles')
    logging.info(f"User_chat_id: {context.user_data['user_id']}")
    registered_users_count = len(users.keys())
    if registered_users_count > context.user_data.get('registered_users_count', 0):
        logging.info(f'User_data: {context.user_data}')
        context.user_data['registered_users_count'] = registered_users_count
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Знакомиться", callback_data='browse')]
        ])
        await context.bot.send_message(chat_id=context.user_data['user_id'], text="Появилась новая анкета! Начинайте знакомиться 😉", reply_markup=reply_markup)
    else:
        logging.info('Новых пользователей нет')

job_monitor = None
async def start_monitor(update, context):
    global job_monitor
    logging.info('Запуск start_monitor')
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    job_queue = context.job_queue
    job_monitor = job_queue.run_repeating(check_new_profiles, interval=86400, first=0, user_id=user_id)

async def check_likes(context):
    logging.info('Запуск check_likes...')
    user_id = context.user_data['user_id']
    user_id = str(user_id)
    logging.info(f'{user_id = }')
    likes_users = [u for u in likes if u != user_id and u not in likes[user_id]['seen'] and u in likes[user_id]['likes']]

    for like_user_id in likes_users:
        logging.info('Запуск поиска...')
        logging.info(f'{like_user_id = }')
        if user_id in likes[like_user_id]['likes']:
            logging.info('Нашли взаимный лайк...')
            likes[user_id]['seen'].append(like_user_id)
            save_to_json(likes, likes_file_path)
            matched_user_data = users.get(like_user_id, dict())
            await context.bot.send_message(chat_id=user_id,
                                           text="Поздравляю! Взаимный лайк! 🎉")
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Продолжить знакомиться", callback_data='browse'),
                 InlineKeyboardButton("Выйти", callback_data='exit')]
            ])
            if like_user_id in photos:
                await context.bot.send_photo(chat_id=user_id, photo=photos[like_user_id])
            await context.bot.send_message(chat_id=user_id,
                text="Вот анкета и фото другого пользователя.\n\n"
                f"Имя: {matched_user_data['name']}\n"
                f"Пол: {matched_user_data['gender']}\n"
                f"Возраст: {matched_user_data['age']}\n"
                f"Цель знакомства: {matched_user_data['goal']}\n"
                f"Регион: {matched_user_data['city']}")
            await context.bot.send_message(chat_id=user_id, text=f"Вы можете связаться друг с другом по телеграму.\n\n"
                                                           f"Логин телеграма владельца анкеты: {matched_user_data['username']}",
                                                           reply_markup=reply_markup)
        else:
            logging.info('Продолжаем поиск...')

job_like = None
async def start_monitor_like(update, context):
    global job_like
    logging.info('Запуск start_monitor_like')
    user_id = update.callback_query.from_user.id
    context.user_data['user_id'] = user_id
    job_queue = context.job_queue
    job_like = job_queue.run_repeating(check_likes, interval=3600, first=0, user_id=user_id)

async def exit_bot(update, context):
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.callback_query.message.reply_text("Спасибо за использование бота!\n\n"
                                                   "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉")
    # context.user_data.clear()

async def exit_app(update, context):
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.message.reply_text("Спасибо за использование бота!\n\n"
                                    "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉")
    # context.user_data.clear()

async def filter_users(update, context):
    logging.info('Запуск поиска пользователей...')
    keyboards = ["Пол", "Цель знакомства", "Возраст", "Регион"]
    context.user_data['state'] = 'filter'
    await update.message.reply_text(
        "Для поиска пользователей выбери один из критериев:",
        reply_markup=ReplyKeyboardMarkup([[keyboard] for keyboard in keyboards], one_time_keyboard=True, resize_keyboard=True))

async def del_filter(update, context):
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

async def support(update, context):
    logging.info('Запуск поддержки...')
    context.user_data['state'] = 'support'
    await update.message.reply_text("Привет! Если у тебя возникли вопросы, то смело пиши нам!")

async def look_my_profile(update, context):
    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_profile = users.get(user_id, dict())
    if user_id in photos:
        await context.bot.send_photo(chat_id=user_id, photo=photos[user_id])
    await context.bot.send_message(chat_id=user_id,
                                   text="Вот твоя анкета.\n\n"
                                        f"Имя: {user_profile['name']}\n"
                                        f"Пол: {user_profile['gender']}\n"
                                        f"Возраст: {user_profile['age']}\n"
                                        f"Цель знакомства: {user_profile['goal']}\n"
                                        f"Регион: {user_profile['city']}")
    context.user_data['state'] = 'look_profile'

async def del_profile(update, context):
    user_id = update.message.from_user.id
    user_id = str(user_id)
    global job_like
    if job_like:
        job_like.schedule_removal()
        logging.info('Мониторинг лайков остановлен...')
    global job_monitor
    if job_monitor:
        job_monitor.schedule_removal()
        logging.info('Мониторинг пользователей остановлен...')
    users.pop(user_id, None)
    likes.pop(user_id, None)
    photos.pop(user_id, None)
    save_to_json(users, users_file_path)
    save_to_json(likes, likes_file_path)
    save_to_json(photos, photos_file_path)
    await update.message.reply_text("Твоя анкета удалена, будем ждать твоего возвращения!")
    context.user_data.clear()

async def correct_profile(update, context):
    logging.info('Запуск изменение анкеты..')
    await update.message.reply_text("Напиши своё новое имя! 📝")
    context.user_data['state'] = 'name'


if __name__ == '__main__':
    application = ApplicationBuilder().token('6497935634:AAHq6foWi8z4q55IzWM_ev6tiHA_Fzj3jH4').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("exit", exit_app))
    application.add_handler(CommandHandler("upload_photo", before_upload_photo))
    application.add_handler(CommandHandler("filter", filter_users))
    application.add_handler(CommandHandler("delete_filter", del_filter))
    application.add_handler(CommandHandler("manual", manual))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("my_profile", look_my_profile))
    application.add_handler(CommandHandler("correct_profile", correct_profile))
    application.add_handler(CommandHandler("delete_profile", del_profile))

    application.add_handler(MessageHandler((filters.TEXT & (~filters.COMMAND)) | filters.Regex("^(Парень|Девушка|Общение|Дружба|Отношения|Интим)$"), input_data))
    application.add_handler(MessageHandler(filters.PHOTO, upload_photo))

    application.add_handler(CallbackQueryHandler(register, pattern='^register$'))
    application.add_handler(CallbackQueryHandler(search, pattern='^browse$'))
    application.add_handler(CallbackQueryHandler(prev_upload_photo, pattern='photo'))
    application.add_handler(CallbackQueryHandler(no_upload_photo, pattern='no_photo'))
    application.add_handler(CallbackQueryHandler(handle_matching_choice, pattern='^(like|dislike)$'))
    application.add_handler(CallbackQueryHandler(exit_bot, pattern='exit'))

    application.run_polling()