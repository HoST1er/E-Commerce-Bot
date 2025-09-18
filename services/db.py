from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import Config


# --- Движок SQLAlchemy ---
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False}  # для SQLite
)

# --- Сессии ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Базовый класс моделей ---
Base = declarative_base()

# --- Функция для инициализации таблиц ---
def init_db():
    import models.product
    import models.category
    import models.order
    import models.user
    import models.cart


    Base.metadata.create_all(engine)
    print("База данных и таблицы созданы!")
