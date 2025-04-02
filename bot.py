import telebot
import requests
from googleapiclient.discovery import build
from flask import Flask

TOKEN = "TELEGRAM_BOT_TOKEN"
YOUTUBE_API_KEY = "YOUTUBE_API_KEY"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_youtube_channels(niche, min_subs, max_subs, country):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    query = f"{niche}"
    request = youtube.search().list(q=query, type="channel", part="snippet", maxResults=50, regionCode=country)
    response = request.execute()
    
    channels = []
    for item in response["items"]:
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
            for result in results:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "No channels found.")
    except Exception as e:
        bot.send_message(message.chat.id, "Error: Invalid input format!")

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    bot.polling()
        
