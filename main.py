import time
import schedule
from datetime import datetime
import database
import rss_parser
import groq_analyzer
import telegram_bot

def run_pipeline():
    """Core workflow for the NeuroNews Automation pipeline."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting News Fetch Pipeline...")
    
    # 1. Initialize Database (ensures table exists)
    database.init_db()
    
    # 2. Fetch Latest News from RSS
    all_news = rss_parser.fetch_latest_news()
    print(f"Fetched {len(all_news)} news items from RSS feeds.")
    
    # 3. Deduplication via Database
    new_and_unique_news = []
    for item in all_news:
        title = item['title']
        if not database.is_duplicate(title):
            # It's unique
            new_and_unique_news.append(item)
            # Save to db to prevent future duplicates
            database.save_news(title, item['link'])
            
    print(f"Found {len(new_and_unique_news)} new unique news items.")
    
    if not new_and_unique_news:
        print("No new unique news. Stopping node pipeline.")
        return

    # 4. Core Analyzer (Groq API)
    print("Sending to Groq API for analysis...")
    analyzed_content = groq_analyzer.analyze_news(new_and_unique_news)
    
    if not analyzed_content:
        print("Error or empty response from Groq API.")
        return
        
    # 5. Telegram Push Bot Node
    print("Pushing finalized content to Telegram...")
    success = telegram_bot.send_telegram_message(analyzed_content)
    
    if success:
        print("Successfully sent content to Telegram! Pipeline finished.")
    else:
        print("Failed to send to Telegram.")

def check_market_hours_and_run():
    """
    Wrapper function to check if current time is within market hours (Mon-Fri, 08:00 - 17:00 WIB)
    and run the pipeline.
    """
    now = datetime.now()
    # Monday is 0, Friday is 4
    if 0 <= now.weekday() <= 4:
        # Check if time is between 08:00 and 17:00
        if 8 <= now.hour <= 17:
            run_pipeline()
        else:
            print(f"[{now.strftime('%H:%M:%S')}] Outside market hours (08:00 - 17:00). Skipping.")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] It's the weekend. Skipping.")

if __name__ == "__main__":
    print("Initializing NeuroNews Automation...")
    # Run once immediately on startup
    run_pipeline()
    
    # Set interval to 15 minutes
    schedule.every(15).minutes.do(check_market_hours_and_run)
    
    print("Scheduler started. Waiting for the next tick...")
    while True:
        schedule.run_pending()
        time.sleep(1)
