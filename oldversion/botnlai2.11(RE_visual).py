import telebot
import os
import hashlib
import json
import logging

# Налаштовуємо логування
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Глобальна змінна для зберігання хешів файлів
file_hashes = {}

# Глобальна змінна для зберігання плейлистів
playlists = []

# Файл для зберігання плейлистів
PLAYLISTS_FILE = 'playlists.json'

# Файл для зберігання музики
MUSIC_FILE = 'music.json'

# Завантаження музики з файлу
def load_music():
    try:
        with open(MUSIC_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.warning("Файл music.json не знайдено. Створено порожню структуру музики.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Помилка декодування JSON: {e}. Створено порожню структуру музики.")
        return {}

# Збереження музики у файл
def save_music(music_data):
    try:
        with open(MUSIC_FILE, 'w', encoding='utf-8') as file:
            json.dump(music_data, file, ensure_ascii=False, indent=4)
        logging.debug("Музика успішно збережена у файл.")
    except Exception as e:
        logging.error(f"Помилка при збереженні музики: {e}")

# Глобальна змінна для зберігання музики
music_data = load_music()

# Функція для завантаження плейлистів з файлу
def load_playlists():
    global playlists
    try:
        with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as file:
            playlists = json.load(file)
            logging.debug("Плейлисти успішно завантажені з файлу.")
    except FileNotFoundError:
        playlists = []
        logging.warning("Файл playlists.json не знайдено. Створено порожню структуру плейлистів.")
    except json.JSONDecodeError as e:
        playlists = []
        logging.error(f"Помилка декодування JSON: {e}. Створено порожню структуру плейлистів.")

# Функція для збереження плейлистів у файл
def save_playlists():
    """
    Зберігає плейлисти у файл.
    """
    try:
        with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(playlists, file, ensure_ascii=False, indent=4)
        logging.debug("Плейлисти успішно збережені у файл.")
    except Exception as e:
        logging.error(f"Помилка при збереженні плейлистів: {e}")

# Функція для отримання плейлистів користувача
def get_user_playlists(user_id):
    for user_data in playlists:
        if user_data["user_id"] == user_id:
            return user_data["playlists"]
    return {}

# Функція для оновлення плейлистів користувача
def update_user_playlists(user_id, updated_playlists):
    for user_data in playlists:
        if user_data["user_id"] == user_id:
            user_data["playlists"] = updated_playlists
            save_playlists()
            return
    # Якщо користувача не знайдено, додаємо нового
    playlists.append({"user_id": user_id, "playlists": updated_playlists})
    save_playlists()

# Завантажуємо плейлисти при запуску
load_playlists()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обробляє команду /start.

    Вітає користувача та відображає головне меню з кнопками для вибору модулів.

    Args:
        message (telebot.types.Message): Повідомлення від користувача.
    """
    # Встановлюємо значення adding_music у False
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
    # Встановлюємо значення adding_music у False
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
        "<b>⚙️Інструменти</b> – видалення музики чи плейлистів.\n\n"
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

    Зберігає ID файлу у JSON файл, якщо такого ID ще немає.
    Якщо ID вже існує, відправляє повідомлення та додає кнопку "Вийти".

    Args:
        message (telebot.types.Message): Повідомлення з аудіофайлом.
    """
    user_state = user_data.get(message.chat.id, {})
    if not user_state.get('adding_music', False):
        bot.send_message(message.chat.id, "🎵 Ви не в режимі додавання музики. Натисніть '➕Додати музику' у меню.")
        return

    file_id = message.audio.file_id

    # Перевіряємо, чи ID вже існує
    if file_id in music_data:
        bot.send_message(message.chat.id, "🎵 Цей файл вже існує у вашій бібліотеці.")
    else:
        music_data[file_id] = {
            "file_name": message.audio.file_name or f"{file_id}.mp3",
            "user_id": message.chat.id
        }
        save_music(music_data)
        bot.send_message(message.chat.id, "🎵 Файл успішно додано до вашої бібліотеки!")

    # Додаємо кнопку "Вийти"
    markup = telebot.types.InlineKeyboardMarkup()
    exit_button = telebot.types.InlineKeyboardButton("🚪Вийти", callback_data='music')
    markup.add(exit_button)

    bot.send_message(message.chat.id, "🎵 Ви можете додати ще один файл або вийти з режиму додавання.", reply_markup=markup)

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('adding_music', False))
def add_music_from_folder(message):
    """
    Видалено функціонал додавання музики з папки, оскільки тепер музика зберігається у JSON.
    """
    bot.send_message(message.chat.id, "❌ Додавання музики з папки більше не підтримується.")

