import time
import schedule
from datetime import datetime
import database
import rss_parser
import content_strategist
import groq_analyzer
import telegram_bot

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEUROTRADE V2 — VIRAL CONTENT PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pipeline Flow:
#   RSS Fetch → Deduplicate → Viral Scoring → Content Generation → Telegram
#
# V2 Rules:
#   - Max 3 contents per day (hard limit via database counter)
#   - Only news with viral score >= 7 get processed
#   - If no viral news found: skip, don't force content
#   - Quality > Quantity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAX_DAILY_CONTENTS = 3
API_DELAY_SECONDS = 3  # Delay between Groq API calls to avoid rate limiting


def run_pipeline():
    """
    Core workflow for NeuroTrade V2 — Viral Content Filter Pipeline.
    
    Stages:
        1. Check daily content limit
        2. Fetch RSS news
        3. Deduplicate against database
        4. STAGE 1: Viral scoring & filtering (content_strategist)
        5. STAGE 2: Premium content generation (groq_analyzer)
        6. Push to Telegram
    """
    print(f"\n{'━'*60}")
    print(f"  🚀 NEUROTRADE V2 — VIRAL CONTENT PIPELINE")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB")
    print(f"{'━'*60}")
    
    # ━━━ STEP 0: Check daily content limit ━━━
    database.init_db()
    daily_count = database.get_daily_content_count()
    remaining = MAX_DAILY_CONTENTS - daily_count
    
    print(f"\n📊 Status Harian: {daily_count}/{MAX_DAILY_CONTENTS} konten terkirim")
    
    if remaining <= 0:
        print(f"⛔ LIMIT HARIAN TERCAPAI ({daily_count}/{MAX_DAILY_CONTENTS})")
        print(f"   Pipeline dihentikan. Lanjut besok.")
        print(f"{'━'*60}\n")
        return
    
    print(f"   Sisa slot: {remaining} konten")
    
    # ━━━ STEP 1: Fetch Latest News from RSS ━━━
    print(f"\n{'─'*40}")
    print(f"📡 STEP 1: Fetching RSS Feeds...")
    all_news = rss_parser.fetch_latest_news()
    print(f"   Diterima: {len(all_news)} berita dari RSS")
    
    if not all_news:
        print("❌ Tidak ada berita dari RSS. Pipeline dihentikan.")
        return
    
    # ━━━ STEP 2: Deduplication ━━━
    print(f"\n{'─'*40}")
    print(f"🔍 STEP 2: Deduplication...")
    new_and_unique_news = []
    for item in all_news:
        title = item['title']
        if not database.is_duplicate(title):
            new_and_unique_news.append(item)
            database.save_news(title, item['link'])
    
    print(f"   Berita unik baru: {len(new_and_unique_news)}")
    
    if not new_and_unique_news:
        print("❌ Tidak ada berita baru. Pipeline dihentikan.")
        return
    
    # ━━━ STEP 3 (STAGE 1): Viral Scoring & Filtering ━━━
    print(f"\n{'─'*40}")
    print(f"🔬 STAGE 1: Viral Scoring & Filtering...")
    print(f"   Mengevaluasi {len(new_and_unique_news)} berita...")
    
    viral_news = content_strategist.get_viral_news(new_and_unique_news)
    
    if not viral_news:
        print("\n⚠️  TIDAK ADA BERITA VIRAL KUAT HARI INI")
        print("    Semua berita tidak memenuhi standar viral score minimum (7/10).")
        print("    Pipeline dihentikan — Quality > Quantity.")
        print(f"{'━'*60}\n")
        return
    
    # Cap viral news by remaining daily slots
    if len(viral_news) > remaining:
        print(f"   ⚠️ {len(viral_news)} berita viral, tapi hanya {remaining} slot tersisa.")
        viral_news = viral_news[:remaining]
    
    # ━━━ STEP 4 (STAGE 2): Premium Content Generation ━━━
    print(f"\n{'─'*40}")
    print(f"🎬 STAGE 2: Generating {len(viral_news)} Premium Content(s)...")
    
    success_count = 0
    
    for i, news_item in enumerate(viral_news):
        headline = news_item.get('viral_headline', 'N/A')
        score = news_item.get('viral_score', '?')
        emotion = news_item.get('primary_emotion', '?')
        
        print(f"\n   {'─'*35}")
        print(f"   🎬 Content {i+1}/{len(viral_news)}")
        print(f"   📰 {headline}")
        print(f"   📊 Score: {score}/10 | Emosi: {emotion}")
        print(f"   ⏳ Generating premium content...")
        
        # Add delay between API calls to avoid rate limiting
        if i > 0:
            print(f"   ⏳ Menunggu {API_DELAY_SECONDS}s (rate limit protection)...")
            time.sleep(API_DELAY_SECONDS)
        
        # Generate full premium content
        content = groq_analyzer.generate_viral_content(news_item)
        
        if not content:
            print(f"   ❌ Gagal generate content untuk: {headline}")
            continue
        
        # ━━━ STEP 5: Push to Telegram ━━━
        print(f"   📤 Mengirim ke Telegram...")
        success = telegram_bot.send_telegram_message(content)
        
        if success:
            new_count = database.increment_daily_content_count()
            success_count += 1
            print(f"   ✅ BERHASIL! Content #{success_count} terkirim")
            print(f"   📊 Total hari ini: {new_count}/{MAX_DAILY_CONTENTS}")
        else:
            print(f"   ❌ Gagal kirim ke Telegram!")
    
    # ━━━ PIPELINE COMPLETE ━━━
    print(f"\n{'━'*60}")
    print(f"  🏁 PIPELINE SELESAI")
    print(f"  ✅ Berhasil: {success_count}/{len(viral_news)} konten terkirim")
    print(f"  📊 Total hari ini: {database.get_daily_content_count()}/{MAX_DAILY_CONTENTS}")
    print(f"{'━'*60}\n")


def check_market_hours_and_run():
    """
    Wrapper function to check if current time is within market hours 
    (Mon-Fri, 08:00 - 17:00 WIB) and run the pipeline.
    """
    now = datetime.now()
    # Monday is 0, Friday is 4
    if 0 <= now.weekday() <= 4:
        # Check if time is between 08:00 and 17:00
        if 8 <= now.hour <= 17:
            run_pipeline()
        else:
            print(f"[{now.strftime('%H:%M:%S')}] ⏰ Di luar jam pasar (08:00 - 17:00). Skip.")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] 📅 Hari libur (weekend). Skip.")


if __name__ == "__main__":
    print("━"*60)
    print("  🧠 NEUROTRADE V2 — VIRAL CONTENT AUTOMATION")
    print("  📋 Rules: Max 3 konten/hari | Score >= 7 only")
    print("  ⏰ Interval: 15 menit | Jam pasar: 08:00-17:00 WIB")
    print("━"*60)
    
    # Run once immediately on startup
    run_pipeline()
    
    # Set interval to 15 minutes
    schedule.every(15).minutes.do(check_market_hours_and_run)
    
    print("\n⏰ Scheduler aktif. Menunggu tick berikutnya...")
    while True:
        schedule.run_pending()
        time.sleep(1)
