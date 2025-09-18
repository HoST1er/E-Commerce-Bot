from services.order_service import OrderService

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "📦 Мои заказы")  # или use /myorders
    def my_orders(message):
        user_id = message.from_user.id
        orders = OrderService.list_user_orders(user_id)

        if not orders:
            bot.send_message(message.chat.id, "У вас пока нет заказов.")
            return

        for o in orders:
            text = (
                f"🆔 Заказ №{o['id']}\n"
                f"Статус: {o['status']}\n"
                f"Сумма: {o['total']} руб.\n"
                f"Способ доставки: {o['delivery']}\n"
                f"Адрес: {o['address']}\n"
                f"Дата: {o['created_at']}\n\n"
                "🛒 Товары в заказе:\n"
            )

            if o["items"]:
                for it in o["items"]:
                    text += f"• {it['name']} — {it['quantity']} шт. — {it['price']} руб.\n"
            else:
                text += "— Нет позиций —\n"


            bot.send_message(message.chat.id, text)
