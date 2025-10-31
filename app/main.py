from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.telegram_handlers import start, help_command, handle_document, handle_text, delete_resume, handle_tone_selection, error_handler
import logging
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TELE_BOT_KEY")
ENV = os.getenv("ENV", "production").lower()  # default to production if not set

# Determine webhook URL based on environment
if ENV == "development" or ENV == "dev":
    # For local development
    WEBHOOK_URL = os.getenv("LOCAL_WEBHOOK_URL", "http://localhost:8000/telegram-webhook")
    logger.info(f"🔧 Running in DEVELOPMENT mode")
else:
    # For production (Vercel, Railway, etc.)
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    logger.info(f"🚀 Running in PRODUCTION mode")

if not BOT_TOKEN:
    raise ValueError("TELE_BOT_KEY environment variable is not set. Please check your .env file.")

if not WEBHOOK_URL:
    raise ValueError(f"WEBHOOK_URL is not set for {ENV} environment. Please check your .env file.")

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

# Track initialization state
_init_lock = asyncio.Lock()
_is_initialized = False


async def ensure_application_initialized():
    """Ensure the application is initialized before processing updates"""
    global _is_initialized

    async with _init_lock:
        if not _is_initialized:
            logger.info("Initializing bot application (first request)...")
            await application.initialize()
            await application.start()

            # Set webhook if not in local mode
            if ENV != "local":
                try:
                    # Delete any existing webhook first
                    await application.bot.delete_webhook(drop_pending_updates=True)
                    logger.info("Deleted existing webhook")
                    # Set new webhook
                    webhook_info = await application.bot.set_webhook(
                        url=WEBHOOK_URL,
                        allowed_updates=["message", "callback_query"]
                    )
                    logger.info(f"✅ Bot started. Webhook set to: {WEBHOOK_URL}")
                    logger.info(f"Webhook response: {webhook_info}")
                except Exception as e:
                    logger.error(f"❌ Failed to set webhook: {e}")
                    raise
            else:
                logger.info(f"✅ Bot started in LOCAL mode (no webhook set)")

            _is_initialized = True
            logger.info("✅ Application initialized successfully")


# NEW: Lifespan event handler (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bot lifecycle: startup and shutdown"""
    # Startup - Initialize on startup if not serverless
    logger.info("Lifespan startup triggered...")
    await ensure_application_initialized()

    yield  # App runs here

    # Shutdown
    logger.info("Shutting down bot...")
    try:
        await application.stop()
        await application.shutdown()
        logger.info("🛑 Bot stopped.")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app WITH lifespan
app = FastAPI(lifespan=lifespan)


# FastAPI Health check endpoint
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    try:
        # Ensure application is initialized (important for serverless)
        await ensure_application_initialized()

        data = await request.json()
        logger.info(f"📥 Received webhook update: {data.get('update_id', 'unknown')}")
        update = Update.de_json(data, application.bot)

        # Process the update
        await application.process_update(update)
        logger.info(f"✅ Successfully processed update: {data.get('update_id', 'unknown')}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@app.get("/")
async def health_check():
    """Health check endpoint for deployment platforms"""
    try:
        # Ensure application is initialized
        await ensure_application_initialized()

        # Try to get bot info to verify connection
        bot_info = await application.bot.get_me()
        webhook_info = await application.bot.get_webhook_info()

        return {
            "status": "ok",
            "bot": "running",
            "bot_username": bot_info.username,
            "environment": ENV,
            "webhook_url": webhook_info.url,
            "pending_update_count": webhook_info.pending_update_count,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "initialized": _is_initialized
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "bot": "error",
            "environment": ENV,
            "error": str(e),
            "initialized": _is_initialized
        }


# For local testing with polling
if __name__ == "__main__":
    logger.info("Starting bot in polling mode (local testing)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
