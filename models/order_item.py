from sqlalchemy import Column, Integer, String, Float, ForeignKey
from services.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)

    name = Column(String(255), nullable=False)   # название товара
    price = Column(Float, nullable=False)        # цена за единицу
    quantity = Column(Integer, nullable=False)   # количество
