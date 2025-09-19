from services.db import SessionLocal
from models.cart import CartItem

class CartService:
    @staticmethod
    def remove_one(user_id: int, product_id: int):
        session = SessionLocal()
        try:
            item = session.query(CartItem).filter(
                CartItem.user_id == user_id, CartItem.product_id == product_id
            ).first()
            if item:
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    session.delete(item)
                session.commit()
        finally:
            session.close()
    @staticmethod
    def get_cart(user_id: int):
        session = SessionLocal()
        try:
            items = session.query(CartItem).filter(CartItem.user_id == user_id).all()
            return items
        finally:
            session.close()

    @staticmethod
    def add_to_cart(user_id: int, product_id: int, name: str, price: float, quantity: int = 1):
        """Добавить товар в корзину или увеличить количество"""
        session = SessionLocal()
        try:
            item = session.query(CartItem).filter(
                CartItem.user_id == user_id, CartItem.product_id == product_id
            ).first()
            if item:
                item.quantity += quantity
                if item.quantity <= 0:  # если стало 0 или меньше — удаляем
                    session.delete(item)
            else:
                if quantity > 0:  # не создаём запись с отрицательным количеством
                    item = CartItem(
                        user_id=user_id,
                        product_id=product_id,
                        name=name,
                        price=price,
                        quantity=quantity
                    )
                    session.add(item)
            session.commit()
        finally:
            session.close()

    @staticmethod
    def clear_cart(user_id: int):
        session = SessionLocal()
        try:
            session.query(CartItem).filter(CartItem.user_id == user_id).delete()
            session.commit()
        finally:
            session.close()

    @staticmethod
    def get_cart_items(user_id: int):
        session = SessionLocal()
        try:
            items = session.query(CartItem).filter(CartItem.user_id == user_id).all()
            return items
        finally:
            session.close()