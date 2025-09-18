import logging
import os
from logging.handlers import RotatingFileHandler

# Папка для логов
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Основной лог-файл
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# Создаём логгер
logger = logging.getLogger("ecommerce_bot")
logger.setLevel(logging.INFO)  # можно поменять на DEBUG, если нужно больше деталей

# Формат логов
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 📌 Логи в файл (с ротацией, чтобы файл не рос бесконечно)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)

# 📌 Логи в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Подключаем хендлеры
logger.addHandler(file_handler)
logger.addHandler(console_handler)
