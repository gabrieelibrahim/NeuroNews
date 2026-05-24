import sqlite3
import hashlib
from config import DB_FILE

def init_db():
    """Initialize the SQLite database and create the news_feeds table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_hash VARCHAR(64) UNIQUE,
            article_url TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_title_hash(title):
    """Generate an MD5 hash for the given title string."""
    return hashlib.md5(title.encode('utf-8')).hexdigest()

def is_duplicate(title):
    """Check if the title hash already exists in the database."""
    title_hash = get_title_hash(title)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM news_feeds WHERE title_hash = ?', (title_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_news(title, article_url):
    """Save a new news item's hash and URL to the database."""
    title_hash = get_title_hash(title)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO news_feeds (title_hash, article_url) VALUES (?, ?)', (title_hash, article_url))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # In case it was inserted concurrently or is a duplicate
        return False
    finally:
        conn.close()
