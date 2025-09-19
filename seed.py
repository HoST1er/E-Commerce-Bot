# scripts/seed.py
import os
from services.db import SessionLocal
from models.category import Category
from models.product import Product

MEDIA_PATH = "media/products"  # папка с фото

def seed():
    session = SessionLocal()

    # --- Очистка таблиц ---
    session.query(Product).delete()
    session.query(Category).delete()
    session.commit()

    # --- Создаем категории ---
    electronics = Category(name="Электроника")
    books = Category(name="Книги")
    clothing = Category(name="Одежда")
    session.add_all([electronics, books, clothing])
    session.commit()

    # --- Создаем товары с фото ---
    products_data = [
        {"name": "Смартфон", "description": "Современный смартфон с хорошей камерой", "price": 299.99,
         "category_id": electronics.id, "photo": os.path.join(MEDIA_PATH, "phone.png")},
        {"name": "Ноутбук", "description": "Мощный ноутбук для работы и игр", "price": 899.99,
         "category_id": electronics.id, "photo": os.path.join(MEDIA_PATH, "laptop.png")},
        {"name": "Наушники", "description": "Беспроводные наушники с шумоподавлением", "price": 129.99,
         "category_id": electronics.id, "photo": os.path.join(MEDIA_PATH, "headphones.png")},
        {"name": "Роман", "description": "Интересный художественный роман", "price": 19.99,
         "category_id": books.id, "photo": os.path.join(MEDIA_PATH, "novel.png")},
        {"name": "Энциклопедия", "description": "Полная энциклопедия для детей", "price": 49.99,
         "category_id": books.id, "photo": os.path.join(MEDIA_PATH, "encyclopedia.png")},
        {"name": "Футболка", "description": "Классическая футболка из хлопка", "price": 14.99,
         "category_id": clothing.id, "photo": os.path.join(MEDIA_PATH, "t_shirt.png")},
        {"name": "Джинсы", "description": "Удобные джинсы для повседневной носки", "price": 39.99,
         "category_id": clothing.id, "photo": os.path.join(MEDIA_PATH, "jeans.png")},
    ]

    products = []
    for data in products_data:
        product = Product(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            category_id=data["category_id"],
            photo=data["photo"]
        )
        products.append(product)

    session.add_all(products)
    session.commit()
    session.close()

    print("Сеанс заполнения базы завершен. Категории и товары созданы!")

if __name__ == "__main__":
    seed()
