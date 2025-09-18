from models.category import Category
from models.product import Product
from services.db import SessionLocal
from utils.logger import logger


class CatalogService:
    @staticmethod
    def list_categories():
        """Возвращает список всех категорий"""
        session = SessionLocal()
        try:
            categories = session.query(Category).all()
            return categories
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {e}")
            return []
        finally:
            session.close()

    @staticmethod
    def list_products_by_category(category_id: int):
        """Возвращает список товаров в категории"""
        session = SessionLocal()
        try:
            products = session.query(Product).filter(Product.category_id == category_id).all()
            return products
        except Exception as e:
            logger.error(f"Ошибка при получении товаров для категории {category_id}: {e}")
            return []
        finally:
            session.close()

    @staticmethod
    def get_product(product_id: int):
        """Возвращает товар по ID"""
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            return product
        except Exception as e:
            logger.error(f"Ошибка при получении товара {product_id}: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def add_category(name: str):
        """Добавление новой категории"""
        session = SessionLocal()
        try:
            category = Category(name=name)
            session.add(category)
            session.commit()
            logger.info(f"Добавлена категория: {name}")
            return category
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при добавлении категории {name}: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def add_product(name: str, description: str, price: float, category_id: int = None, photo: str = None):
        """Добавление нового товара"""
        session = SessionLocal()
        try:
            product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                photo=photo
            )
            session.add(product)
            session.commit()
            logger.info(f"Добавлен товар: {name} (Категория {category_id})")
            return product
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при добавлении товара {name}: {e}")
            return None
        finally:
            session.close()
