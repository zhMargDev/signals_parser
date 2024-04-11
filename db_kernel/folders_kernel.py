import asyncio
import db_kernel.requests as db_requests
import db_kernel.channels_kernel as channels_kernel
import bot_buttons.channels_buttons as channels_buttons
import main_core.search_chanels as search_chanels
import main_core.configs_kernel as configs_kernel

def check_folders(folders):
    # Функция проверяет наличие папок в базе данныз, при их отсутствии добавляет названия в отдельную переменную
    # Те которые зарегестрированы в бд но их нету в отправленной форме, добавит в отдельную переменную
    new_folders = [] # Массив для папок которые надо добавить
    folders_for_deleting = [] # Массив для папок которые надо удалить

    # Получить все папки из бд
    db_folders = db_requests.select_all_folders()

    if len(db_folders) == 0:
        # Если таблица папок пустая то вызвать фукнцию для добавления всех папок
        added_folders = db_requests.add_folders(folders)
        if 'Ошибка' not in added_folders:
            # Если ошибки нету в возвращенном тексте то передать данные всех папок массиву
            new_folders = folders

            # Вернуть добавленные папки с пустым массивом для удалённых
            # Возвращаение пропускает остальной код, скорение приложения
            return {'new_folders':new_folders, 'deleted_folders':folders_for_deleting}
        else:
            return 'Ошибка, что то пошло не так, пропобуйте ещё раз.'
    else:
        # Если таблица папок из базы данных не пуста

        # Проверка какие папки не были зарегестррованы
        # Проверка, если ли папка в базе данных
        for folder in folders:
            flag = True # Флаг для проверки, становится False если название папки найдено в базе данных
            for db_folder in db_folders:
                if folder['title'] == db_folder[2]:
                    flag = False
                    break
            if flag:
                new_folders.append(folder)
        
        # Добавить в базу данных новые папки
        added_folders = db_requests.add_folders(new_folders)

        if 'Ошибка' in added_folders:
            # Вернуть текст ошибки, если вышла ошибка
            return 'Ошибка, что то пошло не так, пропобуйте ещё раз.'
        # Проверка на наличие папки для удаления
        for db_folder in db_folders:
            flag = False # Флаг для проверки папки, если она становиться True то папки есть и в тг канале и в бд
            for folder in folders:
                if db_folder[2] == folder['title']:
                    flag = True
                    break
            if flag == False: # Рассортировать папки для удаления, которые не было получено и тг
                folders_for_deleting.append(db_folder)
        # Удалить папки которые не были получены из тг
        delete_folders = db_requests.delete_folders(folders_for_deleting)

        if 'Ошибка' in delete_folders:
            # Вернуть текст ошибки, если вышла ошибка
            return 'Ошибка, что то пошло не так, пропобуйте ещё раз.'
        else:
            # Вернуть добавленные и удалённые папки
            return {'new_folders':new_folders, 'deleted_folders':folders_for_deleting}

def activate_folder(folder_id):
    # Изменить статус папки на активный
    folder_returned_message = db_requests.change_folder_status(folder_id, 'active')
                # Если при попытке изменить данные в таблице появилась ошибка, то показать его пользователю
    returned_message = ''
    if 'Ошибка' in folder_returned_message:
        returned_message = folder_returned_message
        #bot.send_message(call.message.chat.id, folder_returned_message, parse_mode='html')
    else:
        # В ином случаи получить данные об каналах в этой папке, добавить их в базу данных и активировать все
        channels = asyncio.run(search_chanels.search_channels_in_activated_folders())
        channels_message = channels_kernel.add_channels_by_folder_id(folder_id, channels)
        if 'Ошибка' in channels_message:
                        # Если вернулась ошибка при попытке добавить каналы в базу данных то показать эту ошибку
            returned_message = channels_message

            #bot.send_message(call.message.chat.id, channels_message, parse_mode='html')
        else:
                        # channels_message вернуло количество добавленных каналов
                        # Если ошибки не было, то получить список всех каналов папки
            channels_by_folder = db_requests.select_channels_by_folder_id(folder_id)
                        # Получить список кнопок канала
            markup = channels_buttons.channels(channels_by_folder)
                        # Получаем данные об папке
            folder = db_requests.select_folder_by_id(folder_id)
                        # Текст бота для вывода
            returned_message = f'📂 Папка: {folder[2]}\nСтатус: 🟢 Активен\nПапка была успешно активирована.\nТакже были активированы все каналы которы находились в папке.'
    return returned_message

def deactivate_folder(folder_id):
    # Функция декативирует папку и удаляет его каналы из базы данных
    folder_returned_message = db_requests.change_folder_status(folder_id, 'disable')

    # Получение списка каналов для дальнейших действий
    channels = db_requests.select_channels_by_folder_id(folder_id)

    # Удалить все каналы данноой папки
    del_message = db_requests.delete_channels_by_folder(folder_id)

    # Сообщение которое будет возвращаться
    returned_message = ''
    # Вернуть сообщение ошибки
    if 'Ошибка' in del_message:
        returned_message = del_message
    else:
        # Если не было ошибки то перместить конфигурационные папки каналов в temp папку
        for channel in channels:
            # Вызов функции для перемещения конфигурационных файлов
            asyncio.run(configs_kernel.move_config(channel[2]))
            
    # Получаем данные об папке для дальнейшего приминения
    folder = db_requests.select_folder_by_id(folder_id)
    # Сообщение об успешной деактивации папки и его каналов
    returned_message = f'📂 Папка: {folder[2]}\nСтатус: 🔴 Не активен\nПапка была успешно деактивирована.\nВсе каналы которые находились в этой папке успешно были деактивированы.'
    return returned_message