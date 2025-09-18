# services/category_service.py
from services.db import SessionLocal
from models.category import Category

class CategoryService:
    @staticmethod
    def get_all_categories():
        session = SessionLocal()
        try:
            categories = session.query(Category).all()
            return categories
        finally:
            session.close()

    @staticmethod
    def add_category(name):
        session = SessionLocal()
        try:
            category = Category(name=name)
            session.add(category)
            session.commit()
            session.refresh(category)
            return {"id": category.id, "name": category.name}  # возвращаем словарь
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении категории: {e}")
            return None
        finally:
            session.close()
