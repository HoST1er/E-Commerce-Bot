from telebot import types

# --------------------
# Главное меню для пользователя
# --------------------
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🛍️ Каталог", "🛒 Корзина")
    keyboard.row("📦 Мои заказы")
    return keyboard


# --------------------
# Меню для администратора
# --------------------
def admin_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🛍️ Каталог", "🛒 Корзина")
    keyboard.row("📦 Мои заказы", "📊 Отчеты")
    keyboard.row("⬅️ Главное меню")
    return keyboard


# --------------------
# Inline-кнопки для действий с товаром
# --------------------
def product_actions(product_id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Добавить в корзину 🛒", callback_data=f"add_to_cart:{product_id}")
    )
    return keyboard


# --------------------
# Inline-кнопки для действий в корзине
# --------------------
def cart_actions(product_id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Удалить ❌", callback_data=f"remove_from_cart:{product_id}")
    )
    return keyboard
