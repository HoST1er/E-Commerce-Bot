from telebot import types
from services.cart_service import CartService
from services.order_service import OrderService
from utils.logger import logger

# Временное хранилище данных пользователя
user_checkout_data = {}

def register(bot):
    """
    Хендлеры оформления заказа
    """

    # --- Inline-кнопка из корзины запускает оформление ---
    @bot.callback_query_handler(func=lambda call: call.data == "checkout:start")
    def start_checkout_from_cart(call):
        user_id = call.from_user.id
        cart = CartService.get_cart(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Ваша корзина пуста!")
            return

        # Сохраняем корзину во временное хранилище
        user_checkout_data[user_id] = {"cart": cart}
        bot.answer_callback_query(call.id)

        # Начало ввода данных
        msg = bot.send_message(call.message.chat.id, "Введите ваше имя:")
        bot.register_next_step_handler(msg, process_name)

    # --- Ввод имени ---
    def process_name(message):
        user_checkout_data[message.from_user.id]["name"] = message.text
        msg = bot.send_message(message.chat.id, "Введите номер телефона:")
        bot.register_next_step_handler(msg, process_phone)

    # --- Ввод телефона ---
    def process_phone(message):
        user_checkout_data[message.from_user.id]["phone"] = message.text
        msg = bot.send_message(message.chat.id, "Введите адрес доставки:")
        bot.register_next_step_handler(msg, process_address)

    # --- Ввод адреса и выбор способа доставки ---
    def process_address(message):
        user_checkout_data[message.from_user.id]["address"] = message.text

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🚚 Курьером", callback_data="delivery:courier"))
        keyboard.add(types.InlineKeyboardButton("🏪 Самовывоз", callback_data="delivery:pickup"))

        bot.send_message(message.chat.id, "Выберите способ доставки:", reply_markup=keyboard)

    # --- Обработка выбора доставки ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delivery:"))
    def process_delivery(call):
        user_id = call.from_user.id
        delivery_type = call.data.split(":")[1]

        data = user_checkout_data.get(user_id)
        if not data:
            bot.answer_callback_query(call.id, "Ошибка: данные пользователя не найдены.")
            return

        cart = data["cart"]
        total = sum(item.price * item.quantity for item in cart)

        order_data = {
            "name": data["name"],
            "phone": data["phone"],
            "address": data["address"],
            "delivery": delivery_type
        }

        # --- Создание заказа ---
        # try:
        print(user_id)
        print(cart)
        print(order_data)
        print(total)
        order = OrderService.create_order(
            user_id=user_id,
            cart_items=cart,  # это уже объекты CartItem
            user_data=order_data,
            total=total
        )
        # except Exception as e:
        #     bot.answer_callback_query(call.id)
        #     bot.send_message(call.message.chat.id, f"❌ Ошибка при оформлении заказа. Попробуйте снова.\n{e}")
        #     logger.error(f"Ошибка при создании заказа: {e}")
        #     return

        if not order:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "❌ Ошибка при оформлении заказа. Попробуйте снова.")
            return

        # Очистка корзины и временных данных
        CartService.clear_cart(user_id)
        user_checkout_data.pop(user_id, None)

        bot.answer_callback_query(call.id)
        if delivery_type == 'pickup':
            delivery_type = 'Самовывоз'
        else:
            delivery_type = 'Курьером'
        bot.send_message(
            call.message.chat.id,
            f"✅ Заказ оформлен!\nНомер заказа: {order['id']}\nСумма: {total} руб.\nСпособ доставки: {delivery_type}"
        )

        logger.info(f"Пользователь {user_id} создал заказ {order['id']} на сумму {total} руб.")
