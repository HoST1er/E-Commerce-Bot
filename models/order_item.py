from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from services.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # <<< ВАЖНО!

    name = Column(String(255), nullable=False)   # название товара
    price = Column(Float, nullable=False)        # цена за единицу
    quantity = Column(Integer, nullable=False)   # количество

    # Связь с заказом и продуктом
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")