@bot.callback_query_handler(func=lambda call: call.data == 'music_option')
def handle_music_option(call):
    """
    Обробляє вибір опції "Прослухати музику".

    Видаляє попереднє меню "music" і відображає список доступної музики для вибору та прослуховування.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id

    # Видаляємо попереднє меню
    bot.delete_message(chat_id, call.message.message_id)

    # Отримуємо список музики для користувача
    user_tracks = [file_id for file_id, info in music_data.items() if info["user_id"] == chat_id]

    if not user_tracks:
        bot.send_message(chat_id, "🎵 У вас поки немає музичних файлів. Додайте їх через меню '➕Додати музику'.")
        return

    # Зберігаємо поточний індекс треку для користувача
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['current_track_index'] = 0

    # Відправляємо перший трек разом із кнопками
    current_track_id = user_tracks[user_data[chat_id]['current_track_index']]
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⏮️ Попередня", callback_data='prev_track')
    next_button = telebot.types.InlineKeyboardButton("⏭️ Наступна", callback_data='next_track')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(prev_button, next_button)
    markup.add(back_button)

    bot.send_audio(chat_id, current_track_id, caption="🎵 Відтворення музики:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['prev_track', 'next_track'])
def handle_track_navigation(call):
    """
    Обробляє навігацію між треками ("Попередня" та "Наступна").

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_tracks = [file_id for file_id, info in music_data.items() if info["user_id"] == chat_id]

    if not user_tracks:
        bot.answer_callback_query(call.id, "🎵 У вас немає музичних файлів.")
        return

    # Отримуємо поточний індекс треку
    current_index = user_data[chat_id].get('current_track_index', 0)

    # Оновлюємо індекс залежно від кнопки
    if call.data == 'prev_track':
        current_index = (current_index - 1) % len(user_tracks)
    elif call.data == 'next_track':
        current_index = (current_index + 1) % len(user_tracks)

    # Зберігаємо оновлений індекс
    user_data[chat_id]['current_track_index'] = current_index

    # Відправляємо новий трек разом із кнопками
    current_track_id = user_tracks[current_index]
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⏮️ Попередня", callback_data='prev_track')
    next_button = telebot.types.InlineKeyboardButton("⏭️ Наступна", callback_data='next_track')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(prev_button, next_button)
    markup.add(back_button)

    bot.edit_message_media(
        chat_id=chat_id,
        message_id=call.message.message_id,
        media=telebot.types.InputMediaAudio(media=current_track_id, caption="🎵 Відтворення музики:"),
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'playlist')
def handle_playlist_menu(call):
    """
    Обробляє вибір модуля "Плейлисти".

    Відображає меню з опціями для керування плейлистами.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Переглянути плейлисти", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Створити плейлист", callback_data='create_playlist')
    edit_playlist_button = telebot.types.InlineKeyboardButton("✏️Редагувати плейлист", callback_data='edit_playlist')
    markup.row(create_playlist_button, edit_playlist_button)
    markup.row(view_playlists_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📄 <b>Меню плейлистів:</b>\n\n"
             "➕Створити плейлист – створення нового плейлиста.\n"
             "✏️Редагувати плейлист – керування треками у плейлисті.\n"
             "📂Переглянути плейлисти – перегляд та вибір існуючих плейлистів.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'edit_playlist')
def handle_edit_playlist_menu(call):
    """
    Відображає список плейлистів для редагування.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас поки немає плейлистів для редагування. Створіть новий через меню плейлистів.")
        return

    # Створюємо кнопки для кожного плейлиста
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in user_playlists:
        edit_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'manage_playlist:{playlist_name}')
        markup.add(edit_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="✏️ <b>Виберіть плейлист для редагування:</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'create_playlist')
def handle_create_playlist(call):
    """
    Обробляє створення нового плейлиста.

    Запитує у користувача назву нового плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📄 Введіть назву нового плейлиста:")

    # Встановлюємо стан для створення плейлиста
    user_data[call.message.chat.id] = {'creating_playlist': True}

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('creating_playlist', False))
def save_playlist_name(message):
    """
    Зберігає назву нового плейлиста та додає його до списку плейлистів користувача.

    Args:
        message (telebot.types.Message): Повідомлення від користувача з назвою плейлиста.
    """
    chat_id = message.chat.id
    playlist_name = message.text.strip()
    user_playlists = get_user_playlists(chat_id)

    if (playlist_name in user_playlists):
        bot.send_message(chat_id, "❌ Плейлист з такою назвою вже існує. Спробуйте іншу назву.")
    else:
        user_playlists[playlist_name] = []
        update_user_playlists(chat_id, user_playlists)
        logging.debug(f"Створено новий плейлист: {playlist_name} для чату {chat_id}.")
        bot.send_message(chat_id, f"✅ Плейлист '{playlist_name}' успішно створено!")

    # Скидаємо стан
    user_data[chat_id]['creating_playlist'] = False

@bot.callback_query_handler(func=lambda call: call.data == 'view_playlists')
def handle_view_playlists(call):
    """
    Відображає список плейлистів користувача.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас поки немає плейлистів. Створіть новий через меню плейлистів.")
        return

    # Створюємо кнопки для кожного плейлиста
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in user_playlists:
        playlist_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'open_playlist:{playlist_name}')
        markup.add(playlist_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📂 <b>Ваші плейлисти:</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('open_playlist:'))
