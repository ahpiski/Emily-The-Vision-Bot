with open('api_key.txt', 'r') as file : api_key = file.readline().strip()

import telebot

bot = telebot.TeleBot(api_key, parse_mode=None)

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(content_types=['photo'])
def describe_photo(message):
    bot.reply_to(message, 'photo!')


@bot.message_handler(content_types=['sticker'])
def describe_photo(message):
    bot.reply_to(message, 'sticker!')


@bot.message_handler(content_types=['animation'])
def describe_photo(message):
    bot.reply_to(message, 'gif!')


bot.infinity_polling()
