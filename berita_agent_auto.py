from datetime import datetime, timedelta
import openai
import requests
import telegram
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ========== SETUP ==========
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# ========== FUNGSI AMBIL BERITA ==========
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&category=business&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = data["articles"][:3]
    return articles

# ========== RANGKUM + TRANSLASI ==========
def summarize_and_translate(text):
    prompt = f"Ringkas berita berikut dalam 3 poin utama dan ubah ke Bahasa Indonesia agar mudah dipahami investor muda:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message['content']

# ========== KIRIM KE TELEGRAM ==========
def send_news_to_telegram():
    articles = get_news()
    for article in articles:
        title = article["title"]
        url = article["url"]
        content = article.get("content") or article.get("description") or ""
        summary = summarize_and_translate(content)

        message = f"📰 *{title}*\n{url}\n\n{summary}"
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

# ========== JADWAL ==========
schedule.every(3).hours.do(send_news_to_telegram)  # Bisa diganti sesuai kebutuhan

# ========== JALANKAN ==========
print("🤖 Bot jalan otomatis sekarang...")
while True:
    schedule.run_pending()
    time.sleep(60)
