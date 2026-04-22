import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import aiohttp
import json
from datetime import datetime
from config import BOT_TOKEN, LOG_LEVEL, API_BASE_URL

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Класс для работы с API судебной практики
class JudicialCaseSearcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.session = None

    async def search_cases(self, query: str, limit: int = 10):
        """Поиск судебных дел по теме"""
        try:
            # Используем публичный API для поиска дел
            # Примеры: Справочник судебных решений, Kaznet.kz (для Казахстана)
            # или другие открытые источники судебной практики
            
            async with aiohttp.ClientSession() as session:
                # Пример для API судебной практики
                search_results = await self._search_database(session, query, limit)
                return search_results
        except Exception as e:
            logger.error(f"Ошибка при поиске дел: {e}")
            return []

    async def _search_database(self, session, query: str, limit: int):
        """Поиск в БД судебной практики"""
        try:
            # Здесь можно добавить интеграцию с реальным API
            # Пример структуры результатов:
            mock_results = [
                {
                    "id": "1",
                    "title": "Спор о взыскании задолженности",
                    "case_number": "12-ГП/2025",
                    "date": "2025-12-10",
                    "court": "Московский городской суд",
                    "summary": "Истец обратился в суд с иском о взыскании задолженности по договору поставки. Суд удовлетворил иск полностью.",
                    "url": "https://example.com/case/1"
                },
                {
                    "id": "2",
                    "title": "Трудовой спор",
                    "case_number": "45-ТД/2025",
                    "date": "2025-11-15",
                    "court": "Арбитражный суд РФ",
                    "summary": "Работник обратился с иском о восстановлении на работе. Суд частично удовлетворил иск.",
                    "url": "https://example.com/case/2"
                }
            ]
            # Фильтруем по запросу
            filtered = [r for r in mock_results if query.lower() in r['title'].lower()]
            return filtered[:limit]
        except Exception as e:
            logger.error(f"Ошибка при поиске в БД: {e}")
            return []

# Инициализация поискового класса
case_searcher = JudicialCaseSearcher(API_BASE_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_text = (
        "🏛️ Добро пожаловать в бот поиска судебной практики!\n\n"
        "Я помогу вам найти судебные решения по интересующей вас теме.\n\n"
        "Просто напишите тему поиска (например: 'спор о задолженности', 'трудовой спор', 'наследство')\n\n"
        "/help - справка по командам\n"
        "/about - о боте"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "📖 Справка по использованию бота:\n\n"
        "1. Введите тему поиска в сообщении\n"
        "2. Бот найдет релевантные судебные решения\n"
        "3. Для каждого дела будут показаны:\n"
        "   • Номер дела\n"
        "   • Суд\n"
        "   • Дата решения\n"
        "   • Краткая фабула\n"
        "   • Ссылка на полный текст\n\n"
        "Команды:\n"
        "/start - начало работы\n"
        "/help - эта справка\n"
        "/about - информация о боте"
    )
    await update.message.reply_text(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about"""
    about_text = (
        "ℹ️ О боте\n\n"
        "Бот поиска судебной практики v1.0\n"
        "Помогает найти судебные решения по заданной тематике\n\n"
        "Возможности:\n"
        "• Поиск по ключевым словам\n"
        "• Вывод краткой фабулы дела\n"
        "• Предоставление ссылок на полные тексты решений\n"
        "• Информация о суде и дате решения"
    )
    await update.message.reply_text(about_text)

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик поисковых запросов"""
    query = update.message.text
    
    if len(query) < 3:
        await update.message.reply_text("❌ Пожалуйста, введите более подробный запрос (минимум 3 символа)")
        return
    
    # Показываем статус поиска
    status_message = await update.message.reply_text("🔍 Ищу судебные решения по теме: '{}...".format(query))
    
    try:
        # Выполняем поиск
        results = await case_searcher.search_cases(query, limit=10)
        
        if not results:
            await status_message.edit_text(f"❌ По запросу '{query}' не найдено судебных решений")
            return
        
        # Удаляем статус-сообщение
        await status_message.delete()
        
        # Выводим результаты
        for idx, case in enumerate(results, 1):
            result_text = format_case_result(case, idx, len(results))
            
            # Создаем кнопку для перехода на полный текст
            keyboard = [[
                InlineKeyboardButton(
                    "📄 Полный текст решения",
                    url=case['url']
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                result_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            
            # Небольшая задержка между сообщениями
            if idx < len(results):
                await update.message.reply_text("━" * 40)
        
        # Итоговое сообщение
        summary = f"\n✅ Найдено {len(results)} судебных решений по теме '{query}'"
        await update.message.reply_text(summary)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        await status_message.edit_text(
            "❌ При поиске произошла ошибка. Попробуйте позже."
        )

def format_case_result(case: dict, number: int, total: int) -> str:
    """Форматирование результата поиска"""
    text = (
        f"<b>{number}. {case.get('title', 'N/A')}</b>\n\n"
        f"📋 <b>Номер дела:</b> {case.get('case_number', 'N/A')}\n"
        f"🏢 <b>Суд:</b> {case.get('court', 'N/A')}\n"
        f"📅 <b>Дата решения:</b> {case.get('date', 'N/A')}\n\n"
        f"<b>Фабула дела:</b>\n{case.get('summary', 'N/A')}"
    )
    return text

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(msg="Исключение при обработке обновления:", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )

async def main() -> None:
    """Основная функция запуска бота"""
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    
    # Обработчик текстовых сообщений (для поисковых запросов)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("🤖 Бот запущен...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
