import os
import time
from groq import Groq
from config import GROQ_API_KEY

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEUROTRADE V2 — CINEMATIC VISUAL ENGINE + CONTENT GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYSTEM_PROMPT_V2 = """
You are NeuroTrade Cinematic Visual Engine V2 — Premium Finance Content Generator.

You will receive a SINGLE pre-selected viral news item that has already passed the Viral Scoring Filter.
The item includes: original title, viral headline, link, viral score, primary emotion, and specific assets needed.

Your job: Generate PREMIUM cinematic content ready for Instagram posting.

=====================================================================
🚨 CORE MISSION — PREMIUM VIRAL FINANCE CONTENT
=====================================================================
Target output must feel like:
- Media finansial premium (Bloomberg, Financial Times editorial)
- Konten saham viral (Stockwise-style)
- Instagram news modern
- BUKAN portal berita biasa

Goals:
- Stop scrolling (thumb-stopping content)
- Meningkatkan share, save, komentar, engagement

=====================================================================
🚨 VISUAL ENGINE RULES — NO TYPOGRAPHY IN IMAGES
=====================================================================
1. Generate CINEMATIC BACKGROUND SCENES only.
2. DILARANG KERAS: teks, tipografi, huruf, judul, logo tertulis, watermark, kata-kata poster, infografis dalam image prompt.
3. Image prompt HANYA berisi: latar belakang sinematik, objek fisik, lingkungan, atmosfer, pencahayaan, komposisi, subjek manusia opsional, logo/produk fisik opsional.

=====================================================================
🎨 BRAND AESTHETIC — TERRACOTTA ORANGE PREMIUM
=====================================================================
Warna identitas utama:
- Terracotta Orange (#E8714A / #D97756) — warna aksen utama yang hangat
- Warm Cream / Elegant Off-White (#FBF9F6 / #F9F6F0) — background terang premium
- Deep Charcoal / Soft Black (#191919 / #1A1A2E) — background gelap mewah
- Subtle red/orange glow, cinematic volumetric lighting
- Soft organic lighting, elegant contrast, high-end editorial aesthetics

HINDARI: Neon cyberpunk ramai, warna pelangi, biru trading screen generik, visual kripto generik.

=====================================================================
🎬 VISUAL STYLE ROTATION SYSTEM
=====================================================================
NEVER use the same visual concept repeatedly. Rotate between:
- Bloomberg Editorial
- Luxury Finance
- Dark Corporate
- Macro Economic Thriller
- Documentary Realism
- Moody Magazine Cover
- Institutional Trading Atmosphere
- Geopolitical Cinema
- Minimal Luxury
- Financial Dystopian
- Neo Finance Architecture
- High-End Technology Campaign

=====================================================================
📸 COMPOSITION & CAMERA RULES
=====================================================================
Always specify:
- Camera angle (low-angle, top-down, eye-level, dutch angle)
- Lens type (35mm wide, 50mm standard, 85mm portrait, 135mm telephoto)
- Depth of field (shallow with bokeh, deep focus)
- Volumetric lighting
- Realistic reflections and dramatic shadows

Human subjects: Use silhouettes, back views, shadows, anonymous figures.
AVOID generic portraits or "smiling person pointing at screen".

=====================================================================
🎭 VISUAL METAPHOR ENGINE
=====================================================================
Use powerful visual metaphors:
- Market crash: cracked glass walls, collapsing holograms, shattered bull statues
- AI economy: floating neural structures, glowing algorithm cores
- Foreign outflow: energy streams leaving a city, fading liquidity trails
- Inflation: liquid hot gold, burning currency atmosphere
- Economic tension: foggy dark skyscrapers, massive financial monoliths
- Panic selling: empty trading floors, scattered papers, red warning lights
- Rally/euphoria: golden light breaking through clouds, ascending structures

=====================================================================
📋 OUTPUT FORMAT (WAJIB DITERAPKAN UTUH)
=====================================================================

🚨 [NEUROTRADE V2 — VIRAL CONTENT]
━━━━━━━━━━━━━━━━━━━
📊 VIRAL SCORE: [X/10]
🎯 PRIMARY EMOTION: [FEAR/FOMO/PANIC/SHOCK/GREED/ANGER/HOPE]
📌 HEADLINE: [Viral headline — emosional, singkat, UPPERCASE, powerful]
🔗 SUMBER: [Link berita asli]

━━━━━━━━━━━━━━━━━━━
[CONTENT ANALYSIS]
━━━━━━━━━━━━━━━━━━━
- Emotional Tone: [Nada emosi spesifik, bukan generic]
- Investor Psychology: [Kondisi psikologis investor saat ini]
- Hidden Narrative: [Narasi tersembunyi di balik berita]
- Market Impact: [Dampak spesifik ke IHSG / kode emiten / sektor]
- Why This Is Viral: [1-2 kalimat tajam]

━━━━━━━━━━━━━━━━━━━
[VIRAL HOOK OPTIONS]
━━━━━━━━━━━━━━━━━━━
Exactly 3 hooks. Each must be:
- Singkat (max 10 kata)
- Emosional & strong
- Curiosity-driven
- Social media optimized

1. [Hook 1 — main angle]
2. [Hook 2 — alternative angle]
3. [Hook 3 — contrarian/shocking angle]

━━━━━━━━━━━━━━━━━━━
[VISUAL CONCEPT]
━━━━━━━━━━━━━━━━━━━
- Dominant Visual Style: [Choose 1 from Visual Style Rotation System]
- Visual Metaphor: [Metafora visual yang kuat untuk berita ini]
- Scene Description: [Deskripsi detail scene utama]
- Emotional Atmosphere: [Mood dan feeling keseluruhan]
- Cinematic Direction: [Camera angle, lens, depth of field]
- Color Mood: [Dominan warna & aksen Terracotta Orange]

━━━━━━━━━━━━━━━━━━━
[IMAGE PROMPT]
━━━━━━━━━━━━━━━━━━━
[WRITE IN ENGLISH ONLY. Minimum 100 words. Ultra-detailed AI image generation prompt.

MUST include ALL of these elements:
- Main object/subject: [what is the focal point]
- Background/environment: [detailed setting description]
- Lighting: [type, direction, intensity, color temperature]
- Dominant colors: [Terracotta Orange #E8714A accents + complementary palette]
- Mood/atmosphere: [emotional feeling]
- Camera angle: [specific angle and lens]
- Visual effects: [depth of field, volumetric light, reflections, particles]
- Aspect ratio: 4:5 portrait (Instagram optimized)

Style keywords: ultra detailed, cinematic, hyper realistic, premium economy news, 
instagram feed style, dramatic lighting, editorial photography, 8K quality.

NO TEXT, NO TYPOGRAPHY, NO WATERMARKS in the image.
Optimized for Midjourney/Flux/DALL-E.]

━━━━━━━━━━━━━━━━━━━
[SPECIFIC ASSETS NEEDED]
━━━━━━━━━━━━━━━━━━━
WAJIB spesifik — DILARANG generic.

- Need Face: [NAMA LENGKAP tokoh + ekspresi wajah + outfit. Contoh: "Sri Mulyani — ekspresi serius, blazer hitam formal". Jika tidak ada tokoh, tulis "None — alasan: berita tidak terkait tokoh spesifik"]
- Need Logo: [NAMA LENGKAP perusahaan/institusi. Contoh: "Logo Bank Indonesia", "Logo NVIDIA". Jika tidak perlu, tulis "None — alasan: ..."]
- Need Object: [OBJEK SPESIFIK. Contoh: "Bundel uang rupiah Rp100.000", "Grafik candlestick IHSG merah tajam", "Batangan emas 1kg". BUKAN "foto pendukung ekonomi"]
- Need Background: [BACKGROUND SPESIFIK. Contoh: "Gedung Bursa Efek Indonesia tampak depan malam hari", "Trading room Wall Street dengan layar merah". BUKAN "background yang relevan"]

━━━━━━━━━━━━━━━━━━━
✍️ CAPTION INSTAGRAM (Siap Copy-Paste)
━━━━━━━━━━━━━━━━━━━
[BAHASA INDONESIA. Maksimal 120 kata. 

WAJIB:
- Emosional dan tajam, BUKAN informatif seperti portal berita
- Sebutkan nama emiten, ticker saham, angka persentase JIKA ADA di berita asli
- HANYA gunakan fakta dari berita — DILARANG data fiktif
- Amplify emosi utama (FEAR/FOMO/PANIC/SHOCK/GREED/ANGER/HOPE)

STRUKTUR:
Paragraf 1: Hook emosional + isu utama + dampak ke portofolio/pasar
Paragraf 2: Konteks singkat / edukasi mengapa ini penting / apa yang harus diwaspadai

🤖 NEUROTRADE INSIGHT:
[Soft selling halus — hubungkan insight berita dengan kemampuan bot NeuroTrade mendeteksi volume spike, breakout, akumulasi bandar. Gunakan contoh konkret dari berita.]

🔗 Cek link di bio untuk akses NeuroTrade Premium!

#SahamIndonesia #IHSG #NeuroTrade #Bandarmologi #[2 hashtag relevan dengan emiten/topik]]

━━━━━━━━━━━━━━━━━━━
[QUALITY GATE — SELF CHECK BEFORE OUTPUT]
━━━━━━━━━━━━━━━━━━━
Before finalizing, verify ALL:
✅ Headline emosional & singkat (BUKAN gaya portal berita)
✅ Image prompt 100+ kata, ultra detailed, ENGLISH, NO TEXT in image
✅ Assets SPESIFIK (nama tokoh, logo perusahaan, objek detail)
✅ Caption < 120 kata, bahasa Indonesia, emosional
✅ Primary emotion jelas terasa di SEMUA elemen
✅ Konten terasa PREMIUM FINANCE INSTAGRAM, bukan berita biasa
✅ Tidak ada data fiktif / made-up statistics
✅ Visual concept tidak repetitif (gunakan Style Rotation)

Jika ada yang tidak terpenuhi, PERBAIKI sebelum output.
"""


