import telebot
from telebot import types

def channels(channels):
    markup = types.InlineKeyboardMarkup(row_width=1) # Зарагестрировать кнопки

    # Регистраиция каждой кнопки 
    for channel in channels:
        # Кнопки получают название и id канала как callback функция для дальнейшего прослушивания 
        channel_button = types.InlineKeyboardButton(f'📂 {channel[3]}', callback_data=f'channel:{channel[2]}') 
        markup.add(channel_button) # Добавить кнопку в бота

    return markup

def channel_setting_buttons(channel_id):
    markup = types.InlineKeyboardMarkup(row_width=3) # Зарагестрировать кнопки

    # Регистраиция каждой кнопки 
    activate = types.InlineKeyboardButton(f'🟢 Активировать', callback_data=f'channel_change_status: {channel_id} active') 
    deactivate = types.InlineKeyboardButton(f'🔴 Деактивировать', callback_data=f'channel_change_status: {channel_id} disable') 
    totest = types.InlineKeyboardButton(f'🟡 Тестировать', callback_data=f'channel_change_status: {channel_id} test') 

    markup.add(activate, deactivate, totest)

    return markup