from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationBuilder
import logging
import json
import os
import random
import threading
from telegram.ext import CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

chats_file_path = 'chats_test.json'

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


chats = load_from_json(chats_file_path)


# Словарь для хранения пар пользователей
# chats = {}


async def start(update: Update, context: CallbackContext) -> None:
	await update.message.reply_text('Привет! Введите /chat для организации чата.')


async def chat(update: Update, context: CallbackContext) -> None:
	user_id = update.message.chat.id

	# Проверяем, есть ли уже пара для текущего пользователя
	if user_id in chats and chats[user_id] is not None:
		await update.message.reply_text('Вы уже в чате!')
	else:
		# Создаем случайный чат с другим пользователем
		engaged_users = [user for user in chats.keys() if user != user_id]

		if engaged_users:
			partner = random.choice(engaged_users)
			chats[user_id] = partner
			chats[partner] = user_id
			save_to_json(chats, chats_file_path)
			await update.message.reply_text(f'Вы в чате с {partner}. Пишите сообщения!')
			await context.bot.send_message(chat_id=partner, text=f'Вы в чате с {user_id}. Пишите сообщения!')
		else:
			# Если нет других пользователей, то добавляем текущего пользователя в список
			chats[user_id] = None
			save_to_json(chats, chats_file_path)
			await update.message.reply_text('Ожидание другого пользователя для чата...')


async def echo(update: Update, context: CallbackContext) -> None:
	user_id = update.message.chat.id

	if user_id in chats and chats[user_id] is not None:
		partner_id = chats[user_id]
		await context.bot.send_message(chat_id=partner_id, text=update.message.text)


async def next_partner(update, context):
	user_id = update.message.chat.id
	partner_id = chats[user_id]

	chats[user_id] = None
	chats[partner_id] = None
	save_to_json(chats, chats_file_path)

	await update.message.reply_text('Проверка...')

	# engaged_users = [user for user in chats.keys() if user != user_id]
	#
	# if engaged_users:
	# 	partner = random.choice(engaged_users)
	# 	chats[user_id] = partner
	# 	chats[partner] = user_id
	# 	save_to_json(chats, chats_file_path)
	# 	await update.message.reply_text(f'Вы в чате с {partner}. Пишите сообщения!')
	# 	await context.bot.send_message(chat_id=partner, text=f'Вы в чате с {user_id}. Пишите сообщения!')
	# else:
	# 	# Если нет других пользователей, то добавляем текущего пользователя в список
	# 	chats[user_id] = None
	# 	save_to_json(chats, chats_file_path)
	# 	await update.message.reply_text('Ожидание другого пользователя для чата...')


def main() -> None:
	application = ApplicationBuilder().token('7047282882:AAFZZu6RqOuGxzFA8wFxgGZbbzESWrO0Oq0').build()

	application.add_handler(CommandHandler('start', start))
	application.add_handler(CommandHandler('chat', chat))
	application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

	application.add_handler(CommandHandler('next_partner', next_partner))
	# application.add_handler(CommandHandler('stop', stop))

	application.run_polling()


if __name__ == '__main__':
	main()
