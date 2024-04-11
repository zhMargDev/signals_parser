import asyncio, api_config, telethon, re
import db_kernel.requests as db_requests
import telethon.tl.functions as _fn 
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, ChatParticipantAdmin, ChatParticipantCreator

async def search_channels_in_activated_folders():
    """
        Данная функция Проверяет все папки, те которе активны, добавляет их каналы в базу если их там нету
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
    # Массив для обоаботки активных папок        
    activated_folders = []
    # Получает данные обо всех папках их базы данных
    folders = db_requests.select_all_folders()

    # Проверяет какие папки активны и добавляет их в макссив для дольнейшей обработки
    for folder in folders:
        if folder[3] == 'active':
            activated_folders.append(folder)

    # Получить список каналов из папко в телеграме, если эти ппапки были активировоны в базе данных
    all_channels = []
    # Массив для хранения id и hash каналов, чтобы потом остартировать
    not_sorted_channels = []
    # Получить все папки с каналами внутри
    dialogs = await client(functions.messages.GetDialogFiltersRequest()) 
    # Пройтись по списку активированных папок
    for folder in activated_folders:    
        # Пройтись по папкам и найти те которые подходят под активированные
        for dialog in dialogs:
            # Проверить тип папок чтобы совпало с DialogFilter
            if isinstance(dialog, telethon.tl.types.DialogFilter) and dialog.title != 'Личные': 
                # Найти активированную папку в диалогах
                if folder[1] == dialog.id:
                    for channel in dialog.include_peers:
                        not_sorted_channels.append({
                            'channel_id':channel.channel_id,
                            'access_hash':channel.access_hash,
                            'folder_id':folder[1]
                        })
                    break
                
    # Получить список всех диалогов телеграм, для дальнейшей сортировки и добавления названия
    all_dialogs = await client.get_dialogs()
    # Пройтись по списку каналов
    for channel in not_sorted_channels:
        # Пройтись по списку диалогов
        for dialog in all_dialogs:
            # Проверить подходит ли диалог к каналу
            if channel['channel_id'] == dialog.entity.id:
                # Если диалог ялвяется каналом из активированных папок
                all_channels.append({
                    'folder_id':channel['folder_id'],
                    'channel_id':channel['channel_id'],
                    'channel_name':dialog.name,
                    'access_hash':channel['access_hash'],
                })

    # Закрыть клиент
    await client.disconnect()
    return all_channels

async def select_channel_info(channel_id):
    """
        Данная функция получает и выводит всю информацию об каналах активных папок
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
    # Массив для обоаботки активных папок        
    activated_folders = []
    # Получает данные обо всех папках их базы данных
    folders = db_requests.select_all_folders()

    # Проверяет какие папки активны и добавляет их в макссив для дольнейшей обработки
    for folder in folders:
        if folder[3] == 'active':
            activated_folders.append(folder)

    # Получить список всех диалогов телеграм, для дальнейшей сортировки и добавления названия
    all_dialogs = await client.get_dialogs()
    # Пройтись по списку каналов
    for dialog in all_dialogs:
        # Проверить подходит ли диалог к каналу
        if channel_id == dialog.entity.id:
            channel_f = dialog

    # Параметры которые надо отправить
    dialogs_main_info = []
    # Получить результат 
    d = channel_f

    # Получить link канала
    channel_link = ''
    try:
        en = d.entity # Информация про канал
        public = hasattr(en, 'username') and en.username # Публичное название
        is_chat = d.is_group and not d.is_channel and not en.deactivated # Проверка является ли диалог часто или группой
        admin = en.creator or (en.admin_rights and en.admin_rights.invite_users) # Получить информацию есть ли админ или нет 
        
        # Получить Лнк чата
        if public: channel_link = f'https://t.me/{en.username}' # 
        elif admin:
            if is_chat: r = await client(_fn.messages.GetFullChatRequest(en.id))
            else: r = await client(_fn.channels.GetFullChannelRequest(en))
            link = r.full_chat.exported_invite
            channel_link = f'{link.link}'
        
        if channel_link == '':
            channel_link = 'NONE'
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

    channel_admins = ''
    try:
        # Отсортировка админов
        # Регулярное выражение для поиска ссылок
        pattern = r"(?:@)([a-zA-Z0-9\_]+)"
        # Поиск ссылок
        admins = re.findall(pattern, str(d))
        # Отсартировка списка в строку
        for admin in admins:
            channel_admins += f'@{admin}, '
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

    if channel_admins == '':
        channel_admins = 'NONE'

    dialogs_main_info = {
        'channel_id':d.entity.id,
        'link':channel_link,
        'channel_admins':channel_admins
    }

    # Закрыть клиент
    await client.disconnect()
    return dialogs_main_info

async def select_all_channels_from_account():
    """Данная функция получает все каналы аккаунта и возвращает их"""

    # Конфигурация
    api_id = api_config.API_ID
    api_hash = api_config.API_HASH
    system_version="4.16.30-vxCUSTOM"
    phone_number = api_config.PARSE_CLIENT

    # Создать экземпляр клиента
    client = TelegramClient('session_name', api_id, api_hash, system_version=system_version)

    # Запусть клиент
    await client.start()

    all_channels = []
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel and dialog.title != 'Личные':
            all_channels.append(dialog)

    # Закрыть клиент
    await client.disconnect()
    return all_channels