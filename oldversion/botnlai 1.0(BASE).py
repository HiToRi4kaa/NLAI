import telebot
import os


# Створення об'єкта бота
bot = telebot.TeleBot('8064955635:AAHe78CWompJ-CQxoIOUQ_4OryhjeIkd6vw')

# Глабальна змінна для зберігання даних користувачів
user_data = {}
'''
Глобальна змінна для зберігання даних користувачів.

Ключ - ID чату, значення - словник з даними користувача.
'''

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обробляє команду /start.

    Вітає користувача та відображає головне меню з кнопками для вибору модулів.
   
    Args:
        message (telebot.types.Message): Повідомлення від бота.
    """
    # Створення клавіатури з кнопками
    markup = telebot.types.InlineKeyboardMarkup()
    music_button = telebot.types.InlineKeyboardButton("🎵Музыка", callback_data='music')
    button1 = telebot.types.InlineKeyboardButton("1", callback_data='1')
    button2 = telebot.types.InlineKeyboardButton("2", callback_data='2')
    button3 = telebot.types.InlineKeyboardButton("3", callback_data='3')
    markup.row(music_button)  # Додаємо кнопку "Музыка" в окремий рядок
    markup.row(button1, button2, button3)  # Додаємо кнопки "1", "2", "3" в один рядок
    bot.send_message(message.chat.id, "Выберите модуль:", reply_markup=markup)  # Відправляємо повідомлення з клавіатурою


@bot.callback_query_handler(func=lambda call: call.data == 'music')
def music_menu(call):
    """
    Обробляє вибір модуля "Музыка".

    Видаляє попереднє повідомлення та відображає меню з опціями для музики, плейлистів та інструментів.
    
    Args:
        call (telebot.types.CallbackQuery): обєкт з даними про натиснуту кнопку.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)  # Видаляємо попереднє повідомлення
    markup = telebot.types.InlineKeyboardMarkup()
    music_button = telebot.types.InlineKeyboardButton("🎶Музыка", callback_data='music_option')
    playlist_button = telebot.types.InlineKeyboardButton("📄Плейлист", callback_data='playlist')
    tools_button = telebot.types.InlineKeyboardButton("⚙️Инструменты", callback_data='tools')
    markup.add(music_button, playlist_button, tools_button)  # Додаємо кнопки до клавіатури
    bot.send_message(call.message.chat.id, "Выберите:", reply_markup=markup)  # Відправляємо нове меню


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    """
    Обробляє аудіофайли, надіслані користувачем.
    
    Завантажує аудіофайл, перевіряє, чи існує він у папці downloads, і зберігає його, якщо це новий файл.
    
    Args:
        message (telebot.types.Message): Повідомлення з аудіофайлом.
    """
    file_info = bot.get_file(message.audio.file_id)  # Отримуємо інформацію про файл
    downloaded_file = bot.download_file(file_info.file_path)  # Завантажуємо файл

    # Перевіряємо, чи існує папка downloads, якщо ні — створюємо її
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    file_path = os.path.join('downloads', message.audio.file_name)  # Формуємо шлях до файлу

    # Перевіряємо, чи файл вже існує
    if os.path.exists(file_path):
        bot.reply_to(message, "⚠️Идентичный аудиофайл уже существует!")  # Відправляємо повідомлення про існування файлу
        return
    else:
        # Зберігаємо файл
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "✅Аудиофайл сохранен!")  # Відправляємо повідомлення про успішне збереження


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
        bot.send_message(chat_id, "🎵 Музыкальные файлы не найдены.")
        return

    # Зберігаємо дані користувача
    user_data[chat_id] = {'music_files': music_files, 'current_index': 0}
    current_music = music_files[0]

    # Створюємо клавіатуру з кнопками управління
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⬅️Предыдущая", callback_data='prev_music')
    play_button = telebot.types.InlineKeyboardButton("▶️Прослушать", callback_data='play_music')
    next_button = telebot.types.InlineKeyboardButton("➡️Следующая", callback_data='next_music')
    markup.add(prev_button, play_button, next_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Выбрать: {current_music}",
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
        bot.send_message(chat_id, "🎵 Музыкальные файлы не найдены.")
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
    prev_button = telebot.types.InlineKeyboardButton("⬅️Предыдущая", callback_data='prev_music')
    play_button = telebot.types.InlineKeyboardButton("▶️Прослушать", callback_data='play_music')
    next_button = telebot.types.InlineKeyboardButton("➡️Следующая", callback_data='next_music')
    markup.add(prev_button, play_button, next_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=f"🎵 Выбрать: {current_music}", reply_markup=markup)


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