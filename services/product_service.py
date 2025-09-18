from models.product import Product
from models.category import Category
from services.db import SessionLocal

class ProductService:

    @staticmethod
    def update_product(product_id, **kwargs):
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            for key, value in kwargs.items():
                setattr(product, key, value)
            session.commit()
            return product
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении продукта: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def list_products():
        session = SessionLocal()
        products = session.query(Product).all()
        session.close()
        return products

    @staticmethod
    def get_product_by_id(product_id: int):
        session = SessionLocal()
        product = session.query(Product).filter(Product.id == product_id).first()
        session.close()
        return product
    @staticmethod
    def get_all_categories():
        session = SessionLocal()
        categories = session.query(Category).all()
        session.close()
        return categories

    @staticmethod
    def get_category_by_name(name: str):
        session = SessionLocal()
        category = session.query(Category).filter(Category.name == name).first()
        session.close()
        return category

    @staticmethod
    def get_products_by_category(category_id: int):
        session = SessionLocal()
        products = session.query(Product).filter(Product.category_id == category_id).all()
        session.close()
        return products

    @staticmethod
    def get_product(product_id: int):
        session = SessionLocal()
        product = session.query(Product).filter(Product.id == product_id).first()
        session.close()
        return product

    @staticmethod
    def add_product(name, price, description=None, category_id=None):
        session = SessionLocal()
        try:
            product = Product(
                name=name,
                price=price,
                description=description,
                category_id=category_id
            )
            session.add(product)
            session.flush()
            product_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "category_id": product.category_id
            }
            session.commit()
            return product_data
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении продукта: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def update_product(product_id, **kwargs):
        session = SessionLocal()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                return None
            for key, value in kwargs.items():
                setattr(product, key, value)
            session.commit()
            return product
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()