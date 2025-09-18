from services.db import SessionLocal
from models.category import Category
from models.product import Product

def seed():
    session = SessionLocal()

    # --- Проверка, есть ли данные ---
    if session.query(Category).first():
        print("Данные уже существуют. Пропускаем заполнение.")
        session.close()
        return

    # --- Создаем категории ---
    electronics = Category(name="Электроника")
    books = Category(name="Книги")
    clothing = Category(name="Одежда")
    session.add_all([electronics, books, clothing])
    session.commit()

    # --- Создаем товары ---
    products = [
        Product(name="Смартфон", description="Современный смартфон с хорошей камерой", price=299.99, category_id=electronics.id),
        Product(name="Ноутбук", description="Мощный ноутбук для работы и игр", price=899.99, category_id=electronics.id),
        Product(name="Наушники", description="Беспроводные наушники с шумоподавлением", price=129.99, category_id=electronics.id),
        Product(name="Роман", description="Интересный художественный роман", price=19.99, category_id=books.id),
        Product(name="Энциклопедия", description="Полная энциклопедия для детей", price=49.99, category_id=books.id),
        Product(name="Футболка", description="Классическая футболка из хлопка", price=14.99, category_id=clothing.id),
        Product(name="Джинсы", description="Удобные джинсы для повседневной носки", price=39.99, category_id=clothing.id),
    ]

    session.add_all(products)
    session.commit()
    session.close()

    print("Сеанс заполнения базы завершен. Категории и товары созданы!")


if __name__ == "__main__":
    seed()
