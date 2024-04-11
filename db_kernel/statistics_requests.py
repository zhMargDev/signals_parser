import psycopg2
import api_config

def connect_to_db():
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=api_config.HOST,
        port=api_config.PORT,
        database="signals_parser",
        user=api_config.DBUSER,
        password=api_config.DBPASS,
    )
    return conn

def select_signals_by_date(date):
    # Данная функция находит все сигналы до назначенной даты

    # Подключиться к бае данных
    conn = connect_to_db()
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    signals_request = f"SELECT * FROM signals WHERE date >= {date}"
    # Сделать запрос
    cursor.execute(signals_request)
    # Получить данные канала
    signals = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return signals

def select_signals():
    # Данная функция находит все сигналы после назначенной даты

    # Подключиться к бае данных
    conn = connect_to_db()
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    signals_request = f"SELECT * FROM signals"
    # Сделать запрос
    cursor.execute(signals_request)
    # Получить данные канала
    signals = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return signals