import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает! Напишите /track аренда")

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Укажите тему. Пример: /track аренда")
        return
    await update.message.reply_text(f"🔍 Ищу: {query}...")

def run_bot():
    if not TOKEN:
        print("❌ Ошибка: TELEGRAM_TOKEN не задан!")
        return
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("track", track))
    print("✅ Бот запущен!")
    bot_app.run_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=5000)
