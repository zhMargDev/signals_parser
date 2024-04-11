import api_config, re, requests, ccxt, json, os, asyncio
import telethon.tl.functions as _fn 
import db_kernel.requests as db_requests
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, ChatParticipantAdmin, ChatParticipantCreator

"""
    Данный файл ищет в диалогах новые сигналы
"""

async def parser(client):
    try:
        """
            Данная функция получает и выводит всю информацию об каналах активных папок
        """
        
        # Получить список всех диалогов телеграм канала
        dialogs = await client.get_dialogs()

        # Отфильтровать каналы
        all_channels = []
        for dialog in dialogs:
            if dialog.is_channel:
                all_channels.append(dialog)

        # Получить список каналов из базы данных
        db_channels = db_requests.select_all_channels()

        # Перебор только активных и тестируемых каналов
        active_channels = [db_channel for db_channel in db_channels if db_channel[4] == 'active' or db_channel[4] == 'test']
        
        # Перебор каналов для парсинга
        channels = []
        status_types = []
        for channel in all_channels:
            for a_channel in active_channels:
                if channel.entity.id == a_channel[2]:
                    channels.append(channel)
                    status_types.append(a_channel[4])
        
        # Парсинг сообщения канала
        # Получить последнее сообщение каналов
        datas = []
        for channel in channels:
            channel_message = await client.get_messages(channel, limit=1)
            datas.append({
                'channel_id' : channel.entity.id,
                'channel_name' : channel.name,
                'message_id' : channel.message.id,
                'datetime' : channel.date,
                'message' : channel_message[0].message,
                'channel_status' : status_types[channels.index(channel)], # Индекс статуса равен индексу канала поэтому находим индекс канала и сразу присваиваем,
            })

        # Запрос на список коинов
        exchange = ccxt.binance()
        markets = exchange.load_markets()


        # Разметка до папки с конфиами
        channels_configs_path = os.path.join(os.getcwd(), "channels_configs")
        # Получить список слов ключей
        with open(os.path.join(channels_configs_path, "config.json"), "r") as f:
            key_words = json.load(f)

        signals = []
        for data in datas:

            original_message = str(data['message'])
            message_lowercase = str(data['message']).lower()

            coin = ''
            # Проверка есть ли коин в сообщении
            for market in markets:
                splited_market = market.split('/')[0].lower()
                if splited_market != 'usdt' and splited_market in message_lowercase:
                    coin = market.split('/')[0]
                    break
            
            if coin == '': continue # Если коина не было найдено то пропустить это сообщение
            traid = ''
            # Проверка есть ли ключевые слова long или short в сообщении
            for long in key_words['Traid']['long']:
                if long in message_lowercase: 
                    traid = 'LONG'
                    break
            for short in key_words['Traid']['short']:
                if short in message_lowercase:
                    traid = 'SHORT'
                    break
            if traid == '': continue # Если не было найдено ни того ни другого то пропустить

            tvh_result = await tvh_checker(message_lowercase, key_words)

            if not tvh_result: continue # Если вернуло фалс значит это уже не синал
            else:
                # Если все данные нормальные и это явялется сигналом то ищнм второстепенные данные
                take_profits = await tp_checker(message_lowercase, key_words['Take_profit']) 
                stop_less = await stop_point_checker(message_lowercase, key_words['Stop_loss'])
                leverage = await leverage_checker(message_lowercase, key_words['Leverage'])
                margin = await margin_checker(message_lowercase, key_words['Margin_type'])

                signals.append({
                    'channel_id':data['channel_id'],
                    'message_id':data['message_id'],
                    'datetime':data['datetime'],
                    'channel_name':data['channel_name'],
                    'channel_status':data['channel_status'],
                    'coin':coin,
                    'traid':traid,
                    'tvh':tvh_result['tvh'],
                    'rvh':tvh_result['rvh'],
                    'lvh':tvh_result['lvh'],
                    'targets':take_profits,
                    'stop_less': stop_less,
                    'leverage':leverage,
                    'margin':margin,
                    'original_message':original_message
                })

        return signals
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')


