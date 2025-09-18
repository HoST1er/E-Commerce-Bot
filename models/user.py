from sqlalchemy import Column, Integer, String
from services.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
