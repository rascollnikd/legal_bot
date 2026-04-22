import logging
import os
import requests
from bs4 import BeautifulSoup
import time
import json
import asyncio
import nest_asyncio
from google import genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# === ПРИМЕНЯЕМ nest_asyncio ДЛЯ ИСПРАВЛЕНИЯ EVENT LOOP ===
nest_asyncio.apply()

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyCjdUlJI6fUJ9n8LTEdYaYq6NkWIgEqrCE")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_KEY)

class JudicialCaseSearcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def _get_ai_description(self, number, title):
        try:
            prompt = f"""
Ты юрист. Верни ТОЛЬКО JSON (без пояснений):
{{"fabula": "суть спора (до 10 слов)", "decision": "решение суда (до 8 слов)"}}

Дело: {number}
Название: {title}
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            data = json.loads(text)
            return data.get('fabula', ''), data.get('decision', '')
        except Exception as e:
            logger.error(f"Ошибка Gemini: {e}")
            return "", ""

    async def search_cases(self, query: str, limit: int = 5):
        try:
            url = f"https://kad.arbitr.ru/Kad/SearchInstances?query={query}"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for block in soup.find_all('div', class_='instance-card')[:limit]:
                number = block.find('div', class_='case-number')
                title = block.find('div', class_='case-title')
                link = block.find('a', href=True)

                case_number = number.text.strip() if number else "Номер не найден"
                case_title = title.text.strip()[:150] if title else "Название не найдено"

                if link:
                    href = link.get('href')
                    case_link = "https://kad.arbitr.ru" + href if href.startswith('/') else href
                else:
                    case_link = None

                fabula, decision = self._get_ai_description(case_number, case_title)

                results.append({
                    'number': case_number,
                    'title': case_title,
                    'link': case_link,
                    'fabula': fabula,
                    'decision': decision
                })
                time.sleep(1)

            return results
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []

case_searcher = JudicialCaseSearcher()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏛️ *Юридический охотник* 🏛️\n\n"
        "Я ищу судебную практику на сайте kad.arbitr.ru\n"
        "Добавляю описание от Gemini и ссылку на дело.\n\n"
        "🔍 *Просто напишите тему поиска:*\n"
        "Например: *расторжение договора аренды*",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Как пользоваться:*\n\n"
        "1️⃣ Напишите тему поиска\n"
        "2️⃣ Бот найдёт дела на kad.arbitr.ru\n"
        "3️⃣ Gemini добавит краткое описание\n"
        "4️⃣ Вы получите ссылку на карточку дела\n\n"
        "📎 *Примеры:* аренда, поставка, А40-12345/2024",
        parse_mode="Markdown"
    )

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    if len(query) < 3:
        await update.message.reply_text("❓ Введите минимум 3 символа для поиска")
        return

    msg = await update.message.reply_text(f"🔍 *Ищу:* {query}\n\n⏳ Подождите 10-20 секунд...", parse_mode="Markdown")

    results = await case_searcher.search_cases(query)

    if not results:
        await msg.edit_text(f"😔 *Ничего не найдено* по запросу: {query}", parse_mode="Markdown")
        return

    await msg.delete()

    for case in results:
        text = (
            f"*{case['number']}*\n"
            f"📖 {case['title']}\n"
            f"📋 *Фабула:* {case['fabula']}\n"
            f"⚖️ *Решение:* {case['decision']}\n"
        )

        keyboard = [[InlineKeyboardButton("🔗 Смотреть дело", url=case['link'])]]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        time.sleep(0.5)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    app.add_error_handler(error_handler)

    logger.info("🤖 Бот запущен...")
    print("✅ Бот запущен и готов к работе!")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
