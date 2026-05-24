import feedparser
from config import RSS_FEEDS

def fetch_latest_news():
    """
    Fetch and parse the latest news from all configured RSS feeds.
    Returns a list of dictionaries containing 'title' and 'link'.
    """
    all_news = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                news_item = {
                    'title': entry.title,
                    'link': entry.link
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")
    
    return all_news
