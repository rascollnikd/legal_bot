import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from multi_searcher import MultiCourtSearcher

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚖️ *Юридический охотник* ⚖️\n\n"
        "Напишите /track [тема] для поиска судебной практики\n"
        "Пример: `/track расторжение договора аренды`",
        parse_mode="Markdown"
    )

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❓ Укажите тему. Пример: `/track аренда`", parse_mode="Markdown")
        return
    
    await update.message.reply_text(f"🔍 *Ищу:* {query}\n\nЭто может занять 20-30 секунд...", parse_mode="Markdown")
    
    searcher = MultiCourtSearcher()
    results = searcher.search_all(query)
    
    if not results:
        await update.message.reply_text(f"😔 *Ничего не найдено* по запросу: {query}", parse_mode="Markdown")
        return
    
    message = f"✅ *Найдено {len(results)} дел:*\n\n"
    for i, case in enumerate(results[:5], 1):
        message += f"*{i}. {case['number']}*\n"
        message += f"📖 {case['title'][:100]}\n"
        if case.get('fabula'):
            message += f"📋 {case['fabula']}\n"
        if case.get('decision'):
            message += f"⚖️ {case['decision']}\n"
        message += f"🔗 [Смотреть дело]({case['link']})\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)

def main():
    if not TOKEN:
        print("❌ Ошибка: TELEGRAM_TOKEN не задан!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("track", track))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
