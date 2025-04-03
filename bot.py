import telebot
import time
import requests

# Bot Token
TOKEN = "telegram_bot_token"
YOUTUBE_API_KEY = "youtube_api_key"

bot = telebot.TeleBot(TOKEN)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

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
            channel_name = item["snippet"].get("title")
            channel_link = f"https://www.youtube.com/channel/{channel_id}"
            
            # Store channel info
            channels.append(f"{channel_name} - {channel_link}")
    return channels


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

if __name__ == "__main__":
    bot.infinity_polling()
        
