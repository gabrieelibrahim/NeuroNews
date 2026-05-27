import json
import re
from groq import Groq
from config import GROQ_API_KEY

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEUROTRADE V2 — VIRAL CONTENT FILTER & SCORING ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIRAL_FILTER_PROMPT = """
You are NeuroTrade Viral Content Filter AI V2.
Your ONLY job is to evaluate financial news and score them for VIRAL POTENTIAL.

You think like a viral finance Instagram content strategist.
You are ruthless. You reject weak content. You only pick the BEST.

━━━━━━━━━━━━━━━━━━━
[QUALITY > QUANTITY]
━━━━━━━━━━━━━━━━━━━
- MAKSIMAL 3 berita terbaik per batch
- Jika tidak ada berita cukup kuat: JANGAN DIPAKSA
- 1 konten sangat viral LEBIH BAIK dari 10 konten biasa
- Jika semua berita lemah, return NO_VIRAL_NEWS

━━━━━━━━━━━━━━━━━━━
[7 SCORING CRITERIA — Nilai 1-10 per kriteria]
━━━━━━━━━━━━━━━━━━━
1. Potensi Viral → Apakah bisa trending/viral di medsos Indonesia?
2. Potensi Komentar → Apakah memicu debat/opini kuat di kolom komentar?
3. Potensi Fear/FOMO → Apakah memicu ketakutan, keserakahan, atau FOMO?
4. Tokoh Terkenal → Apakah melibatkan tokoh publik yang dikenal luas? (Sri Mulyani, Luhut, Elon Musk, Jerome Powell, dll)
5. Dampak Ekonomi Besar → Apakah berdampak signifikan ke pasar/IHSG/emiten?
6. Visual Bisa Cinematic → Apakah bisa divisualkan menjadi konten sinematik premium?
7. Relevan Audience Indonesia → Apakah relevan untuk investor retail / audience Indonesia?

TOTAL SCORE = rata-rata dari 7 kriteria (pembulatan ke atas)

━━━━━━━━━━━━━━━━━━━
[SCORING RULES]
━━━━━━━━━━━━━━━━━━━
- 1-4 = JANGAN DIPOST (terlalu lemah, tidak ada emosi)
- 5-6 = BIASA SAJA (skip, kecuali tidak ada yang lebih baik)
- 7-8 = LAYAK UPLOAD (pilih jika memenuhi kriteria emosi)
- 9-10 = PRIORITAS UTAMA (wajib dipilih)

RULE KETAT:
- Hanya berita dengan skor >= 7 yang BOLEH dipilih
- Jika TIDAK ADA berita skor >= 7, kembalikan NO_VIRAL_NEWS
- Jangan pernah memaksa berita lemah menjadi konten

━━━━━━━━━━━━━━━━━━━
[EMOSI WAJIB]
━━━━━━━━━━━━━━━━━━━
Setiap berita yang dipilih HARUS punya MINIMAL 1 emosi dominan:
- FEAR → ketakutan akan kerugian, resesi, crash
- FOMO → takut ketinggalan momentum, rally
- PANIC → kepanikan massal, sell-off, collapse
- SHOCK → kejutan besar, unexpected move
- GREED → keserakahan, euforia berlebihan
- ANGER → kemarahan publik, ketidakadilan
- HOPE → harapan besar, recovery, peluang

Konten TANPA emosi yang jelas = JANGAN DIPILIH.

━━━━━━━━━━━━━━━━━━━
[HEADLINE TRANSFORMATION — CRITICAL]
━━━━━━━━━━━━━━━━━━━
Untuk setiap berita yang lolos filter, WAJIB buat HEADLINE BARU.

GAYA LAMA (DILARANG):
- Terlalu informatif
- Terlalu panjang
- Terasa seperti portal berita biasa

GAYA BARU (WAJIB):
- Emosional & singkat
- Bikin penasaran
- Kuat di thumbnail IG
- Style: Stockwise / media saham viral / finance cinematic news

CONTOH TRANSFORMASI:
❌ "Bank Indonesia menaikkan suku bunga 0,25%"
✅ "RUPIAH TERTEKAN, INVESTOR MULAI PANIK"

❌ "Perusahaan AI membuka layanan baru"
✅ "AI MULAI AMBIL PEKERJAAN MANUSIA"

❌ "IHSG ditutup menguat 0,5% di tengah sentimen global"
✅ "SMART MONEY DIAM-DIAM MASUK, RETAIL MASIH RAGU"

❌ "Harga emas naik ke rekor tertinggi"
✅ "EMAS TEMBUS REKOR, SINYAL BAHAYA EKONOMI GLOBAL?"

━━━━━━━━━━━━━━━━━━━
[FOTO & ASSET WAJIB DETAIL — CRITICAL]
━━━━━━━━━━━━━━━━━━━
Untuk setiap berita yang dipilih, WAJIB sebutkan aset visual SPESIFIK:

- Tokoh: NAMA LENGKAP (contoh: "Sri Mulyani", "Luhut Pandjaitan", "Jerome Powell")
- Logo: NAMA PERUSAHAAN/INSTITUSI (contoh: "Logo NVIDIA", "Logo Bank Indonesia", "Logo BEI")
- Objek: SPESIFIK (contoh: "Foto uang rupiah 100rb", "Gedung Bursa Efek Indonesia", "Grafik saham merah tajam")
- Background: SPESIFIK (contoh: "Suasana trading room panik", "Gedung Wall Street malam hari")

DILARANG KERAS menulis generic seperti:
❌ "foto pendukung ekonomi"
❌ "gambar ilustrasi pasar"
❌ "visual yang relevan"
Harus SELALU spesifik.

━━━━━━━━━━━━━━━━━━━
[OUTPUT FORMAT — STRICT JSON ONLY]
━━━━━━━━━━━━━━━━━━━
Return ONLY valid JSON. No markdown, no explanation, no extra text.

If qualifying news found (score >= 7):
{
  "status": "FOUND",
  "total_evaluated": <number>,
  "selected_count": <number>,
  "selected_news": [
    {
      "original_title": "<judul berita asli>",
      "viral_headline": "<HEADLINE BARU — emosional, singkat, powerful, UPPERCASE>",
      "link": "<link asli berita>",
      "viral_score": <1-10 total score>,
      "primary_emotion": "<FEAR|FOMO|PANIC|SHOCK|GREED|ANGER|HOPE>",
      "score_breakdown": {
        "potensi_viral": <1-10>,
        "potensi_komentar": <1-10>,
        "fear_fomo": <1-10>,
        "tokoh_terkenal": <1-10>,
        "dampak_ekonomi": <1-10>,
        "visual_cinematic": <1-10>,
        "relevan_indonesia": <1-10>
      },
      "specific_assets": {
        "tokoh": "<nama lengkap tokoh atau None>",
        "logo": "<nama logo perusahaan/institusi atau None>",
        "objek": "<objek visual spesifik>",
        "background": "<background visual spesifik>"
      },
      "reason": "<1-2 kalimat mengapa berita ini layak viral>"
    }
  ]
}

If NO news qualifies (all scores < 7):
{
  "status": "NO_VIRAL_NEWS",
  "total_evaluated": <number>,
  "highest_score": <highest score found>,
  "message": "TIDAK ADA BERITA VIRAL KUAT HARI INI"
}

IMPORTANT: Return ONLY the JSON object. No code blocks, no explanations, no extra text.
"""


