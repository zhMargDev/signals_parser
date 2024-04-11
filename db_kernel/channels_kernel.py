import asyncio
import db_kernel.requests as db_requests
import main_core.configs_kernel as confgis_kernel

def add_channels_by_folder_id(folder_id, channels):
    # Данная функция получает все каналы активированных папок
    # Получает все каналы из базы данных
    db_channels = db_requests.select_all_channels()
    # Каналы которые были добавлены
    added_channels = []
    # Находит каналы для активированной папки
    for channel in channels:
        if channel['folder_id'] == folder_id:
            # Проверка есть ли данный канал в базе данных
            flag = True
            if len(db_channels) != 0: # Проверка пустал ли база данных с каналами
                for db_channel in db_channels:
                    if db_channel[2] == channel['channel_id']:
                        flag = False
                        break
            # Если канала не было найдено в базе данных то добавить его туда
            if flag:
                db_result = db_requests.add_channel(channel)
                if 'Ошибка' in db_result:
                    # Если вернулась ошибка вернуть ошибку боту для вывода
                    return db_result
                else:
                    # Если не было ошибки то вызвать функцию для создания конфигурационных файлов 
                    asyncio.run(confgis_kernel.make_configs(channel['channel_id']))
                    
            
    # Вернуть количество добавленных канало в виде сроки
    return str(len(added_channels))

def change_channel_status(channel_id, status):
    # Этот метод активирует канал по его id

    # Вызов метода для изменения данных в бд на активированный
    returned_message = db_requests.change_channel_status(channel_id, status)

    if 'Ошибка' in returned_message:
        return returned_message
    else:
        # Получить данные канала
        channel = db_requests.select_channels_by_id(channel_id)

        if status == 'active':
            status_message = '🟢 Активирован'
        elif status == 'disable':
            status_message = '🔴 Деактивирован'
        else:
            status_message = '🟡 Тест включён.'

        # Сообщение которое надо вернуть
        message = f'Канал {channel[3]} ID: {channel[2]}.\nСтатус успешно изменён.\nСтатус: {status_message}'

        return message