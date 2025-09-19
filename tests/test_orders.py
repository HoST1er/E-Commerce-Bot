import types
from services.order_service import OrderService


# Фейковый объект "товар в корзине"
class FakeCartItem:
    def __init__(self, product_id, name="Товар", price=100.0, quantity=1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity


def test_create_order():
    cart_items = [FakeCartItem(product_id=1, quantity=2)]
    user_data = {"name": "Иван", "phone": "12345", "address": "Улица 1", "delivery": "Курьер"}
    order = OrderService.create_order(user_id=1, cart_items=cart_items, user_data=user_data, total=200.0)

    assert isinstance(order, dict)
    assert order["user_id"] == 1
    assert order["total"] == 200.0
    assert order["status"] == "Новый"


def test_update_status():
    cart_items = [FakeCartItem(product_id=1, quantity=1)]
    user_data = {"name": "Иван", "phone": "12345", "address": "Улица 1", "delivery": "Курьер"}
    order = OrderService.create_order(user_id=1, cart_items=cart_items, user_data=user_data, total=100.0)

    updated_order = OrderService.update_status(order["id"], "Отправлен")
    assert updated_order.status == "Отправлен"


def test_order_not_found():
    result = OrderService.update_status(99999, "Отменён")
    assert result is None
