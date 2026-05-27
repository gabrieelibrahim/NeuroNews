import sqlite3
import hashlib
from datetime import datetime
from config import DB_FILE


def init_db():
    """Initialize the SQLite database and create all required tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Original news_feeds table for deduplication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_hash VARCHAR(64) UNIQUE,
            article_url TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # V2: Daily content counter to enforce max 3 contents/day
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_content_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_date DATE UNIQUE,
            content_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# V2: DAILY CONTENT COUNTER
# Enforces maximum 3 contents per day across all pipeline runs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_daily_content_count():
    """
    Get the number of contents generated today.
    
    Returns:
        int: Number of contents already generated today (0 if none)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_content_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_date DATE UNIQUE,
            content_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT content_count FROM daily_content_log WHERE content_date = ?', (today,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0


def increment_daily_content_count():
    """
    Increment the daily content counter by 1.
    Creates today's entry if it doesn't exist.
    
    Returns:
        int: New total content count for today after incrementing
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_content_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_date DATE UNIQUE,
            content_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO daily_content_log (content_date, content_count, last_updated) 
        VALUES (?, 1, ?)
        ON CONFLICT(content_date) DO UPDATE SET 
            content_count = content_count + 1,
            last_updated = ?
    ''', (today, now, now))
    
    conn.commit()
    
    # Return the new count
    cursor.execute('SELECT content_count FROM daily_content_log WHERE content_date = ?', (today,))
    new_count = cursor.fetchone()[0]
    conn.close()
    
    return new_count


def get_remaining_daily_slots():
    """
    Get the number of remaining content slots for today.
    Max 3 contents per day.
    
    Returns:
        int: Number of remaining slots (0-3)
    """
    MAX_DAILY = 3
    current = get_daily_content_count()
    return max(0, MAX_DAILY - current)
