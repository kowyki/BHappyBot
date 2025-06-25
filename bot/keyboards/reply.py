from telebot import types

def remove_kb():
    return types.ReplyKeyboardRemove(selective=False)
    
def main_kb():
    main_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    main_markup.add('Управление чатами', 'Добавить чат')
    return main_markup

def choose_chat_kb(options: list):
    chats_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    chats_markup.add(*options)
    return chats_markup

def chat_actions_kb():
    chat_actions = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    chat_actions.add('Пользователи', 'Таймер', 'Синхронизация с таблицами', 'Добавить таблицы', 'Назад')
    return chat_actions

def users_actions_kb():
    users_actions = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    users_actions.add('Список', 'Добавить', 'Удалить', 'Очистить', 'Добавить список', 'Назад')
    return users_actions

def timer_actions_kb():
    timer_actions = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    timer_actions.add('Запуск', 'Изменить время', 'Удалить', 'Назад')
    return timer_actions

no_kb = remove_kb()
main_markup = main_kb()
chat_actions_markup = chat_actions_kb()
users_actions_markup = users_actions_kb()
timer_actions_markup = timer_actions_kb()
