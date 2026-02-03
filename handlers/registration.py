import logging
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

import config
from utils import handle_errors, ValidationError


@handle_errors()
async def send_question(update: Update, context: CallbackContext, database) -> None:
    logging.info('发送验证问题')
    question = random.choice(list(config.QUESTIONS.keys()))

    try:
        await update.message.reply_text(
            f"Привет! 😄 Прежде чем перейти к регистрации, мне необходимо убедиться"
            f"что ты реальный человек, поэтому ответь пожалуйста на один мой вопрос! \n"
            f"{question}"
        )
    except Exception as e:
        logging.error(f"Failed to send verification question: {e}")
        raise

    correct_answer = config.QUESTIONS[question]
    context.user_data['state'] = 'verification'
    context.user_data['correct_answer'] = correct_answer

    answers = list(config.QUESTIONS.values())
    random.shuffle(answers)

    try:
        await update.message.reply_text(
            "Выбери правильный ответ.",
            reply_markup=ReplyKeyboardMarkup(
                [[answer] for answer in answers],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
    except Exception as e:
        logging.error(f"Failed to send answer options: {e}")
        raise


@handle_errors()
async def check_answer(update: Update, context: CallbackContext, database) -> None:
    user_answer = update.message.text
    correct_answer = context.user_data.get('correct_answer')

    if not correct_answer:
        await update.message.reply_text("Время ответа истекло. Попробуйте снова с командой /start")
        context.user_data.clear()
        return

    if correct_answer and user_answer == correct_answer:
        context.user_data['verification'] = 'Yes'
        await update.message.reply_text("Отлично, можешь продолжить регистрацию!")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Регистрация", callback_data='register')]
        ])
        await update.message.reply_text("Привет! 😄 Давай начнем знакомство? ", reply_markup=reply_markup)

        try:
            context.user_data['registered_users_count'] = database.get_users_count() + 1
        except Exception as e:
            logging.error(f"Failed to get users count: {e}")
            context.user_data['registered_users_count'] = 0
    else:
        context.user_data['verification'] = 'No'
        await update.message.reply_text("Неверно!")
        await exit_app(update, context)
        context.user_data.clear()


@handle_errors()
async def register(update: Update, context: CallbackContext) -> None:
    logging.info('Запуск регистрации..')
    try:
        await update.callback_query.message.reply_text("Как тебя зовут? 📝")
    except Exception as e:
        logging.error(f"Failed to send registration prompt: {e}")
        raise
    context.user_data['state'] = 'name'


@handle_errors(error_message="Ошибка при вводе имени")
async def input_name(update: Update, context: CallbackContext) -> None:
    name = update.message.text.strip()

    if not name or len(name) < 2:
        await update.message.reply_text("Имя должно содержать минимум 2 символа. Попробуйте снова.")
        return

    if len(name) > 50:
        await update.message.reply_text("Имя слишком длинное (максимум 50 символов). Попробуйте снова.")
        return

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


@handle_errors(error_message="Ошибка при вводе пола")
async def input_gender(update: Update, context: CallbackContext) -> None:
    gender = update.message.text

    if gender not in ["Парень", "Девушка"]:
        await update.message.reply_text("Пожалуйста, выберите 'Парень' или 'Девушка'.")
        return

    logging.info(f'Сохранение гендера...')
    context.user_data['gender'] = gender
    await update.message.reply_text("Сколько тебе лет? 🎂")
    context.user_data['state'] = 'age'


@handle_errors(error_message="Ошибка при вводе возраста")
async def input_age(update: Update, context: CallbackContext) -> None:
    age = update.message.text.strip()

    try:
        age_num = int(age)
        if age_num < 12 or age_num > 100:
            raise ValidationError("Возраст должен быть от 12 до 100 лет")
        age = str(age_num)
    except ValueError:
        raise ValidationError("Пожалуйста, введите корректное число для возраста")

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


@handle_errors(error_message="Ошибка при вводе цели знакомства")
async def input_goal(update: Update, context: CallbackContext, regions: tuple) -> None:
    goal = update.message.text

    if goal not in ["Общение", "Дружба", "Отношения", "Интим"]:
        await update.message.reply_text("Пожалуйста, выберите одну из предложенных целей.")
        return

    context.user_data['goal'] = goal

    if not regions:
        await update.message.reply_text("Не удалось загрузить список регионов. Попробуйте позже.")
        context.user_data['state'] = 'exit'
        return

    keyboard = ReplyKeyboardMarkup(
        [[region] for region in regions],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text("Из какого ты региона? 🏙️", reply_markup=keyboard)
    context.user_data['state'] = 'city'


@handle_errors(error_message="Ошибка при создании профиля")
async def input_city(update: Update, context: CallbackContext, database) -> None:
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username

    if not user_name:
        user_name = "unknown"

    city = update.message.text.strip()

    if not city:
        await update.message.reply_text("Укажите ваш регион")
        return

    context.user_data['city'] = city

    user_data = {
        'name': context.user_data.get('name'),
        'username': '@' + user_name,
        'gender': context.user_data.get('gender'),
        'age': context.user_data.get('age'),
        'goal': context.user_data.get('goal'),
        'city': context.user_data.get('city'),
        'photo': None,
        'seen': []
    }

    try:
        database.add_user(user_id, user_data)
        database.save_users()

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Загрузить фото", callback_data='photo'),
             InlineKeyboardButton("Без фото", callback_data='no_photo')]
        ])
        await update.message.reply_text(
            "Вот так, мы познакомились! Я сохранил твою анкету. Теперь скажи мне, хочешь ли ты загрузить своё фото?",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Failed to save user profile: {e}")
        await update.message.reply_text("Не удалось сохранить профиль. Попробуйте позже с команды /start")
        raise


@handle_errors()
async def exit_app(update: Update, context: CallbackContext) -> None:
    logging.info('Выход')
    context.user_data['state'] = 'exit'
    await update.message.reply_text(
        "Спасибо за использование бота!\n\n"
        "Если захочешь продолжить знакомства, просто выбери в меню 'Начать знакомство' 😉"
    )
    context.user_data.clear()
