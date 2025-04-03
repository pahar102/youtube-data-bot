import os
import time
import telebot
from flask import Flask, request
from googleapiclient.discovery import build

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-app-name.onrender.com/

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# YouTube API Setup
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Home route (required for Render deployment)
@app.route("/")
def home():
    return "Bot is running!"

# Telegram Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_data().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

# Set webhook manually on startup
@app.before_request
def set_webhook():
    if not bot.get_webhook_info().url:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

# Command to fetch YouTube data
@bot.message_handler(commands=["fetch"])
def fetch_youtube_data(message):
    try:
        args = message.text.split(" ", 4)
        if len(args) < 5:
            bot.reply_to(message, "Usage: /fetch <niche> <min_subs> <max_subs> <country>")
            return

        niche, min_subs, max_subs, country = args[1], int(args[2]), int(args[3]), args[4]
        channels = []
        next_page_token = None

        while len(channels) < 500:
            search_response = youtube.search().list(
                q=niche,
                type="channel",
                part="snippet",
                maxResults=50,
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

        # Send results in batches of 20 with 3-second gaps
        batch_size = 20
        for i in range(0, len(channels), batch_size):
            bot.send_message(message.chat.id, "\n".join(channels[i:i+batch_size]))
            time.sleep(3)

        bot.send_message(message.chat.id, "✅ 500 YouTube channels sent!\nThank you! 😊")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    
