import asyncio, json, os, datetime
import db_kernel.statistics_requests as statistics_requests
import db_kernel.requests as db_requests
import main_core.search_chanels as channels_kernel
from datetime import date, timedelta


def last_dwm_statistics():
    """
        Данная функция получает список сигналов за последние сутки, неделю и месяц и возврощает эти данные
    """

    # Составить дату поледнего месяца
    # Получение текущей даты
    today = date.today()

    # Дата 1 день назад
    yesterday = today - timedelta(days=1)
    # Дата неделя назад
    week_ago = today - timedelta(days=7)
    # Дата месяц назад
    month_ago = today - timedelta(days=30)


    # Получаем сигналы за последний месяц
    month_signals = statistics_requests.select_signals_by_date(str(month_ago))


    # Получить все сигналы за последнюю неделю
    week_signals = []
    for signal in month_signals:
        if signal[4] >= str(week_ago):
            week_signals.append(signal)

    # Получить все сигналы за последние сутки
    last_day_signals = []
    for signal in week_signals:
        if signal[4] >= str(yesterday):
            last_day_signals.append(signal)

    # Получить количество сигналов за сутки, неделю и месяц и вернуть их
    return f'<b><u>СИГНАЛЫ:</u></b>\nЗа сутки - {len(last_day_signals)} || За неделю - {len(week_signals)} || За месяц - {len(month_signals)}'

def last_day_coins():
    """
        Данная функция проверяет и выводит все моенты и каналы которые повтоярись
        В самом верху выводит те каналы которые на 100% повторялись
    """
    # Вчеращняя дата
    yesterday = date.today() - timedelta(days=1)
    # Получаем все сигналы за последние сутки
    last_day_signals = statistics_requests.select_signals_by_date(yesterday)
    # Массив для хранения 100% совпадающих сигналов
    full_copy_signals = []
    message_form = '<b><u>ПОДНОБНО О СИГНАЛАХ ЗА СУТКИ:</u></b>\n\n' # Текст для структуры возвращаемого текста
    # Проверить сигналы на 100% совпадений
    for signal in last_day_signals:
        # Массив для хранения копий каналов, в стандарте 3 значения с коином трендом и названием канала
        channels_info = [signal[6], signal[7], signal[3]] 
        for last_signal in last_day_signals:
            if signal[1] != last_signal[1]: # Если сигналы не из одного и того же канала
                all_fields_match = (
                    signal[6] == last_signal[6] and 
                    signal[7] == last_signal[7] and 
                    signal[8] == last_signal[8] and 
                    signal[9] == last_signal[9] and 
                    signal[10] == last_signal[10] and 
                    signal[11] == last_signal[11] and 
                    signal[12] == last_signal[12] and 
                    signal[13] == last_signal[13] and 
                    signal[14] == last_signal[14] 
                )
                if all_fields_match:
                    channels_info.append(last_signal[3])
        # Если в массиве хранения сигналов только 2 данных, то нету 100% совподений, в ином случаи добавить в список
        if len(channels_info) > 3:
            if channels_info not in full_copy_signals:
                full_copy_signals.append(channels_info)

    if len(full_copy_signals) != 0:
        for copy_info in full_copy_signals: 
            message_form_d = f'💯 {copy_info[0]} в {copy_info[1]} - {copy_info[2]}'
            # Цикл в списке названий каналов
            for channel_name in copy_info:
                # Проверяем чтобы не добавить первые 3 значения коин тренд и название первого канала потому что они уже вписаны вручную
                if channel_name != copy_info[0] and channel_name != copy_info[1] and channel_name != copy_info[2]:
                    message_form_d += f' | {channel_name}'
            # Проверяем если нету такой строки
            if message_form != '<b><u>ПОДНОБНО О СИГНАЛАХ ЗА СУТКИ:</u></b>\n\n':
                checker_flag = True
                # Проверяем если в хотя бы одной из строк имеющегося списка есть данный список то не добавлять его (это исправление бага с дубликатами)
                for line in message_form.splitlines():
                    for word in message_form_d:
                        if word in line: checker_flag = True
                        else: 
                            checker_flag = False
                            break
                if not checker_flag:
                    # В конце добавляем перенос строки
                    message_form += f'{message_form_d}\n'
            else:
                # В конце добавляем перенос строки
                message_form += f'{message_form_d}\n'

    # Проверяем какие коины и у каких каналов повторялись
    # Получаем тип всех коинов в тренд
    coins_trend = []
    for signal in last_day_signals:
        # Проверяем добавлены ли уже эти коины в тренде
        unice_signal = True
        for c_t in coins_trend:
            if c_t['coin'] == signal[6] and c_t['trend'] == signal[7]:
                unice_signal = False
                break
        # Если этото коин и тренд не было найдено то добавляем
        if unice_signal:
            coins_trend.append({'coin':signal[6], 'trend':signal[7], 'channels':[]})


    # Проверяем у каких каналов есть больше 1ого совпадения
    channels_list = [] # Массив для хранения каналов
    checked_channels = [] # Массив где добавляются id каналов чтобы быстро проверить, канал уже проверен или нет
    for signal in last_day_signals:
        # Проверяем проверялся ли канал этого сигнала
        if signal[1] in checked_channels: continue # Если да то пропускаем этот сигнал
        else:
            coinst_and_trends = [] # Масси для хранения коинов и трендов
            # Если этот канал ещшё не проверялся то проверяем его сигналы
            for channels_signals in last_day_signals:
                # Проверяем чтобы был именно этот канал
                if signal[1] == channels_signals[1]:
                    # Добавляем коин и тренд этоко канала в массив
                    coinst_and_trends.append([signal[6], signal[7]])
            # Рассфасовывем массив с коинами и трендами, не повторяющиеся удаляем
            removing_indexes = [] # Массив для хранения коинов которые надо удалить
            for coin in coinst_and_trends:
                dublicate_flag = False # Флаг для проверки есть ли такой же
                for c_t in coinst_and_trends:
                    # Проверяем чтобы индекс не совпал, тобишь не проверил самого себя
                    if coinst_and_trends.index(coin) != coinst_and_trends.index(c_t):
                        if coin[0] == c_t[0] and coin[1] == c_t[1]:
                            dublicate_flag = True
                            break
                # Проверяем был ли этот коин единственным, если да то добавляем для удаления
                if not dublicate_flag and coinst_and_trends.index(coin) not in removing_indexes:
                    removing_indexes.append(coinst_and_trends.index(coin))

            # Удаляем лишние коины
            for index in removing_indexes:
                coinst_and_trends.pop(index)
            
            # Добавляем название канала в список коинов
            for coin in coins_trend:
                for singal_coins in coinst_and_trends:
                    # Если нашёлся нужный коин в тренде
                    if coin['coin'] == singal_coins[0] and coin['trend'] == singal_coins[1] and signal[3] not in coins_trend[coins_trend.index(coin)]['channels']:
                        # Добавляем название канала и закрываем 2ой цикл для продолжения проверки каналов
                        coins_trend[coins_trend.index(coin)]['channels'].append(signal[3])
                        break
    
    # Добавляем названия и тренд коинов в сообщение
    for coin in coins_trend:
        if len(coin['channels']) > 0:
            message_form += f"{coin['coin']} в {coin['trend']} - "
            for channel_name in coin['channels']:
                message_form += f'{channel_name} | '
            message_form += '\n'

    return message_form

