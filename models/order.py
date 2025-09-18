from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from services.db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    total = Column(Float, nullable=False)  # <-- добавляем сюда
    created_at = Column(DateTime, nullable=False)

    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    delivery = Column(String(20), nullable=False)
    products = relationship("OrderItem", back_populates="order")
