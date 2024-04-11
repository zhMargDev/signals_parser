import asyncio, telebot, api_config
import time as timeer_delay
import db_kernel.parser_requests as parser_requests
import parser.parser_core as parser_core
import parser.parser_template_maker as parser_template
import telethon.tl.functions as _fn 
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, ChatParticipantAdmin, ChatParticipantCreator
from datetime import datetime, timedelta
from telebot import types

"""
    Это главный файл парсер, который запускается постоянно
    Данный файл получает список последних сигналов
    Проверяет сигналы полученные из файла parser_core с базой данных
    Новые сигналы формирует в макет с помощу файла parser_template_maker
    И отправляет с помощу файла parser_bot
"""

async def parser():
    try:
        # Конфигурация
        api_id = api_config.API_ID
        api_hash = api_config.API_HASH
        system_version="4.16.30-vxCUSTOM"
        phone_number = api_config.PARSE_CLIENT
        # Создать экземпляр клиента
        client = TelegramClient('session_name', api_id, api_hash, system_version=system_version)
        # Запусть клиент
        await client.start()
        # Получаем список последних сигналлов
        signals = await parser_core.parser(client)
        
        # Получаем сигналы из базы данных, которые были отправлены
        db_signals = parser_requests.select_all_signals()
        db_testing_signals = parser_requests.select_all_testing_signals()
        # Массивы для определения новых сигналов
        new_signals = []
        new_testing_signals = []
        for signal in signals:
            # Проверяем был ли такой сигнал уже, учитывая статус канала
            if signal['channel_status'] == 'test': # Статус который в тесте
                signals_list = db_testing_signals
            else:
                signals_list = db_signals # Список сигналов из бд (по  умолчаню обычные сигналы)
            # Переобразовать datetime в отдельные date и time
            date_time_obj = datetime.strptime(str(signal['datetime']), "%Y-%m-%d %H:%M:%S%z")
            date = str(date_time_obj.date())
            time = str(date_time_obj.time())
            new_signal_flag = True # Флаг для проверки сигнала на новый
            changed_signal = False # Это фалн для проверки, если сигнал уже был но изменился то добавть этот флаг чтобы отправить данные об изменении
            for db_signal in signals_list:
                if db_signal[1] == signal['channel_id'] and db_signal[2] == signal['message_id']:
                    """
                    Проверяем, если есть сигнал с таким же id канала и id сообщения, то это не новый сигнал
                    Id сообщений в чатах не повторяется
                    Если нашёлся такой сигнал то останавливаем проверку и пропускаем этот сигнал
                    """
                    
                    # Если такой сигнал нашёлся в базе то проверяем все ли данные подходят, если нет то этот сигнал тоже отправлять    
                    all_fields_match = (
                        db_signal[3] != str(signal['channel_name']) or
                        db_signal[4] != str(date) or
                        db_signal[5] != str(time) or
                        db_signal[6] != str(signal['coin']) or
                        db_signal[7] != str(signal['traid']) or
                        db_signal[8] != str(signal['tvh']) or
                        db_signal[9] != str(signal['rvh']) or
                        db_signal[10] != str(signal['lvh']) or
                        db_signal[11] != str(signal['targets']) or
                        db_signal[12] != str(signal['stop_less']) or
                        db_signal[13] != str(signal['leverage']) or
                        db_signal[14] != str(signal['margin'])
                    )
                    if all_fields_match:
                        changed_signal = True
                        break
                    else:
                        new_signal_flag = False
                        break
                    
            new_signal_frame = {
                    'channel_id':signal['channel_id'],
                    'message_id':signal['message_id'],
                    'date':str(date),
                    'time':str(time),
                    'channel_name':str(signal['channel_name']),
                    'channel_status':str(signal['channel_status']),
                    'coin':str(signal['coin']),
                    'trend':str(signal['traid']),
                    'tvh':str(signal['tvh']),
                    'rvh':str(signal['rvh']),
                    'lvh':signal['lvh'],
                    'targets':signal['targets'],
                    'stop_less': str(signal['stop_less']),
                    'leverage':str(signal['leverage']),
                    'margin':str(signal['margin'])
            }
            if signal['channel_status'] == 'test':
                if new_signal_flag or changed_signal:
                    # Если такой тестовый сигнал не был найден в базе данных или был изменён, то добавляем в список новых сигналов
                    new_testing_signals.append([new_signal_frame, signal['original_message']])
            elif signal['channel_status'] == 'active':
                if new_signal_flag or changed_signal:
                    # Если такой тестовый сигнал не был найден в базе данных или был изменён, то добавляем в список новых сигналов
                    new_signals.append(new_signal_frame)
        # Добавляем новые сигналы в базу данных
        returned_message = returned_message_test = ''
        # Добавляем новы обычные сигналы если список не пуст (в ином случая потратиться ресуры на подключение к базе данных)
        if len(new_signals) != 0 and not changed_signal: returned_message = parser_requests.add_new_signal(new_signals)
        # Если сигнал был изенён то изменяем его в бд
        elif len(new_signals) != 0 and changed_signal: returned_message = parser_requests.change_signal(new_signals)
        if 'Ошибка' in returned_message:
            print(f'___ERROR___')
            print(returned_message)
        # Добавляем новые тестовые сигналы если список не пуст (в ином случая потратиться ресуры на подключение к базе данных)
        if len(new_testing_signals) != 0 and not changed_signal: returned_message_test = parser_requests.add_new_testing_signal(new_testing_signals)
        elif len(new_testing_signals) != 0 and changed_signal: returned_message_test = parser_requests.change_testing_signal(new_testing_signals)
        if 'Ошибка' in returned_message_test:
            print(f'___ERROR___')
            print(returned_message)
        bot = telebot.TeleBot(api_config.BOT_TOKEN) # Подключение к ТГ боту через токен
        # Форматировать макет и отправляем в чат в зависимости от сигнала
        for signal in new_signals:  
            # Форматируем макет и получаем отформотированный html макет
            signal_html_template = await parser_template.signal_template_format(signal, changed_signal)
            bot.send_message(chat_id=f"{api_config.SIGNALS_CHANNEL}", text=f"{signal_html_template}", parse_mode='html')
        
        for signal in new_testing_signals:
            # Форматируем макет тестого сигнала и отправляем в чат тестировки
            testing_signal_html_template = await parser_template.testing_signal_template_format(signal[0], changed_signal)
            bot.send_message(chat_id=f"{api_config.TESTING_SIGNALS_CHANNEL}", text=f"{signal[1]}\n{testing_signal_html_template}", parse_mode='html')
        await client.disconnect()
        print('Сигналы проверены, программа отключилась от аккаунта.')
        timeer_delay.sleep(5)
        await parser()
    except:
        timeer_delay.sleep(5)
        print('Конфликт при попытке подключиться - парсинг сигналов. (ЕСЛИ ДАННОЕ СООБЩЕНИЕ ПОВТОРЯЕТСЯ ПОСТОЯННО ТО ВЫКЛЮЧИТЬ ПАРСЕР И ПРОВЕРИТЬ ПРОГРАММУ)')
        await parser()

if __name__ == '__main__':
    # Запуск функции парсинга
    asyncio.run(parser())