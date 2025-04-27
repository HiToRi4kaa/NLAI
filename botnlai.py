import telebot
import json
import logging

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Для кінечної версії бота вимкнемо логування
telebot.logger.setLevel(logging.WARNING)

# Створення об'єкта бота
bot = telebot.TeleBot('8064955635:AAHe78CWompJ-CQxoIOUQ_4OryhjeIkd6vw')

# Глобальні змінні
user_data = {}
playlists = []
PLAYLISTS_FILE = 'playlists.json'
MUSIC_FILE = 'music.json'

# Функції
def load_music():
    """
    Завантажує дані про музику з файлу.

    Якщо файл не знайдено або виникає помилка декодування JSON, повертає порожню структуру.

    Returns:
        dict: Дані про музику.
    """
    try:
        with open(MUSIC_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.warning("Файл music.json не знайдено. Створено порожню структуру музики.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Помилка декодування JSON: {e}. Створено порожню структуру музики.")
        return {}

def save_music(music_data):
    """
    Зберігає дані про музику у файл.

    Args:
        music_data (dict): Дані про музику для збереження.
    """
    try:
        with open(MUSIC_FILE, 'w', encoding='utf-8') as file:
            json.dump(music_data, file, ensure_ascii=False, indent=4)
        logging.debug("Музика успішно збережена у файл.")
    except Exception as e:
        logging.error(f"Помилка при збереженні музики: {e}")

def load_playlists():
    """
    Завантажує плейлисти з файлу у глобальну змінну `playlists`.

    Якщо файл не знайдено або виникає помилка декодування JSON, створює порожню структуру.
    """
    global playlists
    try:
        with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as file:
            playlists = json.load(file)
            logging.debug(f"Плейлисти успішно завантажені з файлу: {playlists}")
    except FileNotFoundError:
        playlists = []
        logging.warning("Файл playlists.json не знайдено. Створено порожню структуру плейлистів.")
    except json.JSONDecodeError as e:
        playlists = []
        logging.error(f"Помилка декодування JSON: {e}. Створено порожню структуру плейлистів.")

def save_playlists():
    """
    Зберігає плейлисти у файл.

    Якщо виникає помилка, записує її у лог.
    """
    try:
        with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(playlists, file, ensure_ascii=False, indent=4)
        logging.debug("Плейлисти успішно збережені у файл.")
    except Exception as e:
        logging.error(f"Помилка при збереженні плейлистів: {e}")

def get_user_playlists(user_id):
    """
    Повертає плейлисти користувача за його ID.

    Args:
        user_id (int): ID користувача.

    Returns:
        dict: Словник з плейлистами користувача.
    """
    for user_data in playlists:
        if user_data.get("user_id") == user_id:
            return user_data.get("playlists", {})
    return {}

def update_user_playlists(user_id, updated_playlists):
    """
    Оновлює плейлисти користувача у глобальній змінній та зберігає їх у файл.

    Args:
        user_id (int): ID користувача.
        updated_playlists (dict): Оновлені плейлисти користувача.
    """
    for user_data in playlists:
        if user_data["user_id"] == user_id:
            user_data["playlists"] = updated_playlists
            save_playlists()
            return
    # Якщо користувача не знайдено, додаємо нового
    playlists.append({"user_id": user_id, "playlists": updated_playlists})
    save_playlists()

# Завантажуємо дані при запуску
music_data = load_music()
load_playlists()

#Основні команди
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обробляє команду /start.

    Відправляє користувачу привітання та головне меню.

    Args:
        message (telebot.types.Message): Повідомлення від користувача.
    """
    # Встановлюємо значення у False
    if message.chat.id in user_data:
        user_data[message.chat.id]['adding_music'] = False
        user_data[message.chat.id]['creating_playlist'] = False

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

@bot.message_handler(commands=['help'])
def send_help(message):
    """
    Відправляє користувачу інформацію про його ID.

    Args:
        message (telebot.types.Message): Повідомлення від користувача.
    """
    bot.send_message(message.chat.id, f"Ваш ID: {message.from_user.id}")  # Відправляємо ID користувача

@bot.message_handler(commands=['info'])
def send_info(message):
    """
    Відправляє користувачу інформацію про автора бота.

    Args:
        message (telebot.types.Message): Повідомлення від користувача.
    """
    bot.send_message(
        message.chat.id,
        "<b>ℹ️ Інформація про розробника:</b>\n\n"
        "👨‍🎓 <b>Автор:</b> студент <i>Новокаховського фахового коледжу</i>\n"
        "📚 <b>Група:</b> 12221\n"
        "✍️ <b>Ім'я:</b> Миллєр Максим\n\n"
        "Дякую, що користуєтесь ботом! 😊",
        parse_mode='HTML'
    )

# --- Callback Query Handlers for Music ---
@bot.callback_query_handler(func=lambda call: call.data == 'music')
def music_menu(call):
    """
    Відображає меню модуля "Музика".

    Видаляє попереднє повідомлення та показує кнопки для вибору опцій.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    # Встановлюємо значення у False
    if call.message.chat.id in user_data:
        user_data[call.message.chat.id]['adding_music'] = False
        user_data[call.message.chat.id]['creating_playlist'] = False

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

    Відправляє користувачу інструкцію для завантаження музики.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

    # Додаємо кнопку "Назад"
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.add(back_button)

    bot.send_message(
        call.message.chat.id,
        "🎵 Надішліть файл з музикою в цей чат, щоб додати його, або натисніть 'Назад', щоб повернутися.",
        reply_markup=markup
    )
    user_data[call.message.chat.id] = {'adding_music': True}

@bot.message_handler(content_types=['audio'])
def save_music_file(message):
    """
    Обробляє отримання аудіофайлу від користувача.

    Зберігає файл у бібліотеці користувача або повідомляє про дублювання.

    Args:
        message (telebot.types.Message): Повідомлення з аудіофайлом.
    """
    user_state = user_data.get(message.chat.id, {})
    if not user_state.get('adding_music', False):
        bot.send_message(message.chat.id, "🎵 Ви не в режимі додавання музики. Натисніть '➕Додати музику' у меню.")
        return

    file_name = message.audio.file_name or f"{message.audio.file_id}.mp3"
    file_id = message.audio.file_id
    user_id = message.chat.id

    # Перевіряємо, чи файл з такою назвою вже існує для цього користувача
    if file_name in music_data and any(entry["user_id"] == user_id for entry in music_data[file_name]):
        bot.send_message(message.chat.id, "🎵 Файл з такою назвою вже існує у вашій бібліотеці.")
    else:
        if (file_name not in music_data):
            music_data[file_name] = []
        music_data[file_name].append({"file_id": file_id, "user_id": user_id})
        save_music(music_data)
        bot.send_message(message.chat.id, "🎵 Файл успішно додано до вашої бібліотеки!")

    # Додаємо кнопку "Вийти"
    markup = telebot.types.InlineKeyboardMarkup()
    exit_button = telebot.types.InlineKeyboardButton("🚪Вийти", callback_data='music')
    markup.add(exit_button)

    bot.send_message(message.chat.id, "🎵 Ви можете додати ще один файл або вийти з режиму додавання.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'music_option')
def handle_music_option(call):
    """
    Відображає список доступної музики для прослуховування.

    Видаляє попереднє меню та показує кнопки для навігації між треками.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id

    # Видаляємо попереднє меню
    bot.delete_message(chat_id, call.message.message_id)

    # Отримуємо список музики для користувача
    user_tracks = [file_name for file_name, entries in music_data.items() if any(entry["user_id"] == chat_id for entry in entries)]

    if not user_tracks:
        bot.send_message(chat_id, "🎵 У вас поки немає музичних файлів. Додайте їх через меню '➕Додати музику'.")
        return

    # Зберігаємо поточний індекс треку для користувача
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['current_track_index'] = 0

    # Відправляємо перший трек разом із кнопками
    current_track_name = user_tracks[user_data[chat_id]['current_track_index']]
    current_track_id = next(entry["file_id"] for entry in music_data[current_track_name] if entry["user_id"] == chat_id)
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⏮️ Попередня", callback_data='prev_track')
    next_button = telebot.types.InlineKeyboardButton("⏭️ Наступна", callback_data='next_track')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(prev_button, next_button)
    markup.add(back_button)

    bot.send_audio(chat_id, current_track_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['prev_track', 'next_track'])
def handle_track_navigation(call):
    """
    Обробляє навігацію між треками.

    Показує попередній або наступний трек у списку.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_tracks = [file_name for file_name, entries in music_data.items() if any(entry["user_id"] == chat_id for entry in entries)]

    if not user_tracks:
        bot.answer_callback_query(call.id, "🎵 У вас немає музичних файлів.")
        return

    current_index = user_data[chat_id].get('current_track_index', 0)

    if call.data == 'prev_track':
        current_index = (current_index - 1) % len(user_tracks)
    elif call.data == 'next_track':
        current_index = (current_index + 1) % len(user_tracks)

    user_data[chat_id]['current_track_index'] = current_index

    current_track_name = user_tracks[current_index]
    current_track_id = next(entry["file_id"] for entry in music_data[current_track_name] if entry["user_id"] == chat_id)
    markup = telebot.types.InlineKeyboardMarkup()
    prev_button = telebot.types.InlineKeyboardButton("⏮️ Попередня", callback_data='prev_track')
    next_button = telebot.types.InlineKeyboardButton("⏭️ Наступна", callback_data='next_track')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(prev_button, next_button)
    markup.add(back_button)

    bot.edit_message_media(
        chat_id=chat_id,
        message_id=call.message.message_id,
        media=telebot.types.InputMediaAudio(media=current_track_id),
        reply_markup=markup
    )

#Плейлисти
@bot.callback_query_handler(func=lambda call: call.data == 'playlist')
def handle_playlist_menu(call):
    """
    Відображає меню модуля "Плейлисти".

    Показує кнопки для перегляду, створення та редагування плейлистів.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id

    # Ініціалізуємо дані користувача, якщо їх ще немає
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # Скидаємо стан створення плейлиста
    user_data[chat_id]['creating_playlist'] = False

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Переглянути плейлисти", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Створити плейлист", callback_data='create_playlist')
    edit_playlists_button = telebot.types.InlineKeyboardButton("✏️Редагувати плейлисти", callback_data='edit_playlists')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(view_playlists_button, create_playlist_button)
    markup.row(edit_playlists_button)
    markup.add(back_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📄 <b>Меню плейлистів:</b>\n\n"
             "📂Переглянути плейлисти – перегляд та вибір існуючих плейлистів.\n"
             "➕Створити плейлист – створення нового плейлиста.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_playlists'))
def handle_view_playlists(call):
    """
    Відображає список плейлистів користувача з пагінацією.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас поки немає плейлистів. Додайте їх через меню '➕Додати музику'.")
        return

    # Отримуємо поточну сторінку з callback_data
    data_parts = call.data.split(':')
    current_page = int(data_parts[1]) if len(data_parts) > 1 else 0

    # Визначаємо кількість плейлистів на сторінці
    playlists_per_page = 5
    playlist_names = list(user_playlists.keys())
    total_pages = (len(playlist_names) + playlists_per_page - 1) // playlists_per_page

    # Отримуємо плейлисти для поточної сторінки
    start_index = current_page * playlists_per_page
    end_index = start_index + playlists_per_page
    page_playlists = playlist_names[start_index:end_index]

    # Створюємо кнопки для плейлистів
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in page_playlists:
        playlist_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'play_playlist:{playlist_name}')
        markup.add(playlist_button)

    # Додаємо кнопки пагінації
    if current_page > 0 and current_page < total_pages - 1:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'view_playlists:{current_page - 1}')
        next_button = telebot.types.InlineKeyboardButton("➡️ Следующая страница", callback_data=f'view_playlists:{current_page + 1}')
        markup.row(prev_button, next_button)
    elif current_page > 0:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'view_playlists:{current_page - 1}')
        markup.add(prev_button)
    elif current_page < total_pages - 1:
        next_button = telebot.types.InlineKeyboardButton("➡️ Следующая страница", callback_data=f'view_playlists:{current_page + 1}')
        markup.add(next_button)

    # Додаємо кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.add(back_button)

    # Відправляємо повідомлення з плейлистами
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 <b>Ваши плейлисты (страница {current_page + 1} из {total_pages}):</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('play_playlist:'))
def handle_play_playlist(call):
    """
    Відображає треки з вибраного плейлиста з пагінацією.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    data_parts = call.data.split(':')
    playlist_name = data_parts[1]
    current_page = int(data_parts[2]) if len(data_parts) > 2 else 0

    user_playlists = get_user_playlists(chat_id)

    if (playlist_name not in user_playlists):
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    playlist_tracks = user_playlists[playlist_name]

    if not playlist_tracks:
        bot.answer_callback_query(call.id, f"❌ Плейлист '{playlist_name}' пустий.")
        return

    # Параметри пагінації
    tracks_per_page = 5
    total_pages = (len(playlist_tracks) + tracks_per_page - 1) // tracks_per_page
    start_index = current_page * tracks_per_page
    end_index = start_index + tracks_per_page
    page_tracks = playlist_tracks[start_index:end_index]

    # Видаляємо попереднє меню
    bot.delete_message(chat_id, call.message.message_id)

    # Відправляємо треки на поточній сторінці
    for track_name in page_tracks:
        track_id = next(
            (entry["file_id"] for entry in music_data.get(track_name, []) if entry["user_id"] == chat_id),
            None
        )
        if track_id:
            bot.send_audio(chat_id, track_id)

    # Створюємо кнопки пагінації
    markup = telebot.types.InlineKeyboardMarkup()
    if current_page > 0:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Попередня сторінка", callback_data=f'play_playlist:{playlist_name}:{current_page - 1}')
        markup.add(prev_button)
    if current_page < total_pages - 1:
        next_button = telebot.types.InlineKeyboardButton("➡️ Наступна сторінка", callback_data=f'play_playlist:{playlist_name}:{current_page + 1}')
        markup.add(next_button)

    # Додаємо кнопку "Видалити плейлист"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='view_playlists')
    markup.add(back_button)

    # Відправляємо повідомлення з плейлистом
    bot.send_message(
        chat_id,
        f"🎵 Плейлист '{playlist_name}' (Сторінка {current_page + 1} з {total_pages}):",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'edit_playlists' or call.data.startswith('edit_playlists:'))
def handle_edit_playlists_menu(call):
    """
    Відображає меню редагування плейлистів з пагінацією.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас поки немає плейлистів для редагування. Створіть новий через меню плейлистів.")
        return

    # Отримуємо поточну сторінку з callback_data
    data_parts = call.data.split(':')
    current_page = int(data_parts[1]) if len(data_parts) > 1 else 0

    # Визначаємо кількість плейлистів на сторінці
    playlists_per_page = 5
    playlist_names = list(user_playlists.keys())
    total_pages = (len(playlist_names) + playlists_per_page - 1) // playlists_per_page

    # Отримуємо плейлисти для поточної сторінки
    start_index = current_page * playlists_per_page
    end_index = start_index + playlists_per_page
    page_playlists = playlist_names[start_index:end_index]

    # Створюємо кнопки для редагування плейлистів
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in page_playlists:
        edit_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'edit_playlist:{playlist_name}')
        markup.add(edit_button)

    # Додаємо кнопки пагінації
    if current_page > 0 and current_page < total_pages - 1:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Попередня сторінка", callback_data=f'edit_playlists:{current_page - 1}')
        next_button = telebot.types.InlineKeyboardButton("➡️ Наступна сторінка", callback_data=f'edit_playlists:{current_page + 1}')
        markup.row(prev_button, next_button)
    elif current_page > 0:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Попередня сторінка", callback_data=f'edit_playlists:{current_page - 1}')
        markup.add(prev_button)
    elif current_page < total_pages - 1:
        next_button = telebot.types.InlineKeyboardButton("➡️ Наступна сторінка", callback_data=f'edit_playlists:{current_page + 1}')
        markup.add(next_button)

    # Додаємо кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='playlist')
    markup.add(back_button)

    # Відправляємо повідомлення з плейлистами
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✏️ <b>Редагування плейлистів (Сторінка {current_page + 1} з {total_pages}):</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_playlist:'))
def handle_edit_playlist(call):
    """
    Обробляє вибір конкретного плейлиста для редагування.

    Зберігає назву плейлиста в user_data і відображає меню редагування.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':')[1]

    # Зберігаємо плейлист у user_data
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['editing_playlist'] = playlist_name

    # Видаляємо старе меню
    bot.delete_message(chat_id, call.message.message_id)

    # Створюємо кнопки
    markup = telebot.types.InlineKeyboardMarkup()
    edit_tracks_button = telebot.types.InlineKeyboardButton("🎵 Редагувати треки", callback_data='manage_tracks:0')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='edit_playlists:0')
    markup.row(edit_tracks_button, back_button)

    # Відправляємо повідомлення
    bot.send_message(
        chat_id,
        f"📂 Плейлист: <b>{playlist_name}</b>",
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
    # Видаляємо старе повідомлення
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

    # Додаємо кнопку "Назад"
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='playlist')
    markup.add(back_button)

    bot.send_message(
        call.message.chat.id,
        "📄 Введіть назву нового плейлиста або натисніть 'Назад', щоб повернутися:",
        reply_markup=markup
    )

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
    playlist_name = message.text.strip().lower()

    # Перевіряємо, якщо користувач відправив "назад"
    if playlist_name == "назад":
        # Скидаємо стан і повертаємося до меню плейлистів
        if chat_id in user_data:
            user_data[chat_id]['creating_playlist'] = False
        handle_playlist_menu_direct(chat_id)
        return

    user_playlists = get_user_playlists(chat_id)

    if playlist_name in user_playlists:
        bot.send_message(chat_id, "❌ Плейлист з такою назвою вже існує. Спробуйте іншу назву.")
    else:
        user_playlists[playlist_name] = []
        update_user_playlists(chat_id, user_playlists)
        logging.debug(f"Створено новий плейлист: {playlist_name} для чату {chat_id}.")
        bot.send_message(chat_id, f"✅ Плейлист '{playlist_name}' успішно створено!")

    # Скидаємо стан
    if chat_id in user_data:
        user_data[chat_id]['creating_playlist'] = False

    # Повертаємося до меню плейлистів
    handle_playlist_menu_direct(chat_id)

def handle_playlist_menu_direct(chat_id):
    """
    Відображає меню плейлистів без використання CallbackQuery.

    Args:
        chat_id (int): ID чату.
    """
    # Ініціалізуємо дані користувача, якщо їх ще немає
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # Скидаємо стан створення плейлиста
    user_data[chat_id]['creating_playlist'] = False

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Переглянути плейлисти", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Створити плейлист", callback_data='create_playlist')
    edit_playlists_button = telebot.types.InlineKeyboardButton("✏️Редагувати плейлисти", callback_data='edit_playlists')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(view_playlists_button, create_playlist_button)
    markup.row(edit_playlists_button)
    markup.add(back_button)

    # Відправляємо повідомлення
    bot.send_message(
        chat_id,
        "📄 <b>Меню плейлистів:</b>\n\n"
        "📂Переглянути плейлисти – перегляд та вибір існуючих плейлистів.\n"
        "➕Створити плейлист – створення нового плейлиста.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_tracks:'))
def handle_manage_tracks(call):
    """
    Відображає список треків для редагування у плейлисті з пагінацією.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    current_page = int(call.data.split(':')[1])

    # Отримуємо назву плейлиста з user_data
    playlist_name = user_data.get(chat_id, {}).get('editing_playlist')
    if not playlist_name:
        bot.answer_callback_query(call.id, "❌ Помилка: плейлист не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)
    playlist_tracks = user_playlists.get(playlist_name, [])

    # Отримуємо список усіх треків користувача
    user_tracks = [file_name for file_name, entries in music_data.items() if any(entry["user_id"] == chat_id for entry in entries)]

    # Параметри пагінації
    tracks_per_page = 5
    total_pages = (len(user_tracks) + tracks_per_page - 1) // tracks_per_page
    start_index = current_page * tracks_per_page
    end_index = start_index + tracks_per_page
    page_tracks = user_tracks[start_index:end_index]

    # Видаляємо попереднє меню
    bot.delete_message(chat_id, call.message.message_id)

    # Створюємо кнопки для треків
    markup = telebot.types.InlineKeyboardMarkup()
    for track_name in page_tracks:
        # Скорочуємо callback_data
        if track_name in playlist_tracks:
            button = telebot.types.InlineKeyboardButton("❌ " + track_name[:20], callback_data=f'rm:{current_page}:{track_name}')
        else:
            button = telebot.types.InlineKeyboardButton("➕ " + track_name[:20], callback_data=f'add:{current_page}:{track_name}')
        markup.add(button)

    # Додаємо кнопки пагінації
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(telebot.types.InlineKeyboardButton("⬅️ Попередня", callback_data=f'manage_tracks:{current_page - 1}'))
    if current_page < total_pages - 1:
        pagination_buttons.append(telebot.types.InlineKeyboardButton("➡️ Наступна", callback_data=f'manage_tracks:{current_page + 1}'))
    if pagination_buttons:
        markup.row(*pagination_buttons)

    # Додаємо кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data=f'edit_playlist:{playlist_name}')
    markup.add(back_button)

    # Відправляємо повідомлення
    bot.send_message(
        chat_id,
        f"🎵 Треки для редагування у плейлисті '{playlist_name}' (Сторінка {current_page + 1} з {total_pages}):",
        reply_markup=markup
    )

def update_manage_tracks_message(call, playlist_name, chat_id):
    """
    Оновлює повідомлення з кнопками для редагування треків у плейлисті.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
        playlist_name (str): Назва плейлиста.
        chat_id (int): ID чату.
    """
    user_playlists = get_user_playlists(chat_id)
    playlist_tracks = user_playlists.get(playlist_name, [])
    user_tracks = [file_name for file_name, entries in music_data.items() if any(entry["user_id"] == chat_id for entry in entries)]

    # Параметри пагінації
    current_page = int(call.data.split(':')[-1]) if call.data.split(':')[-1].isdigit() else 0
    tracks_per_page = 5
    total_pages = (len(user_tracks) + tracks_per_page - 1) // tracks_per_page
    start_index = current_page * tracks_per_page
    end_index = start_index + tracks_per_page
    page_tracks = user_tracks[start_index:end_index]

    # Створюємо кнопки для треків
    markup = telebot.types.InlineKeyboardMarkup()
    for track_name in page_tracks:
        if track_name in playlist_tracks:
            # Якщо трек є у плейлисті, показуємо кнопку "Видалити"
            button = telebot.types.InlineKeyboardButton("❌ Видалити " + track_name[:20], callback_data=f'rm:{current_page}:{track_name}')
        else:
            # Якщо треку немає у плейлисті, показуємо кнопку "Додати"
            button = telebot.types.InlineKeyboardButton("➕ Додати " + track_name[:20], callback_data=f'add:{current_page}:{track_name}')
        markup.add(button)

    # Додаємо кнопки пагінації
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(telebot.types.InlineKeyboardButton("⬅️ Попередня", callback_data=f'manage_tracks:{current_page - 1}'))
    if current_page < total_pages - 1:
        pagination_buttons.append(telebot.types.InlineKeyboardButton("➡️ Наступна", callback_data=f'manage_tracks:{current_page + 1}'))
    if pagination_buttons:
        markup.row(*pagination_buttons)

    # Додаємо кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data=f'edit_playlist:{playlist_name}')
    markup.add(back_button)

    # Оновлюємо повідомлення
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Треки для редагування у плейлисті '{playlist_name}' (Сторінка {current_page + 1} з {total_pages}):",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add:'))
def handle_add_track_to_playlist(call):
    """
    Додає вибраний трек до плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    data_parts = call.data.split(':')
    current_page = int(data_parts[1])
    track_name = ':'.join(data_parts[2:])

    # Отримуємо назву плейлиста з user_data
    playlist_name = user_data.get(chat_id, {}).get('editing_playlist')
    if not playlist_name:
        bot.answer_callback_query(call.id, "❌ Помилка: плейлист не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)
    if playlist_name in user_playlists:
        # Перевіряємо, чи трек вже є у плейлисті
        if track_name not in user_playlists[playlist_name]:
            # Додаємо трек до плейлиста
            user_playlists[playlist_name].append(track_name)
            update_user_playlists(chat_id, user_playlists)
            bot.answer_callback_query(call.id, f"✅ Трек '{track_name}' додано до плейлиста.")
            # Оновлюємо повідомлення з кнопками
            update_manage_tracks_message(call, playlist_name, chat_id)
        else:
            bot.answer_callback_query(call.id, "❌ Трек вже є у плейлисті.")
    else:
        bot.answer_callback_query(call.id, "❌ Помилка: плейлист не знайдено.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('rm:'))
def handle_remove_track(call):
    """
    Видаляє вибраний трек з плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    data_parts = call.data.split(':')
    current_page = int(data_parts[1])
    track_name = ':'.join(data_parts[2:])

    # Отримуємо назву плейлиста з user_data
    playlist_name = user_data.get(chat_id, {}).get('editing_playlist')
    if not playlist_name:
        bot.answer_callback_query(call.id, "❌ Помилка: плейлист не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)
    if playlist_name in user_playlists and track_name in user_playlists[playlist_name]:
        # Видаляємо трек з плейлиста
        user_playlists[playlist_name].remove(track_name)
        update_user_playlists(chat_id, user_playlists)
        bot.answer_callback_query(call.id, f"✅ Трек '{track_name}' видалено.")
        # Оновлюємо повідомлення з кнопками
        update_manage_tracks_message(call, playlist_name, chat_id)
    else:
        bot.answer_callback_query(call.id, "❌ Трек не знайдено у плейлисті.")

#Кінець
if __name__ == "__main__":
    """
    Запускає бота у режимі опитування.
    """
    bot.polling()