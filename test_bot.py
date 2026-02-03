import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, CallbackQueryHandler
import json
import os
import random

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для знакомств. Давай начнем!")
#
# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
users_file_path = 'users.json'
photos_file_path = 'photos.json'
likes_file_path = 'likes.json'

# Функция для сохранения данных в JSON-файл
def save_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)

# Функция для загрузки данных из JSON-файла
def load_from_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    return {}

users = load_from_json(users_file_path)
photos = load_from_json(photos_file_path)
likes = load_from_json(likes_file_path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in users:
        users[user_id] = {'name': None, 'gender': None, 'age': None, 'goal': None, 'city': None, 'photo': None, 'seen': []}
        save_to_json(users, users_file_path)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Регистрация", callback_data='register')]
    ])
    await update.message.reply_text("Привет! 😄 Давай начнем знакомство? Сначала заполни анкету!", reply_markup=reply_markup)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    update.callback_query.message.reply_text("Заполни свою анкету!")
    questions = {"Имя": 'name', "Пол": 'gender', "Возраст": 'age', "Цель знакомства": 'goal', "Город": 'city'}

    for question in questions.keys():
        await update.callback_query.message.reply_text(f"Укажите {question}:")
        response = update.callback_query.message.text
        users[user_id][questions[question]] = response
        save_to_json(users, users_file_path)

    await update.callback_query.message.reply_text("Анкета заполнена! Теперь ты можешь загрузить фото!")

# async def form(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.message.from_user.id
#     questions = {"Имя": 'name', "Пол": 'gender', "Возраст": 'age', "Цель знакомства": 'goal', "Город": 'city'}
#
#     for question in questions.keys():
#         await update.message.reply_text(f"Укажите {question}:")
#         response = update.message.text
#         users[user_id][questions[question]] = response
#         save_to_json(users, users_file_path)

    # reply_markup = InlineKeyboardMarkup([
    #     [InlineKeyboardButton("Знакомиться", callback_data='browse')],
    #     [InlineKeyboardButton("Хватит", callback_data='stop')]
    # ])
    # await update.message.reply_text("Анкета заполнена! Теперь ты можешь загрузить фото!")

async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_id = update.message.photo[-1].file_id
    users[user_id]['photo'] = photo_id
    photos[user_id] = photo_id
    save_to_json(photos, photos_file_path)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Знакомиться", callback_data='browse')],
        [InlineKeyboardButton("Хватит", callback_data='stop')]
    ])
    await update.message.reply_text("Отлично! Теперь выбери действие:", reply_markup=reply_markup)

async def browse_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    unseen_users = [u for u in photos if u != user_id and u not in users[user_id]['seen']]
    if unseen_users:
        random_user = random.choice(unseen_users)
        users[user_id]['seen'].append(random_user)
        save_to_json(users, users_file_path)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Лайк ❤️", callback_data=f'like_{random_user}')],
            [InlineKeyboardButton("Дизлайк 🚫", callback_data=f'dislike_{random_user}')],
        ])
        await context.bot.send_photo(chat_id=user_id, photo=photos[random_user], reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("Вы просмотрели все фотографии 😅. Ждите новых участников!")

def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    liked_user = int(update.callback_query.data.split('_')[1])
    if liked_user not in likes:
        likes[liked_user] = []
    likes[liked_user].append(user_id)
    users[user_id]['seen'].append(liked_user)
    save_to_json(likes, likes_file_path)
    save_to_json(users, users_file_path)
    if user_id in likes and liked_user in likes[user_id]:
        context.bot.send_message(chat_id=user_id, text=f"Ура! 🎉 Взаимный лайк с {liked_user}. Начните общение!")
        context.bot.send_message(chat_id=liked_user, text=f"Ура! 🎉 Взаимный лайк с {user_id}. Начните общение!")
    else:
        update.callback_query.answer("Лайк учтен! Давайте продолжим.")

# def dislike(update: Update, context):
#     user_id = update.callback_query.from_user.id
#     disliked_user = int(update.callback_query.data.split('_')[1])
#     users[user_id]['seen'].append(disliked_user)  # добавляем пользователя в список просмотренных
#
#     # Сохранение данных после обновления
#     save_to_json(users, users_file_path)
#
#     send_next_photo(update, context, user_id)

if __name__ == '__main__':
    application = ApplicationBuilder().token('6497935634:AAHq6foWi8z4q55IzWM_ev6tiHA_Fzj3jH4').build()

    # start_handler = CommandHandler('start', start)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(register, pattern='^register$'))
    # application.add_handler(MessageHandler(filters.TEXT, form))
    application.add_handler(MessageHandler(filters.PHOTO, photo_received))
    application.add_handler(CallbackQueryHandler(browse_photos, pattern='^browse$'))
    application.add_handler(CallbackQueryHandler(like, pattern='^like_\d+$'))

    application.run_polling()