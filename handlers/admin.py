from telebot import types
from services.product_service import ProductService
from services.order_service import OrderService
from services.category_service import CategoryService
from utils.logger import logger

# Временное хранилище данных админов
admin_data = {}

# Список админов (Telegram ID)
ADMIN_IDS = [328729390]


def main_keyboard(user_id):
    """
    Возвращает клавиатуру в зависимости от роли пользователя.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id in ADMIN_IDS:
        # Кнопки для админа
        keyboard.add("➕ Добавить товар")
        keyboard.add("✏️ Редактировать товар")
        keyboard.add("📦 Список заказов")
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

    # Проверка админа
    def is_admin(message):
        return message.from_user.id in ADMIN_IDS

    # Старт /start
    @bot.message_handler(commands=['start'])
    def start(message):
        kb = main_keyboard(message.from_user.id)
        bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=kb)

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
            save_product(user_id, call.message.chat.id)

    def add_new_category(message):
        user_id = message.from_user.id
        category = CategoryService.add_category(message.text)
        if category:
            admin_data[user_id]["category_id"] = category["id"]
            save_product(user_id, message.chat.id)
        else:
            bot.send_message(message.chat.id, "Ошибка при добавлении категории.")

    def save_product(user_id, chat_id):
        data = admin_data[user_id]
        product = ProductService.add_product(
            name=data["name"],
            price=data["price"],
            description=data.get("description"),
            category_id=data.get("category_id")
        )
        if product:
            bot.send_message(chat_id, f"✅ Товар '{product['name']}' добавлен!")
        else:
            bot.send_message(chat_id, "❌ Ошибка при добавлении товара.")
        admin_data.pop(user_id, None)

    # --- Просмотр всех заказов ---
    @bot.message_handler(func=lambda message: message.text == "📦 Список заказов")
    def view_orders(message):
        if not is_admin(message):
            bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде")
            return

        try:
            orders = OrderService.list_all_orders()
            if not orders:
                bot.send_message(message.chat.id, "Список заказов пуст.")
                return

            for order in orders:
                items_text = "\n".join(
                    [f"{i.product.name} x{i.quantity} - {i.price} руб." for i in order.products]
                )

                bot.send_message(
                    message.chat.id,
                    f"🆔 Заказ №{order.id}\n"
                    f"Статус: {order.status}\n"
                    f"Сумма: {order.total} руб.\n"
                    f"Способ доставки: {order.delivery}\n"
                    f"Адрес: {order.address}\n"
                    f"Дата: {order.created_at}\n"
                    f"Товары:\n{items_text}"
                )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при получении заказов: {e}")

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
                               "Введите новое название товара (или напишите 'нет', чтобы оставить без изменений):")
        bot.register_next_step_handler(msg, edit_product_name)

    def edit_product_name(message):
        admin_data["name"] = None if message.text.lower() == "нет" else message.text
        msg = bot.send_message(message.chat.id,
                               "Введите новую цену товара (или напишите 'нет', чтобы оставить без изменений):")
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
                               "Введите новое описание товара (или напишите 'нет', чтобы оставить без изменений):")
        bot.register_next_step_handler(msg, edit_product_description)

    def edit_product_description(message):
        admin_data["description"] = None if message.text.lower() == "нет" else message.text
        kwargs = {k: v for k, v in admin_data.items() if k in ["name", "price", "description"] and v is not None}

        try:
            product = ProductService.update_product(admin_data["product_id"], **kwargs)
            if not product:
                bot.send_message(message.chat.id, "❌ Товар с таким ID не найден.")
            else:
                bot.send_message(message.chat.id, f"✅ Товар обновлен: {product.name}")
                logger.info(f"Админ обновил товар: {product.id} - {product.name}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при обновлении товара: {e}")

        admin_data.clear()