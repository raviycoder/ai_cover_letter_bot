from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.telegram_handlers import start, help_command, handle_document, handle_text, delete_resume, handle_tone_selection, error_handler

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TELE_BOT_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("TELE_BOT_KEY environment variable is not set. Please check your .env file.")

# Create the application instance
application = Application.builder().token(BOT_TOKEN).build()

# Register handlers immediately (for both webhook and polling)
application.add_error_handler(error_handler)
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("delete", delete_resume))
application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.add_handler(CallbackQueryHandler(handle_tone_selection, pattern="^tone_"))


# NEW: Lifespan event handler (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bot lifecycle: startup and shutdown"""
    # Startup
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Bot started. Webhook set to: {WEBHOOK_URL}")

    yield  # App runs here

    # Shutdown
    await application.stop()
    await application.shutdown()
    print("🛑 Bot stopped.")


# Create FastAPI app WITH lifespan
app = FastAPI(lifespan=lifespan)


# FastAPI Health check endpoint
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()  # Initialize if not already done
    await application.process_update(update)
    return {"ok": True}


@app.get("/")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {"status": "ok", "bot": "running"}


# For local testing with polling
if __name__ == "__main__":
    print("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
