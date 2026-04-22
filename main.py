import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, LOG_LEVEL, API_BASE_URL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

class JudicialCaseSearcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    async def search_cases(self, query: str, limit: int = 10):
        try:
            results = await self._search_database(query, limit)
            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            return []

    async def _search_database(self, query: str, limit: int):
        cases_db = [
            {"id": "1", "title": "Спор о взыскании задолженности", "case_number": "А40-12345/2025", "date": "2025-12-10", "court": "Московский суд", "summary": "Иск о взыскании задолженности по договору поставки", "url": "https://sudrf.ru/1", "decision": "Удовлетворен"},
            {"id": "2", "title": "Трудовой спор", "case_number": "45-ТД/2025", "date": "2025-11-15", "court": "Арбитражный суд РФ", "summary": "Иск о восстановлении на работе", "url": "https://sudrf.ru/2", "decision": "Частично удовлетворен"},
            {"id": "3", "title": "Наследственный спор", "case_number": "2-156/2025", "date": "2025-10-20", "court": "Санкт-Петербургский суд", "summary": "Раздел наследственного имущества", "url": "https://sudrf.ru/3", "decision": "Удовлетворен"},
            {"id": "4", "title": "ДТП - взыскание убытков", "case_number": "2-234/2025", "date": "2025-09-05", "court": "Басманный суд", "summary": "Возмещение убытков от ДТП", "url": "https://sudrf.ru/4", "decision": "Удовлетворен"},
        ]
        
        filtered = [c for c in cases_db if query.lower() in c['title'].lower() or query.lower() in c['summary'].lower()]
        return filtered[:limit]

case_searcher = JudicialCaseSearcher(API_BASE_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏛️ Добро пожаловать в бот поиска судебной практики РФ!\n\nВведите тему поиска (спор, наследство, ДТП)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Введите тему поиска для поиска судебных дел")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Бот поиска судебной практики РФ v1.0")

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if len(query) < 3:
        await update.message.reply_text("Введите минимум 3 символа")
        return
    
    msg = await update.message.reply_text(f"🔍 Ищу: '{query}'...")
    results = await case_searcher.search_cases(query)
    
    if not results:
        await msg.edit_text("Ничего не найдено")
        return
    
    await msg.delete()
    for case in results:
        text = f"*{case['title']}*\nНомер: `{case['case_number']}`\nСуд: {case['court']}\nДата: {case['date']}\nРешение: {case['decision']}\n\n{case['summary']}"
        keyboard = [[InlineKeyboardButton("Полный текст", url=case['url'])]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    app.add_error_handler(error_handler)
    logger.info("🤖 Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