def last_signal_dates():
    """
        Данная функция проверяет какие каналы сколько дней уже не вносили сигналы
    """
    # Разметка до папки с конфиами
    channels_configs_path = os.path.join(os.getcwd(), "channels_configs")
    # Получить количество дней для проверки
    with open(os.path.join(channels_configs_path, "config.json"), "r") as f:
        keys = json.load(f)
        
    days_for_checking = keys['Statistics_days_for_checking']

    # Получить список последних синалов которые были сделаны раньше чем количество дней указанной в конфигах
    # Дата, учитывая количество дней
    date_from = date.today() - timedelta(days=int(days_for_checking))
    # Время (час) сейчас
    datetime_now = datetime.datetime.now()

    # Получить список сигналов которые были отправлены с указанного дня
    all_signals = statistics_requests.select_signals()
    signals = []
    for signal in all_signals:
        if str(signal[4]) <= str(date_from): signals.append(signal)

    # Получить список с названием канала, сколько дней и часов не было сигналов 
    data = []
    for signal in signals:
        # Проверка есть ли такой сигнал в data
        check_flag = False
        for i in data:
            if signal[1] == i['channel_id']: 
                check_flag = True
                break
        # Если не было найдно этого канала в data, то добавить его
        if not check_flag:
            # Получить время в часах, на сколько был пропуск 
            signal_datatime = datetime.datetime.combine(datetime.date.fromisoformat(str(signal[4])), datetime.time.fromisoformat(str(signal[5])))
            # Раздробить на части даты
            d_now = datetime.datetime.strptime(str(datetime_now), "%Y-%m-%d %H:%M:%S.%f")
            d_signal = datetime.datetime.strptime(str(signal_datatime), "%Y-%m-%d %H:%M:%S")
            # Вычисление разницы в днях
            days_difference = (d_now - d_signal).days
            # Вычисление в часах
            hours_difference = int((d_now - d_signal).seconds / 3600)
            # Получить сколько не было 
            data.append({
                'channel_id': signal[1],
                'channel_name': signal[3],
                'days':days_difference,
                'hours':hours_difference
            })
    # Составляем сообщение которое надо вернуть
    message = '<b><u>ПРОПУСКИ СИГНАЛОВ:</u></b>\n'
    
    for d in data:
        message += f"{d['days']}д {d['hours']}ч - {d['channel_name']}\n"

    return message

