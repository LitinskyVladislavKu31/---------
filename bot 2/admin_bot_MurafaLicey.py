import datetime
import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("6608156741:AAGt8-MxAnGZ8-r2zJkb_rzFd7SPpHx_1bY")

# Змінні для збереження стану перегляду
feedback_offset = 0
feedback_limit = 5
rating_offset = 0
rating_limit = 5

# Команди бота

# Команди старт #
@bot.message_handler(commands=['start'])
def start(message):
    user_first_name = str(message.chat.first_name)
    current_hour = datetime.datetime.now().hour

    if 7 <= current_hour < 12:
        greeting = "Добрий ранок"
    elif 12 <= current_hour < 18:
        greeting = "Добрий день"
    elif 18 <= current_hour <= 23:
        greeting = "Добрий вечір"
    else:
        greeting = "Доброї ночі"

    # Додаємо кнопки у меню
    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(text='📑 Історія відгуків')
    btn1 = types.KeyboardButton(text='📑 Історія оцінок якості роботи ліцею')
    markup1.add(btn)
    markup1.add(btn1)

    bot.send_message(message.from_user.id, f"{greeting}, {user_first_name}", reply_markup=markup1)
    bot.send_message(message.from_user.id,
                     f"*Інструкція*:\n Після старту бота у вас з'явиться меню, "
                     'де вам буде запропонований вибір обрати кнопки "📑 Історія відгуків" та "📑 Історія оцінок якості роботи ліцею". При натисканні на одну з них дотримуйтесь відповідних кроків, що прописані там. \n'
                     'А також нижче ви можете подивитись на список команд, які зараз і користуватись ними.\n'
                     f'*Доступні команди:*\n '
                     '1. /start - запуск боту (старт);\n '
                     '2. /Viewresponse - Передивитись історію відгуків (або проханнь, пропозицій та зауважень);\n '
                     '3. /Viewraiting - Передивитись історію оцінок якості роботи ліцею;',
                     parse_mode='Markdown', reply_markup=markup1)

    bot.send_message(message.from_user.id, "Виберіть відповідний пункт з меню нижче⤵️", reply_markup=markup1)

# Команда Viewresponse #
@bot.message_handler(commands=['Viewresponse'])
def view_response(message):
    global feedback_offset
    feedback_offset = 0  # Скидаємо offset при новому запиті

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_right = types.KeyboardButton(text="➡️")
    btn_left = types.KeyboardButton(text="⬅️")
    btn_cancel = types.KeyboardButton(text='❌ Скасувати')
    markup.add(btn_left, btn_right)
    markup.add(btn_cancel)

    rows = get_feedback(feedback_offset, feedback_limit)
    bot.send_message(message.from_user.id, "Стрілочками ви можете перемикати аби подивитись попередні 5 записів(стрілка вліво) чи наступні(стрілка вправо)", reply_markup=markup)
    bot.send_message(message.from_user.id, "Відгуки:", reply_markup=markup)
    print_feedback(rows, message.chat.id)

    bot.register_next_step_handler(message, handle_feedback_navigation, markup)


def get_feedback(offset, limit):
    connection = sqlite3.connect('MurafaLicey.db')
    cursor = connection.cursor()

    query = "SELECT * FROM Feedback LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))

    rows = cursor.fetchall()

    connection.close()

    return rows


def print_feedback(rows, chat_id):
    for row in rows:
        bot.send_message(chat_id, f"ID: {row[0]}\n Date: {row[1]}\n Прізвище та ім'я: {row[2]}\n Відгук: {row[3]}")


def handle_feedback_navigation(message, markup):
    global feedback_offset

    if message.text == '❌ Скасувати':
        start(message)
        return  
    elif message.text == '➡️':
        feedback_offset += feedback_limit
    elif message.text == '⬅️':
        feedback_offset = max(0, feedback_offset - feedback_limit)

    rows = get_feedback(feedback_offset, feedback_limit)
    bot.send_message(message.from_user.id, "Відгуки:", reply_markup=markup)
    print_feedback(rows, message.chat.id)

    bot.register_next_step_handler(message, handle_feedback_navigation, markup)

# Команда Viewraiting #
@bot.message_handler(commands=['Viewraiting'])
def view_rating(message):
    global rating_offset
    rating_offset = 0  # Скидаємо offset при новому запиті

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_right = types.KeyboardButton(text="➡️")
    btn_left = types.KeyboardButton(text="⬅️")
    btn_cancel = types.KeyboardButton(text='❌ Скасувати')
    markup.add(btn_left, btn_right)
    markup.add(btn_cancel)

    rows = get_rating(rating_offset, rating_limit)
    bot.send_message(message.from_user.id, "Стрілочками ви можете перемикати аби подивитись попередні 5 записів(стрілка вліво) чи наступні(стрілка вправо)", reply_markup=markup)
    bot.send_message(message.from_user.id, "Оцінка якості:", reply_markup=markup)
    print_rating(rows, message.chat.id)

    bot.register_next_step_handler(message, handle_rating_navigation, markup)


def get_rating(offset, limit):
    connection = sqlite3.connect('MurafaLicey.db')
    cursor = connection.cursor()

    query = "SELECT * FROM Raiting LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))

    rows = cursor.fetchall()

    connection.close()

    return rows


def print_rating(rows, chat_id):
    for row in rows:
        bot.send_message(chat_id, f"ID: {row[0]}\n Date: {row[1]}\n Оцінка: {row[2]}\n")


def handle_rating_navigation(message, markup):
    global rating_offset

    if message.text == '❌ Скасувати':
        start(message)
        return  
    elif message.text == '➡️':
        rating_offset += rating_limit
    elif message.text == '⬅️':
        rating_offset = max(0, rating_offset - rating_limit)

    rows = get_rating(rating_offset, rating_limit)
    bot.send_message(message.from_user.id, "Оцінка якості:", reply_markup=markup)
    print_rating(rows, message.chat.id)

    bot.register_next_step_handler(message, handle_rating_navigation, markup)

@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    if message.text == '📑 Історія відгуків':
        view_response(message)
    elif message.text == '📑 Історія оцінок якості роботи ліцею':
        view_rating(message)
    elif message.text == '❌ Скасувати':
        start(message)
    else:
        # Перевірка правильності вводу команди
        allowed_commands = ['/start', '/Viewresponse', '/Viewraiting']

        # Перевіряємо, чи введене повідомлення є командою
        if message.text.startswith('/'):
            # Якщо команда не є в списку дозволених команд
            if message.text not in allowed_commands:
                bot.send_message(message.chat.id, "Неправильна команда. Будь ласка, використовуйте одну з наступних команд: /start, /Viewresponse, /Viewraiting.")
        else:
            bot.send_message(message.chat.id, "Невідома команда. Використовуйте меню для навігації.")

bot.infinity_polling(timeout=20)
