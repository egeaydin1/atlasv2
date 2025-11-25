import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MEMORY_SERVICE_URL = os.getenv("MEMORY_SERVICE_URL", "http://memory-service.railway.internal:8000")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am Atlas, your proactive AI assistant.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    logging.info(f"Received message from {user_id}: {text}")

    try:
        # Call Memory Service
        response = requests.post(
            f"{MEMORY_SERVICE_URL}/chat",
            json={"user_id": user_id, "text": text},
            timeout=30
        )
        response.raise_for_status()
        reply_text = response.json().get("response", "Error: No response from memory service.")
        
    except Exception as e:
        logging.error(f"Error communicating with memory service: {e}")
        reply_text = "I'm having trouble accessing my memory right now. Please try again later."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set.")
        exit(1)
        
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("Telegram Bot Service Started")
    application.run_polling()
