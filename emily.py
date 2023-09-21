with open('api_key.txt', 'r') as file : api_key = file.readline().strip()

import telebot
import requests
import os
import requests
import cv2
import tempfile
import shutil
import warnings

warnings.filterwarnings("ignore")
bot = telebot.TeleBot(api_key, parse_mode=None)

from transformers import pipeline
describer  = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

def describe_image(url):
     return describer(url)[0]['generated_text']   

def get_file_url(message , content_type):
    # Get the photo with the highest resolution
    if(content_type == "photo") :content = message.photo[-1]
    if(content_type == "sticker") :content = message.sticker
    if(content_type == "animation") :content = message.animation
    file_id = content.file_id

    # Get the file path
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    # Construct the image URL
    url = f'https://api.telegram.org/file/bot{bot.token}/{file_path}'
    return url

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, describe_image(get_file_url(message , 'photo')))


@bot.message_handler(content_types=['sticker'])
def describe_photo(message):
    bot.reply_to(message, describe_image(get_file_url(message , 'sticker')))
    
@bot.message_handler(content_types=['animation'])
def describe_photo(message):
     try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            mp4_file_path = os.path.join(temp_dir, "video.mp4")

            # Download the MP4 file
            response = requests.get(get_file_url(message , 'animation'))
            if response.status_code == 200:
                with open(mp4_file_path, 'wb') as f:
                    f.write(response.content)
            else:
                return None

            # Extract the middle frame
            cap = cv2.VideoCapture(mp4_file_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame_idx = frame_count // 2
            success, frame = cap.read()
            if success:
                middle_frame_path = os.path.join(temp_dir, "middle_frame.jpg")
                cv2.imwrite(middle_frame_path, frame)
                bot.reply_to(message, describe_image(str(middle_frame_path)))
            else:
                return None

     except Exception as e:
         print(f"{e}")
         return None
    

bot.infinity_polling()
