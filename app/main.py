from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.telegram_handlers import start, help_command, handle_document, handle_text, delete_resume, handle_tone_selection
# Load environment variables from .env file
load_dotenv()

app = FastAPI()
BOT_TOKEN = os.getenv("TELE_BOT_KEY")
application = Application.builder().token(BOT_TOKEN).build()

def create_application():
    """Create and return a configured telegram Application (does not start it).

    Validates that TELE_BOT_KEY is set and raises a clear error if not.
    """
    if not BOT_TOKEN:
        raise ValueError("TELE_BOT_KEY environment variable is not set. Please check your .env file.")


    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("delete", delete_resume))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_tone_selection, pattern="^tone_"))

    return application


# FastAPI Health check endpoint
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    await application.process_update(Update.de_json(data, application.bot))
    return {"ok": True}


# For local testing with polling
if __name__ == "__main__":
    print("Starting bot polling...")
    app_instance = create_application()
    app_instance.run_polling(allowed_updates=Update.ALL_TYPES)