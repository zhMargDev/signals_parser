from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ! ВАЖНО ЕСЛИ НАДО ДОБАВИТЬ НОВЫЕ ТАБЛИЦЫ ТО СПЕРВА УАЛИТЬ СТАРЫЙ ФАЙЛ БАЗЫ ДАННЫХ !

# Подключение к бд, при отсутсвии файла database.db создаст его с указанным ниже таблицами
DATABASE_URL = "sqlite:///database.db" 

# Находит модели бд и создает их при отсутсвии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Таблица папок
class Folders(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True) # ID для бд, УНИКАЛЬНЫЙ
    folder_id = Column(Integer, unique=True) # ID папки из телеграм, УНИКАЛЬНЫЙ 
    folder_title = Column(String) # Название таблицы
    folder_status = Column(String) # Статус таблицы, включенный или отключенный

# Таблица каналов
class Channels(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True) # ID для бд, УНИКАЛЬНЫЙ
    folder_id = Column(Integer) # ID папки из телеграм
    channel_id = Column(Integer, unique=True) # ID канала
    channel_name = Column(String) # Название канала
    channel_stats = Column(String) # Статус канала, включенный или отключенный
    access_hash = Column(Integer)

Base.metadata.create_all(engine)  # Создать таблицы если их нету

# Запуск файла
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()