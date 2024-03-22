from walker import walk, get_closer_to_first, get_closer_to_second
from threading import Thread
from flask import Flask
import asyncio
import random
import time


import os
from dotenv import load_dotenv
load_dotenv()
import telegram
import requests
from telegram.ext import Application
from openai import AsyncOpenAI
from flask import request



app = Flask(__name__)
client = AsyncOpenAI()

# Hardcoded data for two users
user_data = [
    {
        "user_id": "user123",
        "name": "Alice",
        "balance": 1500.00,
        "currency": "USD",
        "token": "366208780"
        #"token": "283625101"
    },
    {
        "user_id": "user456",
        "name": "Bob",
        "balance": 2300.00,
        "currency": "EUR",
        "token": "347061215"
        #"token": "283625101"

    }
]


async def generate_random_shop_item():
    response = await client.chat.completions.create(
    messages=[
    {"role": "system", "content": "You are a the greatest product comedy generator. You remake the names of some famous products."},
    {"role": "user", "content": "Generate a product"},
    {"role": "assistant", "content": "Shrek Flip-Flops"},
    {"role": "user", "content": "Generate a product"},
    {"role": "assistant", "content": "A Horse named Joe"},
    {"role": "user", "content": "Generate a product"}

    ],
    model="gpt-3.5-turbo")
    
    return response.choices[0].message.content

# A function to simulate a stream of messages about buying something
async def generate_purchase_messages(payment_data):
        product = await generate_random_shop_item()
        quantity = random.randint(1, 2)
        message = f"Purchase made: {quantity} x {product} for ${payment_data['amount']} each."
        return message
        

async def send_telegram_message(chat_id, message, bot):
    res = await bot.send_message(chat_id=chat_id, text=message)
    res = await bot.sendDocument(chat_id=chat_id, document ="analytics/data/supermarket-receipt.jpg")
    # voice_file_path = await generate_voice(message=message)
    # # Correct the return value of generate_voice to be a file path instead of a file object
    # voice_file_path = 'output.mp3'  # Assuming 'output.mp3' is the intended file path
    # with open(voice_file_path, 'rb') as voice:
    #     res = await bot.send_voice(chat_id=chat_id, voice=voice)
    # os.remove(voice_file_path)  # Clean up the file after sending it
    return 200


# async def generate_voice(message):

#     CHUNK_SIZE = 1024
#     url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"

#     headers = {
#     "Accept": "audio/mpeg",
#     "Content-Type": "application/json",
#     "xi-api-key": os.getenv("ELEVEN_LABS")
#     }

#     data = {
#     "text": message,
#     "model_id": "eleven_turbo_v2",
#     "voice_settings": {
#         "stability": 0.5,
#         "similarity_boost": 0.5
#     }
#     }

#     response = requests.post(url, json=data, headers=headers)
    
#     with open('output.mp3', 'wb') as f:
#         for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
#             if chunk:
#                 f.write(chunk)
                
#     return f

# Call the function to start generating messages
async def init_telegram_bot(chat_id, payment_data):
    token = os.getenv('TELEGRAM_TOKEN')
    application = Application.builder().token(token).build()
    bot = application.bot
    message = await generate_purchase_messages(payment_data)
    await send_telegram_message(chat_id, message=message, bot=bot)


@app.route('/', methods=['POST'])
async def receive_payment_notification():
    # Extract the JSON content from the incoming POST request
    payment_data = request.json
    print("Received payment notification:", payment_data)
    station = payment_data.get('station')
    if station == 1:
        res = get_closer_to_first()
    elif station == 2:
        res = get_closer_to_second()
    else:
        return "Error: Invalid station", 400
    
    if res == "red":
        res_value = 0
    elif res == "blue":
        res_value = 1
    
    await init_telegram_bot(user_data[res_value]['token'], payment_data=payment_data)
    return "Payment notification received", 200




# @app.route('/')
# def hello_world():
#     res = "closer to first: " + get_closer_to_first() + '\n'
#     res += "closer to second: " + get_closer_to_second()
#     print("closer to first: ", get_closer_to_first())
#     print("closer to second: ", get_closer_to_second())
#     return res

if __name__ == '__main__':
    t1 = Thread(target=lambda: app.run(host="0.0.0.0", port=5001, use_reloader=False))
    t1.start()
    walk()
    t1.join()

# Since the instruction is to integrate asyncio, we should ensure that the function call is within an async context.
# Assuming `generate_random_shop_item` is an asynchronous function, we should call it using `await` inside an async function.
# Here's how you might integrate it:

# # async function to print a random shop item
# async def print_random_shop_item():
#     random_shop_item = await generate_random_shop_item()
#     print(random_shop_item)

# # Now you would call `print_random_shop_item` from within an async context, for example:
# asyncio.run(print_random_shop_item())