def folders_and_channels_statistics():
    """
        Данная функция нполучает все данные про активные папки и выводит их в виде табоицы
        А так же получает общее количество каналов в аккаунте
    """
    # Получение всех активных папок
    folders = db_requests.slect_all_active_folders()
    # Получение всех каналов из активных папок
    channels = db_requests.select_all_channels()
    
    # Получить общее количество каналов в аккаунте
    accaunt_channels_count = len(asyncio.run(channels_kernel.select_all_channels_from_account()))

    # Сообщение которое надо показать
    message = f'Всего папок {len(folders)}, в папках {len(channels)} из {accaunt_channels_count} каналов.\n\n'

    for folder in folders:
        # Расфасовываем каналы по активным не активным и тестовым для каждой папки
        activ_channels = []
        deactiv_channels = []
        testing_channels = []
        for channel in channels:
            if folder[1] == channel[1]:
                if channel[4] == 'active': activ_channels.append(channel)
                elif channel[4] == 'disable': deactiv_channels.append(channel)
                elif channel[4] == 'test': testing_channels.append(channel)
        # После получения количество всех каналов, показываем их
        message += f'{folder[2]}:  🟢  -  {len(activ_channels)}        🔴  -  {len(deactiv_channels)}      🟡  -  {len(testing_channels)}\n'

    
    return message

def long_and_short_for_last_day():
    """
        Данная функция получает количество лонг и шорт сигналов и возвращает сообщение о них
    """
    # Получаем вчерашнюю дату
    yesterday = date.today() - timedelta(days=1)
    # Получаем все сигналы за последние сутки
    last_day_signals = statistics_requests.select_signals_by_date(str(yesterday))

    # Проверяем количество шорт и лонг
    short = 0
    long = 0
    for signal in last_day_signals:
        if signal[7].lower() == 'long': long += 1
        elif signal[7].lower() == 'short': short += 1
    
    # Получить коины и тренд какой и сколько каналов рекомендует
    coins_in_trends = []
    for signal in last_day_signals:
        coins_in_trends_check_flag = True
        index_of_cit = -1
        # Находим уже добавленный коин
        for cit in coins_in_trends:
            if cit['coin'] == signal[6] and cit['trend'] == signal[7]:
                coins_in_trends_check_flag = False
                index_of_cit = coins_in_trends.index(cit)
                break
        # Если такой коин в тренде уже есть то плюсуем канал
        if not coins_in_trends_check_flag:
            # Если id канала уже не был добавлен то добавляем
            if signal[1] not in coins_in_trends[index_of_cit]['channels']:
                coins_in_trends[index_of_cit]['channels'].append(signal[1]) 
        else:
            # Если же коинов не было добавлено но добавляем и создаем пустой массив для каналов
            coins_in_trends.append({
                'coin': signal[6],
                'trend': signal[7],
                'channels':[]
            })
    print(coins_in_trends)
    # Формируем сообщение которое будет показывать какой коин  каком тренде сколько каналов рекомендуют
    cit_message = ''
    for cit in coins_in_trends:
        channels_message_test = ''
        if len(cit['channels']) == 1: channels_message_test = 'канал'
        elif len(cit['channels']) < 5: channels_message_test = 'канала'
        else: channels_message_test = 'каналов'
        cit_message += f"\n{cit['coin']} в {cit['trend']} рекомендуют {len(cit['channels'])} {channels_message_test}"
    
    # Выводим сообщение
    message = f"<b><u>ТРЕНД за сутки:</u></b>  LONG - {long} | SHORT - {short}\n{cit_message}"

    return message