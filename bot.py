import os
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Environment variable fetch karo

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Please set it in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)  # Bot Initialize

# Function jo YouTube API se data fetch karega
def get_youtube_channels(niche, min_subs, max_subs, country):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={niche}&type=channel&regionCode={country}&key={YOUTUBE_API_KEY}&maxResults=50"
    response = requests.get(url).json()
    
    results = []
    for item in response.get("items", []):
        channel_id = item["id"]["channelId"]
        channel_name = item["snippet"]["title"]
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        results.append(f"{channel_name} - {channel_url}")
    
    return "\n".join(results) if results else "No channels found."

# Start command ka response
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Send command: /find niche min_subs max_subs country")

# Find command ka response
@bot.message_handler(commands=['find'])
def find_channels(message):
    try:
        _, niche, min_subs, max_subs, country = message.text.split(" ")
        result = get_youtube_channels(niche, int(min_subs), int(max_subs), country)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, "Invalid command! Use: /find niche min_subs max_subs country")

# Bot ko polling mode me start karna
bot.polling()
