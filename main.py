import telebot
import requests
from telebot import types

bot =  telebot.TeleBot('8295719402:AAGQZyp7L4SeLG-rDawVYAPKJbqBU5H2FCg')
bot.remove_webhook()


@bot.message_handler(commands=['start'])
def start_message(message):
  user_id = message.from_user.id
  pressStartButton = 'Кнопка старт'
  
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  filmSearchButton = types.KeyboardButton('ВОТ ТУТ КНОПКА ДЛЯ СТАРТА ПОИСКА')
  markup.add (filmSearchButton)
  
  bot.send_message(message.chat.id, "ВОТ ТУТ ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ БОТА ПОСЛЕ КНОПКИ СТАРТ", 
                  parse_mode='html', reply_markup=markup)
 
  
  
@bot.message_handler(content_types=['text'])
def lalala (message):
 if message.chat.type == 'private':
   if message.text == 'ВОТ ТУТ КНОПКА ДЛЯ СТАРТА ПОИСКА':
     bot.send_message(message.chat.id, 'ВОТ ТУТ ОПИСАНИЕ ЧТО МОЖНО ИСКАТЬ')
   else:
      user_id = message.from_user.id
      searchQuery = message.text
      url = f"https://sudact.ru/search/?page=1&query={query}&source=all" wp-json/wp/v2/posts?search={searchQuery}"
      responce = requests.get(url) 
      if not responce.json():
        bot.send_message(message.chat.id, 'Я ничего не нашел по вашему запросу') 
      for SearchResult in responce.json():
        title = SearchResult['title']
        completeMessage = f"{title['rendered']} {SearchResult['link']}"
        bot.send_message(message.chat.id, completeMessage)
        
          
 
bot.polling(none_stop=True)
