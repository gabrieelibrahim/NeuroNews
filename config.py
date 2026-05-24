import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Groq API Key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# RSS Feed URLs
RSS_FEEDS = [
    'https://www.cnbcindonesia.com/market/rss',
    'https://investasi.kontan.co.id/rss',
    'https://www.bloombergtechnoz.com/rss'
]

# Database File
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'news_feeds.db')
