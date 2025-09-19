# admin.py
import os
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
ADMIN_IDS = [328729390]

# Папка для хранения фото товаров
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)


def main_keyboard(user_id):
    """
    Возвращает клавиатуру в зависимости от роли пользователя.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id in ADMIN_IDS:
        # Кнопки для админа
        keyboard.add("➕ Добавить товар")
        keyboard.add("✏️ Редактировать товар")
        keyboard.add("📋 Список заказов")
        keyboard.add("🛍️ Каталог", "🛒 Корзина")
        keyboard.add("📦 Мои заказы")
    else:
        # Кнопки для обычного пользователя
        keyboard.add("🛍️ Каталог", "🛒 Корзина")
        keyboard.add("📦 Мои заказы")
    return keyboard


def register(bot):
    """
    Регистрация хендлеров
    """

    # --- Проверка админа ---
    def is_admin(message):
        return message.from_user.id in ADMIN_IDS

    # --- Старт ---
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

    # --- Админ-панель через команду ---
    @bot.message_handler(commands=["admin"])
    def admin_panel(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа к админ-панели")
            return
        keyboard = main_keyboard(message.from_user.id)
        bot.send_message(message.chat.id, "Админ-панель:", reply_markup=keyboard)

    # --- Добавление нового товара ---
    @bot.message_handler(func=lambda message: message.text == "➕ Добавить товар")
    def start_add_product(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде")
            return
        msg = bot.send_message(message.chat.id, "Введите название товара:")
        bot.register_next_step_handler(msg, process_product_name)

    def process_product_name(message):
        admin_data[message.from_user.id] = {"name": message.text}
        msg = bot.send_message(message.chat.id, "Введите цену товара:")
        bot.register_next_step_handler(msg, process_product_price)

    def process_product_price(message):
        admin_data[message.from_user.id]["price"] = float(message.text)
        msg = bot.send_message(message.chat.id, "Введите описание товара (или 'нет'):")
        bot.register_next_step_handler(msg, process_product_description)

    def process_product_description(message):
        desc = message.text
        admin_data[message.from_user.id]["description"] = None if desc.lower() == "нет" else desc

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
        if not is_admin(call):
            bot.send_message(call.message.chat.id, "❌ У вас нет доступа к этой команде")
            return

        cat_id = call.data.split(":")[1]

        if cat_id == "new":
            msg = bot.send_message(call.message.chat.id, "Введите название новой категории:")
            bot.register_next_step_handler(msg, add_new_category)
        else:
            admin_data[user_id]["category_id"] = int(cat_id)
            # Теперь просим фото и создаем товар
            msg = bot.send_message(call.message.chat.id, "Отправьте фото товара:")
            bot.register_next_step_handler(msg, lambda m: save_product_photo(bot, m, product_data=admin_data[user_id]))

    def add_new_category(message):
        user_id = message.from_user.id
        category = CategoryService.add_category(message.text)
        if category:
            admin_data[user_id]["category_id"] = category["id"]
            msg = bot.send_message(message.chat.id, "Отправьте фото товара:")
            bot.register_next_step_handler(msg, lambda m: save_product_photo(bot, m, product_data=admin_data[user_id]))
        else:
            bot.send_message(message.chat.id, "Ошибка при добавлении категории.")

    # --- Функция сохранения фото ---
    def save_product_photo(bot, message, product_data=None, product_id=None):
        if not message.photo:
            msg = bot.send_message(message.chat.id, "Это не фото. Отправьте фото товара:")
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
            if product_data and message.from_user.id in admin_data:
                admin_data.pop(message.from_user.id, None)

    # --- Редактирование товара ---
    @bot.message_handler(func=lambda message: message.text == "✏️ Редактировать товар")
    def edit_product_prompt(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде")
            return
        msg = bot.send_message(message.chat.id, "Введите ID товара для редактирования:")
        bot.register_next_step_handler(msg, edit_product_id)

    def edit_product_id(message):
        try:
            product_id = int(message.text)
        except ValueError:
            msg = bot.send_message(message.chat.id, "❌ ID должен быть числом. Попробуйте снова:")
            bot.register_next_step_handler(msg, edit_product_id)
            return
        admin_data["product_id"] = product_id
        msg = bot.send_message(message.chat.id,
                               "Введите новое название товара (или 'нет'):")
        bot.register_next_step_handler(msg, edit_product_name)

    def edit_product_name(message):
        admin_data["name"] = None if message.text.lower() == "нет" else message.text
        msg = bot.send_message(message.chat.id,
                               "Введите новую цену товара (или 'нет'):")
        bot.register_next_step_handler(msg, edit_product_price)

    def edit_product_price(message):
        if message.text.lower() == "нет" or not message.text.strip():
            admin_data["price"] = None
        else:
            try:
                admin_data["price"] = float(message.text)
            except ValueError:
                msg = bot.send_message(message.chat.id, "❌ Цена должна быть числом. Введите заново (или 'нет'):")
                bot.register_next_step_handler(msg, edit_product_price)
                return
        msg = bot.send_message(message.chat.id,
                               "Введите новое описание товара (или 'нет'):")
        bot.register_next_step_handler(msg, edit_product_description)

    def edit_product_description(message):
        admin_data["description"] = None if message.text.lower() == "нет" else message.text
        msg = bot.send_message(message.chat.id,
                               "Отправьте новое фото товара (или 'нет', чтобы оставить старое):")
        bot.register_next_step_handler(msg, process_edit_photo)

    def process_edit_photo(message):
        if message.text and message.text.lower() == "нет":
            # Обновляем только текстовые поля
            kwargs = {k: v for k, v in admin_data.items() if k in ["name", "price", "description"] and v is not None}
            try:
                product = ProductService.update_product(admin_data["product_id"], **kwargs)
                if product:
                    bot.send_message(message.chat.id, f"✅ Товар '{product.name}' обновлен!")
                else:
                    bot.send_message(message.chat.id, "❌ Товар не найден.")
            finally:
                admin_data.clear()
            return

        # Если прислали фото — обновляем фото вместе с текстовыми полями
        kwargs = {k: v for k, v in admin_data.items() if k in ["name", "price", "description"] and v is not None}
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == admin_data["product_id"]).first()
            if not product:
                bot.send_message(message.chat.id, "❌ Товар не найден")
                return
            for k, v in kwargs.items():
                setattr(product, k, v)
            # Сохраняем фото
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(MEDIA_DIR, f"{file_id}.jpg")
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
            product.photo = file_path
            session.commit()
            bot.send_message(message.chat.id, f"✅ Товар '{product.name}' обновлен с новым фото!")
        finally:
            session.close()
            admin_data.clear()

    # --- Просмотр всех заказов ---
    @bot.message_handler(func=lambda message: message.text == "📋 Список заказов")
    def show_orders(message):
        try:
            orders = OrderService.get_all_orders()
            if not orders:
                bot.send_message(message.chat.id, "Заказы не найдены.")
                return

            response = ""
            for order in orders:
                user_name = order.name if order.name else "Неизвестный"
                response += f"Заказ #{order.id} | Пользователь: {user_name}\n"
                total = 0
                for item in order.items:
                    product_name = item.product.name if item.product else "Неизвестный продукт"
                    subtotal = (item.product.price if item.product else 0) * item.quantity
                    total += subtotal
                    response += f"  - {product_name} x {item.quantity} = {subtotal}₽\n"
                response += f"Итого: {total}₽\n\n"

            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при получении заказов: {e}")



