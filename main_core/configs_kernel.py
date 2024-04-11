import os, shutil, asyncio, json
import db_kernel.requests as db_requests
import main_core.search_chanels as search_chanels
from telethon import TelegramClient

async def move_config(channel_id):
    """
        Перемещение конфигураций в темп
    """
    # Определение путей
    channels_configs_path = os.path.join(os.getcwd(), "channels_configs")
    temp_folder_path = os.path.join(channels_configs_path, "temp")
    target_folder_path = os.path.join(channels_configs_path, f"{channel_id}")
    target_folder_in_temp_path = os.path.join(temp_folder_path, f"{channel_id}")

    # Удаление папки из temp если она там уже существовала
    # Еслиесть папки с конфигами, переместить в темп, если есть такая папки в темп то удалить его перед перемешением
    if os.path.exists(target_folder_path):
        if os.path.exists(target_folder_in_temp_path):
            shutil.rmtree(target_folder_in_temp_path)
        shutil.move(target_folder_path, temp_folder_path)

async def make_configs(channel_id):
    """
        Создать папку с названием id канала
    """
    # Определение пути к папке конфигов
    channels_configs_path = os.path.join(os.getcwd(), "channels_configs")
    # Формируем путь к папе канала
    cat_folder_path = os.path.join(channels_configs_path, f"{channel_id}")
    # Определяем путь к папке канала в temp
    temp_folder_path = os.path.join(channels_configs_path, "temp")
    target_folder_in_temp_path = os.path.join(temp_folder_path, f"{channel_id}")

    """
        Проверяет есть ли такая папка в темп, если есть то перемещает, если нету тосоздаёт новую
    """
    if os.path.exists(target_folder_in_temp_path):
        shutil.move(target_folder_in_temp_path, channels_configs_path)
    else:
        if not os.path.exists(cat_folder_path):
            os.mkdir(cat_folder_path)

            """
                Создать config.sjon файл в созданной папке конфигураций
            """

            # Получить данные о канале
            channel = db_requests.select_channels_by_id(channel_id)
            channel_name = channel[3]

            # Получить данные всех активных каналов
            channel_main_info = await search_chanels.select_channel_info(channel_id)

            # Шаблон файла конфигурации
            config_data ={
                'ID': channel_id,
                'Channel_name': channel_name,
                'Channel_link': channel_main_info['link'],
                'Admin': channel_main_info['channel_admins'],
                'Workspace': 'none',
                'Rate': 50,
                'Confidence_rate': 50,
                'Signal_rate': 50,
                'Leverage': 'none',
                'Margin_type': 'none',
                'Entrance_point': 'none',
                'Take_profit': 'none',
                'Stop_loss': 'none',
            }
            # Переоброзовать словарь в json
            json_config_data = json.dumps(config_data)

            
            cat_folder_path = os.path.join(channels_configs_path, f"{channel_id}")
            # Сохранение JSON-файла в папку конфига канала
            with open(os.path.join(cat_folder_path, "config.json"), "w") as f:
                json.dump(config_data, f, indent=4)

async def configs_check(channels):
    """
        Данный метод проверяет все папки конфигураций, если там есть те которые не подходят ни к одной активированной папке, то перемещает в темп
        При вызове получает список всех активных папок
        Данная функция используется только для постоянно  проверки папок
    """
    # Проверить папки, если есть те которые не подходят ни к одному каналу, то переместить их в temp
    channels_configs_path = os.path.join(os.getcwd(), "channels_configs")
    temp_folder_path = os.path.join(channels_configs_path, "temp")
    # Получение списка всех папок в channels_configs
    channels_configs_paths = os.listdir(channels_configs_path)

    # Проверить есть ли папки конфигураций в активных папках
    for conf_channel in channels_configs_paths:
        if conf_channel == 'temp' or conf_channel == 'config.json': # Если это папка temp или config.json то пропустить его
            continue
        else:
            flag = False
            for channel in channels:
                if conf_channel == str(channel['channel_id']):
                    flag = True
                    break
            if not flag:
                # Если нету совподений, проверить есть ли таккая папка в temp если есть то удалить потом переместить папку в temp в любом случаи
                target_folder_in_temp_path = os.path.join(temp_folder_path, conf_channel)
                if os.path.exists(target_folder_in_temp_path):
                    shutil.rmtree(target_folder_in_temp_path)
                shutil.move(os.path.join(channels_configs_path, conf_channel), temp_folder_path)
