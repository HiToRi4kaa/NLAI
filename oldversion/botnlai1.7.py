import telebot
import os
import hashlib
import json
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(уровень)s - %(сообщение)s')

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

# Глобальна переменная для хранения плейлистов
playlists = []

# Файл для хранения плейлистов
PLAYLISTS_FILE = 'playlists.json'

# Функция для загрузки плейлистов из файла
def load_playlists():
    global playlists
    try:
        with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as file:
            playlists = json.load(file)
            logging.debug("Плейлисты успешно загружены из файла.")
    except FileNotFoundError:
        playlists = []
        logging.warning("Файл playlists.json не найден. Создана пустая структура плейлистов.")
    except json.JSONDecodeError as e:
        playlists = []
        logging.error(f"Ошибка декодирования JSON: {e}. Создана пустая структура плейлистов.")

# Функция для сохранения плейлистов в файл
def save_playlists():
    """
    Сохраняет плейлисты в файл.
    """
    try:
        with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(playlists, file, ensure_ascii=False, indent=4)
        logging.debug("Плейлисты успешно сохранены в файл.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении плейлистов: {e}")

# Функция для получения плейлистов пользователя
def get_user_playlists(user_id):
    for user_data in playlists:
        if user_data["user_id"] == user_id:
            return user_data["playlists"]
    return {}

# Функция для обновления плейлистов пользователя
def update_user_playlists(user_id, updated_playlists):
    for user_data in playlists:
        if user_data["user_id"] == user_id:
            user_data["playlists"] = updated_playlists
            save_playlists()
            return
    # Если пользователь не найден, добавляем нового
    playlists.append({"user_id": user_id, "playlists": updated_playlists})
    save_playlists()

# Загружаем плейлисты при запуске
load_playlists()

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
    Обрабатывает добавление музыки из файловой системы.
    """
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🎵 Введите путь к папке с музыкой для добавления треков.")
    user_data[call.message.chat.id] = {'adding_music': True}

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('adding_music', False))
def add_music_from_folder(message):
    """
    Добавляет музыку из указанной пользователем папки.
    """
    folder_path = message.text.strip()
    chat_id = message.chat.id

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        bot.send_message(chat_id, "❌ Указанная папка не найдена. Убедитесь, что путь указан правильно.")
        return

    music_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp3', '.wav'))]
    if not music_files:
        bot.send_message(chat_id, "🎵 В указанной папке нет музыкальных файлов.")
        return

    os.makedirs('downloads', exist_okей=True)
    for music_file in music_files:
        source_path = os.path.join(folder_path, music_file)
        destination_path = os.path.join('downloads', music_file)
        if not os.path.exists(destination_path):
            os.rename(source_path, destination_path)

    bot.send_message(chat_id, "✅ Музыка успешно добавлена из указанной папки!")
    user_data[chat_id]['adding_music'] = False

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
        os.makedirs('downloads', exist_okей=True)
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


@bot.callback_query_handler(func=lambda call: call.data == 'playlist')
def handle_playlist_menu(call):
    """
    Обрабатывает выбор модуля "Плейлисты".

    Отображает меню с опциями для управления плейлистами.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id

    # Создаем меню
    markup = telebot.types.InlineKeyboardMarkup()
    view_playlists_button = telebot.types.InlineKeyboardButton("📂Просмотреть плейлисты", callback_data='view_playlists')
    create_playlist_button = telebot.types.InlineKeyboardButton("➕Создать плейлист", callback_data='create_playlist')
    edit_playlist_button = telebot.types.InlineKeyboardButton("✏️Редактировать плейлист", callback_data='edit_playlist')
    markup.row(create_playlist_button, edit_playlist_button)
    markup.row(view_playlists_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📄 <b>Меню плейлистов:</b>\n\n"
             "➕Создать плейлист – создание нового плейлиста.\n"
             "✏️Редактировать плейлист – управление треками в плейлисте.\n"
             "📂Просмотреть плейлисты – просмотр и выбор существующих плейлистов.",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'edit_playlist')
