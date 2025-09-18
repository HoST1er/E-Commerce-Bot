from datetime import datetime
from services.db import SessionLocal
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from utils.logger import logger


class OrderService:
    @staticmethod
    def create_order(user_id, cart_items, user_data, total):
        session = SessionLocal()
        try:
            order = Order(
                user_id=user_id,
                status="Новый",
                total=total,
                created_at=datetime.now(),
                name=user_data.get("name"),
                phone=user_data.get("phone"),
                address=user_data.get("address"),
                delivery=user_data.get("delivery")
            )
            session.add(order)
            session.flush()  # получили order.id

            for item in cart_items:
                # Если item уже содержит имя/цену — используем, иначе берём из Product
                product = session.query(Product).filter(Product.id == item.product_id).first()
                price = getattr(item, "price", None) or (product.price if product else 0.0)
                name = getattr(item, "name", None) or (product.name if product else "Неизвестный товар")

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    name=name,
                    price=price,
                    quantity=item.quantity
                )
                session.add(order_item)

            session.commit()

            # Собираем словарь, чтобы не возвращать "отвязанный" ORM-объект
            return {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total": float(order.total) if order.total is not None else 0.0,
                "created_at": order.created_at.isoformat() if hasattr(order.created_at, "isoformat") else str(order.created_at),
                "name": order.name,
                "phone": order.phone,
                "address": order.address,
                "delivery": order.delivery,
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при создании заказа: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def list_all_orders():
        session = SessionLocal()
        try:
            orders = session.query(Order).all()
            for order in orders:
                order.items  # подгружаем items для каждого заказа
            return orders
        finally:
            session.close()

    @staticmethod
    def list_user_orders(user_id):
        """
        Возвращает список заказов пользователя с подробными позициями (items).
        Формат: [{id, status, total, delivery, address, created_at, items: [{product_id,name,price,quantity,subtotal}, ...]}, ...]
        """
        session = SessionLocal()
        try:
            orders = (
                session.query(Order)
                .filter(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .all()
            )

            result = []
            for o in orders:
                # Получаем позиции заказа и соответствующие продукты
                rows = (
                    session.query(OrderItem, Product)
                    .outerjoin(Product, OrderItem.product_id == Product.id)
                    .filter(OrderItem.order_id == o.id)
                    .all()
                )

                items = []
                for order_item, product in rows:
                    price = order_item.price if order_item.price is not None else (product.price if product else 0.0)
                    name = order_item.name if order_item.name else (product.name if product else "Неизвестный товар")
                    qty = order_item.quantity or 0
                    items.append({
                        "product_id": order_item.product_id,
                        "name": name,
                        "price": float(price),
                        "quantity": qty,
                        "subtotal": round(float(price) * qty, 2)
                    })

                result.append({
                    "id": o.id,
                    "status": o.status,
                    "total": float(o.total) if o.total is not None else 0.0,
                    "delivery": o.delivery,
                    "address": o.address,
                    "created_at": o.created_at.isoformat() if hasattr(o.created_at, "isoformat") else str(o.created_at),
                    "items": items
                })

            return result
        except Exception as e:
            logger.error(f"Ошибка при чтении заказов пользователя {user_id}: {e}")
            return []
        finally:
            session.close()

    @staticmethod
    def list_all_orders():
        session = SessionLocal()
        try:
            orders = session.query(Order).all()
            return orders
        finally:
            session.close()

    @staticmethod
    def update_order_status(order_id, status):
        session = SessionLocal()
        try:
            order = session.query(Order).filter_by(id=order_id).first()
            if not order:
                return None
            order.status = status
            session.commit()
            return order
        finally:
            session.close()