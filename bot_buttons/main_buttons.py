import telebot

from telebot import types

def main_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # Зарагестрировать кнопки
    
    statistice = types.KeyboardButton('📊 Статистика') # Кнопка статистики
    channels = types.KeyboardButton('📑 Каналы') # Кнопка каналы
    settings = types.KeyboardButton('⚙️ Настройки') # Кнопка настроект
    
    markup.add(statistice, channels, settings) # добавить кнопки 

    return markup

def settings():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # Зарагестрировать кнопки

    back_button = types.KeyboardButton('⬅️ Назад') # Кнопка назад для настроек
    folders_button = types.KeyboardButton('📂 Папки') # Кнопка показа всех папок
    folders_search_button = types.KeyboardButton('🔍 Поиск Папок') # Кнопка для проверки всех папок
    #channels_button = types.KeyboardButton('📑 Каналы') # Кнопка показа всех каналов

    markup.add(back_button, folders_button, folders_search_button) # Добавить кнопку в бота

    return markup

def statistics():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # Зарагестрировать кнопки

    back_button = types.KeyboardButton('⬅️ Назад') # Кнопка назад для настроек
    signals_button = types.KeyboardButton('📈 Сигналы за сутки') # Кнопка показа всех папок
    channels_button = types.KeyboardButton('📈 Каналы') # Кнопка для проверки всех папок

    markup.add(back_button, signals_button, channels_button) # Добавить кнопку в бота

    return markup