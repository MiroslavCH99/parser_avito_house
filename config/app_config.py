import os

from dotenv import load_dotenv
# Загрузка переменных из .env файла
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise NameError