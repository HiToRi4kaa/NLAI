import telebot
import os
import hashlib

def calculate_file_hash(file_content):
    """
    Обчислює SHA-256 хеш для вмісту файлу.

    Args:
        file_content (bytes): Вміст файлу у байтах.

    Returns:
        str: SHA-256 хеш у вигляді шістнадцяткового рядка.
    """
    sha256 = hashlib.sha256()
    sha256.update(file_content)
    return sha256.hexdigest()

# Створення об'єкта бота
bot = telebot.TeleBot('8064955635:AAHe78CWompJ-CQxoIOUQ_4OryhjeIkd6vw')

# Глобальна змінна для зберігання даних користувачів
user_data = {}
"""
Глобальна змінна для зберігання даних користувачів.

Ключ - ID чату, значення - словник з даними користувача.
"""

# Глобальна змінна для зберігання хешів файлів
file_hashes = {}
"""
Глобальна змінна для зберігання хешів файлів.

Ключ - хеш файлу, значення - шлях до файлу.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обробляє команду /start.

    Вітає користувача та відображає головне меню з кнопками для вибору модулів.

    Args:
        message (telebot.types.Message): Повідомлення від користувача.
    """
    # Ставимо значення adding_music в False
    if message.chat.id in user_data:
        user_data[message.chat.id]['adding_music'] = False

    # Створення клавіатури з кнопками
    markup = telebot.types.InlineKeyboardMarkup()
    music_button = telebot.types.InlineKeyboardButton("🎵Почати", callback_data='music')
    markup.row(music_button)

    # Відправляємо повідомлення
    bot.send_message(
        message.chat.id,
        "🎵 <b>Привіт!</b> Я — твій музичний бот! 🎶\n\n"
        "Я можу допомогти тобі слухати улюблену музику, створювати плейлисти та насолоджуватися звуком! 🔥\n\n"
        "<i>Давай слухати музику разом!</i> 🎧✨",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'music')
def music_menu(call):
    """
    Обробляє вибір модуля "Музика".

    Видаляє попереднє повідомлення та відображає меню з опціями для музики, плейлистів та інструментів.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    # Ставимо значення adding_music в False
    if call.message.chat.id in user_data:
        user_data[call.message.chat.id]['adding_music'] = False

    # Видаляємо попереднє повідомлення
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    music_button = telebot.types.InlineKeyboardButton("🎶Прослухати музику", callback_data='music_option')
    playlist_button = telebot.types.InlineKeyboardButton("📄Плейлисти", callback_data='playlist')
    tools_button = telebot.types.InlineKeyboardButton("⚙️Інструменти", callback_data='tools')
    add_music_button = telebot.types.InlineKeyboardButton("➕Додати музику", callback_data='add_music')
    markup.row(music_button, playlist_button)
    markup.row(tools_button, add_music_button)

    # Відправляємо повідомлення
    bot.send_message(
        call.message.chat.id,
        "<b>🎵 Опис кнопок:</b> \n\n"
        "<b>🎶Прослухати музику</b> – вибір і відтворення треків.\n\n"
        "<b>📄Плейлисти</b> – перегляд та керування плейлистами.\n\n"
        "<b>⚙️Інструменти</b> – видалення музики чи плейлістів.\n\n"
        "<b>➕Додати музику</b> – завантаження нових треків.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'add_music')
def handle_add_music(call):
    """
    Обробляє натискання кнопки "Додати музику".

    Відправляє користувачу повідомлення з проханням надіслати аудіофайл.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🎵 Надішліть файл з музикою в цей чат, щоб додати його.")
    user_data[call.message.chat.id] = {'adding_music': True}

