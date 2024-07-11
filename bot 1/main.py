from flask import Flask, request
import telebot
import os
import sqlite3
import datetime
import time

bot = telebot.TeleBot("7334943468:AAFm3N30GuknTexTwmVAWQcBfZSW-gHiExc")
app = Flask(__name__)

INTERVAL = 600
user_last_feedback_time = {}
user_last_rating_time = {}

def can_send_message(chat_id, message_type):
    current_time = time.time()
    if message_type == 'feedback':
        if chat_id in user_last_feedback_time:
            last_message_time = user_last_feedback_time[chat_id]
            if current_time - last_message_time < INTERVAL:
                return False, time.strftime('%H:%M:%S', time.localtime(last_message_time + INTERVAL))
        user_last_feedback_time[chat_id] = current_time
    elif message_type == 'rating':
        if chat_id in user_last_rating_time:
            last_message_time = user_last_rating_time[chat_id]
            if current_time - last_message_time < INTERVAL:
                return False, time.strftime('%H:%M:%S', time.localtime(last_message_time + INTERVAL))
        user_last_rating_time[chat_id] = current_time
    return True, None

@app.route('/' + bot.token, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def index():
    return 'Hello, this is the bot server!', 200

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

    markup1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = telebot.types.KeyboardButton(text=' 📝 Залишити відгук')
    btn1 = telebot.types.KeyboardButton(text='⭐ Оцінити якість роботи ліцею')
    markup1.add(btn)
    markup1.add(btn1)

    bot.send_message(message.from_user.id, f"{greeting}, {user_first_name}. Вас вітає Мурафський ліцей Мурафської сільської ради", reply_markup=markup1)
    bot.send_message(message.from_user.id,
                     f"*Інструкція*:\n Після старту бота у вас з'явиться меню, "
                     'де вам буде запропонований вибір обрати кнопки "📝 Залишити відгук" та  "⭐ Оцінити якість роботи ліцею". '
                     'При натисканні на одну з них дотримуйтесь відповідних кроків, що прописані там. \n'
                     'А також нижче ви можете подивитись на список команд, які зараз і користуватись ними.\n'
                     f'*Доступні команди:*\n '
                     '1. /start - запуск боту (старт);\n '
                     '2. /response - Залишити відгук (або прохання, пропозиції та зауваження);\n '
                     '3. /raiting - Оцінити якість роботи ліцею;',
                     reply_markup=markup1)

    bot.send_message(message.from_user.id, "Виберіть відповідний пункт з меню нижче ⤵️", reply_markup=markup1)

@bot.message_handler(commands=['response'])
def response_command(message):
    can_send, available_at = can_send_message(message.chat.id, 'feedback')
    if not can_send:
        bot.reply_to(message, f"Будь ласка, зачекайте ⏲️ {INTERVAL / 60} хвилин перед відправкою наступного повідомлення. Ви зможете відправити повідомлення о {available_at}.")
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cancel = telebot.types.KeyboardButton(text='❌ Скасувати')
    markup.add(btn_cancel)
    bot.send_message(message.chat.id, "Введіть прізвище та ім'я:", reply_markup=markup)
    bot.register_next_step_handler(message, process_name_step, markup)

def process_name_step(message, markup):
    if message.text == '❌ Скасувати':
        start(message)
        return
    user_data = {'name': message.text}
    bot.send_message(message.chat.id, "Напишіть відгук (прохання або пропозицію):", reply_markup=markup)
    bot.register_next_step_handler(message, print_feedback, user_data, markup)

def print_feedback(message, user_data, markup):
    if message.text == '❌ Скасувати':
        start(message)
        return
    user_data['feedback'] = message.text
    response = (f"*Дата:* {datetime.date.today()}\n"
                f"*Прізвище та ім'я:* {user_data['name']}\n"
                f"*Відгук:* {user_data['feedback']}")

    connection = sqlite3.connect('MurafaLicey.db')
    cursor = connection.cursor()
    query = "INSERT INTO Feedback (Date, Fio, Feedback) VALUES (?, ?, ?)"
    cursor.execute(query, (datetime.date.today(), user_data['name'], user_data['feedback']))
    connection.commit()
    connection.close()

    bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['raiting'])
def raiting_quality(message):
    can_send, available_at = can_send_message(message.chat.id, 'rating')
    if not can_send:
        bot.reply_to(message, f"Будь ласка, зачекайте ⏲️ {INTERVAL / 60} хвилин перед відправкою наступного повідомлення. Ви зможете відправити повідомлення о {available_at}.")
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text='⭐ - Погано')
    btn2 = telebot.types.KeyboardButton(text='⭐⭐ - Задовільно')
    btn3 = telebot.types.KeyboardButton(text='⭐⭐⭐ - Нормально')
    btn4 = telebot.types.KeyboardButton(text='⭐⭐⭐⭐ - Добре')
    btn5 = telebot.types.KeyboardButton(text='⭐⭐⭐⭐⭐ - Супер')
    btn_cancel = telebot.types.KeyboardButton(text='❌ Скасувати')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    markup.add(btn_cancel)
    bot.send_message(message.chat.id, "Оцініть якість роботи в ліцеї обравши нижче від 1 до 5 зірок", reply_markup=markup)
    bot.register_next_step_handler(message, handle_rating, markup)

def handle_rating(message, markup):
    if message.text == '❌ Скасувати':
        start(message)
        return
    bot.send_message(message.chat.id, f"Дата: {datetime.date.today()} \nВаша оцінка: {message.text}", reply_markup=markup)
    connection = sqlite3.connect('MurafaLicey.db')
    cursor = connection.cursor()
    query = "INSERT INTO Raiting (Date, Raiting) VALUES (?, ?)"
    cursor.execute(query, (datetime.date.today(), message.text))
    connection.commit()
    connection.close()

@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    known_commands = ['📝 Залишити відгук', '⭐ Оцінити якість роботи ліцею', '❌ Скасувати']
    if message.text in known_commands:
        if message.text == '📝 Залишити відгук':
            response_command(message)
        elif message.text == '⭐ Оцінити якість роботи ліцею':
            raiting_quality(message)
        elif message.text == '❌ Скасувати':
            start(message)
    else:
        allowed_commands = ['/start', '/response', '/raiting']
        if message.text.startswith('/'):
            if message.text not in allowed_commands:
                bot.send_message(message.chat.id, "Неправильна команда. Будь ласка, використовуйте одну з наступних команд: /start, /response, /raiting.")
        else:
            bot.send_message(message.chat.id, "Невідома команда. Використовуйте меню для навігації.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://client-bot-three.vercel.app/' + bot.token)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
