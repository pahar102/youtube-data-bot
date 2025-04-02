import telebot
import time
from youtube_api import get_youtube_channels  # Tumhara function jo YouTube data fetch karta hai

# Bot Token
TOKEN = "your_telegram_bot_token"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Send: niche, min_subs, max_subs, country\nExample: Technology, 1000, 10000, US")

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
            for i in range(0, min(len(results), 500), 20):  # ✅ Har 20 results ek message me
                batch = results[i:i+20]
                result_message = "\n".join(batch)
                bot.send_message(message.chat.id, result_message)
                time.sleep(3)  # ✅ 3 second ka delay
        else:
            bot.send_message(message.chat.id, "No results found!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

bot.polling(none_stop=True)
