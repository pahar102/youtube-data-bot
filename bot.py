import os
import telebot
import requests
import time
from flask import Flask, request

# ✅ Bot Token Validation
TOKEN = os.getenv("TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not TOKEN:
    raise ValueError("Bot Token is missing! Set the TOKEN environment variable.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

@app.route('/')
def home():
    return "Bot is running!"

# ✅ Webhook Fix: POST aur GET methods dono allow kiye gaye hain
@app.route(f'/{TOKEN}', methods=['POST', 'GET'])
def webhook():
    if request.method == "POST":
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    return "Webhook Set!", 200  # GET request ka response

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "Send: niche, min_subs, max_subs, country\nExample: Technology, 1000, 10000, US"
    )

def get_youtube_channels(niche, min_subs, max_subs, country):
    channels = []
    params = {
        "part": "snippet",
        "q": niche,
        "type": "channel",
        "maxResults": 50,
        "regionCode": country,
        "key": YOUTUBE_API_KEY
    }

    while len(channels) < 500:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                channel_id = item["id"].get("channelId")
                channel_name = item["snippet"]["title"]
                channel_link = f"https://www.youtube.com/channel/{channel_id}"
                
                subs_count = get_subscriber_count(channel_id)
                if subs_count and min_subs <= subs_count <= max_subs:
                    channels.append(f"{channel_name} - {subs_count} Subs\n{channel_link}")
                
                if len(channels) >= 500:
                    break
            time.sleep(1)  # API rate limit avoid karne ke liye
        else:
            print("YouTube API Error:", response.text)
            break  # Agar API error de rahi hai to loop break kar do

    return channels

def get_subscriber_count(channel_id):
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
        data = [x.strip() for x in message.text.split(',')]
        if len(data) != 4:
            bot.send_message(message.chat.id, "Invalid format! Use: niche, min_subs, max_subs, country")
            return
        
        niche, min_subs, max_subs, country = data[0], int(data[1]), int(data[2]), data[3]
        
        bot.send_message(message.chat.id, "Fetching data, please wait...")
        results = get_youtube_channels(niche, min_subs, max_subs, country)
        
        if results:
            for i in range(0, min(len(results), 500), 20):
                bot.send_message(message.chat.id, "\n".join(results[i:i+20]))
                time.sleep(3)
            bot.send_message(message.chat.id, "Thank you! Data fetching complete.")
        else:
            bot.send_message(message.chat.id, "No results found!")
    except ValueError:
        bot.send_message(message.chat.id, "Error: min_subs and max_subs must be numbers!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
        
