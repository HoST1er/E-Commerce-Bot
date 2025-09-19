import os

from telebot import types
from services.product_service import ProductService
from services.cart_service import CartService
from utils.keyboards import main_menu

def register(bot):
    """Регистрируем обработчики каталога"""

    # --- Обработчик кнопки "Каталог" ---
    @bot.message_handler(func=lambda m: m.text == "🛍️ Каталог")
    def show_categories(message):
        categories = ProductService.get_all_categories()
        if not categories:
            bot.send_message(message.chat.id, "Категории отсутствуют.", reply_markup=main_menu())
            return

        # Создаем инлайн-кнопки для категорий
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for cat in categories:
            button = types.InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")
            buttons.append(button)
        markup.add(*buttons)

        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)

    # --- Обработчик выбора категории ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
    def show_products_by_category(call):
        cat_id = int(call.data.split("_")[1])
        products = ProductService.get_products_by_category(cat_id)

        if not products:
            bot.send_message(call.message.chat.id, "В этой категории пока нет товаров.", reply_markup=main_menu())
            return

        for p in products:
            text = f"📦 {p.name}\n💰 Цена: {p.price} руб."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_{p.id}"))
            # Если есть фото и файл существует, отправляем фото
            if p.photo and os.path.exists(p.photo):
                with open(p.photo, "rb") as photo:
                    bot.send_photo(call.message.chat.id, photo, caption=text, reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, text, reply_markup=markup)

    # --- Обработчик нажатий inline-кнопок "Добавить в корзину" ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
    def add_to_cart(call):
        product_id = int(call.data.split("_")[1])
        product = ProductService.get_product_by_id(product_id)
        if not product:
            bot.send_message(call.message.chat.id, "Товар не найден.")
            return

        # Добавляем товар в корзину (CartService должен принимать id, name, price, quantity)
        from services.cart_service import CartService
        CartService.add_to_cart(
            user_id=call.from_user.id,
            product_id=product.id,
            name=product.name,
            price=product.price,
            quantity=1
        )
        bot.answer_callback_query(call.id, f"{product.name} добавлен в корзину!")