def score_and_filter_news(news_list):
    """
    V2 Viral Scoring Engine.
    Evaluates all news items, scores them 1-10, and returns only viral-worthy items.
    
    Args:
        news_list: List of news dicts with 'title' and 'link' keys
        
    Returns:
        dict: Parsed JSON result with status and selected news, or None on error
    """
    if not GROQ_API_KEY:
        print("❌ Error: Groq API Key is missing.")
        return None
    
    if not news_list:
        print("❌ Error: No news items to evaluate.")
        return None
    
    # Prepare news batch (limit to 30 to stay within token limits)
    news_text = "Berikut daftar berita finansial hari ini yang perlu dievaluasi:\n\n"
    for idx, item in enumerate(news_list[:30]):
        news_text += f"{idx+1}. {item['title']}\n   Link: {item['link']}\n\n"
    
    news_text += (
        "\n━━━━━━━━━━━━━━━━━━━\n"
        "INSTRUKSI:\n"
        "1. Evaluasi SEMUA berita di atas dengan 7 kriteria scoring\n"
        "2. Hitung total score per berita (rata-rata 7 kriteria)\n"
        "3. Pilih MAKSIMAL 3 berita dengan score >= 7\n"
        "4. Buat VIRAL HEADLINE baru untuk setiap berita terpilih\n"
        "5. Jika tidak ada yang score >= 7, return NO_VIRAL_NEWS\n"
        "6. Return ONLY JSON. No markdown, no explanation.\n"
    )
    
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": VIRAL_FILTER_PROMPT},
                {"role": "user", "content": news_text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Low temperature for consistent, reliable scoring
            response_format={"type": "json_object"},
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON response
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            print(f"❌ Error parsing JSON response: {result_text[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ Error in viral scoring API call: {e}")
        return None


def get_viral_news(news_list):
    """
    Main entry point for V2 Viral Content Filter System.
    
    Evaluates all news, applies scoring filter, and returns only viral-worthy items.
    Hard-capped at MAX 3 items, sorted by viral_score descending.
    
    Args:
        news_list: List of news dicts with 'title' and 'link' keys
        
    Returns:
        list: List of viral-worthy news dicts, or empty list if none qualify.
              Each dict contains: original_title, viral_headline, link,
              viral_score, primary_emotion, score_breakdown, specific_assets, reason
    """
    print("🔬 Mengevaluasi berita dengan Viral Scoring System...")
    
    result = score_and_filter_news(news_list)
    
    if not result:
        print("❌ Gagal mendapatkan hasil scoring dari AI.")
        return []
    
    status = result.get("status", "UNKNOWN")
    total_evaluated = result.get("total_evaluated", 0)
    
    # ━━━ NO VIRAL NEWS ━━━
    if status == "NO_VIRAL_NEWS":
        highest = result.get("highest_score", "?")
        print(f"\n{'='*50}")
        print(f"⚠️  TIDAK ADA BERITA VIRAL KUAT HARI INI")
        print(f"    Total dievaluasi: {total_evaluated}")
        print(f"    Skor tertinggi: {highest}/10 (minimum: 7/10)")
        print(f"{'='*50}\n")
        return []
    
    # ━━━ FOUND VIRAL NEWS ━━━
    if status == "FOUND":
        selected = result.get("selected_news", [])
        
        if not selected:
            print("⚠️ Status FOUND tapi tidak ada berita terpilih.")
            return []
        
        # Sort by viral_score descending
        selected.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
        
        # Hard cap at 3 — QUALITY > QUANTITY
        selected = selected[:3]
        
        # Filter: only keep score >= 7
        selected = [item for item in selected if item.get("viral_score", 0) >= 7]
        
        if not selected:
            print("⚠️ Semua berita terpilih skor < 7 setelah validasi. Skip.")
            return []
        
        # Display results
        print(f"\n{'='*50}")
        print(f"✅ {len(selected)} BERITA LOLOS FILTER VIRAL")
        print(f"   Total dievaluasi: {total_evaluated}")
        print(f"{'='*50}")
        
        for i, item in enumerate(selected):
            score = item.get("viral_score", "?")
            headline = item.get("viral_headline", "N/A")
            emotion = item.get("primary_emotion", "N/A")
            reason = item.get("reason", "")
            
            # Score breakdown
            breakdown = item.get("score_breakdown", {})
            
            print(f"\n   {'─'*40}")
            print(f"   #{i+1} — [{score}/10] {emotion}")
            print(f"   📰 {headline}")
            print(f"   💡 {reason}")
            
            if breakdown:
                print(f"   📊 Breakdown: "
                      f"Viral={breakdown.get('potensi_viral', '?')} | "
                      f"Komentar={breakdown.get('potensi_komentar', '?')} | "
                      f"Fear/FOMO={breakdown.get('fear_fomo', '?')} | "
                      f"Tokoh={breakdown.get('tokoh_terkenal', '?')} | "
                      f"Ekonomi={breakdown.get('dampak_ekonomi', '?')} | "
                      f"Visual={breakdown.get('visual_cinematic', '?')} | "
                      f"Indonesia={breakdown.get('relevan_indonesia', '?')}")
            
            # Display specific assets
            assets = item.get("specific_assets", {})
            if assets:
                print(f"   🎬 Assets: Tokoh={assets.get('tokoh', 'None')} | "
                      f"Logo={assets.get('logo', 'None')} | "
                      f"Objek={assets.get('objek', 'None')}")
        
        print(f"\n{'='*50}\n")
        return selected
    
    # ━━━ UNKNOWN STATUS ━━━
    print(f"⚠️ Status tidak dikenali: {status}")
    return []