async def tvh_checker(message_lowercase, key_words):
    try:
        tvh = '' # Первая цифра после точки входа
        lvh = [] # После слово лимитный ордер
        rvh = False # по рынку
        """
                Этот мотед проверяет следующие значения
            Если есть вход: цифра то это ТВХ 
            Если есть вход: по рынку и цифра то это тоже ТВХ
            Если где то написано ТВХ и цифра, то это тоже ТВХ
            Если есть Вход по рынку и нету цифры то это РВХ
            Если есть лимит или лвх то это ЛВХ отдельно.
        """
        splited_message = message_lowercase.split()
        tvh_words = key_words['Entrance_point']['tvh']
        rvh_words = key_words['Entrance_point']['rvh']
        lvh_words = key_words['Entrance_point']['lvh']
        index = -1
        tvh_key = ''
        # Перебор ключей твх
        for key in tvh_words:
            # Перебор слов
            for word in splited_message:
                # Проверка совподает ли ключевое слово
                if key in word:
                    # Получить индекс этого слова
                    index = splited_message.index(word)
                    tvh_key = key
                    break
            if tvh_key != '': break

        tvh_index = -1 # Этот параметр нужен для дальнейшей проверки лвх

        # Проверка если совподений не было найдено то это не сигнал и надо его пропустить
        if index == -1:
            # Если не было найдено точки входа то это не сигнал и возврощаем False
            return False
        else:
            # Проверяем если ключь был tvh или твх то значит что там отдельно написано про твх
            # Если есть слово твх значит цифра после него сразу это твх,
            if tvh_key == 'tvh' or tvh_key == 'твх':
                # Перебирать цикл чтобы получить цифру после тввх
                for i in range(index + 1, len(splited_message)):
                    # Проверять если в слове есть цифра то взять эту цифру удаляя все символы кроме точки минуса и /
                    for char in splited_message[i]:
                        if char.isalnum() or char in ["-", ".", ","]: # Перебирать цифры и символы и передать пременной
                            tvh += str(char)

            # Проверка есть ли ключи рвх после входа если не было найдено слово твх со своим значением, потому что если было найдено то пофиг есть ли рынок
            if tvh == '':
                rvh_flag = False
                rvh_index = -1
                for key in rvh_words:
                    # Проверка есть ли этот ключь после индекса входа
                    for i in range(index + 1, len(splited_message)):
                        if key == splited_message[i]:
                            rvh_flag = True
                            rvh_index = i
                            break
                # Если рынок был найден, то проверяем после него идёт цифра или лимит
                if rvh_index != -1:
                    # Флаги для проверки что первее нашлось
                    lvh_check_flag = False # Флаг для лимита 
                    for i in range(rvh_index + 1, len(splited_message)):
                        # Если нашлась цифра то передаём значение TVH и останавливаем весь цикл потому что уже не 
                        number = ""
                        for char in splited_message[i]:
                            if char.isdigit() or char in ["-", ".", ","]:
                                number += char
                        if number:
                            tvh = number
                            tvh_index = i # Передаём индекс найденоой цифры для дальнейшей проверки лвх
                            break
                        else:
                            # Если цифры не было найдено то проверяем является ли элемент одним из ключей ддля лвх
                            for lvh_key in lvh_words:
                                if lvh_key in splited_message[i]:
                                    # Если есть лвх и не нашлась цифра то значит у нас рвх + лвх 
                                    rvh = True
                                    break
                            if rvh: break # Если рвх уже тру то уже останавливаем цикл чтобы за зря не крутилась
                else:
                    # Если не было найдено рынка то ищем цифру 
                    # Если не найдёт цифру до лимита то твх False, его нету
                    lvh_flag = False
                    # Перебирать цикл чтобы получить цифру после тввх
                    for i in range(index + 1, len(splited_message)):
                        if i == len(splited_message): break
                        
                        # Проверять если в слове есть цифра то взять эту цифру удаляя все символы кроме точки минуса и /
                        for char in splited_message[i]:
                            if char.isalnum() or char in ["-", ".", ","]: # Перебирать цифры и символы и передать пременной
                                tvh += str(char)
                                        
                        if tvh != '': break # Оставить цыкл если нашёл цифру для твх, потому что нету смысла искать дальше
                        else:
                            # Если это было слово а не цифра то проверить является ли она лвх ключём
                            for lvh_key in lvh_words:
                                if lvh_key in splited_message[i]:
                                    # Если нашёл то tvh у нас не указан
                                    tvh = False
                            if not tvh:
                                # Если было ключчевое слово лимита и не было цифры для твх, то твх не указан
                                # так что останавливаем цикл чтобы какое то другое значение не получал твх 
                                break
            
            # ВНИМАНИЕ данная проверка  на всякий случай потому что бывают пропуски при изменеии кода, хз почему какой то баг
            # Проверяем если tvh и rvh оба фалс или обоих значеней нету то возвращаем False для пропуска этого сигнала
            if tvh == '' and not rvh or not tvh and not rvh: return False
            else: 
                # Если всё норм то проверяем если в tvh нашёлся текст то тоже пропускаем этот сигнал 
                tvh_chacking_flag = False
                for char in tvh:
                    if not char.isalnum() and char not in ["-", ".", ","]: return False
                
            """
                Ищем лвх ключевое слово, и цифры после него 
                ищем первую цифру, и проверяем после этой цифры идёт другая цифра или слово, 
                если идёт слова то это уже не связано с лимитом.
            """
            # Проверка есть ли ключь для лимитного ордера
            lvh_index = -1
            for word in splited_message:
                for key in lvh_words:
                    if key in word:
                        # Если был найден ключь то останаваливаеме циклы и передаем индекс
                        lvh_index = splited_message.index(word)
                        break
                if lvh_index != -1: break # Если ключевое слово было найдено и получен индекс то останавить цикл

            if lvh_index != -1:
                # Если же ключевое слово было найдено то ищем цифры после него пока не наткнёмся на какое то слово
                lvh_first_nmber_flag = False
                break_flag = False
                for i in range(lvh_index + 1, len(splited_message)):
                    if break_flag: break
                    # Если была найдена первая цифра лвх то проверяем следущее значение это цифра или слово
                    if not lvh_first_nmber_flag:
                        # Ищем цифры в слове если нашлась то передаём эту цифру в лвх
                        number = ''
                        for char in splited_message[i]:
                            if char == 'x' or char == 'х':
                                # Если есть цифра и x то это к примеру x12 или 20x что совсем другое
                                number = '' 
                                break 
                            elif char.isdigit() or char in ["-", ".", ","]:
                                number += char
                        if number != '':
                            lvh.append(number)
                            lvh_first_nmber_flag = True
                            continue
                    else:
                        # Если первая цифра лвх проверяется следущее слово является ли цифрой или ключем лвх
                        key_flag = False
                        for key in lvh_words:
                            if key in splited_message[i]:
                                key_flag = True
                        if not key_flag:
                            # Если следующее слово не было ключём лвх то ищем цифру
                            number = ''
                            for char in splited_message[i]:
                                if char.isdigit() or char in ["-", ".", ","]:
                                    number += char
                            # Если была найдена цифра то добавляем его в масиив лвх
                            if number != '':
                                lvh.append(number)
                            else:
                                # Если слово не было ни цифрой ни ключём то уже останавливаем цикл потому что это слово уже скорее всего не связано с лвх
                                break_flag = True
            else:
                # Если не было найдено ключеово слово для лвх 
                # То проеряем есть ли рвх.
                if not rvh:
                    # Если рвх нету но есть твх (это не проверяем потому что если нету точки входа то эта функция уже останавливается изночально)
                    # То возможно что лвх было написано после твх с помощу - 
                    # поэтому ищем цифру после цифры твх.
                    for i in range(tvh_index + 1, len(splited_message)): # Проводим цикл после значения твх
                        # Проверяем на наличие цифры после занчения твх
                        number = ''
                        for char in splited_message[i]:
                            if char.isdigit() or char in ["-", ".", ","]:
                                number += char
                        if number != '':
                            # Если была найдена цифра то передаём его в массив лвх
                            lvh.append(number)
                        else:
                            # Если цифры не было найдено то это уже слово которое не подходит для лвх, поэтому останваливаем посик
                            break
            # Проверка твх на осечки
            tvh_point_flag = False
            for char in tvh:
                if char.isdigit() or char in ["-", ".", ","]: continue
                else: 
                    tvh_point_flag = True
                    break
            if tvh_point_flag:
                return False
            else:
                return {
                    'tvh':tvh,
                    'rvh':rvh,
                    'lvh':lvh
                    } # Передайм полученные значения
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

