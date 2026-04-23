import telebot
import requests
from telebot import types

bot = telebot.TeleBot('8295719402:AAGQZyp7L4SeLG-rDawVYAPKJbqBU5H2FCg')
bot.remove_webhook()


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    pressStartButton = 'Кнопка старт'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    filmSearchButton = types.KeyboardButton('🔍 Начать поиск')
    markup.add(filmSearchButton)

    bot.send_message(message.chat.id, "🏛️ *Добро пожаловать в бот поиска судебной практики!*\n\nНажмите «Начать поиск» и введите тему (например, *расторжение договора аренды*)", 
                    parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == '🔍 Начать поиск':
            bot.send_message(message.chat.id, '📝 *Введите тему для поиска:*\n\nПримеры:\n- расторжение договора аренды\n- взыскание долга\n- А40-12345/2024', parse_mode='Markdown')
        else:
            user_id = message.from_user.id
            searchQuery = message.text
            url = f"https://kad.arbitr.ru/Kad/SearchInstances?query={searchQuery}"
            
            # Отправляем уведомление о поиске
            bot.send_message(message.chat.id, f'🔍 *Ищу:* {searchQuery}\n\n⏳ Подождите 10-20 секунд...', parse_mode='Markdown')
            
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                
                if not response.json():
                    bot.send_message(message.chat.id, '😔 *Ничего не найдено* по вашему запросу.\n\nПопробуйте изменить формулировку или использовать номер дела', parse_mode='Markdown')
                else:
                    for SearchResult in response.json():
                        title = SearchResult.get('title', {}).get('rendered', 'Без названия')
                        link = SearchResult.get('link', '#')
                        completeMessage = f"📌 *{title}*\n🔗 [Смотреть дело]({link})"
                        bot.send_message(message.chat.id, completeMessage, parse_mode='Markdown', disable_web_page_preview=False)
            except Exception as e:
                bot.send_message(message.chat.id, f'❌ *Ошибка:* {str(e)[:100]}\n\nПопробуйте позже или измените запрос', parse_mode='Markdown')


bot.polling(none_stop=True)
