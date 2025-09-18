from sqlalchemy import Column, Integer, String, Float, ForeignKey
from services.db import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = {'extend_existing': True}  # ← добавляем сюда


    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)

    def __repr__(self):
        return f"<CartItem(user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"
