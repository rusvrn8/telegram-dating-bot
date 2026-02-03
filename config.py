import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '6497935634:AAHq6foWi8z4q55IzWM_ev6tiHA_Fzj3jH4')
SUPPORT_CHAT_ID = int(os.getenv('SUPPORT_CHAT_ID', '6700302188'))

USERS_FILE = 'users_test.json'
PHOTOS_FILE = 'photos_test.json'
LIKES_FILE = 'likes_test.json'
REGIONS_FILE = 'regions_rf.txt'

PROFILE_CHECK_INTERVAL = 86400
LIKES_CHECK_INTERVAL = 3600

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

GOALS = ["Общение", "Дружба", "Отношения", "Интим"]
GENDERS = ["Парень", "Девушка"]
AGE_RANGES = ["12-17", "18-25", "26-35", "36-45", "46-55", "56-70"]

QUESTIONS = {
    "Сколько будет 1 + 1?": "2",
    "Сколько будет 2 + 2?": "4",
    "Сколько будет 3 + 3?": "6"
}
