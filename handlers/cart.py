from telebot import types
from services.cart_service import CartService

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "🛒 Корзина")
    def show_cart(message):
        user_id = message.from_user.id
        cart_items = CartService.get_cart_items(user_id)

        if not cart_items:
            bot.send_message(message.chat.id, "Ваша корзина пуста 🛒")
            return

        text = "Ваша корзина:\n"
        total = 0
        for item in cart_items:
            text += f"{item.name} — {item.quantity} шт. — {item.price} руб.\n"
            total += item.price * item.quantity

        text += f"\nИтого: {total} руб."

        # --- Inline-кнопка "Оформить заказ" ---
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout:start"))

        bot.send_message(message.chat.id, text, reply_markup=keyboard)