def handle_edit_playlist_menu(call):
    """
    Отображает список плейлистов для редактирования.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас пока нет плейлистов для редактирования. Создайте новый через меню плейлистов.")
        return

    # Создаем кнопки для каждого плейлиста
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in user_playlists:
        edit_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'manage_playlist:{playlist_name}')
        markup.add(edit_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="✏️ <b>Выберите плейлист для редактирования:</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'create_playlist')
def handle_create_playlist(call):
    """
    Обрабатывает создание нового плейлиста.

    Запрашивает у пользователя название нового плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📄 Введите название нового плейлиста:")

    # Устанавливаем состояние для создания плейлиста
    user_data[call.message.chat.id] = {'creating_playlist': True}

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('creating_playlist', False))
def save_playlist_name(message):
    """
    Сохраняет название нового плейлиста и добавляет его в список плейлистов пользователя.

    Args:
        message (telebot.types.Message): Сообщение от пользователя с названием плейлиста.
    """
    chat_id = message.chat.id
    playlist_name = message.text.strip()
    user_playlists = get_user_playlists(chat_id)

    if playlist_name in user_playlists:
        bot.send_message(chat_id, "❌ Плейлист с таким названием уже существует. Попробуйте другое название.")
    else:
        user_playlists[playlist_name] = []
        update_user_playlists(chat_id, user_playlists)
        logging.debug(f"Создан новый плейлист: {playlist_name} для чата {chat_id}.")
        bot.send_message(chat_id, f"✅ Плейлист '{playlist_name}' успешно создан!")

    # Сбрасываем состояние
    user_data[chat_id]['creating_playlist'] = False

