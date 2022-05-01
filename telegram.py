import json
import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from db import insert_chat_id, delete_chat_id

API_TOKEN = os.getenv('BOT_APIKEY')


def send_telegram_message(message: str,
                          chat_id: str):
    headers = {'Content-Type': 'application/json'}

    data_dict = {'chat_id': chat_id,
                 'text': message,
                 'parse_mode': 'HTML',
                 'disable_notification': False}

    data = json.dumps(data_dict)
    url = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
    response = requests.post(url,
                             data=data,
                             headers=headers)
    return response


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def welcome_message(message: types.Message) -> None:
    await message.answer(f'Welcome! This bot notifies you about price updates!\n'
                         f'To subscribe to the feed: /sub\n'
                         f'To stop receiving messages: /stop\n')


@dp.message_handler(commands=['sub'])
async def subscribe(message: types.Message) -> None:
    insert_chat_id(message.chat.id)
    await message.answer(f'Subscribed!')


@dp.message_handler(commands=['stop'])
async def subscribe(message: types.Message) -> None:
    delete_chat_id(message.chat.id)
    await message.answer(f'Unsubscribed!')


def start():
    executor.start_polling(dp)
