import telethon, asyncio, threading, time
import main_core.search_chanels as search_chanels
import db_kernel.requests as db_requests
import main_core.configs_kernel as configs_kernel
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import InputPeerEmpty

async def folder_checker():
    # Данный метод получает список активных папок, проверяет каналы внутри, новые добавляет, и пермещает в temp папкиконфигурации удалённых
    try:
        # Получить список активных папок и и их каналы
        channels = await search_chanels.search_channels_in_activated_folders()
        # Проверка всех каналов в базе данных, если там есть канал который не подходит ни одной папке то удалить его
        #  и перместить его конфиг папку в temp
        # Получить список каналов из бд
        db_channels = db_requests.select_all_channels()
        # Пройтись по списку каналов из бд
        for db_channel in db_channels:
            # Пройтись по списку каналов из папок
            flag = False
            for channel in channels:
                # Проверить есть ли канал из бд  в активных папках
                if db_channel[2] == channel['channel_id']:
                    flag = True
                    break
            # Если не было найдено совподений, то удалить канал из бд и перместить его папку конфиов в temp
            if not flag:
                response_message = db_requests.delete_channel_by_id(db_channel[2]) # Функция удаления канала
                
                # Вызвать функцию для перемещения папки в темп
                await configs_kernel.move_config(db_channel[2])
        
        # Проверяем есть ли все каналы из активированных папок в базе если нету то добавить
        for channel in channels:
            flag = True
            for db_channel in db_channels:
                if db_channel[2] == channel['channel_id']:
                    flag = False
            if flag:
                adding_message = db_requests.add_channel(channel)
        # Проверить есть ли папки с названиями каналов, если нету то создать, если она была в temp то удалить из него и создать новую
        for channel in channels:
            # Определение путей
            # Вызвать функцию для создания конфигураций
            await configs_kernel.make_configs(channel['channel_id'])
        # Вызов функции для проверка наналичие лишних конфигураций
        await configs_kernel.configs_check(channels)
        print('Папки проверены, программа отключилась от аккаунта.')
        
        time.sleep(58) # Не ставить цифру которая делиться на 5 ато будет конфликт с парсером сигналов
        await folder_checker()
    except:
        print('Конфликт при попытке подключиться - парсинг папок и каналов. (ЕСЛИ ДАННОЕ СООБЩЕНИЕ ПОВТОРЯЕТСЯ ПОСТОЯННО ТО ВЫКЛЮЧИТЬ ПАРСЕР И ПРОВЕРИТЬ ПРОГРАММУ)')
        time.sleep(58)
        await folder_checker()

asyncio.run(folder_checker())