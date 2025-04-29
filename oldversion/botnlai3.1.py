import telebot
import os
import hashlib
import json
import logging

# Налаштовуємо логування
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(level)s - %(message)s')

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

def generate_callback_data(prefix, data):
    """
    Генерує хешовану callback_data для уникнення перевищення ліміту довжини.

    Args:
        prefix (str): Префікс для callback_data.
        data (str): Дані для хешування.

    Returns:
        str: Скорочена callback_data.
    """
    hashed_data = hashlib.sha256(data.encode()).hexdigest()[:32]
    return f"{prefix}:{hashed_data}"

# Створення об'єкта бота
bot = telebot.TeleBot('8064955635:AAHe78CWompJ-CQxoIOUQ_4OryhjeIkd6vw')

# Глобальна змінна для зберігання даних користувачів
user_data = {}

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
    """
    Завантажує плейлисти з файлу у глобальну змінну `playlists`.
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
    # Встановлюємо значення у False
    if message.chat.id in user_data:
        user_data[message.chat.id]['adding_music'] = False
        user_data[message.chat.id]['creating_playlist'] = False  # Исправлено message.chat_id на message.chat.id

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
    # Встановлюємо значення у False
    if call.message.chat.id in user_data:
        user_data[call.message.chat.id]['adding_music'] = False
        user_data[call.message.chat.id]['creating_playlist'] = False  # Исправлено call.chat_id на call.message.chat.id

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

    Зберігає назву файлу як ключ, а словник з ID Telegram та ID користувача як значення у JSON файл.
    Якщо файл з такою назвою вже існує для цього користувача, відправляє повідомлення про це.

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
    Обробляє вибір опції "Прослухати музику".

    Видаляє попереднє меню "music" і відображає список доступної музики для вибору та прослуховування.

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
    Обробляє навігацію між треками ("Попередня" та "Наступна").

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
        media=telebot.types.InputMediaAudio(media=current_track_id),  # Убрано caption
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

    # Инициализация данных пользователя, если их нет
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # Сбрасываем состояние создания плейлиста
    user_data[chat_id]['creating_playlist'] = False

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Переглянути плейлисти", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Створити плейлист", callback_data='create_playlist')
    edit_playlist_button = telebot.types.InlineKeyboardButton("✏️Редагувати плейлист", callback_data='edit_playlist')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(create_playlist_button, edit_playlist_button)
    markup.row(view_playlists_button)
    markup.add(back_button)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_playlist'))
def handle_edit_playlist_menu(call):
    """
    Відображає список плейлистів для редагування з пагінацією.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас поки немає плейлистів для редагування. Створіть новий через меню плейлистів.")
        return

    # Получаем текущую страницу из callback_data
    data_parts = call.data.split(':')
    current_page = int(data_parts[1]) if len(data_parts) > 1 else 0

    # Определяем количество плейлистов на странице
    playlists_per_page = 5
    playlist_names = list(user_playlists.keys())
    total_pages = (len(playlist_names) + playlists_per_page - 1) // playlists_per_page

    # Получаем плейлисты для текущей страницы
    start_index = current_page * playlists_per_page
    end_index = start_index + playlists_per_page
    page_playlists = playlist_names[start_index:end_index]

    # Создаем кнопки для редактирования плейлистов
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in page_playlists:
        edit_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'manage_playlist:{playlist_name}')
        markup.add(edit_button)

    # Добавляем кнопки пагинации
    if current_page > 0 and current_page < total_pages - 1:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'edit_playlist:{current_page - 1}')
        next_button = telebot.types.InlineKeyboardButton("➡️ Следующая страница", callback_data=f'edit_playlist:{current_page + 1}')
        markup.add(prev_button, next_button)
    elif current_page > 0:
        prev_button = telebot.types.InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'edit_playlist:{current_page - 1}')
        markup.add(prev_button)
    elif current_page < total_pages - 1:
        next_button = telebot.types.InlineKeyboardButton("➡️ Следующая страница", callback_data=f'edit_playlist:{current_page + 1}')
        markup.add(next_button)

    # Добавляем кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='playlist')
    markup.add(back_button)

    # Отправляем сообщение с плейлистами
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✏️ <b>Виберіть плейлист для редагування (страница {current_page + 1} из {total_pages}):</b>",
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
    # Видаляємо попереднє повідомлення
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

    # Проверяем, если пользователь отправил "назад"
    if playlist_name == "назад":
        # Скидаємо стан і повертаємося до меню плейлистів
        if chat_id in user_data:
            user_data[chat_id]['creating_playlist'] = False
        handle_playlist_menu_direct(chat_id, message)
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
    handle_playlist_menu_direct(chat_id, message)


