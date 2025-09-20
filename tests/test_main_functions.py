import pytest
from services.cart_service import CartService
from services.product_service import ProductService
from services.order_service import OrderService


# --------------------- FIXTURES ---------------------

@pytest.fixture(autouse=True)
def setup_db():
    """Очищает корзину перед и после тестов"""
    CartService.clear_cart(1)
    yield
    CartService.clear_cart(1)


# --------------------- ProductService ---------------------

def test_add_and_get_product():
    product = ProductService.add_product("Ноутбук", 50000.0, "Описание", 1)
    assert product["name"] == "Ноутбук"
    fetched = ProductService.get_product_by_id(product["id"])
    assert fetched.name == "Ноутбук"


def test_update_product():
    product = ProductService.add_product("Телефон", 20000.0, "Описание", 1)
    updated = ProductService.update_product(product["id"], name="Смартфон")
    assert updated.name == "Смартфон"


# --------------------- CartService ---------------------

def test_add_and_remove_from_cart():
    CartService.add_to_cart(1, 1, "Мышка", 1000.0, 2)
    items = CartService.get_cart(1)
    assert len(items) == 1
    assert items[0].quantity == 2

    # уменьшаем количество
    CartService.remove_one(1, 1)
    items = CartService.get_cart(1)
    assert items[0].quantity == 1

    # полностью удаляем
    CartService.remove_one(1, 1)
    items = CartService.get_cart(1)
    assert len(items) == 0


def test_clear_cart():
    CartService.add_to_cart(1, 2, "Клавиатура", 3000.0, 1)
    CartService.clear_cart(1)
    items = CartService.get_cart(1)
    assert len(items) == 0


# --------------------- OrderService ---------------------

def test_create_order_and_update_status():
    # создаём заказ
    user_data = {"name": "Иван", "phone": "123456", "address": "Улица 1", "delivery": "Курьер"}
    order = OrderService.create_order(
        user_id=1,
        cart_items=[],
        user_data=user_data,
        total=5000.0
    )
    assert order["status"] == "Новый"

    # меняем статус
    updated = OrderService.update_status(order["id"], "В обработке")
    assert updated.status == "В обработке"


def test_get_user_orders():
    orders = OrderService.list_user_orders(1)
    assert isinstance(orders, list)
