import os

from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv("TELEGRAM_TOKEN")
api_root = os.getenv("API_ROOT")
