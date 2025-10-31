# 🤖 AI Cover Letter Generator Bot

A powerful Telegram bot that generates personalized cover letters using AI. Simply upload your resume, paste a job description, choose your preferred tone, and receive 3 unique cover letter variations instantly!

## ✨ Features

- 📄 **PDF Resume Parsing** - Extracts text from your resume PDF automatically
- 🤖 **AI-Powered Generation** - Uses Google Gemini API to create tailored cover letters
- 🎨 **Multiple Tone Options** - Choose from 6 different writing styles:
  - 🎩 Professional - Formal & corporate
  - ⚡ Concise - Brief & direct
  - 🎯 Enthusiastic - Passionate & motivated
  - 🎨 Creative - Unique & memorable
  - 💻 Technical - Skill-focused
  - 😊 Friendly - Warm & approachable
- 📝 **3 Variants** - Get 3 different cover letter versions to choose from
- 💾 **Resume Storage** - Your resume is saved for quick reuse (via Appwrite)
- 🔒 **Secure** - Environment-based configuration for all sensitive data

## 🎯 Use Cases

1. **Job Seekers** - Quickly generate customized cover letters for multiple job applications
2. **Career Switchers** - Create compelling narratives for different industries
3. **Freelancers** - Generate professional proposals for various clients
4. **Students** - Apply for internships with well-crafted cover letters
5. **HR Professionals** - Demonstrate cover letter best practices to candidates

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Python 3.11 or higher
- A Telegram account
- API Keys:
  - Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
  - Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))
  - Appwrite Instance (for resume storage)

## 🚀 Installation

### Step 1: Clone or Download the Repository

```bash
git clone <your-repository-url>
cd AICoverLatter
```

### Step 2: Create a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Telegram Bot Configuration
TELE_BOT_KEY=your_telegram_bot_token_here

# AI API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Appwrite Configuration (for resume storage)
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id_here
APPWRITE_API_KEY=your_api_key_here

# Optional: OpenRouter API (currently commented out in code)
# OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Step 5: Set Up Appwrite Database

1. Go to [Appwrite Cloud](https://cloud.appwrite.io/) or your self-hosted instance
2. Create a new project
3. Create a database named `cover_letter_db`
4. Create a collection named `resumes` with the following attributes:
   - `user_id` (String, required)
   - `resume_text` (String, required)
   - `uploaded_at` (DateTime, optional)
5. Set appropriate permissions for the collection
6. Copy your Project ID and API Key to the `.env` file

## 🎮 How to Use

### Running the Bot Locally

```bash
cd app
python main.py
```

You should see: `Starting bot polling...`

### Using the Bot in Telegram

1. **Start the bot**
   - Search for your bot on Telegram (use the username you created with BotFather)
   - Send `/start` to begin

2. **Upload your resume**
   - Send your resume as a PDF file
   - The bot will extract and save the text

3. **Send job description**
   - Paste the job description text from the job posting
   - The bot will show tone options

4. **Choose a tone**
   - Click on your preferred tone button
   - Wait for the AI to generate 3 cover letter variants

5. **Get your cover letters**
   - Receive 3 unique cover letter versions
   - Copy and customize the one you like best!

### Available Commands

- `/start` - Start the bot and see instructions
- `/help` - Display help message
- `/delete` - Delete your saved resume

## 🏗️ Project Structure

```
AICoverLatter/
├── app/
│   ├── main.py                 # Main entry point & FastAPI app
│   ├── telegram_handlers.py   # Telegram bot command handlers
│   ├── ai_backend.py           # AI generation logic (Gemini)
│   ├── pdf_parser.py           # PDF parsing utilities
│   ├── promtps.py              # AI prompt templates
│   ├── appwrite_client.py      # Database operations
│   └── config.py               # Configuration management
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel deployment config
├── .env                        # Environment variables (create this)
└── README.md                   # This file
```

## 🔧 Configuration

### Switching AI Providers

The bot currently uses **Google Gemini API**. If you want to switch to OpenRouter:

1. Uncomment the OpenRouter code in `app/ai_backend.py`
2. Add `OPENROUTER_API_KEY` to your `.env` file
3. Comment out the Gemini implementation

### Customizing Tones

Edit `app/promtps.py` to add or modify tone options and their prompts.

### Adjusting AI Parameters

In `app/ai_backend.py`, modify the `generation_config`:

```python
self.generation_config = {
    "temperature": 0.7,      # Creativity (0.0-1.0)
    "top_p": 0.95,           # Diversity
    "top_k": 40,             # Token selection
    "max_output_tokens": 8192 # Max response length
}
```

## 📦 Dependencies

- **fastapi** - Web framework for API endpoints
- **uvicorn** - ASGI server
- **python-telegram-bot** - Telegram bot framework
- **google-genai** - Google Gemini AI API
- **PyMuPDF** - PDF text extraction
- **appwrite** - Backend database service
- **python-dotenv** - Environment variable management
- **httpx** - Async HTTP client
- **pydantic** - Data validation

## 🚢 Deployment

### Deploy to Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Add environment variables in Vercel dashboard

### Deploy to Heroku

1. Create a `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Deploy to Railway

1. Connect your GitHub repository
2. Add environment variables
3. Deploy automatically

## 🐛 Troubleshooting

### Bot Token Error
```
telegram.error.InvalidToken: You must pass the token...
```
**Solution:** Check that `TELE_BOT_KEY` is properly set in your `.env` file

### PDF Parsing Error
```
Invalid PDF file: Failed to open stream
```
**Solution:** Ensure the PDF is not corrupted. Try re-saving the PDF or using a different file

### Gemini API Error
```
Error generating cover letters with Gemini
```
**Solution:** 
- Verify `GEMINI_API_KEY` is valid
- Check your API quota/limits
- Ensure you have internet connection

### Circular Import Error
**Solution:** Already fixed in the current code structure. Make sure imports don't reference each other circularly.

### Module Not Found Error
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Run the bot from the project root or use relative imports correctly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI model for text generation
- [Appwrite](https://appwrite.io/) - Backend server for data storage
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library

## 📧 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review your `.env` configuration
3. Check the console logs for specific error messages
4. Open an issue on GitHub (if repository is public)

## 🔮 Future Enhancements

- [ ] Support for DOCX resume uploads
- [ ] Multi-language support
- [ ] Cover letter templates library
- [ ] Analytics dashboard
- [ ] Email delivery of generated letters
- [ ] Browser extension integration
- [ ] Mobile app version

---

**Made with ❤️ for job seekers worldwide**

*Star ⭐ this repository if you found it helpful!*