@bot.callback_query_handler(func=lambda call: call.data == 'view_playlists')
def handle_view_playlists(call):
    """
    Отображает список плейлистов пользователя.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    user_playlists = get_user_playlists(chat_id)

    if not user_playlists:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📂 У вас пока нет плейлистов. Создайте новый через меню плейлистов.")
        return

    # Создаем кнопки для каждого плейлиста
    markup = telebot.types.InlineKeyboardMarkup()
    for playlist_name in user_playlists:
        playlist_button = telebot.types.InlineKeyboardButton(playlist_name, callback_data=f'open_playlist:{playlist_name}')
        markup.add(playlist_button)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📂 <b>Ваши плейлисты:</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('open_playlist:'))
def handle_open_playlist(call):
    """
    Открывает выбранный плейлист и отправляет все треки из него.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return

    if playlist_name not in user_playlists or not user_playlists[playlist_name]:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"❌ Плейлист '{playlist_name}' пуст.")
        return

    tracks = user_playlists[playlist_name]
    if not tracks:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"📂 Плейлист '{playlist_name}' пуст.")
        return

    # Отправляем все треки из плейлиста
    for track in tracks:
        track_path = os.path.join('downloads', track)
        if (os.path.exists(track_path)):
            with open(track_path, 'rb') as music_file:
                bot.send_audio(chat_id, music_file)
        else:
            bot.send_message(chat_id, f"❌ Трек '{track}' не найден в папке 'downloads'.")

    bot.answer_callback_query(call.id, f"✅ Все треки из плейлиста '{playlist_name}' отправлены.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_playlist:'))
def handle_manage_playlist(call):
    """
    Обрабатывает управление треками в плейлисте (добавление/удаление).

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    # Убедимся, что плейлист существует
    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return

    # Получаем список доступных треков
    music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
    if not music_files:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎵 Музыкальные файлы не найдены.")
        return

    # Создаем кнопки для добавления/удаления треков
    markup = telebot.types.InlineKeyboardMarkup()
    for track in music_files:
        track_id = hashlib.md5(track.encode()).hexdigest()[:10]  # Укорачиваем идентификатор
        if track in user_playlists[playlist_name]:
            button = telebot.types.InlineKeyboardButton(f"❌ Удалить {track}", callback_data=f'remove:{playlist_name}:{track_id}')
        else:
            button = telebot.types.InlineKeyboardButton(f"➕ Добавить {track}", callback_data=f'add:{playlist_name}:{track_id}')
        markup.add(button)

  # Создаем новое меню
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎵 Управление плейлистом '{playlist_name}':",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add:'))
def handle_add_track(call):
    """
    Добавляет трек в плейлист.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    _, playlist_name, track_id = call.data.split(':', 2)

    # Находим трек по его идентификатору
    music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
    track = next((f for f in music_files if hashlib.md5(f.encode()).hexdigest()[:10] == track_id), None)

    # Убедимся, что трек существует в списке файлов
    if not track:
        bot.answer_callback_query(call.id, "❌ Трек не найден.")
        return

    user_playlists = get_user_playlists(chat_id)

    # Убедимся, что доступ к плейлисту осуществляется только по его имени
    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return

    user_playlists[playlist_name].append(track)
    update_user_playlists(chat_id, user_playlists)
    bot.answer_callback_query(call.id, f"✅ Трек '{track}' добавлен в плейлист '{playlist_name}'.")
    # Создаем кнопки для управления плейлистом
    user_playlists = get_user_playlists(call.message.chat.id)
    music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
    markup = telebot.types.InlineKeyboardMarkup()
    for track in music_files:
        track_id = hashlib.md5(track.encode()).hexdigest()[:10]
        if track in user_playlists.get(playlist_name, []):
            button = telebot.types.InlineKeyboardButton(f"❌ Удалить {track}", callback_data=f'remove:{playlist_name}:{track_id}')
        else:
            button = telebot.types.InlineKeyboardButton(f"➕ Добавить {track}", callback_data=f'add:{playlist_name}:{track_id}')
        markup.add(button)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)  # Обновляем кнопки
    handle_manage_playlist(call)  # Обновляем меню после добавления трека

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove:'))
def handle_remove_track(call):
    """
    Удаляет трек из плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    _, playlist_name, track_id = call.data.split(':', 2)

    # Находим трек по его идентификатору
    music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
    track = next((f for f in music_files if hashlib.md5(f.encode()).hexdigest()[:10] == track_id), None)

    # Убедимся, что трек существует в списке файлов
    if not track:
        bot.answer_callback_query(call.id, "❌ Трек не найден.")
        return

    user_playlists = get_user_playlists(chat_id)

# Убедимся, что доступ к плейлисту осуществляется только по его имени
    if playlist_name not in user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return

    # Проверяем наличие трека в плейлисте
    if track in user_playlists.get(playlist_name, []):
        user_playlists[playlist_name].remove(track)
        update_user_playlists(chat_id, user_playlists)
        bot.answer_callback_query(call.id, f"❌ Трек '{track}' удален из плейлиста '{playlist_name}'.")
        # Создаем кнопки для управления плейлистом
        user_playlists = get_user_playlists(call.message.chat.id)
        music_files = [f for f in os.listdir('downloads') if f.endswith(('.mp3', '.wav'))]
        markup = telebot.types.InlineKeyboardMarkup()
        for track in music_files:
            track_id = hashlib.md5(track.encode()).hexdigest()[:10]
            if track in user_playlists.get(playlist_name, []):
                button = telebot.types.InlineKeyboardButton(f"❌ Удалить {track}", callback_data=f'remove:{playlist_name}:{track_id}')
            else:
                button = telebot.types.InlineKeyboardButton(f"➕ Добавить {track}", callback_data=f'add:{playlist_name}:{track_id}')
            markup.add(button)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)  # Обновляем кнопки
        handle_manage_playlist(call)  # Обновляем меню после удаления трека
    else:
        bot.answer_callback_query(call.id, "❌ Трек не найден в плейлисте.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('play_playlist:'))
def handle_play_playlist(call):
    """
    Воспроизводит все треки из выбранного плейлиста.

    Args:
        call (telebot.types.CallbackQuery): Объект с данными о нажатой кнопке.
    """
    chat_id = call.message.chat.id
    playlist_name = call.data.split(':', 1)[1]
    user_playlists = get_user_playlists(chat_id)

    # Проверяем наличие плейлиста с учетом регистра и пробелов
    normalized_playlists = {name.strip().lower(): name for name in user_playlists.keys()}
    normalized_name = playlist_name.strip().lower()

    if not user_playlists:
        bot.answer_callback_query(call.id, "❌ Плейлист не найден.")
        return
    
    # Используем оригинальное имя плейлиста
    playlist_name = normalized_playlists[normalized_name]

    if not user_playlists[playlist_name]:
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"❌ Плейлист '{playlist_name}' пуст.")
        return

    for track in user_playlists[playlist_name]:
        track_path = os.path.join('downloads', track)
        if os.path.exists(track_path):
            with open(track_path, 'rb') as music_file:
                bot.send_audio(chat_id, music_file)
        else:
            bot.send_message(chat_id, f"❌ Трек '{track}' не найден в папке 'downloads'.")

    bot.answer_callback_query(call.id, f"✅ Все треки из плейлиста '{playlist_name}' отправлены.")

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