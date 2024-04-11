import sqlite3

def select_all_signals():
    # Получение списка сигналов в течении 3х дней

    # Подключиться к базе данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    signals_table = f"SELECT * FROM signals ORDER BY id"
    # Сделать запрос
    cursor.execute(signals_table)
    # Передать полученные данные переменному
    signals = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать сигналы из бд
    return signals


def select_all_testing_signals():
    # Получение списока тестовых сигналов в течении 3х дней

    # Подключиться к базе данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    signals_table = f"SELECT * FROM testing_signals ORDER BY id"
    # Сделать запрос
    cursor.execute(signals_table)
    # Передать полученные данные переменному
    signals = cursor.fetchall()
    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать сигналы из бд
    return signals

def add_new_signal(signals):
    # Дабавление новых сигналов в бд

    # Подключиться к бае данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()
    
    for signal in signals:
        try:
            # Комманда SQL запроса
            signals_table = "INSERT INTO signals (channel_id, message_id, channel_name, date, time, coin, trend, tvh, rvh, lvh, targets, stop_less, leverage, margin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (signal['channel_id'], signal['message_id'], signal['channel_name'], signal['date'], signal['time'], signal['coin'], signal['trend'], signal['tvh'], signal['rvh'], str(signal['lvh']), str(signal['targets']), signal['stop_less'], signal['leverage'], signal['margin'])
            # Сделать запрос
            cursor.execute(signals_table, values)
        except:
            # При проблеме во время запроса вернуть ошибку
            return 'Ошибка. Проблема с запросом в базу данных.'
    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return 'True'

def add_new_testing_signal(signals):
    # Дабавление новых сигналов в бд

    # Подключиться к бае данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()
    
    for signal in signals:
        try:
            # Комманда SQL запроса
            signals_table = "INSERT INTO testing_signals (channel_id, message_id, channel_name, date, time, coin, trend, tvh, rvh, lvh, targets, stop_less, leverage, margin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (signal[0]['channel_id'], signal[0]['message_id'], signal[0]['channel_name'], signal[0]['date'], signal[0]['time'], signal[0]['coin'], signal[0]['trend'], signal[0]['tvh'], signal[0]['rvh'], str(signal[0]['lvh']), str(signal[0]['targets']), signal[0]['stop_less'], signal[0]['leverage'], signal[0]['margin'])
            # Сделать запрос
            cursor.execute(signals_table, values)
        except:
            # При проблеме во время запроса вернуть ошибку
            return 'Ошибка. Проблема с запросом в базу данных.'
    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return 'True'

def change_signal(signals):
    # Изменение сигналов в бд

    # Подключиться к бае данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()
    
    for signal in signals:
        try:
            signals_table = "UPDATE signals SET channel_name=?, date=?, time=?, coin=?, trend=?, tvh=?, rvh=?, lvh=?, targets=?, stop_less=?, leverage=?, margin=? WHERE channel_id = ? AND message_id = ?"
            values = (signal['channel_name'], signal['date'], signal['time'], signal['coin'], signal['trend'], signal['tvh'], signal['rvh'], str(signal['lvh']), str(signal['targets']), signal['stop_less'], signal['leverage'], signal['margin'], signal['channel_id'], signal['message_id'])
            cursor.execute(signals_table, values)
        except:
            # При проблеме во время запроса вернуть ошибку
            return 'Ошибка. Проблема с запросом в базу данных.'
    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return 'True'

def change_testing_signal(signals):
    # Изменение сигналов в бд

    # Подключиться к бае данных
    conn = sqlite3.connect('parser.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()
    
    for signal in signals:
        try:
            signals_table = "UPDATE testing_signals SET channel_name=?, date=?, time=?, coin=?, trend=?, tvh=?, rvh=?, lvh=?, targets=?, stop_less=?, leverage=?, margin=? WHERE channel_id = ? AND message_id = ?"
            values = (signal[0]['channel_name'], signal[0]['date'], signal[0]['time'], signal[0]['coin'], signal[0]['trend'], signal[0]['tvh'], signal[0]['rvh'], str(signal[0]['lvh']), str(signal[0]['targets']), signal[0]['stop_less'], signal[0]['leverage'], signal[0]['margin'], signal[0]['channel_id'], signal[0]['message_id'])
            cursor.execute(signals_table, values)
        except:
            # При проблеме во время запроса вернуть ошибку
            return 'Ошибка. Проблема с запросом в базу данных.'
    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return 'True'