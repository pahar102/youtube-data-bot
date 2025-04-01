import logging
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configure the logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys
TELEGRAM_API_KEY = 'YOUR_TELEGRAM_BOT_API_KEY'
YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'

# Setup the YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Type /search followed by your parameters: niche, subscribe range, country.")

def search(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 3:
        update.message.reply_text("Please provide niche, subscribe range (min-max), and country.")
        return

    niche, subscribe_range, country = args[0], args[1], args[2]
    min_subs, max_subs = map(int, subscribe_range.split('-'))

    search_result = youtube.search().list(
        q=niche,
        type="channel",
        part="snippet",
        maxResults=50
    ).execute()

    channels = []
    for item in search_result.get("items", []):
        channel_id = item['snippet']['channelId']
        channel_info = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()
        stats = channel_info['items'][0]['statistics']
        subscribers = int(stats.get("subscriberCount", 0))
        
        if min_subs <= subscribers <= max_subs:
            channels.append({
                'title': item['snippet']['title'],
                'channelId': channel_id,
                'subscribers': subscribers,
                'country': item['snippet'].get('country', 'N/A')
            })

    # Send the first 500 channels
    for channel in channels[:500]:
        update.message.reply_text(f"Channel: {channel['title']}\nSubscribers: {channel['subscribers']}\nCountry: {channel['country']}\nhttps://www.youtube.com/channel/{channel['channelId']}")

def main():
    # Set up the Updater with your bot's token
    updater = Updater(TELEGRAM_API_KEY)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add handlers for commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
