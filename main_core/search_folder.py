import asyncio
import api_config
import telethon
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import InputPeerEmpty

async def search_folders():
    """
        Данная функция Проверяет все папки, новые добавляет, старые убирает и базы данных
        Возвращает результат в виде списка
    """
    # Конфигурация
    api_id = api_config.API_ID
    api_hash = api_config.API_HASH
    system_version="4.16.30-vxCUSTOM"
    phone_number = api_config.PARSE_CLIENT

    # Создать экземпляр клиента
    client = TelegramClient('session_name', api_id, api_hash, system_version=system_version)


    # Запусть клиент
    await client.start()
    # Возвращает список с атрибутами папок
    folders = await client(functions.messages.GetDialogFiltersRequest()) 

    folders_list = []

    for folder in folders:
        """
            Проверяем если параметр DialogFilter тип которого указан в telethon
            То выводим результат, делается потому что в списке есть несколько иных типов которые не нужны и вызывают ошибку
            Так же не добавляет папку личные
        """
        if isinstance(folder, telethon.tl.types.DialogFilter) and folder.title != 'Личные': 
            # Добавляем Id и  название папок в folders_list для вывода
            folders_list.append({'id':folder.id, 'title':folder.title})
        
    # Закрыть клиент
    await client.disconnect()
    return folders_list

# Результат, вызывается эта переменная
result = asyncio.run(search_folders())