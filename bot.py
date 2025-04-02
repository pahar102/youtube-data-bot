import os
import telebot
import requests
from googleapiclient.discovery import build
from flask import Flask, request

# ✅ Environment variables se tokens fetch karna
TOKEN = os.getenv("TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not TOKEN:
    raise ValueError("❌ ERROR: TELEGRAM BOT TOKEN NOT FOUND!")

if not YOUTUBE_API_KEY:
    raise ValueError("❌ ERROR: YOUTUBE API KEY NOT FOUND!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_youtube_channels(niche, min_subs, max_subs, country):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    query = f"{niche}"
    request = youtube.search().list(
        q=query, type="channel", part="snippet", maxResults=50, regionCode=country
    )
    response = request.execute()
    
    channels = []
    for item in response.get("items", []):
        channel_id = item["id"]["channelId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/channel/{channel_id}"
        channels.append(f"{title} - {url}")
    
    return channels[:500]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send: niche, min_subs, max_subs, country")

@bot.message_handler(func=lambda message: True)
def fetch_data(message):
    try:
        niche, min_subs, max_subs, country = message.text.split(",")
        min_subs, max_subs = int(min_subs), int(max_subs)
        results = get_youtube_channels(niche.strip(), min_subs, max_subs, country.strip())
        
        if results:
            for result in results[:10]:  # Limiting to 10 messages to avoid spam
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "No channels found.")
    except Exception as e:
        bot.send_message(message.chat.id, "Error: Invalid input format!")

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is running!"

# ✅ Webhook Setup
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "✅ OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-render-app-url/{TOKEN}")  # ⚠️ Apni Render App URL dalna!
    app.run(host="0.0.0.0", port=5000)
    
