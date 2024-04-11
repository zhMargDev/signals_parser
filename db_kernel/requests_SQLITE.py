import sqlite3

def select_all_folders():
    # Получение всех папок из бд

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    folders_table = "SELECT * FROM folders"
    # Сделать запрос
    cursor.execute(folders_table)
    # Передать полученные данные переменному
    folders = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return folders

def add_folders(folders):
    # Добавить папки в базу данных

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    for folder in folders:
        try:
            # Подготовка SQL запроса
            # Добавить в таблицу folders (названия полей) элементы (не указаны)
            folders_table = "INSERT INTO folders (folder_id, folder_title, folder_status) VALUES (?, ?, ?)"
            # Добавить элементы которые надо добавить
            # ID папки, Название папки, статус не активный
            values = (folder['id'], folder['title'], 'disable')
            # Сделать запрос
            cursor.execute(folders_table, values)
        except:
            # Вернуть текст если вылезла ошибка
            return f'Ошибка, проблема с базой данных. Папка {folder["title"]} Не была добавлена.'
            break

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Вренуть True если все сработало без ошибок, возвращается в виде текста для избежания ошибок с типами
    return 'True'

def delete_folders(folders):
    # Этот метод удаляет папки из базы данных

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    for folder in folders:
        try:
            # Подготовка SQL запроса для удаления
            # ЭфСтрака позволяет добавлять перменные в строку, тут добавлен элемент folder[0] = id
            deleting = f"DELETE FROM folders WHERE id={folder[0]}"  
            # Выполнить запрос на удаление
            cursor.execute(deleting)
        except:
            # Вернуть текст если вылезла ошибка
            return f'Ошибка, проблема с базой данных. Папка {folder["title"]} Не была удалена.'
            break

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Вренуть True если все сработало без ошибок, возвращается в виде текста для избежания ошибок с типами
    return 'True'

def select_folder_by_id(folder_id):
    # Эта функция возвращает данные об папке, находя их по ID папки

    
    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    folders_table = f"SELECT * FROM folders WHERE folder_id={folder_id}"
    # Сделать запрос
    cursor.execute(folders_table)
    # Передать полученные данные переменному
    folder = cursor.fetchone()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return folder

def slect_all_active_folders():
    # Данная функция возвращает список всех активныъ папок

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    folders_table = f"SELECT * FROM folders WHERE folder_status='active'"
    # Сделать запрос
    cursor.execute(folders_table)
    # Передать полученные данные переменному
    folders = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return folders

def change_folder_status(folder_id, status):
    # Этот метод изменяет статус папки, работает и для активации и для деактивации, распознается по полученной переменной status

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    try:
        # Комманда SQL запроса, Изменить статус в таблице где folder_id равен полученному id
        folders_table = f"UPDATE folders SET folder_status = ? WHERE folder_id = ?"
        # назначить элементы вместо вопросов
        values = (status, folder_id)
            # Сделать запрос
        cursor.execute(folders_table, values)
    except:
        # Если появилась ошибка при попытке изменить данные, вернуть Ошибка
        return 'Ошибка. Что то пошло не так.\nНе получилось изменить статус папки.'

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return 'True'

def select_all_channels():
    # Получение всех каналов из бд

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    channels_table = "SELECT * FROM channels"
    # Сделать запрос
    cursor.execute(channels_table)
    # Передать полученные данные переменному
    channels = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return channels

def add_channel(channel):
    # Данная функция получает данные канала и добавляет его в базу данных

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    
    try:
        # Комманда SQL запроса
        channels_table = "INSERT INTO channels (folder_id, channel_id, channel_name, channel_stats, access_hash) VALUES (?, ?, ?, ?, ?)"
        values = (channel['folder_id'], channel['channel_id'], channel['channel_name'], 'active', channel['access_hash'])
            # Сделать запрос
        cursor.execute(channels_table, values)
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

def select_channels_by_folder_id(folder_id):
    # Получение каналов из бд по их id папки

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    channels_table = f"SELECT * FROM channels WHERE folder_id={folder_id}"
    # Сделать запрос
    cursor.execute(channels_table)
    # Передать полученные данные переменному
    channels = cursor.fetchall()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папки из бд
    return channels

def delete_channels_by_folder(folder_id):
    # Удаление каналов по id папки
    
    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    try:
        # Подготовка SQL запроса для удаления
        # ЭфСтрака позволяет добавлять перменные в строку, тут добавлен элемент folder[0] = id
        deleting = f"DELETE FROM channels WHERE folder_id={folder_id}"  
        # Выполнить запрос на удаление
        cursor.execute(deleting)
    except:
        # Вернуть текст если вылезла ошибка
        return f'Ошибка, проблема с базой данных.'

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Вренуть True если все сработало без ошибок, возвращается в виде текста для избежания ошибок с типами
    return 'True'

def delete_channel_by_id(channel_id):
 # Удаление каналов по id канала
    
    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    try:
        # Подготовка SQL запроса для удаления
        # ЭфСтрака позволяет добавлять перменные в строку, тут добавлен элемент folder[0] = id
        deleting = f"DELETE FROM channels WHERE channel_id={channel_id}"  
        # Выполнить запрос на удаление
        cursor.execute(deleting)
    except:
        # Вернуть текст если вылезла ошибка
        return f'Ошибка, проблема с базой данных.'

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Вренуть True если все сработало без ошибок, возвращается в виде текста для избежания ошибок с типами
    return 'True'

def change_channel_status(channel_id, status):
    # Изменить статус канала на отправленный, канал находит по id

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    
    try:
        # Комманда SQL запроса, Изменить статус в таблице где folder_id равен полученному id
        folders_table = f"UPDATE channels SET channel_stats = ? WHERE channel_id = ?"
        # назначить элементы вместо вопросов
        values = (status, channel_id)
            # Сделать запрос
        cursor.execute(folders_table, values)
    except:
        # Если появилась ошибка при попытке изменить данные, вернуть Ошибка
        return 'Ошибка. Что то пошло не так.\nНе получилось изменить статус папки.'

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return 'True'

def select_channels_by_id(channel_id):
    # Получить из бд канал и вернуть его

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    channel_request = f"SELECT * FROM channels WHERE channel_id={channel_id}"
    # Сделать запрос
    cursor.execute(channel_request)
    # Получить данные канала
    channel = cursor.fetchone()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return channel

def select_channels_by_row_id(id):
    # Получить из бд канал и вернуть его

    # Подключиться к бае данных
    conn = sqlite3.connect('database.db')
    # Настроить курсор для работы с таблицами
    cursor = conn.cursor()

    # Комманда SQL запроса
    channel_request = f"SELECT * FROM channels WHERE id={id}"
    # Сделать запрос
    cursor.execute(channel_request)
    # Получить данные канала
    channel = cursor.fetchone()

    # Закоментировать подключение для сохранения изменений
    conn.commit()
    # Закрыть курсор
    cursor.close()
    # Закрыть базу данных
    conn.close()
    #Закрывание нужно для очищения памяти

    # Передать папку из бд
    return channel