async def tp_checker(message_lowercase, tp_words):
    try:
        # Данная функция находит цели и озврощает в виде списка
        splited_message = message_lowercase.split()

        tp_index = -1
        tp = []
        for word in splited_message:
            for key in tp_words:
                # Если есть совподение то добаить индекс и остановить поиск
                if key in word:
                    tp_index = splited_message.index(word)
                    break
            if tp_index != -1: break


        """
            Если был найдено совподение, то ищем все значения и преедаём в массив
            Ищет цифры после ключегого слово, если найдёт цифру то добавит в масиив, если найдёт дургой ключь то пропустит
            а если найдёт слово которого нету в ключах то остановит поиск и передаст значения 
        """
        if tp_index != -1:
            for i in range(tp_index + 1, len(splited_message)): # Цикл начинается со значения индекса + 1 и заканчивается на одну меньше длины сообщения
                # Проверяем является ли этот элемент цифрой, если да то передаём значения в массив
                number = ''
                notOneFlag = False
                for char in splited_message[i]:
                    # Если это цифра с каким то знаком вроде () или x, русская х то пропустить это слово
                    if char in ["x", "х", "(", ")"]:
                        number = ""
                        notOneFlag = True # Этот флаг нужен для того чтобы программа не попыталась найти это значаение в ключевых словах
                        print(notOneFlag)
                        break
                    if char.isdigit() or char in ["-", ".", ","]:
                        number += char
                if number != '':
                    tp.append(number)
                elif number == '' and not notOneFlag: # Если флаг фалс, потому что этот флаг отвечает за находку номерований вроде 1) 2) и тд
                    # Если цифры не было найдено то проверяем является ли слово ключевым
                    key_word_checker = False
                    for key in tp_words:
                        if key in splited_message[i]:
                            key_word_checker = True # Если это слово было ещё одним ключом
                        else:
                            for char in splited_message[i]:
                                if char in ['|', ' | ', '/']:
                                    key_word_checker = True

                    """
                        Если слово под этим индексом не было найдено ни ключа ни цифры обозначающей таргет
                        То программа уже нашла все что нужно было, поэтому останавливаем цикл
                    """
                    if not key_word_checker: break  
            # Проверить tp, если там есть элемент который состоит только из символов то удалить этот элемент
            for el in tp:
                el_checker = False
                for char in el:
                    if char.isdigit() or char in ["-", ".", ","]: 
                        el_checker = True
                        break
                if not el_checker:
                    tp.remove(el)


            # После всех проверок передаём все полученные значения
            return tp         
        else:
            return ['Def']

    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

