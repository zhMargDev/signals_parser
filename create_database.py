import api_config, psycopg2

# Подключение к бд
DATABASE_URL = f"dbname='signals_parser' user='{api_config.DBUSER}' password='{api_config.DBPASS}' host='{api_config.HOST}' port='{api_config.PORT}'"

# Подключение к PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Таблица папок
cur.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER UNIQUE,
    folder_title VARCHAR,
    folder_status VARCHAR
);
""")

# Таблица каналов
cur.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER,
    channel_id INTEGER UNIQUE,
    channel_name VARCHAR,
    channel_stats VARCHAR,
    access_hash INTEGER
);
""")

# Таблица сигналов
cur.execute("""
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER,
    message_id INTEGER,
    channel_name VARCHAR,
    date VARCHAR,
    time VARCHAR,
    coin VARCHAR,
    trend VARCHAR,
    tvh VARCHAR,
    rvh VARCHAR,
    lvh JSONB,
    targets JSONB,
    stop_less VARCHAR,
    leverage VARCHAR,
    margin VARCHAR
);
""")

# Таблица тестовых сигналов
cur.execute("""
CREATE TABLE IF NOT EXISTS testing_signals (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER,
    message_id INTEGER,
    channel_name VARCHAR,
    date VARCHAR,
    time VARCHAR,
    coin VARCHAR,
    trend VARCHAR,
    tvh VARCHAR,
    rvh VARCHAR,
    lvh JSONB,
    targets JSONB,
    stop_less VARCHAR,
    leverage VARCHAR,
    margin VARCHAR
);
""")

print('Database tables is Inserted.')

# Закрытие соединения
conn.commit()
cur.close()
conn.close()

# Функция для работы с бд
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()
