import os
import time
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
    
    channels = []
    next_page_token = None
    max_results = 500  # ✅ Maximum 500 results collect karna
    collected_results = 0
    
    while collected_results < max_results:
        request = youtube.search().list(
            q=query, type="channel", part="snippet", maxResults=50,
            regionCode=country, pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            if collected_results >= max_results:
                break  # ✅ Agar 500 channels ho gaye, to loop se bahar aa jao
            
            channel_id = item["id"]["channelId"]
            title = item["snippet"]["title"]
            url = f"https://www.youtube.com/channel/{channel_id}"

            # ✅ Subscribers count fetch karna
            channel_data = youtube.channels().list(
                id=channel_id, part="statistics"
            ).execute()

            subs = int(channel_data["items"][0]["statistics"]["subscriberCount"])

            if min_subs <= subs <= max_subs:
                channels.append(f"{title} - {url} ({subs} subscribers)")
                collected_results += 1

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # ✅ Agar next page token nahi mila, to loop break kar do
    
    return channels

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send: niche, min_subs, max_subs, country\nExample: Technology, 1000, 10000, IN")

@bot.message_handler(func=lambda message: True)
def fetch_data(message):
    try:
        parts = message.text.split(",")
        if len(parts) != 4:
            raise ValueError("Invalid input format!")
        
        niche = parts[0].strip()
        min_subs = int(parts[1].strip())
        max_subs = int(parts[2].strip())
        country = parts[3].strip().upper()

        results = get_youtube_channels(niche, min_subs, max_subs, country)
        
        if results:
            for i in range(0, len(results), 50):  # ✅ Har 50 results ek message me
                batch = results[i:i+50]
                result_message = "\n".join(batch)
                bot.send_message(message.chat.id, result_message)
                time.sleep(4)  # ✅ 4 second ka delay
        else:
            bot.send_message(message.chat.id, "No channels found.")
    except ValueError:
        bot.send_message(message.chat.id, "Error: Invalid input format!\nExample: Technology, 1000, 10000, IN")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "✅ OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://youtube-data-bot-10.onrender.com/{TOKEN}")  # ✅ Apni actual Render App URL dalni hogi
    app.run(host="0.0.0.0", port=5000)
                
