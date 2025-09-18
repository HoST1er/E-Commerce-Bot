import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Абсолютный путь к корню проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    # Токен Telegram
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', '')

    # Список ID администраторов
    ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
    DATABASE_PATH = os.path.join(BASE_DIR, 'data.db')
    # URL базы данных
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    #DATABASE_URL: str = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'data.db')}")

    @classmethod
    def check(cls):
        """Проверка обязательных переменных"""
        if not cls.TELEGRAM_TOKEN:
            raise RuntimeError('TELEGRAM_TOKEN not set in .env')


# Выполняем проверку при импорте
Config.check()
