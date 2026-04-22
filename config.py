import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.sudrf.ru')
