import telebot
from utils.config import Config
from utils.keyboards import main_menu
from handlers import catalog, cart, orders, checkout, admin

bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)

# Регистрируем хендлеры
catalog.register(bot)
cart.register(bot)
orders.register(bot)
checkout.register(bot)
admin.register(bot)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 Добро пожаловать в магазин!", reply_markup=main_menu())

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