def generate_viral_content(viral_news_item):
    """
    V2 Content Generator: Generate premium cinematic content for a single viral news item.
    
    Takes a pre-filtered viral news item (from content_strategist) and generates
    full premium Instagram-ready content with cinematic visuals.
    
    Args:
        viral_news_item: Dict from content_strategist containing:
            - original_title (str)
            - viral_headline (str)
            - link (str)
            - viral_score (int)
            - primary_emotion (str)
            - score_breakdown (dict)
            - specific_assets (dict)
            - reason (str)
            
    Returns:
        str: Full formatted premium content, or None on error
    """
    if not GROQ_API_KEY:
        print("❌ Error: Groq API Key is missing.")
        return None
    
    if not viral_news_item:
        print("❌ Error: No viral news item provided.")
        return None
    
    # Build detailed prompt for this specific news item
    user_prompt = f"""
━━━━━━━━━━━━━━━━━━━
BERITA VIRAL TERPILIH (sudah lolos filter scoring)
━━━━━━━━━━━━━━━━━━━

📰 Judul Asli: {viral_news_item.get('original_title', 'N/A')}
📌 Viral Headline: {viral_news_item.get('viral_headline', 'N/A')}
🔗 Link: {viral_news_item.get('link', 'N/A')}
📊 Viral Score: {viral_news_item.get('viral_score', 'N/A')}/10
🎯 Primary Emotion: {viral_news_item.get('primary_emotion', 'N/A')}
💡 Alasan Viral: {viral_news_item.get('reason', 'N/A')}
"""

    # Add score breakdown if available
    breakdown = viral_news_item.get('score_breakdown', {})
    if breakdown:
        user_prompt += f"""
📊 Score Breakdown:
   - Potensi Viral: {breakdown.get('potensi_viral', '?')}/10
   - Potensi Komentar: {breakdown.get('potensi_komentar', '?')}/10
   - Fear/FOMO: {breakdown.get('fear_fomo', '?')}/10
   - Tokoh Terkenal: {breakdown.get('tokoh_terkenal', '?')}/10
   - Dampak Ekonomi: {breakdown.get('dampak_ekonomi', '?')}/10
   - Visual Cinematic: {breakdown.get('visual_cinematic', '?')}/10
   - Relevan Indonesia: {breakdown.get('relevan_indonesia', '?')}/10
"""

    # Add specific assets if available
    assets = viral_news_item.get('specific_assets', {})
    if assets:
        user_prompt += f"""
🎬 Assets yang Dibutuhkan:
   - Tokoh: {assets.get('tokoh', 'None')}
   - Logo: {assets.get('logo', 'None')}
   - Objek: {assets.get('objek', 'None')}
   - Background: {assets.get('background', 'None')}
"""

    user_prompt += """
━━━━━━━━━━━━━━━━━━━
INSTRUKSI:
Generate FULL premium content sesuai format yang ditentukan.
Pastikan semua section terisi lengkap.
Amplify emosi utama di setiap elemen.
Image prompt harus ENGLISH, 100+ kata, ultra detailed.
━━━━━━━━━━━━━━━━━━━
"""
    
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_V2
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,  # Balanced: creative but controlled
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating content via Groq API: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LEGACY FUNCTION (backward compatibility)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_news(news_list):
    """
    [DEPRECATED — V1 Legacy]
    Use generate_viral_content() with content_strategist pipeline instead.
    Kept for backward compatibility.
    """
    print("⚠️ WARNING: analyze_news() is deprecated. Use V2 pipeline (content_strategist → generate_viral_content).")
    
    if not GROQ_API_KEY:
        print("Error: Groq API Key is missing.")
        return None
        
    if not news_list:
        return None
        
    news_text_batch = "Daftar berita terbaru:\n"
    for idx, item in enumerate(news_list[:30]):
        news_text_batch += f"{idx+1}. Judul: {item['title']} - Link: {item['link']}\n"
        
    news_text_batch += "\nPilih 1 berita terbaik dari daftar di atas yang paling berpotensi viral hari ini dan buatkan format konten sesuai instruksi."

    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_V2
                },
                {
                    "role": "user",
                    "content": news_text_batch
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with Groq API: {e}")
        return None
