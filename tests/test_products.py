import pytest
from services.db import Base, SessionLocal, engine
from models.product import Product
from models.category import Category
from services.product_service import ProductService


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


# --- Тест добавления продукта ---
def test_add_product(setup_db):
    category = Category(name="Тестовая категория")
    session = SessionLocal()
    session.add(category)
    session.commit()

    product_data = ProductService.add_product(
        name="Тестовый продукт",
        price=100.0,
        description="Описание",
        category_id=category.id
    )

    assert product_data is not None
    assert product_data["name"] == "Тестовый продукт"
    assert product_data["price"] == 100.0
    assert product_data["category_id"] == category.id


# --- Тест получения продукта по id ---
def test_get_product_by_id(setup_db):
    product = ProductService.add_product(name="Продукт 2", price=50)
    prod = ProductService.get_product_by_id(product["id"])
    assert prod is not None
    assert prod.name == "Продукт 2"
    assert prod.price == 50


# --- Тест обновления продукта ---
def test_update_product(setup_db):
    product = ProductService.add_product(name="Продукт 3", price=30)
    updated = ProductService.update_product(product["id"], price=35, name="Обновленный продукт")
    assert updated is not None
    assert updated.price == 35
    assert updated.name == "Обновленный продукт"


# --- Тест получения продуктов по категории ---
def test_get_products_by_category(setup_db):
    category = Category(name="Категория для теста")
    session = SessionLocal()
    session.add(category)
    session.commit()

    ProductService.add_product(name="Продукт A", price=10, category_id=category.id)
    ProductService.add_product(name="Продукт B", price=20, category_id=category.id)

    products = ProductService.get_products_by_category(category.id)
    assert len(products) == 2
    names = [p.name for p in products]
    assert "Продукт A" in names
    assert "Продукт B" in names


# --- Тест получения всех категорий ---
def test_get_all_categories(setup_db):
    Category(name="Категория 1").save = lambda self, session: session.add(self)
    session = SessionLocal()
    cat1 = Category(name="Категория 1")
    cat2 = Category(name="Категория 2")
    session.add_all([cat1, cat2])
    session.commit()
    cats = ProductService.get_all_categories()
    assert len(cats) >= 2
