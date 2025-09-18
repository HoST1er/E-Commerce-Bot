from telebot import types
from utils.keyboards import main_menu, admin_menu
from utils.config import Config
from utils.logger import logger

def register(bot):
    @bot.message_handler(commands=["start"])
    def start_handler(message):
        user_id = message.from_user.id
        first_name = message.from_user.first_name

        if user_id in Config.ADMIN_IDS:
            bot.send_message(
                message.chat.id,
                f"👋 Привет, {first_name}! Вы вошли как администратор.",
                reply_markup=admin_menu()
            )
            logger.info(f"Админ {user_id} начал работу с ботом")
        else:
            bot.send_message(
                message.chat.id,
                f"👋 Привет, {first_name}! Добро пожаловать в наш магазин.",
                reply_markup=main_menu()
            )
            logger.info(f"Пользователь {user_id} начал работу с ботом")

    # Главное меню
    @bot.message_handler(func=lambda m: m.text == "⬅️ Главное меню")
    def back_to_main(message):
        user_id = message.from_user.id
        if user_id in Config.ADMIN_IDS:
            bot.send_message(message.chat.id, "Вы вернулись в админ-меню.", reply_markup=admin_menu())
        else:
            bot.send_message(message.chat.id, "Вы вернулись в главное меню.", reply_markup=main_menu())