@bot.message_handler(content_types=['audio'])
def save_music_file(message):
    """
    Обробляє отримання аудіофайлу від користувача.

    Зберігає файл у папку 'downloads', якщо такого файлу ще немає.
    Якщо файл вже існує, відправляє повідомлення та додає кнопку "Вийти".

    Args:
        message (telebot.types.Message): Повідомлення з аудіофайлом.
    """
    user_state = user_data.get(message.chat.id, {})
    if not user_state.get('adding_music', False):
        bot.send_message(message.chat.id, "🎵 Ви не в режимі додавання музики. Натисніть '➕Додати музику' у меню.")
        return

    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Обчислюємо хеш файлу
    file_hash = calculate_file_hash(downloaded_file)

    # Перевіряємо, чи файл вже існує
    if file_hash in file_hashes:
        bot.send_message(message.chat.id, "🎵 Цей файл вже існує у вашій бібліотеці.")
    else:
        file_name = message.audio.file_name or f"{message.audio.file_id}.mp3"
        file_path = os.path.join('downloads', file_name)
        os.makedirs('downloads', exist_ok=True)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        file_hashes[file_hash] = file_path
        bot.send_message(message.chat.id, "🎵 Файл успішно додано до вашої бібліотеки!")

    # Додаємо кнопку "Вийти"
    markup = telebot.types.InlineKeyboardMarkup()
    exit_button = telebot.types.InlineKeyboardButton("🚪Вийти", callback_data='music')
    markup.add(exit_button)

    bot.send_message(message.chat.id, "🎵 Ви можете додати ще один файл або вийти з режиму додавання.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'music_option')
def handle_music_option(call):
    """
    Обробляє вибір модуля "Музыка".

    Запускає меню з кнопками для вибору музичних файлів.

    Args:
        call (telebot.types.CallbackQuery): обєкт з даними про натиснуту кнопку.
    """
    global user_data
    chat_id = call.message.chat.id

    # Перевіряемо наявніть музичних файлів у папці downloads
    music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
    if not music_files:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎵 Файли не знайдені")
        return

    # Зберігаємо дані користувача
    user_data[chat_id] = {'music_files': music_files, 'current_index': 0}
    current_music = music_files[0]

    # Створюємо клавіатуру з кнопками управління
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⬅️Попередня", callback_data='prev_music')
    play_button = telebot.types.InlineKeyboardButton("▶️Прослухати", callback_data='play_music')
    next_button = telebot.types.InlineKeyboardButton("➡️Наступна", callback_data='next_music')
    markup.add(prev_button, play_button, next_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Зараз: {current_music}",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in ['prev_music', 'next_music', 'play_music'])
def handle_music_controls(call):
    """
    Обробляє натискання кнопок управління музикою.

    Відправляє користувачу аудіофайл або змінює індекс для відображення наступного/попереднього треку.

    Args:
        call (telebot.types.CallbackQuery): Обєкт з даними про натиснуту кнопку.
    """
    global user_data
    chat_id = call.message.chat.id

    # Отримуємо дані користувача
    user_data_entry = user_data.get(chat_id, {})
    music_files = user_data_entry.get('music_files', [])
    current_index = user_data_entry.get('current_index', 0)

    if not music_files:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎵 Файли не знайдені.")
        return

    # Обробляємо натискання кнопок
    if call.data == 'prev_music':
        current_index = (current_index - 1) % len(music_files)
    elif call.data == 'next_music':
        current_index = (current_index + 1) % len(music_files)
    elif call.data == 'play_music':
        music_path = os.path.join('downloads', music_files[current_index])
        with open(music_path, 'rb') as music_file:
            bot.answer_callback_query(call.id)
            bot.send_audio(chat_id, music_file)
        return

    # Оновлюємо індекс та назву треку
    user_data[chat_id]['current_index'] = current_index
    current_music = music_files[current_index]

    # Створюємо нові кнопки управління
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⬅️Попередня", callback_data='prev_music')
    play_button = telebot.types.InlineKeyboardButton("▶️Прослухати", callback_data='play_music')
    next_button = telebot.types.InlineKeyboardButton("➡️Наступна", callback_data='next_music')
    markup.add(prev_button, play_button, next_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=f"🎵 Зараз: {current_music}", reply_markup=markup)


@bot.message_handler(commands=['help'])
def send_help(message):
    """
    Обробляє команду /help.

    Відправляє користувачу повідомлення з інформацією про функціонал бота.
    
    Args:
        message (telebot.types.Message): Повідомлення від бота.
    """
    bot.send_message(message.chat.id, message)  # Відправляємо повідомлення з інформацією якою володіє бот


if __name__ == "__main__":
    # Запускаємо бота
    bot.polling()