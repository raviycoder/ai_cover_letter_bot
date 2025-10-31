"""
Telegram bot handlers for processing user messages and commands
"""
import httpx
import telegram
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes

from app.appwrite_client import save_resume, get_resume
from app.pdf_parser import extract_text_from_pdf, validate_pdf
from app.ai_backend import ai_backend
import os
from dotenv import load_dotenv

from app.promtps import get_tone_options

load_dotenv()
BOT_TOKEN = os.getenv("TELE_BOT_KEY")

#Conversation tones
WAITING_FOR_JD = 1
WAITING_FOR_TONE = 2

async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    await update.message.reply_text(
        "📖 **How to use this bot:**\n\n"
        "1️⃣ Upload your resume (PDF format)\n"
        "2️⃣ Send job description (paste as text)\n"
        "3️⃣ Choose tone (Professional, Creative, etc.)\n"
        "4️⃣ Get 3 unique cover letters\n\n"
        "💡 **Available tones:**\n"
        "• 🎩 Professional - Formal & corporate\n"
        "• ⚡ Concise - Brief & direct\n"
        "• 🎯 Enthusiastic - Passionate & motivated\n"
        "• 🎨 Creative - Unique & memorable\n"
        "• 💻 Technical - Skill-focused\n"
        "• 😊 Friendly - Warm & approachable\n\n"
        "Commands:\n"
        "/start - Start over\n"
        "/help - Show this message\n"
        "/delete - Delete saved resume"
    )


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await update.message.reply_text(
        "📝 How to use this bot:\n\n"
        "1. Send me your resume as a PDF file\n"
        "2. I'll extract the information and generate a cover letter\n"
        "3. You can optionally provide a job description for a tailored cover letter\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF document uploads"""
    print(f"Received document from user {update}")
    user_id = str(update.effective_user.id)
    document = update.message.document

    # Check if it's a PDF
    if not document.mime_type == "application/pdf":
        await update.message.reply_text(
            "Please send a PDF file. Other formats are not supported yet."
        )
        return

    # Check if it's too large
    if document.file_size > 10 * 1024 * 1024:  # 10 MB limit
        await update.message.reply_text(
            "❌ File too large. Max 10MB allowed."
        )
        return

    await update.message.reply_text("📄 Processing your resume... Please wait.")

    try:
        # Download the file (Temporary)
        file = await context.bot.get_file(document.file_id)
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{file.file_path}"
            )
            pdf_bytes = response.content
        # file_bytes = bytearray(pdf_bytes)

        is_valid, error_msg = validate_pdf(pdf_bytes)

        # Validate PDF
        if not is_valid:
            await update.message.reply_text(f"Invalid PDF file: {error_msg}\nPlease send a valid resume PDF.")
            return

        # Extract text from PDF
        resume_text = extract_text_from_pdf(pdf_bytes)

        if not resume_text:
            await update.message.reply_text(
                "⚠️ Could not extract much text from the PDF.\n"
                "Could not extract text from the PDF. Please make sure it's not a scanned image."
            )
            return

        # Step 3: Save only the text to database (PDF is discarded)
        save_resume(
            user_id=user_id,
            resume_text=resume_text,
            file_name=document.file_name
        )

        await update.message.reply_text(
            f"✅ Resume processed successfully!\n\n"
            f"📄 File: {document.file_name}\n"
            f"📏 Extracted: {len(resume_text)} characters\n"
            f"💾 Saved as text only (PDF discarded)\n\n"
            f"Now send me a job description to generate cover letters!"
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ An error occurred while processing your resume. Please try again."
        )
        print(f"Error processing document: {e}")

async def show_tone_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display inline keyboard for tone selection"""
    tone_options = get_tone_options()

    # Create inline keyboard with 2 options per row
    keyboard = []
    for i in range(0, len(tone_options), 2):
        row = []
        for tone in tone_options[i:i+2]:
            row.append(
                InlineKeyboardButton(
                    tone["name"],
                    callback_data=f"tone_{tone['key']}"
                )
            )
        keyboard.append(row)

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎨 **Choose your cover letter tone:**\n\n"
        "Select the style that best fits the job and your personality.\n"
        "Each tone will generate 3 unique variants.",
        reply_markup=reply_markup
    )

async def handle_text(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = str(update.effective_user.id)
    jd_text = update.message.text

    # Check if user has resume
    resume_data = get_resume(user_id)
    if not resume_data:
        await update.message.reply_text(
            "❌ Please upload your resume first!\n"
            "Use /start to begin."
        )
        return

    # Save job description in context for later use
    _context.user_data['job_description'] = jd_text
    _context.user_data['resume_data'] = resume_data

    # show tone selection buttons
    await show_tone_selection(update, _context)

async def handle_tone_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tone selection callback"""
    query = update.callback_query
    await query.answer()

    # Extract tone key from callback data
    tone_key = query.data.replace("tone_", "")

    # Get saved data
    job_description = context.user_data.get("job_description")
    resume_data = context.user_data.get("resume_data")

    if not job_description or not resume_data:
        await query.edit_message_text("❌ Session expired. Please upload resume and JD again.")
        return

    # Show generating message
    await query.edit_message_text(
        f"🤖 Generating 3 cover letters with **{tone_key}** tone...\n"
        f"This may take 15-30 seconds."
    )

    try:
        # Generate cover letters
        cover_letters = ai_backend.generate_cover_letters_with_tone(
            resume_text=resume_data['resume_text'],
            job_description=job_description,
            tone=tone_key
        )

        # Send each cover letter
        for i, letter in enumerate(cover_letters, start=1):
            await context.bot.send_message(
                chat_id= update.effective_chat.id,
                text=f"📝 **Cover Letter Variant {i}/{len(cover_letters)}**\n\n{letter}\n\n{'─' * 40}"
            )

        # Send completion message
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"✅ **Done!** Generated {len(cover_letters)} cover letters.\n\n"
                "💡 **Tips:**\n"
                "• Customize with specific company details\n"
                "• Add personal touches\n"
                "• Proofread before sending\n\n"
                "Want to try a different tone? Send the job description again!"
            )
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error generating cover letters. Please try again."
        )
        print(f"Error: {e}")


async def delete_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete user's saved resume"""
    from app.appwrite_client import delete_resume as delete_user_resume

    user_id = str(update.effective_user.id)
    success = delete_user_resume(user_id)

    if success:
        await update.message.reply_text(
            "🗑️ Your resume has been deleted.\n"
            "Upload a new one to start over."
        )
    else:
        await update.message.reply_text("ℹ️ No resume found to delete.")