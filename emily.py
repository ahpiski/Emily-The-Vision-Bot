with open('api_key.txt', 'r') as file : api_key = file.readline().strip()

import telebot
import requests


bot = telebot.TeleBot(api_key, parse_mode=None)


def get_file_url(message):
    # Get the photo with the highest resolution
    photo = message.photo[-1]
    file_id = photo.file_id

    # Get the file path
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    # Construct the image URL
    url = f'https://api.telegram.org/file/bot{bot.token}/{file_path}'
    return url


@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, get_file_url(message))


@bot.message_handler(content_types=['sticker'])
def describe_photo(message):
    bot.reply_to(message, 'sticker!')


@bot.message_handler(content_types=['animation'])
def describe_photo(message):
    bot.reply_to(message, 'gif!')


bot.infinity_polling()
