from telebot import types
from services.cart_service import CartService
from services.db import SessionLocal
from models.product import Product


def register(bot):
    # --- Показ корзины (вынес в отдельную функцию для удобства) ---
    def get_cart_text_and_keyboard(user_id):
        cart_items = CartService.get_cart_items(user_id)

        if not cart_items:
            return "🛒 Ваша корзина пуста.", None

        text = "🛍️ Ваша корзина:\n\n"
        keyboard = types.InlineKeyboardMarkup()
        total = 0

        for item in cart_items:
            subtotal = item.price * item.quantity
            total += subtotal
            text += f"{item.name} x{item.quantity} = {subtotal}₽\n"

            keyboard.add(
                types.InlineKeyboardButton(f"➕ {item.name}", callback_data=f"inc:{item.product_id}"),
                types.InlineKeyboardButton(f"➖ {item.name}", callback_data=f"dec:{item.product_id}")
            )

        keyboard.add(
            types.InlineKeyboardButton("❌ Очистить корзину", callback_data="clear_cart"),
            types.InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout:start")
        )
        text += f"\nИтого: {total}₽"

        return text, keyboard

    @bot.message_handler(func=lambda message: message.text == "🛒 Корзина")
    def show_cart(message):
        user_id = message.from_user.id
        text, keyboard = get_cart_text_and_keyboard(user_id)
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

    # --- Обработка кнопок в корзине ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith(("inc:", "dec:", "clear_cart")))
    def handle_cart_actions(call):
        user_id = call.from_user.id

        if call.data.startswith("inc:"):
            product_id = int(call.data.split(":")[1])
            session = SessionLocal()
            product = session.query(Product).get(product_id)
            session.close()
            if product:
                CartService.add_to_cart(user_id, product.id, product.name, product.price, 1)

        elif call.data.startswith("dec:"):
            product_id = int(call.data.split(":")[1])
            CartService.remove_one(user_id, product_id)

        elif call.data == "clear_cart":
            CartService.clear_cart(user_id)

        # Обновляем то же самое сообщение, не удаляя его
        text, keyboard = get_cart_text_and_keyboard(user_id)
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )


