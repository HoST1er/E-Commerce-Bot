import pytest
from services.db import Base, SessionLocal, engine
from models.cart import CartItem
from services.cart_service import CartService

# --- Setup: создаём временную БД ---
@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session():
    session = SessionLocal()
    yield session
    session.close()

# --- Тест добавления товара в корзину ---
def test_add_to_cart(setup_db):
    CartService.clear_cart(user_id=1)
    CartService.add_to_cart(user_id=1, product_id=1, name="Продукт 1", price=100.0, quantity=2)

    items = CartService.get_cart(user_id=1)
    assert len(items) == 1
    assert items[0].product_id == 1
    assert items[0].quantity == 2

# --- Тест добавления одного и увеличения количества ---
def test_add_existing_cart_item(setup_db):
    CartService.add_to_cart(user_id=1, product_id=1, name="Продукт 1", price=100.0, quantity=3)
    items = CartService.get_cart(user_id=1)
    assert len(items) == 1
    assert items[0].quantity == 5  # 2 + 3

# --- Тест удаления одного товара ---
def test_remove_one(setup_db):
    CartService.remove_one(user_id=1, product_id=1)
    items = CartService.get_cart(user_id=1)
    assert items[0].quantity == 4

# --- Тест удаления последнего товара (должно удалить запись) ---
def test_remove_last_item(setup_db):
    CartService.remove_one(user_id=1, product_id=1)
    CartService.remove_one(user_id=1, product_id=1)
    CartService.remove_one(user_id=1, product_id=1)
    CartService.remove_one(user_id=1, product_id=1)  # теперь должно быть удалено
    items = CartService.get_cart(user_id=1)
    assert len(items) == 0

# --- Тест очистки корзины ---
def test_clear_cart(setup_db):
    CartService.add_to_cart(user_id=2, product_id=2, name="Продукт 2", price=50.0, quantity=2)
    CartService.clear_cart(user_id=2)
    items = CartService.get_cart(user_id=2)
    assert len(items) == 0
