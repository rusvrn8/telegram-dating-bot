import logging
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

import config


async def send_question(update: Update, context: CallbackContext, database) -> None:
    logging.info('发送验证问题')
    question = random.choice(list(config.QUESTIONS.keys()))
    await update.message.reply_text(
        f"Привет! 😄 Прежде чем перейти к регистрации, мне необходимо убедиться"
        f"что ты реальный человек, поэтому ответь пожалуйста на один мой вопрос! \n"
        f"{question}"
    )
    correct_answer = config.QUESTIONS[question]
    context.user_data['state'] = 'verification'
    context.user_data['correct_answer'] = correct_answer

    answers = list(config.QUESTIONS.values())
    random.shuffle(answers)
    await update.message.reply_text(
        "Выбери правильный ответ.",
        reply_markup=ReplyKeyboardMarkup(
            [[answer] for answer in answers],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


async def check_answer(update: Update, context: CallbackContext, database) -> None:
    user_answer = update.message.text
    correct_answer = context.user_data.get('correct_answer')
    if correct_answer and user_answer == correct_answer:
        context.user_data['verification'] = 'Yes'
        await update.message.reply_text("Отлично, можешь продолжить регистрацию!")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Регистрация", callback_data='register')]
        ])
        await update.message.reply_text("Привет! 😄 Давай начнем знакомство? ", reply_markup=reply_markup)
        context.user_data['registered_users_count'] = database.get_users_count() + 1
    else:
        context.user_data['verification'] = 'No'
        await update.message.reply_text("Неверно!")
        await exit_app(update, context)
        context.user_data.clear()


async def register(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск регистрации..')
    await update.callback_query.message.reply_text("Как тебя зовут? 📝")
    context.user_data['state'] = 'name'


async def input_name(update: Update, context: CallbackContext) -> None:
    name = update.message.text
    context.user_data['name'] = name
    context.user_data['state'] = 'gender'

    reply_keyboard = [["Парень", "Девушка"]]
    await update.message.reply_text(
        "Какой у тебя пол? 🚹🚺",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


async def input_gender(update: Update, context: CallbackContext) -> None:
    gender = update.message.text
    logging.info(f'Сохранение гендера...')
    context.user_data['gender'] = gender
    await update.message.reply_text("Сколько тебе лет? 🎂")
    context.user_data['state'] = 'age'


async def input_age(update: Update, context: CallbackContext) -> None:
    age = update.message.text
    context.user_data['age'] = age
    context.user_data['state'] = 'goal'

    keyboards = ["Общение", "Дружба", "Отношения", "Интим"]
    await update.message.reply_text(
        "Какая у тебя цель знакомства? 🎯",
        reply_markup=ReplyKeyboardMarkup(
            [[keyboard] for keyboard in keyboards],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


async def input_goal(update: Update, context: CallbackContext, regions: tuple) -> None:
    goal = update.message.text
    context.user_data['goal'] = goal
    keyboard = ReplyKeyboardMarkup(
        [[region] for region in regions],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text("Из какого ты региона? 🏙️", reply_markup=keyboard)
    context.user_data['state'] = 'city'


async def input_city(update: Update, context: CallbackContext, database) -> None:
    from telegram import Update

    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_name = update.message.from_user.username
    city = update.message.text
    context.user_data['city'] = city

    database.add_user(user_id, {
        'name': context.user_data.get('name'),
        'username': '@' + user_name,
        'gender': context.user_data.get('gender'),
        'age': context.user_data.get('age'),
        'goal': context.user_data.get('goal'),
        'city': context.user_data.get('city'),
        'photo': None,
        'seen': []
    })
    database.save_users()

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Загрузить фото", callback_data='photo'),
         InlineKeyboardButton("Без фото", callback_data='no_photo')]
    ])
    await update.message.reply_text(
        "Вот так, мы познакомились! Я сохранил твою анкету. Теперь скажи мне, хочешь ли ты загрузить своё фото?",
        reply_markup=reply_markup
    )


async def exit_app(update: Update, context: CallbackContext) -> None:
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.message.reply_text(
        "Спасибо за использование бота!\n\n"
        "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉"
    )
    context.user_data.clear()
