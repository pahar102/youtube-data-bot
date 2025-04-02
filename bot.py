import os
import telebot

# Environment Variable se BOT_TOKEN lo
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Token check karo
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise ValueError("Invalid or missing BOT_TOKEN. Please set it correctly in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Hello! I am your bot.")

# Bot ko continuously run karne ke liye
bot.polling(none_stop=True)

