from sqlalchemy import Column, Integer, String, Float
from services.db import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