def handle_open_playlist(call):
    """
    Відкриває вибраний плейлист та відправляє всі треки з нього.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    if playlist_name not in user_playlists or not user_playlists[playlist_name]:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"❌ Плейлист '{playlist_name}' порожній.")
        return

    tracks = user_playlists[playlist_name]
    if not tracks:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"📂 Плейлист '{playlist_name}' порожній.")
        return

    # Відправляємо всі треки з плейлиста
    for track in tracks:
        if track in music_data:
            bot.send_audio(chat_id, track)
        else:
            bot.send_message(chat_id, f"❌ Трек '{track}' не знайдено у бібліотеці.")

    bot.answer_callback_query(call.id, f"✅ Всі треки з плейлиста '{playlist_name}' відправлені.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_playlist:'))
def handle_manage_playlist(call):
    """
    Обробляє керування треками у плейлисті (додавання/видалення).

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    # Переконаємося, що плейлист існує
    if (playlist_name not in user_playlists):
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    # Отримуємо список доступних треків
    available_tracks = [file_id for file_id, info in music_data.items() if info["user_id"] == chat_id]
    if not available_tracks:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎵 Музичні файли не знайдено.")
        return

    # Створюємо кнопки для додавання/видалення треків
    markup = telebot.types.InlineKeyboardMarkup()
    for track in available_tracks:
        if track in user_playlists[playlist_name]:
            button = telebot.types.InlineKeyboardButton(f"❌ Видалити {music_data[track]['file_name']}", callback_data=f'remove:{playlist_name}:{track}')
        else:
            button = telebot.types.InlineKeyboardButton(f"➕ Додати {music_data[track]['file_name']}", callback_data=f'add:{playlist_name}:{track}')
        markup.add(button)

    # Створюємо нове меню
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Керування плейлистом '{playlist_name}':",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add:'))
def handle_add_track(call):
    """
    Додає трек до плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    _, playlist_name, track_id = call.data.split(':', 2)

    # Переконаємося, що трек існує у списку файлів
    if track_id not in music_data or music_data[track_id]["user_id"] != chat_id:
        bot.answer_callback_query(call.id, "❌ Трек не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)

    # Переконаємося, що доступ до плейлиста здійснюється лише за його назвою
    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    user_playlists[playlist_name].append(track_id)
    update_user_playlists(chat_id, user_playlists)
    bot.answer_callback_query(call.id, f"✅ Трек '{music_data[track_id]['file_name']}' додано до плейлиста '{playlist_name}'.")
    # Створюємо кнопки для керування плейлистом
    user_playlists = get_user_playlists(call.message.chat.id)
    available_tracks = [file_id for file_id, info in music_data.items() if info["user_id"] == call.message.chat.id]
    markup = telebot.types.InlineKeyboardMarkup()
    for track in available_tracks:
        if track in user_playlists.get(playlist_name, []):
            button = telebot.types.InlineKeyboardButton(f"❌ Видалити {music_data[track]['file_name']}", callback_data=f'remove:{playlist_name}:{track}')
        else:
            button = telebot.types.InlineKeyboardButton(f"➕ Додати {music_data[track]['file_name']}", callback_data=f'add:{playlist_name}:{track}')
        markup.add(button)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)  # Оновлюємо кнопки
    handle_manage_playlist(call)  # Оновлюємо меню після додавання треку

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove:'))
def handle_remove_track(call):
    """
    Видаляє трек з плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    _, playlist_name, track_id = call.data.split(':', 2)

    # Переконаємося, що трек існує у списку файлів
    if track_id not in music_data or music_data[track_id]["user_id"] != chat_id:
        bot.answer_callback_query(call.id, "❌ Трек не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)

    # Переконаємося, що доступ до плейлиста здійснюється лише за його назвою
    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    # Перевіряємо наявність треку у плейлисті
    if track_id in user_playlists.get(playlist_name, []):
        user_playlists[playlist_name].remove(track_id)
        update_user_playlists(chat_id, user_playlists)
        bot.answer_callback_query(call.id, f"❌ Трек '{music_data[track_id]['file_name']}' видалено з плейлиста '{playlist_name}'.")
        # Створюємо кнопки для керування плейлистом
        user_playlists = get_user_playlists(call.message.chat.id)
        available_tracks = [file_id for file_id, info in music_data.items() if info["user_id"] == call.message.chat.id]
        markup = telebot.types.InlineKeyboardMarkup()
        for track in available_tracks:
            if track in user_playlists.get(playlist_name, []):
                button = telebot.types.InlineKeyboardButton(f"❌ Видалити {music_data[track]['file_name']}", callback_data=f'remove:{playlist_name}:{track}')
            else:
                button = telebot.types.InlineKeyboardButton(f"➕ Додати {music_data[track]['file_name']}", callback_data=f'add:{playlist_name}:{track}')
            markup.add(button)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)  # Оновлюємо кнопки
        handle_manage_playlist(call)  # Оновлюємо меню після видалення треку
    else:
        bot.answer_callback_query(call.id, "❌ Трек не знайдено у плейлисті.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('play_playlist:'))
def handle_play_playlist(call):
    """
    Відтворює всі треки з вибраного плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    # Перевіряємо наявність плейлиста з урахуванням регістру та пробілів
    normalized_playlists = {name.strip().lower(): name for name in user_playlists.keys()}
    normalized_name = playlist_name.strip().lower()

    if not user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return
    
    # Використовуємо оригінальну назву плейлиста
    playlist_name = normalized_playlists[normalized_name]

    if not user_playlists[playlist_name]:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"❌ Плейлист '{playlist_name}' порожній.")
        return

    for track in user_playlists[playlist_name]:
        if track in music_data:
            bot.send_audio(chat_id, track)
        else:
            bot.send_message(chat_id, f"❌ Трек '{track}' не знайдено у бібліотеці.")

    bot.answer_callback_query(call.id, f"✅ Всі треки з плейлиста '{playlist_name}' відправлені.")

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