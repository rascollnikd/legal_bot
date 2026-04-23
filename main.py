import telebot
import requests
from telebot import types
import time
import json

bot = telebot.TeleBot('8295719402:AAGQZyp7L4SeLG-rDawVYAPKJbqBU5H2FCg')
bot.remove_webhook()

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    filmSearchButton = types.KeyboardButton('🔍 Начать поиск')
    markup.add(filmSearchButton)
    
    bot.send_message(
        message.chat.id,
        "🏛️ *Добро пожаловать в бот поиска судебной практики!*\n\n"
        "Нажмите «Начать поиск» и введите тему.\n"
        "📎 *Примеры:* расторжение договора аренды, взыскание долга, А40-12345/2024",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def search_handler(message):
    if message.chat.type == 'private':
        if message.text == '🔍 Начать поиск':
            bot.send_message(
                message.chat.id,
                '📝 *Введите тему для поиска:*\n\n'
                'Примеры:\n'
                '- расторжение договора аренды\n'
                '- взыскание долга\n'
                '- А40-12345/2024',
                parse_mode='Markdown'
            )
        else:
            query = message.text.strip()
            if len(query) < 3:
                bot.send_message(message.chat.id, '❓ Введите минимум 3 символа для поиска')
                return
            
            msg = bot.send_message(
                message.chat.id,
                f'🔍 *Ищу:* {query}\n\n⏳ Подождите 10-20 секунд...',
                parse_mode='Markdown'
            )
            
            try:
                # Поиск на kad.arbitr.ru
                url = f"https://kad.arbitr.ru/Kad/SearchInstances?query={query}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=15)
                
                # Простой парсинг HTML
                found = False
                if 'instance-card' in response.text:
                    # Нашли карточки дел
                    bot.edit_message_text(
                        f'✅ *Найдены дела по запросу:* {query}\n\n'
                        f'🔗 Ссылка на результаты:\n'
                        f'https://kad.arbitr.ru/Kad/SearchInstances?query={query}',
                        chat_id=message.chat.id,
                        message_id=msg.message_id,
                        parse_mode='Markdown'
                    )
                    found = True
                
                if not found:
                    bot.edit_message_text(
                        f'😔 *Ничего не найдено* по запросу: {query}\n\n'
                        f'Попробуйте:\n'
                        f'- изменить формулировку\n'
                        f'- использовать номер дела\n'
                        f'- более короткие ключевые слова',
                        chat_id=message.chat.id,
                        message_id=msg.message_id,
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                bot.edit_message_text(
                    f'❌ *Ошибка:* {str(e)[:100]}\n\nПопробуйте позже',
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    parse_mode='Markdown'
                )

if __name__ == "__main__":
    print("✅ Бот запущен и готов к работе!")
    bot.polling(none_stop=True)
