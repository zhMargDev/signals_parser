from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ! ВАЖНО ЕСЛИ НАДО ДОБАВИТЬ НОВЫЕ ТАБЛИЦЫ ТО СПЕРВА УАЛИТЬ СТАРЫЙ ФАЙЛ БАЗЫ ДАННЫХ !

# Подключение к бд, при отсутсвии файла database.db создаст его с указанным ниже таблицами
DATABASE_URL = "sqlite:///parser.db" 

# Находит модели бд и создает их при отсутсвии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Таблица сигналов
class Signals(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True) # ID для бд, УНИКАЛЬНЫЙ
    channel_id = Column(Integer) # ID канала
    message_id = Column(Integer) # ID сигнала
    channel_name = Column(String) # Названия канала
    date = Column(String) # Дата добавления сигнала
    time = Column(String) # Время добавления сигнала
    coin = Column(String)
    trend = Column(String)
    tvh = Column(String)
    rvh = Column(String)
    lvh = Column(String) # ЛВХ переобразуется в JSON потом в строку и сохраняется в виде строки потому что спиоск нельзя сохранить как есть
    targets = Column(String) # Таргеты тоже сохраняются в виде строки потому что она тоже может бытьсписком
    stop_less = Column(String)
    leverage = Column(String)
    margin = Column(String)

class TestingSignals(Base):
    __tablename__ = "testing_signals"

    id = Column(Integer, primary_key=True) # ID для бд, УНИКАЛЬНЫЙ
    channel_id = Column(Integer) # ID канала
    message_id = Column(Integer) # ID сигнала
    channel_name = Column(String) # Названия канала
    date = Column(String) # Дата добавления сигнала
    time = Column(String) # Время добавления сигнала
    coin = Column(String)
    trend = Column(String)
    tvh = Column(String)
    rvh = Column(String)
    lvh = Column(String) # ЛВХ переобразуется в JSON потом в строку и сохраняется в виде строки потому что спиоск нельзя сохранить как есть
    targets = Column(String) # Таргеты тоже сохраняются в виде строки потому что она тоже может бытьсписком
    stop_less = Column(String)
    leverage = Column(String)
    margin = Column(String)

Base.metadata.create_all(engine)  # Создать таблицы если их нету

# Запуск файла
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()