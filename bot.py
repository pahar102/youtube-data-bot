import os
import telebot
import time
import requests
import sys
from flask import Flask
import threading

# Bot Token (Environment Variable se le rahe hain)
TOKEN = os.getenv("TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Send: niche, min_subs, max_subs, country\nExample: Technology, 1000, 10000, US")

def get_youtube_channels(niche, min_subs, max_subs, country):
    channels = []
    params = {
        "part": "snippet",
        "q": niche,
        "type": "channel",
        "maxResults": 50,  # Per request limit
        "regionCode": country,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            channel_id = item["id"].get("channelId")
            channel_name = item["snippet"]["title"]
            channel_link = f"https://www.youtube.com/channel/{channel_id}"

            # Fetch Subscriber Count
            subs_count = get_subscriber_count(channel_id)
            if subs_count and min_subs <= subs_count <= max_subs:
                channels.append(f"{channel_name} - {subs_count} Subs\n{channel_link}")
            
            time.sleep(1)  # API Rate Limit ko manage karne ke liye
    return channels

def get_subscriber_count(channel_id):
    """Fetch subscriber count for a given channel ID."""
    params = {
        "part": "statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_CHANNEL_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            return int(data["items"][0]["statistics"]["subscriberCount"])
    return None

@bot.message_handler(func=lambda message: True)
def fetch_youtube_data(message):
    try:
        data = message.text.split(',')
        if len(data) != 4:
            bot.send_message(message.chat.id, "Invalid format! Use: niche, min_subs, max_subs, country")
            return
        
        niche, min_subs, max_subs, country = data[0].strip(), int(data[1]), int(data[2]), data[3].strip()
        
        bot.send_message(message.chat.id, "Fetching data, please wait...")
        results = get_youtube_channels(niche, min_subs, max_subs, country)
        
        if results:
            for i in range(0, min(len(results), 500), 20):
                batch = results[i:i+20]
                result_message = "\n".join(batch)
                bot.send_message(message.chat.id, result_message)
                time.sleep(3)
        else:
            bot.send_message(message.chat.id, "No results found!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
                         
