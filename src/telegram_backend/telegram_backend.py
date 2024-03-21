import random
import time

import os
from dotenv import load_dotenv
import telegram
import requests
from telegram.ext import Application

# Load environment variables from .env file
load_dotenv()

from openai import AsyncOpenAI
client = AsyncOpenAI()


async def generate_random_shop_item():
    response = await client.chat.completions.create(
    messages=[
    {"role": "system", "content": "You are a random product generator, you only generate a random general product bought in shop"},
    {"role": "user", "content": "Generate a product found in shops"},
    {"role": "user", "content": "Laptop"},
    {"role": "user", "content": "Generate a product found in shops"}
    ],
    model="gpt-3.5-turbo")
    
    return response.choices[0].message.content

# A function to simulate a stream of messages about buying something
async def generate_purchase_messages():
        product = await generate_random_shop_item()
        quantity = random.randint(1, 5)
        price = round(random.uniform(5.99, 999.99), 2)
        message = f"Purchase made: {quantity} x {product} for ${price} each."
        print(message)
        time.sleep(random.uniform(5,10))  # Simulate a delay between messages
        return message
        

async def send_telegram_message(chat_id, message, bot):
    res = await bot.send_message(chat_id=chat_id, text=message)
    res = await bot.sendDocument(chat_id, document ="data/supermarket-receipt-template.jpg")
    
    return res

# Call the function to start generating messages
async def main():
    token = os.getenv('TELEGRAM_TOKEN')
    application = Application.builder().token(token).build()
    bot = application.bot
    chat_id = '283625101'
    while True:
        message = await generate_purchase_messages()
        res = await send_telegram_message(chat_id, message=message, bot=bot)
        #print(res)

# Since we are now using async, we need to run the main coroutine with an event loop
import asyncio

if __name__ == "__main__":
    asyncio.run(main())