from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from services.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    photo = Column(String, nullable=True)       # ссылка на фото
    description = Column(String, nullable=True) # описание товара

    category = relationship("Category", back_populates="products")
