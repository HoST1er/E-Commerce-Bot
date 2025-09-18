from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from services.db import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")