async def stop_point_checker(message_lowercase, stop_keys):
    try:
        # Эта фукнция находит стоп поинт и возрощает его
        splited_message = message_lowercase.split()
        stop_less_index = -1
        # Проверка есть ти ключевое слово для стопа
        for word in splited_message:
            for key in stop_keys:
                if key in word:
                    stop_less_index = splited_message.index(word)
                    break
        if stop_less_index == -1: return 'Def'
        else:
            # Если был найден стоп лесс то найти его значение
            for i in range(stop_less_index + 1, len(splited_message)):
                number = ''
                for char in splited_message[i]:
                    if char.isdigit() or char in ['.', ',', '-']: number += char
                    else:
                        number = ''
                        break
                if number == '': return 'Def'
                else:
                    # Если цифра была найдена то вернуть эту цифру
                    return number
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

async def leverage_checker(message_lowercase, leverage_keys):
    try:
        # Эта функция проверяет есть ли плечо в сигнале
        splited_message = message_lowercase.splitlines()
        leverage_index = -1
        # Проверить в какой линии находится ключь слово если оно есть
        for line in splited_message:
            for key in leverage_keys:
                if key in line:
                    leverage_index = splited_message.index(line)
                    break
            if leverage_index != -1: break
        
        # Найти значение плеча 
        if leverage_index == -1: return 'Def'
        else:
            # Разбить строку на слова
            message_words = splited_message[leverage_index].split()
            leverage = ''
            for word in message_words:
                leverage_number = ''
                for char in word:
                    if char.isdigit() or char in ['.', ',', '-', 'x', 'х']: leverage_number += char
                    else:
                        leverage_number = ''
                        break
                if leverage_number != '': 
                    leverage = leverage_number

            # Удалить Х перед отправкой
            pattern = r"[{}]".format("".join(['x', 'X', 'х', 'Х']))
            leverage = re.sub(pattern, "", leverage)
            return leverage
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')

async def margin_checker(message_lowercase, margin_keys):
    try:
        # Данная функция находит маржу по ключевым словам и отправляет обратно
        splited_message = message_lowercase.split()

        for word in splited_message:
            for key in margin_keys:
                if key in word:
                    return word

        return 'Def' # Отправит деф только если до этого ничего не нашёл
    except Exception as e:
        print(e)
        print('____________E_R_R_O_R___________')