import telebot, asyncio, subprocess, api_config # Главная библиотека
import bot_buttons.main_buttons as main_buttons # Файл с кнопками бота
import bot_buttons.folders_buttons as folders_buttons # Файл с кнопками папок
import bot_buttons.channels_buttons as channels_buttons
import main_core.search_folder as search_folders # Файл для проерки папок из телеграм
import main_core.search_chanels as search_chanels # Файл для проерки папок из телеграм
import main_core.statistics_kernel as statistics_kernel
import db_kernel.folders_kernel as folders_kernel # Файл для работы с папками
import db_kernel.requests as db_requests
import db_kernel.channels_kernel as channels_kernel
from bs4 import BeautifulSoup
from telebot import types

async def main():
    bot = telebot.TeleBot(api_config.BOT_TOKEN) # Подключение к ТГ боту через токен

    """
    Данная функцяя выполняется при запуске бота.
    Она выводит текст и добавляет главные кнопки.
    Срабатывает данная функция только при отправке сообщения /start.
    """
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """Обработчик команды /start."""
        # Отправляем приветственное сообщение
        bot.send_message(chat_id=f"{api_config.SIGNALS_CHANNEL}", text=f"test", parse_mode='html')
        bot.send_message(message.chat.id, "Приветствую! \n\nЧем могу помочь,")

        # Отправляем клавиатуру с главными кнопками
        main_markup = main_buttons.main_buttons()
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_markup)


    @bot.message_handler(commands=['help'])
    def help_handler(message):
        """Обработчик команды /help"""
        # Отправляет всю информацию  
        bot.send_message(message.chat.id, message)

    @bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
    def settings_message_handler(message):
        """Обработчик кнопки "Настройки"."""
        # Создаем клавиатуру с настройками
        settings_markup = main_buttons.settings()

        # Отправляем сообщение с выбором настройки
        bot.send_message(message.chat.id, 'Выберите настройку.', parse_mode='html', reply_markup=settings_markup)

        # Обработчик кнопки "Назад"
        @bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
        def back_handler(message):
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            """Обработчик кнопки "Назад"."""
            # Создаем клавиатуру с главными кнопками
            main_markup = main_buttons.main_buttons()

            # Отправляем сообщение о возврате в главное меню
            bot.send_message(message.chat.id, f"Вы вернулись в главное меню.", reply_markup=main_markup)
        
        # Обработчик кнопки "Папки"
        @bot.message_handler(func=lambda message: message.text == '📂 Папки')
        def folders_handler(message):
            """Обработчик кнопки "Папки"."""
            # Создаем клавиатуру с главными кнопками
            folders_markup_btns = folders_buttons.folders()

            # Отправляем сообщение о списке папок и список папок в виде кнопок
            bot.send_message(message.chat.id, f"Вот ваш список доступных папок.", reply_markup=folders_markup_btns)

            # Обработка кнопок папок
            @bot.callback_query_handler(func=lambda call: 'folder:' in call.data)
            def folder_button_handler(call: types.CallbackQuery):
                # Проверяем есть ли название Folder: в coll data
                # Получаем ID папки из call.data
                folder_id = int(call.data.split('folder:')[1])
                # Получаем данные об выбранной папке
                folder = db_requests.select_folder_by_id(folder_id)
                # Создать кнопку для настройки папки,  передаём значение в виде списка с данныеи папки
                markup = folders_buttons.folder_settings_button(folder)
                # Текст который выведет бот
                # Текст зависит от нынешнего статуса папки
                if folder[3] == 'disable':
                    status_text = 'Статус: 🔴 Не активен'
                    about_status = 'Если вы активируете папку, то все каналы которые в нём находятся добавяться в базу данных и будут активны для парсинга.'
                else:
                    status_text = 'Статус: 🟢 Активен'
                    about_status = 'Если вы деактивируете папку, то все каналы которые были в этой папке и были активными, будут деактивированы и удалены из базы данных.'
                bot_message = f'📂 Папка: {folder[2]}\n{status_text}\nЧто вы хотите сделать? Выберите действие.\n{about_status}'
                bot.send_message(call.message.chat.id, bot_message, parse_mode='html', reply_markup=markup)
                
                # Обработка кнопки активации или деактивации
                @bot.callback_query_handler(func=lambda call: 'folder_status' in call.data)
                def change_folder_status(call: types.CallbackQuery):
                    # Нажатие кнопки для активации папки
                    # Проверяется текст в call.data для распознования кнопки активации папки
                    # Получить id папки и статус на который надо поеменять из текста call.data
                    folder_id = int(call.data.split(' ')[1])
                    status = call.data.split(' ')[2]
                    # Вызывать функцию для активации папки
                    if status == 'active':
                        change_status_message = folders_kernel.activate_folder(folder_id)
                    elif status == 'disable':
                        change_status_message = folders_kernel.deactivate_folder(folder_id)

                    bot.send_message(call.message.chat.id, change_status_message, parse_mode='html')

        # Обработчик кнопки "Поиск Папкок"
        @bot.message_handler(func=lambda message: message.text == '🔍 Поиск Папок')
        def folders_search_handler(message):
            # Проверяет все папки, новые добавляет, старые убирает и базы данных и выводит результат в виде сообщения
            # Получает список всех папок
            folders = search_folders.result
            print(folders)
            # Проверка на наличие новых и старых папок, добавляет новые и удаляет старые возврощая массив с добавленными и удаленными
            returned_folders = folders_kernel.check_folders(folders)
            if type(returned_folders) == str:
                # Показать ошибку через сообщение бота, если переменная получила текст вместо массивов
                bot.send_message(message.chat.id, returned_folders, parse_mode='html')
            else:
                # В ином случаи возвращается словарь из 2х перменных, new_folders словарь (ключь - значение), вторая переменная объект, вызывается как обычный словарь, с указанием индекса
                # Количество добавленных папок
                added_folders_count = len(returned_folders['new_folders'])
                # Количество удалённых папок
                deleted_folders_count = len(returned_folders['deleted_folders'])

                messag_about_new_folders = ''
                if added_folders_count != 0:
                    messag_about_new_folders = '❗️ Добавленные папки имею заблокированный статус.\n'
                # Выводим текст и прицепляем кнопки к тексту
                bot.send_message(message.chat.id, f'🟢 Было добавлено {added_folders_count} папок.\n🔴 Было удалено {deleted_folders_count} папок.\n{messag_about_new_folders}\nДля просмотра всех папок, нажмите на кнопку "📂 Папки"', parse_mode='html')
                # При нажатии на название папки тправляется Call data с названием Folder:id_folder
        
    # Обработка кнопки "Каналы"
    @bot.message_handler(func=lambda message: message.text == '📑 Каналы')
    def settings_channels_handlner(message):
        # Получить список всех каналов 
        channels = db_requests.select_all_channels()
        # Создать текстовый форматдля отоброжения всех каналов
        channels_group_message = ''
        # Назначение текста для каждого канала в соответсвтии с статусом и индексом
        for channel in channels:
            if channel[4] == 'active':
                channels_group_message += f'🟢 {channel[0]} - {channel[3]}\n'
            elif channel[4] == 'disable':
                channels_group_message += f'🔴 {channel[0]} - {channel[3]}\n'
            elif channel[4] == 'test':
                channels_group_message += f'🟡 {channel[0]} - {channel[3]} \n'

        bot.send_message(message.chat.id, f'Список каналов:\n\n{channels_group_message}\n\nДля изменения, введите № нужного канала.', parse_mode='html')
            
        # Обработка написанного id
        @bot.message_handler(func=lambda message: message.text.isdigit())
        def channel_id_indentifity_handler(message):
            # Проверка является ли текст id
            id_flag = False

            # Проверка является ли написанный текст значением int
            try:
                int(message.text)
                id_flag = True # Если не является int форматом
            except:
                id_flag = False
            if id_flag:
                # Написанный id равен id поля в таблице
                channel_row_id = int(message.text)
                # Найти канал по написанному id
                channel = db_requests.select_channels_by_row_id(channel_row_id)
                channels_group_message = ''
                if type(channel) is tuple:
                    # Если id был найден
                    if channel[4] == 'active':
                        channels_group_message += f'🟢 ID: {channel[2]} Канал: {channel[3]}\n'
                    elif channel[4] == 'disable':
                        channels_group_message += f'🔴 ID: {channel[2]} Канал: {channel[3]}\n'
                    elif channel[4] == 'test':
                        channels_group_message += f'🟡 ID: {channel[2]} Канал: {channel[3]}\n'
                    
                    channel_markup = channels_buttons.channel_setting_buttons(channel[2])
                    
                    bot.send_message(message.chat.id, f'{channels_group_message}', parse_mode='html', reply_markup=channel_markup)
                else:
                    bot.send_message(message.chat.id, f'❗️Не существует канала с таким ID.\nНапишите Id который указан в списке.', parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'❗️Не существует канала с таким ID.\nНапишите Id который указан в списке.', parse_mode='html')

                
            # Обработка запроса на изменеие статуса канала
            @bot.callback_query_handler(func=lambda call: 'channel_change_status:' in call.data)
            def change_channel_status(call: types.CallbackQuery):
                # Получает из call.data значения id и status
                channel_id = int(call.data.split(' ')[1])
                status = call.data.split(' ')[2]

                # Изменение статуса канала
                returned_message = channels_kernel.change_channel_status(channel_id, status)

                if 'Ошибка' in returned_message: # Если произашла ошибка
                    bot.send_message(message.chat.id, returned_message, parse_mode='html')
                else:    # Если статус успешно был изменён
                    bot.send_message(message.chat.id, f'{returned_message}', parse_mode='html')
    # Обработка кнопки "Статистика"
    @bot.message_handler(func=lambda message: message.text == '📊 Статистика')
    def statistics_button(message):
        # Получить статистику; тренд за сутки (пункт 6), сигналы (1 пункт), пропуски сигналов (3 пункт)
        trends_message = statistics_kernel.long_and_short_for_last_day()
        signals_message = statistics_kernel.last_dwm_statistics()
        last_signals = statistics_kernel.last_signal_dates()
        # Формируем кнопки
        markps = main_buttons.statistics()
        # Отправляем сообщение с кнопками управления статистикой
        bot.send_message(message.chat.id, f'-= Статистика =-\n\n{trends_message}\n\n{signals_message}\n\n{last_signals}', parse_mode='html', reply_markup=markps)

        # Обработчик кнопки "Назад"
        @bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
        def back_handler(message):
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            """Обработчик кнопки "Назад"."""
            # Создаем клавиатуру с главными кнопками
            main_markup = main_buttons.main_buttons()

            # Отправляем сообщение о возврате в главное меню
            bot.send_message(message.chat.id, f"Вы вернулись в главное меню.", reply_markup=main_markup)
        
        # Обработчик кнопки "📈 Сигналы за сутки"
        @bot.message_handler(func=lambda message: message.text == '📈 Сигналы за сутки')
        def signals_for_day(message):
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            """Обработчик кнопки "Сигналы за сутки"."""
            # Получаем статистику об синалах зха последние сутки
            last_day_signals = statistics_kernel.last_day_coins()


            # Отправляем сообщение о статистике за сутки
            bot.send_message(message.chat.id, f"{last_day_signals}", parse_mode='html')

        # Обработчик кнопки "📈 Каналы"
        @bot.message_handler(func=lambda message: message.text == '📈 Каналы')
        def statistics_channels(message):
            """Обрабатывае кнопки каналы в сатистиках"""
            # Получить сообщение про информацию об каналах и папках (пункт 4)
            folders_and_channels_info = statistics_kernel.folders_and_channels_statistics()

            # Вывести информацию об папких и каналах
            bot.send_message(message.chat.id, f"{folders_and_channels_info}", parse_mode='html')


    bot.polling(none_stop=True)

if __name__ == '__main__':
    # Запустить бота
    asyncio.run(main())
    # Запустить функцию ежеминутную проверку папок в фоновом режиме
    subprocess.Popen(["python", "folder_check_delay.py"]) 
    # Запустить функцию постоянной проверки сигналов в фоновом режиме
    subprocess.Popen(["python", "parser_run.py"]) 