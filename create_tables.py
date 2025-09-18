from services.db import Base, engine
from models.product import Product
from models.category import Category
from models.order import Order, OrderItem
from models.user import User

Base.metadata.create_all(engine)
print("Таблицы созданы!")