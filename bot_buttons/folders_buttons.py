import telebot
import db_kernel.requests as db_requests
from telebot import types

def folders():
    markup = types.InlineKeyboardMarkup(row_width=1) # Зарагестрировать кнопки

    # Получить спиисок папок из базы данныз
    folders = db_requests.select_all_folders()

    # Регистраиция каждой кнопки 
    for folder in folders:
        # Кнопки получают название и id папки как callback функция для дальнейшего прослушивания 
        if folder[3] == 'active':
            back_button = types.InlineKeyboardButton(f'🟢 {folder[2]}', callback_data=f'folder:{folder[1]}') 
        elif folder[3] == 'disable':
            back_button = types.InlineKeyboardButton(f'🔴 {folder[2]}', callback_data=f'folder:{folder[1]}') 
        else:
            back_button = types.InlineKeyboardButton(f'🟡 {folder[2]}', callback_data=f'folder:{folder[1]}') 

        markup.add(back_button) # Добавить кнопку в бота

    return markup

def folder_settings_button(folder):
    markup = types.InlineKeyboardMarkup(row_width=1) # Зарагестрировать кнопки

    # Получить спиисок папок из базы данныз
    folders = db_requests.select_all_folders()

    # Регистраиция каждой кнопки 
    # Кнопка для активации папки
    # Если папка не активна добавить кнопку для его активации
    if folder[3] == 'disable':
        status_button = types.InlineKeyboardButton('🟢 Активировать папку', callback_data=f'folder_status: {folder[1]} active') 
        markup.add(status_button) # Добавить кнопки
    # Если папка не активна добавить кнопку для его деактивации
    else:
        status_button = types.InlineKeyboardButton('🔴 Деактивировать папку', callback_data=f'folder_status: {folder[1]} disable') 
        markup.add(status_button) # Добавить кнопки

    return markup

def folder_activate(folder_id):
    pass
