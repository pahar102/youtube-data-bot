import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send niche, subscriber range and country (e.g., tech, 5K-50K, US)")

# Function to get YouTube channels
def get_youtube_channels(niche, min_subs, max_subs, country):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={niche}&regionCode={country}&maxResults=50&key={YOUTUBE_API_KEY}"
    response = requests.get(url).json()
    channels = []
    
    for item in response.get("items", []):
        channel_id = item["id"]["channelId"]
        channel_title = item["snippet"]["title"]
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        
        # Get subscriber count
        stats_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
        stats_response = requests.get(stats_url).json()
        subscriber_count = int(stats_response["items"][0]["statistics"]["subscriberCount"])
        
        if min_subs <= subscriber_count <= max_subs:
            channels.append(f"{channel_title} - {channel_url} ({subscriber_count} subs)")
        
        if len(channels) >= 500:
            break
    
    return channels

def handle_message(update: Update, context: CallbackContext):
    try:
        text = update.message.text
        niche, subs_range, country = text.split(",")
        min_subs, max_subs = [int(s.replace("K", "000")) for s in subs_range.strip().split("-")]
        
        channels = get_youtube_channels(niche.strip(), min_subs, max_subs, country.strip().upper())
        
        if channels:
            update.message.reply_text("\n".join(channels[:10]))  # Send first 10 results to avoid Telegram limit
        else:
            update.message.reply_text("No channels found.")
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

# Main Function
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
      
