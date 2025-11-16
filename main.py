import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# КОНФИГУРАЦИЯ
BOT_TOKEN = "8546542607:AAHtrKbRjGA_W-sgSKLZp7XEHDcHT79zKuw"  # Замените на токен вашего бота
MUSIC_DB_FILE = "music_database.json"
FORTE_CARD = "5177 9200 1180 9782"

# Работа с JSON базой данных
def load_music_db():
    """Загрузка базы данных музыки из JSON"""
    if os.path.exists(MUSIC_DB_FILE):
        with open(MUSIC_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Создаем пустую базу данных
        default_db = {
            "music": []
        }
        save_music_db(default_db)
        return default_db

def save_music_db(data):
    """Сохранение базы данных в JSON"""
    with open(MUSIC_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_music_to_db(music_id, channel_link, author, title):
    """Добавление музыки в базу данных"""
    db = load_music_db()
    
    # Проверка, существует ли уже такой ID
    for music in db['music']:
        if music['id'] == music_id:
            return False, "Музыка с таким ID уже существует"
    
    new_music = {
        "id": music_id,
        "channel_link": channel_link,
        "author": author,
        "title": title
    }
    
    db['music'].append(new_music)
    save_music_db(db)
    return True, "Музыка успешно добавлена"

def find_music_by_id(music_id):
    """Поиск музыки по ID"""
    db = load_music_db()
    for music in db['music']:
        if music['id'] == music_id:
            return music
    return None

def get_all_music():
    """Получить всю музыку из базы"""
    db = load_music_db()
    return db['music']

def extract_message_id_from_link(link):
    """Извлечение ID сообщения из ссылки канала"""
    # Пример: https://t.me/SuduanMusic/3 -> 3
    try:
        return int(link.split('/')[-1])
    except:
        return None

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("🎵 Найти музыку по ID", callback_data='search_music')],
        [InlineKeyboardButton("📋 Показать все треки", callback_data='show_all')],
        [InlineKeyboardButton("💳 Поддержать донатом", callback_data='donate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

🎵 **Музыкальный бот**

**Как использовать:**
1. Нажмите "Найти музыку по ID"
2. Отправьте ID музыки (например: 244)
3. Получите трек из канала!

📊 В базе данных: {len(get_all_music())} треков
"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'search_music':
        await query.message.reply_text(
            "🎵 Отправьте ID музыки\n\n"
            "Например: 244"
        )
    
    elif query.data == 'show_all':
        all_music = get_all_music()
        
        if not all_music:
            await query.message.reply_text("❌ База данных пуста")
            return
        
        # Формируем список всех треков
        music_list = "📋 **Все треки в базе:**\n\n"
        for music in all_music[:20]:  # Показываем первые 20
            music_list += f"🆔 ID: {music['id']}\n"
            music_list += f"👤 {music['author']}\n"
            music_list += f"🎵 {music['title']}\n"
            music_list += "─────────────\n"
        
        if len(all_music) > 20:
            music_list += f"\n... и еще {len(all_music) - 20} треков"
        
        await query.message.reply_text(music_list, parse_mode='Markdown')
    
    elif query.data == 'donate':
        donate_text = f"""
💳 **Поддержать проект**

Спасибо, что пользуетесь нашим ботом! 🎵

Вы можете поддержать разработку донатом:

💳 **Forte Bank**
`{FORTE_CARD}`

_Нажмите на номер карты, чтобы скопировать_

🙏 Любая сумма будет очень полезна для развития бота!

Спасибо за вашу поддержку! ❤️
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(donate_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("🎵 Найти музыку по ID", callback_data='search_music')],
            [InlineKeyboardButton("📋 Показать все треки", callback_data='show_all')],
            [InlineKeyboardButton("💳 Поддержать донатом", callback_data='donate')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "🏠 **Главное меню**\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    
    # Проверка, что это число (ID музыки)
    if message_text.isdigit():
        music_id = int(message_text)
        await search_and_send_music(update, context, music_id)
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте корректный ID музыки (число)\n\n"
            "Например: 244"
        )

async def search_and_send_music(update: Update, context: ContextTypes.DEFAULT_TYPE, music_id: int):
    """Поиск и отправка музыки пользователю"""
    
    # Ищем музыку в базе данных
    music = find_music_by_id(music_id)
    
    if not music:
        keyboard = [[InlineKeyboardButton("📋 Показать все треки", callback_data='show_all')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ Музыка с ID {music_id} не найдена в базе данных",
            reply_markup=reply_markup
        )
        return
    
    # Отправляем информацию о треке
    music_info = f"""
🎵 **Трек найден!**

🆔 ID: {music['id']}
👤 Исполнитель: {music['author']}
📀 Название: {music['title']}
🔗 Данная музыка не хранится на наших серверах. Это музыка идет через API SoundClub, VK, BuddyMusic, и т.д

⏳ Отправляю музыку...
"""
    
    await update.message.reply_text(music_info, parse_mode='Markdown')
    
    # Извлекаем ID сообщения из ссылки
    message_id = extract_message_id_from_link(music['channel_link'])
    
    if message_id:
        # Извлекаем название канала из ссылки (например: @SuduanMusic)
        try:
            channel_username = music['channel_link'].split('/')[-2]
            if not channel_username.startswith('@'):
                channel_username = f"@{channel_username}"
            
            # Пересылаем музыку из канала пользователю
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=channel_username,
                message_id=message_id
            )
            
            logger.info(f"Музыка ID {music_id} успешно отправлена пользователю {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Ошибка при пересылке музыки: {e}")
            await update.message.reply_text(
                "❌ Ошибка при получении музыки из канала\n\n"
                "Возможные причины:\n"
                "• Бот не имеет доступа к каналу\n"
                "• Неверная ссылка на сообщение\n"
                "• Сообщение было удалено"
            )
    else:
        await update.message.reply_text("❌ Некорректная ссылка на музыку в базе данных")

# Команда для администратора (добавление музыки)
async def add_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для добавления музыки в базу данных
    Формат: /add 244 https://t.me/SuduanMusic/3 "Исполнитель" "Название трека"
    """
    
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(
            "❌ Неверный формат команды\n\n"
            "Используйте:\n"
            "/add ID ССЫЛКА ИСПОЛНИТЕЛЬ НАЗВАНИЕ\n\n"
            "Пример:\n"
            "/add 244 https://t.me/SuduanMusic/3 \"Артист\" \"Название песни\""
        )
        return
    
    try:
        music_id = int(context.args[0])
        channel_link = context.args[1]
        
        # Объединяем оставшиеся аргументы для автора и названия
        remaining_text = ' '.join(context.args[2:])
        
        # Простой парсинг (можно улучшить)
        parts = remaining_text.split('"')
        author = parts[1] if len(parts) > 1 else "Неизвестный исполнитель"
        title = parts[3] if len(parts) > 3 else "Без названия"
        
        success, message = add_music_to_db(music_id, channel_link, author, title)
        
        if success:
            await update.message.reply_text(
                f"✅ {message}\n\n"
                f"🆔 ID: {music_id}\n"
                f"👤 Исполнитель: {author}\n"
                f"🎵 Название: {title}\n"
                f"🔗 Ссылка: {channel_link}"
            )
        else:
            await update.message.reply_text(f"❌ {message}")
            
    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def show_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать содержимое базы данных (для админа)"""
    all_music = get_all_music()
    
    if not all_music:
        await update.message.reply_text("📋 База данных пуста")
        return
    
    db_text = f"📊 **База данных ({len(all_music)} треков):**\n\n"
    
    for music in all_music:
        db_text += f"🆔 ID: {music['id']}\n"
        db_text += f"👤 {music['author']}\n"
        db_text += f"🎵 {music['title']}\n"
        db_text += f"🔗 {music['channel_link']}\n"
        db_text += "─────────────\n"
    
    # Telegram имеет ограничение на длину сообщения (4096 символов)
    if len(db_text) > 4000:
        # Отправляем по частям
        for i in range(0, len(db_text), 4000):
            await update.message.reply_text(db_text[i:i+4000], parse_mode='Markdown')
    else:
        await update.message.reply_text(db_text, parse_mode='Markdown')

def main():
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_music))
    application.add_handler(CommandHandler("db", show_db))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()