def handle_playlist_menu_direct(chat_id, message):
    """
    Відображає меню плейлистів без використання CallbackQuery.

    Args:
        chat_id (int): ID чату.
        message (telebot.types.Message): Повідомлення від користувача.
    """
    # Инициализация данных пользователя, если их нет
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # Сбрасываем состояние создания плейлиста
    user_data[chat_id]['creating_playlist'] = False

    # Створюємо меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Переглянути плейлисти", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Створити плейлист", callback_data='create_playlist')
    edit_playlist_button = telebot.types.InlineKeyboardButton("✏️Редагувати плейлист", callback_data='edit_playlist')
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='music')
    markup.row(create_playlist_button, edit_playlist_button)
    markup.row(view_playlists_button)
    markup.add(back_button)

    # Відправляємо повідомлення
    bot.send_message(
        chat_id,
        "📄 <b>Меню плейлистів:</b>\n\n"
        "➕Створити плейлист – створення нового плейлиста.\n"
        "✏️Редагувати плейлист – керування треками у плейлисті.\n"
        "📂Переглянути плейлисти – перегляд та вибір існуючих плейлистів.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_playlist:'))
def handle_manage_playlist(call):
    """
    Обробляє керування треками у плейлисті (додавання/видалення).

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]  # Используем прямое сопоставление

    user_playlists = get_user_playlists(chat_id)

    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    # Отримуємо список доступних треків
    available_tracks = [
        file_name for file_name, entries in music_data.items()
        if any(entry["user_id"] == chat_id for entry in entries)
    ]

    if not available_tracks:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎵 Музичні файли не знайдено.")
        return

    # Створюємо кнопки для додавання/видалення треків
    markup = telebot.types.InlineKeyboardMarkup()
    for track_name in available_tracks:
        track_id = hashlib.md5(track_name.encode()).hexdigest()[:10]  # Генерация сокращенного идентификатора
        if track_name in user_playlists[playlist_name]:
            button = telebot.types.InlineKeyboardButton(
                f"❌ Видалити {track_name}", callback_data=f'remove:{playlist_name}:{track_id}'
            )
        else:
            button = telebot.types.InlineKeyboardButton(
                f"➕ Додати {track_name}", callback_data=f'add:{playlist_name}:{track_id}'
            )
        markup.add(button)

    # Добавляем кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='edit_playlist:0')
    markup.add(back_button)

    # Створюємо нове меню
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Керування плейлистом '{playlist_name}':",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add:') or call.data.startswith('remove:'))
def handle_track_action(call):
    """
    Обробляє додавання або видалення треку з плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Об'єкт з даними про натиснуту кнопку.
    """
    chat_id = call.message.chat.id
    action, playlist_name, track_id = call.data.split(':', 2)

    # Знаходимо трек за його ідентифікатором
    available_tracks = [
        file_name for file_name, entries in music_data.items()
        if any(entry["user_id"] == chat_id for entry in entries)
    ]
    track_name = next((f for f in available_tracks if hashlib.md5(f.encode()).hexdigest()[:10] == track_id), None)

    if not track_name:
        bot.answer_callback_query(call.id, "❌ Трек не знайдено.")
        return

    user_playlists = get_user_playlists(chat_id)

    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не знайдено.")
        return

    if action == "add":
        if track_name not in user_playlists[playlist_name]:
            user_playlists[playlist_name].append(track_name)
            update_user_playlists(chat_id, user_playlists)
            bot.answer_callback_query(call.id, f"✅ Трек '{track_name}' додано до плейлиста '{playlist_name}'.")
        else:
            bot.answer_callback_query(call.id, "❌ Трек вже є у плейлисті.")
    elif action == "remove":
        if track_name in user_playlists[playlist_name]:
            user_playlists[playlist_name].remove(track_name)
            update_user_playlists(chat_id, user_playlists)
            bot.answer_callback_query(call.id, f"❌ Трек '{track_name}' видалено з плейлиста '{playlist_name}'.")
        else:
            bot.answer_callback_query(call.id, "❌ Трек не знайдено у плейлисті.")

    # Обновляем кнопки для управления плейлистом
    markup = telebot.types.InlineKeyboardMarkup()
    for track in available_tracks:
        track_id = hashlib.md5(track.encode()).hexdigest()[:10]
        if track in user_playlists[playlist_name]:
            button = telebot.types.InlineKeyboardButton(f"❌ Удалить {track}", callback_data=f'remove:{playlist_name}:{track_id}')
        else:
            button = telebot.types.InlineKeyboardButton(f"➕ Добавить {track}", callback_data=f'add:{playlist_name}:{track_id}')
        markup.add(button)

    # Добавляем кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='edit_playlist:0')
    markup.add(back_button)

    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_playlists'))
def handle_view_playlists(call):
    """
    Обрабатывает просмотр плейлистов пользователя с пагинацией.

    Отображает список плейлистов, доступных для прослушивания.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас пока нет плейлистов. Создайте новый через меню плейлистов.")
        return

    # Получаем текущую страницу из callback_data
    data_parts = call.data.split(':')
    current_page = int(data_parts[1]) if len(data_parts) > 1 else 0

    # Определяем количество плейлистов на странице
    playlists_per_page = 5
    playlist_names = list(user_playlists.keys())
    total_pages = (len(playlist_names) + playlists_per_page - 1) // playlists_per_page

    # Получаем плейлисты для текущей страницы
    start_index = current_page * playlists_per_page
    end_index = start_index + playlists_per_page
    page_playlists = playlist_names[start_index:end_index]

    # Создаем кнопки для плейлистов
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in page_playlists:
        playlist_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'play_playlist:{playlist_name}')
        markup.add(playlist_button)

    # Добавляем кнопки пагинации
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

    # Добавляем кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='playlist')
    markup.add(back_button)

    # Отправляем сообщение с плейлистами
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
    Обрабатывает выбор плейлиста для прослушивания.

    Отправляет все треки из выбранного плейлиста одним сообщением.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return

    playlist_tracks = user_playlists[playlist_name]

    if not playlist_tracks:
        bot.answer_callback_query(call.id, f"❌ Плейлист '{playlist_name}' пуст.")
        return

    # Удаляем список плейлистов
    bot.delete_message(chat_id, call.message.message_id)

    # Собираем все треки из плейлиста
    media_group = []
    for track_name in playlist_tracks:
        track_id = next(
            (entry["file_id"] for entry in music_data.get(track_name, []) if entry["user_id"] == chat_id),
            None
        )
        if track_id:
            media_group.append(telebot.types.InputMediaAudio(media=track_id))

    if media_group:
        bot.send_media_group(chat_id, media_group)
    else:
        bot.send_message(chat_id, f"❌ Треки из плейлиста '{playlist_name}' не найдены в библиотеке.")

    # Добавляем кнопку "Назад"
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='view_playlists')
    markup.add(back_button)

    bot.send_message(chat_id, f"🎵 Плейлист '{playlist_name}' завершен.", reply_markup=markup)

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