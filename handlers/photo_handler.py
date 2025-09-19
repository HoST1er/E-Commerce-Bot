import os
from services.db import SessionLocal
from models.product import Product

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

def save_product_photo(bot, message, product_data=None, product_id=None):
    """
    Сохраняет фото товара и обновляет/добавляет продукт в базе.
    Если product_data задан - добавление нового товара.
    Если product_id задан - редактирование существующего товара.
    """
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
            # добавление нового товара
            product = Product(**product_data, photo=file_path)
            session.add(product)
            session.commit()
            bot.send_message(message.chat.id, f"✅ Товар '{product.name}' добавлен с фото!")
        elif product_id:
            # редактирование существующего товара
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                bot.send_message(message.chat.id, "Товар не найден")
                return
            product.photo = file_path
            session.commit()
            bot.send_message(message.chat.id, f"✅ Фото товара '{product.name}' обновлено!")
    finally:
        session.close()
