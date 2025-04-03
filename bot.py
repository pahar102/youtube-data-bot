import os
import time
import telebot
from flask import Flask, request
from googleapiclient.discovery import build
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  
PORT = int(os.getenv("PORT", 10000))  # Render ke liye 10000 default port set

# API Key List
API_KEYS = [key for key in [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
    os.getenv("YOUTUBE_API_KEY_3"),
    os.getenv("YOUTUBE_API_KEY_4"),
] if key]  

if not API_KEYS:
    raise ValueError("No valid YouTube API keys found!")

api_index = 0  

def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEYS[api_index])

def switch_api_key():
    global api_index, youtube
    if api_index < len(API_KEYS) - 1:
        api_index += 1
        youtube = get_youtube_service()
        logger.info(f"Switched to API Key {api_index + 1}")
    else:
        logger.error("All API keys have exceeded quota!")
        raise Exception("Quota limit reached for all API keys")

# Initialize bot & YouTube API
bot = telebot.TeleBot(BOT_TOKEN)
youtube = get_youtube_service()
app = Flask(__name__)

@app.route("/")
def home():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return "Bot is running with webhook set!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_data().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@bot.message_handler(commands=["fetch"])
def fetch_youtube_data(message):
    global api_index
    try:
        args = message.text.split(" ", 4)
        if len(args) < 5:
            bot.reply_to(message, "Usage: /fetch <niche> <min_subs> <max_subs> <country>")
            return

        niche, min_subs, max_subs, country = args[1], int(args[2]), int(args[3]), args[4]
        channels = []
        next_page_token = None

        while len(channels) < 500:
            try:
                search_response = youtube.search().list(
                    q=niche,
                    type="channel",
                    part="snippet",
                    maxResults=10,  # Reduce API usage
                    pageToken=next_page_token
                ).execute()

                for item in search_response["items"]:
                    channel_id = item["id"]["channelId"]
                    channel_name = item["snippet"]["title"]
                    channels.append(f"{channel_name}: https://www.youtube.com/channel/{channel_id}")
                    if len(channels) >= 500:
                        break

                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
                time.sleep(2)  # Slow API usage

            except Exception as e:
                if "quotaExceeded" in str(e):
                    try:
                        switch_api_key()
                        bot.send_message(message.chat.id, f"⚠️ Quota exceeded! Switched to API Key {api_index + 1}...")
                        time.sleep(1)
                    except Exception:
                        bot.send_message(message.chat.id, "❌ All API keys exceeded quota! Try again later.")
                        return
                else:
                    bot.reply_to(message, f"Error: {str(e)}")
                    return

        batch_size = 10
        for i in range(0, len(channels), batch_size):
            bot.send_message(message.chat.id, "\n".join(channels[i:i+batch_size]))
            time.sleep(2)

        bot.send_message(message.chat.id, "✅ 500 YouTube channels sent!")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
    
