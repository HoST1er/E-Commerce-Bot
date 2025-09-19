# admin.py
import os
from utils.config import Config
from telebot import types
from services.product_service import ProductService
from services.order_service import OrderService
from services.category_service import CategoryService
from utils.logger import logger
from services.db import SessionLocal
from models.product import Product

# Временное хранилище данных админов
admin_data = {}

# Список админов (Telegram ID)
ADMIN_IDS = Config.ADMIN_IDS

# Папка для хранения фото товаров
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)


def main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id in ADMIN_IDS:
        keyboard.add("➕ Добавить товар")
        keyboard.add("✏️ Редактировать товар")
        keyboard.add("📋 Список заказов")
        keyboard.add("🛍️ Каталог", "🛒 Корзина")
        keyboard.add("📦 Мои заказы")
    else:
        keyboard.add("🛍️ Каталог", "🛒 Корзина")
        keyboard.add("📦 Мои заказы")
    return keyboard


def add_cancel_button(text):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return text, keyboard


def register(bot):
    # Проверка админа
    def is_admin(message):
        return message.from_user.id in ADMIN_IDS

    # Старт
    @bot.message_handler(commands=['start'])
    def start(message):
        kb = main_keyboard(message.from_user.id)
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        if user_id in ADMIN_IDS:
            bot.send_message(
                message.chat.id,
                f"👋 Привет, {first_name}! Вы вошли как администратор.",
                reply_markup=kb
            )
            logger.info(f"Админ {user_id} начал работу с ботом")
        else:
            bot.send_message(
                message.chat.id,
                f"👋 Привет, {first_name}! Добро пожаловать в наш магазин.",
                reply_markup=kb
            )
            logger.info(f"Пользователь {user_id} начал работу с ботом")

    # Админ-панель
    @bot.message_handler(commands=["admin"])
    def admin_panel(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа к админ-панели")
            return
        keyboard = main_keyboard(message.from_user.id)
        bot.send_message(message.chat.id, "Админ-панель:", reply_markup=keyboard)

    # --- Отмена ---
    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def cancel_action(call):
        user_id = call.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        admin_data[user_id]["cancelled"] = True
        bot.edit_message_text("❌ Действие отменено", chat_id=call.message.chat.id, message_id=call.message.message_id)

    # --- Добавление товара ---
    @bot.message_handler(func=lambda message: message.text == "➕ Добавить товар")
    def start_add_product(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа")
            return
        user_id = message.from_user.id
        admin_data[user_id] = {"cancelled": False}
        text, keyboard = add_cancel_button("Введите название товара:")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_product_name)

    def process_product_name(message):
        user_id = message.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        admin_data[user_id]["name"] = message.text
        text, keyboard = add_cancel_button("Введите цену товара:")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_product_price)

    def process_product_price(message):
        user_id = message.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        try:
            admin_data[user_id]["price"] = float(message.text)
        except ValueError:
            text, keyboard = add_cancel_button("❌ Цена должна быть числом. Введите заново:")
            msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, process_product_price)
            return
        text, keyboard = add_cancel_button("Введите описание товара (или 'нет'):")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_product_description)

    def process_product_description(message):
        user_id = message.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        desc = message.text
        admin_data[user_id]["description"] = None if desc.lower() == "нет" else desc

        # Выбор категории
        categories = CategoryService.get_all_categories()
        keyboard = types.InlineKeyboardMarkup()
        for c in categories:
            keyboard.add(types.InlineKeyboardButton(c.name, callback_data=f"category:{c.id}"))
        keyboard.add(types.InlineKeyboardButton("➕ Добавить новую категорию", callback_data="category:new"))

        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("category:"))
    def process_category(call):
        user_id = call.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        cat_id = call.data.split(":")[1]
        if cat_id == "new":
            text, keyboard = add_cancel_button("Введите название новой категории:")
            msg = bot.send_message(call.message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, add_new_category)
        else:
            admin_data[user_id]["category_id"] = int(cat_id)
            text, keyboard = add_cancel_button("Отправьте фото товара:")
            msg = bot.send_message(call.message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, lambda m: save_product_photo(bot, m, product_data=admin_data[user_id]))

    def add_new_category(message):
        user_id = message.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        category = CategoryService.add_category(message.text)
        if category:
            admin_data[user_id]["category_id"] = category["id"]
            text, keyboard = add_cancel_button("Отправьте фото товара:")
            msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, lambda m: save_product_photo(bot, m, product_data=admin_data[user_id]))
        else:
            bot.send_message(message.chat.id, "Ошибка при добавлении категории.")

    def save_product_photo(bot, message, product_data=None, product_id=None):
        user_id = message.from_user.id
        if admin_data.get(user_id, {}).get("cancelled"):
            return
        if not message.photo:
            text, keyboard = add_cancel_button("Это не фото. Отправьте фото товара:")
            msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, lambda m: save_product_photo(bot, m, product_data, product_id))
            return
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join(MEDIA_DIR, f"{file_id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        session = SessionLocal()
        try:
            if product_data:
                product = Product(
                    name=product_data["name"],
                    price=product_data["price"],
                    description=product_data.get("description"),
                    category_id=product_data.get("category_id"),
                    photo=file_path
                )
                session.add(product)
                session.commit()
                bot.send_message(message.chat.id, f"✅ Товар '{product.name}' добавлен с фото!")
            elif product_id:
                product = session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    bot.send_message(message.chat.id, "❌ Товар не найден")
                    return
                product.photo = file_path
                session.commit()
                bot.send_message(message.chat.id, f"✅ Фото товара '{product.name}' обновлено!")
        finally:
            session.close()
            if product_data and user_id in admin_data:
                admin_data.pop(user_id, None)

    # --- Редактирование товара ---
    @bot.message_handler(func=lambda message: message.text == "✏️ Редактировать товар")
    def edit_product_prompt(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа")
            return
        user_id = message.from_user.id
        admin_data[user_id] = {"cancelled": False}
        text, keyboard = add_cancel_button("Введите ID товара для редактирования:")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, edit_product_id)

    def edit_product_id(message):
        user_id = message.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        if admin_data[user_id].get("cancelled"):
            return
        try:
            product_id = int(message.text)
        except ValueError:
            text, keyboard = add_cancel_button("❌ ID должен быть числом. Попробуйте снова:")
            msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
            bot.register_next_step_handler(msg, edit_product_id)
            return
        admin_data[user_id]["product_id"] = product_id
        text, keyboard = add_cancel_button("Введите новое название товара (или 'нет'):")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, edit_product_name)

    def edit_product_name(message):
        user_id = message.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        if admin_data[user_id].get("cancelled"):
            return
        admin_data[user_id]["name"] = None if message.text.lower() == "нет" else message.text
        text, keyboard = add_cancel_button("Введите новую цену товара (или 'нет'):")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, edit_product_price)

    def edit_product_price(message):
        user_id = message.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        if admin_data[user_id].get("cancelled"):
            return
        if message.text.lower() == "нет" or not message.text.strip():
            admin_data[user_id]["price"] = None
        else:
            try:
                admin_data[user_id]["price"] = float(message.text)
            except ValueError:
                text, keyboard = add_cancel_button("❌ Цена должна быть числом. Введите заново (или 'нет'):")
                msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
                bot.register_next_step_handler(msg, edit_product_price)
                return
        text, keyboard = add_cancel_button("Введите новое описание товара (или 'нет'):")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, edit_product_description)

    def edit_product_description(message):
        user_id = message.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        if admin_data[user_id].get("cancelled"):
            return
        admin_data[user_id]["description"] = None if message.text.lower() == "нет" else message.text
        text, keyboard = add_cancel_button("Отправьте новое фото товара (или 'нет', чтобы оставить старое):")
        msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_edit_photo)

    def process_edit_photo(message):
        user_id = message.from_user.id
        admin_data.setdefault(user_id, {"cancelled": False})
        if admin_data[user_id].get("cancelled"):
            return
        kwargs = {k: v for k, v in admin_data[user_id].items() if
                  k in ["name", "price", "description"] and v is not None}

        if message.text and message.text.lower() == "нет":
            product = ProductService.update_product(admin_data[user_id]["product_id"], **kwargs)
            if product:
                bot.send_message(message.chat.id, f"✅ Товар '{product.name}' обновлен!")
            else:
                bot.send_message(message.chat.id, "❌ Товар не найден.")
            admin_data.pop(user_id, None)
            return

        # Обновление фото
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join(MEDIA_DIR, f"{file_id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == admin_data[user_id]["product_id"]).first()
            if not product:
                bot.send_message(message.chat.id, "❌ Товар не найден")
                return
            for k, v in kwargs.items():
                setattr(product, k, v)
            product.photo = file_path
            session.commit()
            bot.send_message(message.chat.id, f"✅ Товар '{product.name}' обновлен с новым фото!")
        finally:
            session.close()
            admin_data.pop(user_id, None)
    # (Функции edit_product_id, edit_product_name, edit_product_price, edit_product_description, process_edit_photo остаются как в предыдущей версии,
    # только с проверкой cancelled через admin_data[user_id].get("cancelled"))

    # --- Просмотр заказов с редактированием ---
    @bot.message_handler(func=lambda message: message.text == "📋 Список заказов")
    def show_orders(message):
        try:
            orders = OrderService.get_all_orders()
            if not orders:
                bot.send_message(message.chat.id, "Заказы не найдены.")
                return
            for order in orders:
                user_name = order.name if order.name else "Неизвестный"
                total = sum((item.product.price if item.product else 0) * item.quantity for item in order.items)
                response = f"Заказ #{order.id} | Пользователь: {user_name} | Статус: {order.status} | Итого: {total}₽"

                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(
                    "✏️ Редактировать статус",
                    callback_data=f"edit_order:{order.id}"
                ))
                bot.send_message(message.chat.id, response, reply_markup=keyboard)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при получении заказов: {e}")

    # --- Редактирование статуса заказа ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_order:"))
    def edit_order(call):
        if not is_admin(call):
            bot.answer_callback_query(call.id, "❌ У вас нет доступа")
            return
        order_id = int(call.data.split(":")[1])
        keyboard = types.InlineKeyboardMarkup()
        for status in ["Новый", "В обработке", "Отправлен", "Выполнен", "Отменен"]:
            keyboard.add(types.InlineKeyboardButton(
                status,
                callback_data=f"status:{order_id}:{status}"
            ))
        bot.edit_message_text(
            f"Выберите новый статус для заказа #{order_id}:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status:"))
    def change_order_status(call):
        if not is_admin(call):
            bot.answer_callback_query(call.id, "❌ У вас нет доступа")
            return

        parts = call.data.split(":")
        order_id = int(parts[1])
        new_status = parts[2]

        try:
            order = OrderService.update_status(order_id, new_status)
            if order:
                bot.edit_message_text(
                    f"✅ Статус заказа #{order.id} изменен на '{new_status}'",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            else:
                bot.answer_callback_query(call.id, "❌ Заказ не найден")
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status:"))
    def change_order_status(call):
        if not is_admin(call):
            bot.answer_callback_query(call.id, "❌ У вас нет доступа")
            return

        parts = call.data.split(":")
        order_id = int(parts[1])
        new_status = parts[2]

        try:
            order = OrderService.update_status(order_id, new_status)
            if order:
                bot.edit_message_text(
                    f"✅ Статус заказа #{order.id} изменен на '{new_status}'",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            else:
                bot.answer_callback_query(call.id, "❌ Заказ не найден")
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")

