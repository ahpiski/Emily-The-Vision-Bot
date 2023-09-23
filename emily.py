with open('api_key.txt', 'r') as file : api_key = file.readline().strip()

import telebot
import requests
import os
import cv2
import tempfile
import shutil
import warnings
import sqlite3

try:
    conn = sqlite3.connect('ignoredb')
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ids (id INTEGER PRIMARY KEY);")
    conn.close()
except sqlite3.Error as e:
    print(f"Error: {e}")
    exit()

def add_id_to_database(database_name, id_to_add):
    try:
        conn = sqlite3.connect(database_name)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ids (id INTEGER PRIMARY KEY);")
        print(id_to_add)
        cursor.execute("INSERT INTO ids (id) VALUES (?);", (id_to_add,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")

def remove_id_from_database(database_name, id_to_remove):
    try:
        conn = sqlite3.connect(database_name)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ids WHERE id = ?;", (id_to_remove,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")

def check_id_in_database(database_name, id_to_check):
    try:
        conn = sqlite3.connect(database_name)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ids WHERE id = ?;", (id_to_check,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False



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

@bot.message_handler(func=lambda message: True)
def check_ignore(message):
        text = ''.join(message.text.split()).lower()
        print(text)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if(check_id_in_database('ignoredb', message.from_user.id)) : pass
    bot.reply_to(message, describe_image(get_file_url(message , 'photo')))


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, describe_image(get_file_url(message , 'sticker')))
    
@bot.message_handler(content_types=['animation'])
def handle_animation(message):
        bot.send_chat_action(message.chat.id, 'typing')
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
